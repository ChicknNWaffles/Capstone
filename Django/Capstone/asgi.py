"""
ASGI config for Capstone project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Capstone.settings')

django_asgi_app = get_asgi_application() # Grab the standard Django HTTP handler

import api.routing

# WEBSOCKETS! The ProtocolTypeRouter tells the server what to do based on the connection type.
application = ProtocolTypeRouter({
    "http": django_asgi_app, # If an old-school HTTP request comes in, send it to normal Django Views!
    
    # WEBSOCKETS! If a websocket upgrade connection comes in, do this instead:
    "websocket": AuthMiddlewareStack( # This stack gives websocket consumers access to the current logged-in user (request.user)
        URLRouter(
            api.routing.websocket_urlpatterns # Hands the connection over to our custom routing list (acting like urls.py for WebSockets)
        )
    ),
})
