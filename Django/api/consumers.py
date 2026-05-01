import json
import asyncio
import subprocess
import os
import struct
import tempfile
import shutil
import sys

if sys.platform != "win32":
    import pty
    import fcntl
    import termios

from channels.generic.websocket import AsyncWebsocketConsumer

# Global session store: maps session_key -> TerminalSession
_sessions: dict = {}


class TerminalSession:
    """
    Holds the state of a single persistent terminal session.
    Survives WebSocket disconnects and can be reattached.
    """

    def __init__(self):
        self.fd = None
        self.process = None
        self.workspace_dir = None
        self.bashrc_path = None
        self.read_task = None
        self.consumer = None  # currently attached WebSocket consumer
        self.buffer = b""

    def is_alive(self) -> bool:
        if sys.platform == "win32":
            return self.process is not None and self.process.poll() is None
        return self.process is not None and self.fd is not None

    def detach(self):
        """Detach the consumer without killing the process."""
        self.consumer = None

    def attach(self, consumer: "TerminalConsumer"):
        """Attach a new consumer to this session."""
        self.consumer = consumer


class TerminalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that proxies a persistent PTY session.

    Sessions are keyed by Django session key so the same user
    can reconnect and continue where they left off.
    """

    # ------------------------------------------------------------------ #
    #  Connection lifecycle                                                #
    # ------------------------------------------------------------------ #

    async def connect(self):
        await self.accept()

        session_key = self.scope["session"].session_key or "anonymous"

        if session_key in _sessions and _sessions[session_key].is_alive():
            # Reattach to the existing session
            self.session = _sessions[session_key]
            self.session.attach(self)
            if self.session.buffer:
                await self.send(text_data=self.session.buffer.decode("utf-8", errors="replace"))
        else:
            # Spin up a brand-new session
            self.session = TerminalSession()
            self.session.attach(self)
            _sessions[session_key] = self.session
            await asyncio.get_event_loop().run_in_executor(None, self._spawn_process)

        # Start (or restart) the read loop for this consumer
        if self.session.read_task is None or self.session.read_task.done():
            self.session.read_task = asyncio.create_task(self._read_output())

    async def disconnect(self, close_code):
        """Detach consumer but keep the process alive for future reconnects."""
        if hasattr(self, "session"):
            self.session.detach()

    # ------------------------------------------------------------------ #
    #  Process spawning                                                    #
    # ------------------------------------------------------------------ #

    def _spawn_process(self):
        """Create a sandboxed PTY/subprocess. Called in a thread executor."""
        bashrc_content = r"""
export BASH_SILENCE_DEPRECATION_WARNING=1
ESC=$(printf "\033")
export REAL_WORKSPACE="$PWD"
export PS1="\[${ESC}[36m\]~/workspace\${PWD#$REAL_WORKSPACE}$\[${ESC}[97m\] "
trap 'printf "${ESC}[32m"' DEBUG

pwd() {
    echo "~/workspace${PWD#$REAL_WORKSPACE}"
}

