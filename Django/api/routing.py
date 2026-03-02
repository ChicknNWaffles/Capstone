from django.urls import re_path
from . import consumers

# WEBSOCKETS! This acts just like `urls.py`, but it's specifically for WebSocket connections.
# When a WS request comes in (wss://url/ws/terminal/), it hands it off to our TerminalConsumer class!
websocket_urlpatterns = [
    re_path(r'ws/terminal/$', consumers.TerminalConsumer.as_asgi()), # .as_asgi() creates an instance of the class for the connection
]
