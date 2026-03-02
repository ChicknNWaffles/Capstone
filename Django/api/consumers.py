import json
import asyncio
import subprocess
import os
import struct
import shlex
import tempfile
import shutil
import sys
from channels.generic.websocket import AsyncWebsocketConsumer

# Conditionally import Unix-only PTY modules
if sys.platform != 'win32':
    import pty
    import fcntl
    import termios
from channels.generic.websocket import AsyncWebsocketConsumer

class TerminalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that handles full pseudo-terminal interactions.
    This consumer maintains a persistent WebSocket connection with the frontend
    and translates messages to an isolated background Bash process.
    """
    
    async def connect(self):
        """
        Triggered when a new WebSocket connection is established.
        Accepts the connection and spawns the isolated bash process.
        """
        await self.accept()
        self.spawn_process()

    def spawn_process(self):
        """
        Initializes a new pseudo-terminal (PTY) in a temporary directory.
        Creates a custom `.bashrc` profile to sandbox directory navigation
        and format prompt output cleanly for the frontend client.
        """
        bashrc_content = """
export BASH_SILENCE_DEPRECATION_WARNING=1
ESC=$(printf "\033")
# Fake the prompt directory to look like a friendly project path instead of /tmp/...
# Calculate the real path length to strip it from the PS1 prompt
export REAL_WORKSPACE="$PWD"
export PS1="\[${ESC}[36m\]~/workspace\${PWD#$REAL_WORKSPACE}$\[${ESC}[97m\] "
trap 'printf "${ESC}[32m"' DEBUG

# Override pwd to strip the ugly /tmp/project_... prefix
pwd() {
    local fake_path="~/workspace${PWD#$REAL_WORKSPACE}"
    echo "$fake_path"
}

# Override cd to prevent users from leaving the workspace directory!
cd() {
    # If no arguments or just `cd ~`, go to the workspace root
    if [ -z "$1" ] || [ "$1" = "~" ]; then
        builtin cd "$REAL_WORKSPACE"
        return
    fi
    
    # Try to change directory normally
    builtin cd "$@" >/dev/null 2>&1
    
    # If we escaped the designated workspace, force us back in!
    if [[ "$PWD" != "$REAL_WORKSPACE"* ]]; then
        builtin cd "$REAL_WORKSPACE"
    fi
}
"""
        # Write bash profile to a temporary file
        fd, self.bashrc_path = tempfile.mkstemp(suffix=".bashrc")
        with os.fdopen(fd, 'w') as f:
            f.write(bashrc_content)

        # Create an isolated temporary directory for the workspace session
        self.workspace_dir = tempfile.mkdtemp(prefix="project_", dir=tempfile.gettempdir())

        env = os.environ.copy()
        
        if sys.platform == 'win32':
            # WINDOWS FALLBACK: Use a standard subprocess instead of a full PTY
            # Windows users won't get full interactive terminal features, but it won't crash!
            self.process = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.workspace_dir,
                env=env,
                bufsize=0,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Use the subprocess pipes for I/O instead of a raw file descriptor
            self.fd = None
            self.read_task = asyncio.create_task(self.read_windows_output())
            
        else:
            # UNIX/MAC: Fork a new pseudo-terminal simulating an interactive terminal device
            pid, self.fd = pty.fork()
            
            if pid == 0:
                # Child process: configure environment and initialize shell
                env["TERM"] = "xterm-256color"
                
                # Start the shell isolated within the temporary workspace
                os.chdir(self.workspace_dir)
                os.execvpe("bash", ["bash", "--init-file", self.bashrc_path], env)
            else:
                # Parent process: monitor the child process asynchronously
                self.process = pid
                
                # Switch PTY file descriptor to non-blocking mode
                flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
                fcntl.fcntl(self.fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                
                # Initialize the background output polling loop
                self.read_task = asyncio.create_task(self.read_output())

    async def disconnect(self, close_code):
        """Handles WebSocket disconnect events and ensures resources are freed."""
        self.cleanup_process()

    def cleanup_process(self):
        """Terminates the shell process and purges temporary files/directories."""
        if hasattr(self, 'process') and self.process:
            if sys.platform == 'win32':
                try:
                    self.process.terminate()
                except Exception:
                    pass
            else:
                try:
                    os.kill(self.process, 9)
                except OSError:
                    pass
            self.process = None

        if hasattr(self, 'fd') and self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
            
        if hasattr(self, 'read_task') and self.read_task:
            self.read_task.cancel()
            self.read_task = None
            
        # Clean up the temporary bashrc file
        if hasattr(self, 'bashrc_path') and os.path.exists(self.bashrc_path):
            try:
                os.remove(self.bashrc_path)
            except OSError:
                pass

        # Clean up the temporary workspace directory
        if hasattr(self, 'workspace_dir') and os.path.exists(self.workspace_dir):
            try:
                shutil.rmtree(self.workspace_dir)
            except OSError:
                pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming data from the WebSocket.
        Parses resize/kill JSON control commands from the frontend or
        forwards raw keystroke input directly to the bash process.
        """
        if not hasattr(self, 'process') or not self.process:
            return
            
        if text_data and text_data.startswith('{'):
            try:
                data = json.loads(text_data)
                
                if data.get('type') == 'resize':
                    # Windows doesn't support PTY resizing naturally through termios
                    if sys.platform != 'win32' and self.fd:
                        cols = data.get('cols', 80)
                        rows = data.get('rows', 24)
                        winsize = struct.pack("HHHH", rows, cols, 0, 0)
                        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
                    return
                    
                elif data.get('type') == 'kill':
                    # Terminate current session and spawn a fresh replacement
                    self.cleanup_process()
                    await self.send(text_data='\r\n[Process Terminated by User]\r\n\r\n')
                    self.spawn_process()
                    return
                    
            except json.JSONDecodeError:
                pass
                
        # Forward direct terminal keystrokes to the underlying process
        try:
            input_data = text_data.encode('utf-8') if text_data else bytes_data
            
            if sys.platform == 'win32':
                if self.process and self.process.stdin:
                    self.process.stdin.write(input_data)
                    self.process.stdin.flush()
            else:
                if self.fd is not None:
                    os.write(self.fd, input_data)
        except (OSError, BrokenPipeError):
            pass

    async def read_windows_output(self):
        """Fallback background loop to read standard Windows subprocess stdout."""
        while hasattr(self, 'process') and self.process:
            try:
                await asyncio.sleep(0.01)
                if self.process.stdout:
                    # Non-blocking read trick for Windows PIPE
                    output = self.process.stdout.read1(1024)
                    if output:
                        await self.send(text_data=output.decode('utf-8', errors='replace'))
            except Exception:
                break

    async def read_output(self):
        """Asynchronously polls the pseudo-terminal output and pushes to WebSocket."""
        while self.fd:
            try:
                await asyncio.sleep(0.01)
                output = os.read(self.fd, 1024)
                if output:
                    await self.send(text_data=output.decode('utf-8', errors='replace'))
            except BlockingIOError:
                pass
            except OSError:
                self.cleanup_process()
                await self.send(text_data='\r\n[Process exited]\r\n')
                break
            except Exception:
                break