cd() {
    if [ -z "$1" ] || [ "$1" = "~" ]; then
        builtin cd "$REAL_WORKSPACE"
        return
    fi
    builtin cd "$@" >/dev/null 2>&1
    if [[ "$PWD" != "$REAL_WORKSPACE"* ]]; then
        builtin cd "$REAL_WORKSPACE"
    fi
}
"""
        fd, self.session.bashrc_path = tempfile.mkstemp(suffix=".bashrc")
        with os.fdopen(fd, "w") as f:
            f.write(bashrc_content)

        self.session.workspace_dir = tempfile.mkdtemp(
            prefix="project_", dir=tempfile.gettempdir()
        )

        env = os.environ.copy()

        if sys.platform == "win32":
            self._spawn_windows(env)
        else:
            self._spawn_unix(env)

    def _spawn_unix(self, env: dict):
        """Fork a PTY on Unix/macOS/Linux."""
        env["TERM"] = "xterm-256color"
        pid, fd = pty.fork()

        if pid == 0:
            # Child: exec bash inside the workspace
            os.chdir(self.session.workspace_dir)
            os.execvpe("bash", ["bash", "--init-file", self.session.bashrc_path], env)
        else:
            # Parent
            self.session.process = pid
            self.session.fd = fd

            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def _spawn_windows(self, env: dict):
        """Spawn cmd.exe on Windows as a fallback."""
        self.session.process = subprocess.Popen(
            ["cmd.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.session.workspace_dir,
            env=env,
            bufsize=0,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.session.fd = None

    # ------------------------------------------------------------------ #
    #  Incoming messages                                                   #
    # ------------------------------------------------------------------ #

    async def receive(self, text_data=None, bytes_data=None):
        if not self.session.is_alive():
            return

        # Try to parse control messages first
        if text_data and text_data.startswith("{"):
            try:
                msg = json.loads(text_data)
                msg_type = msg.get("type")

                if msg_type == "resize":
                    self._resize(msg.get("cols", 80), msg.get("rows", 24))
                    return

                if msg_type == "kill":
                    self._cleanup_session()
                    self.session.buffer = b""
                    await self.send(
                        # \x1b[2J clears screen, \x1b[3J clears scrollback, \x1b[H moves cursor home
                        text_data="\x1b[2J\x1b[3J\x1b[H"
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._spawn_process
                    )
                    self.session.read_task = asyncio.create_task(self._read_output())
                    return

            except json.JSONDecodeError:
                pass  # Not a control message — fall through to raw input

        # Forward raw keystrokes to the process
        try:
            payload = text_data.encode("utf-8") if text_data else bytes_data
            if sys.platform == "win32":
                if self.session.process and self.session.process.stdin:
                    self.session.process.stdin.write(payload)
                    self.session.process.stdin.flush()
            else:
                if self.session.fd is not None:
                    os.write(self.session.fd, payload)
        except (OSError, BrokenPipeError):
            pass

    # ------------------------------------------------------------------ #
    #  Output reading                                                      #
    # ------------------------------------------------------------------ #

    async def _read_output(self):
        """Continuously read PTY/pipe output and forward to the attached consumer."""
        if sys.platform == "win32":
            await self._read_windows()
        else:
            await self._read_unix()

    async def _read_unix(self):
        loop = asyncio.get_event_loop()
        while self.session.fd is not None:
            try:
                await asyncio.sleep(0.01)
                output = os.read(self.session.fd, 4096)
                if output:
                    self.session.buffer += output
                    if len(self.session.buffer) > 65536:
                        self.session.buffer = self.session.buffer[-65536:]
                    if self.session.consumer:
                        await self.session.consumer.send(
                            text_data=output.decode("utf-8", errors="replace")
                        )
            except BlockingIOError:
                pass
            except OSError:
                # Process exited
                if self.session.consumer:
                    await self.session.consumer.send(
                        text_data="\r\n\x1b[31m[Process exited]\x1b[0m\r\n"
                    )
                self._cleanup_session()
                break
            except Exception:
                break

    async def _read_windows(self):
        loop = asyncio.get_event_loop()
        while self.session.is_alive():
            try:
                # Run blocking read in a thread so the event loop stays free
                output = await loop.run_in_executor(
                    None, self.session.process.stdout.read, 1024
                )
                if output:
                    self.session.buffer += output
                    if len(self.session.buffer) > 65536:
                        self.session.buffer = self.session.buffer[-65536:]
                    if self.session.consumer:
                        await self.session.consumer.send(
                            text_data=output.decode("utf-8", errors="replace")
                        )
                elif not output:
                    break
            except Exception:
                break

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _resize(self, cols: int, rows: int):
        """Send a TIOCSWINSZ ioctl to resize the PTY window."""
        if sys.platform == "win32" or self.session.fd is None:
            return
        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.session.fd, termios.TIOCSWINSZ, winsize)
        except OSError:
            pass

    def _cleanup_session(self):
        """Kill the running process and free all associated resources."""
        s = self.session

        if s.read_task:
            s.read_task.cancel()
            s.read_task = None

        if sys.platform == "win32":
            if s.process:
                try:
                    s.process.terminate()
                except Exception:
                    pass
        else:
            if s.process:
                try:
                    os.kill(s.process, 9)
                except OSError:
                    pass
            if s.fd is not None:
                try:
                    os.close(s.fd)
                except OSError:
                    pass

        s.process = None
        s.fd = None

        if s.bashrc_path and os.path.exists(s.bashrc_path):
            try:
                os.remove(s.bashrc_path)
            except OSError:
                pass

        if s.workspace_dir and os.path.exists(s.workspace_dir):
            try:
                shutil.rmtree(s.workspace_dir)
            except OSError:
                pass

        s.bashrc_path = None
        s.workspace_dir = None


class EditorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for collaborative file editing.

    All users with the same project open join a Channels group
    (editor_{project_id}). When one user edits, the change is
    broadcast to all others in the group AND saved to S3.
    """

    async def connect(self):
        # Accept all connections immediately — group join happens on first message
        self.group_name = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") == "content_change":
            file_id = data.get("file_id")
            content = data.get("content", "")

            # Look up the project from the file so we don't rely on session timing
            project_id = await asyncio.get_event_loop().run_in_executor(
                None, self._get_project_id, file_id
            )
            if not project_id:
                return

            # Join the project group if not already in it
            new_group = f"editor_{project_id}"
            if self.group_name != new_group:
                if self.group_name:
                    await self.channel_layer.group_discard(self.group_name, self.channel_name)
                self.group_name = new_group
                await self.channel_layer.group_add(self.group_name, self.channel_name)

            # Save to S3 in a background thread (non-blocking)
            await asyncio.get_event_loop().run_in_executor(
                None, self._save_to_s3, file_id, content
            )

            # Broadcast to all other collaborators in the project
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "editor.update",
                    "file_id": file_id,
                    "content": content,
                    "sender_channel": self.channel_name,
                },
            )

    def _get_project_id(self, file_id):
        from projectfiles.models import ProjectFile
        try:
            return ProjectFile.objects.get(id=file_id).project_id
        except Exception:
            return None

    def _save_to_s3(self, file_id, content):
        from projectfiles.models import ProjectFile
        from api.file_service import file_service
        try:
            file_obj = ProjectFile.objects.get(id=file_id)
            file_service.create_file(
                file_obj.project.id,
                file_obj.branch.name,
                file_obj.name,
                content,
            )
        except Exception as e:
            print(f"[EditorConsumer] S3 save error: {e}")

    async def editor_update(self, event):
        """Called by group_send — forward to WebSocket unless we are the sender."""
        if event.get("sender_channel") == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            "type": "content_change",
            "file_id": event["file_id"],
            "content": event["content"],
        }))