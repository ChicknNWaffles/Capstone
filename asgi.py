import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import Capstone.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Capstone.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), # ADDED: HTTP requests go here
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                Capstone.routing.websocket_urlpatterns # ADDED: WebSocket requests go to our routing file
            )
        )
    ),
})
