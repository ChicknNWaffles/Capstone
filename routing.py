from django.urls import re_path
from api.consumers import TerminalConsumer

websocket_urlpatterns = [
    re_path(r'ws/terminal/$', TerminalConsumer.as_asgi()), # ADDED: Connects the 'ws/terminal/' URL to our Python terminal code
]
