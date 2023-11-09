"""
ASGI config for EstateIQAPI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EstateIQAPI.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

#  using the chats routing
from estate_chats import routing as estate_chat_routing
from estate_group_chats import routing as estate_group_chat_routing
from estate_chats.middleware import TokenAuthMiddleware

routing = estate_chat_routing.websocket_urlpatterns
routing += estate_group_chat_routing.websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddleware(URLRouter(routing)),
    }
)
