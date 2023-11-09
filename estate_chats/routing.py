from django.urls import path

from .consumers import ChatConsumer


websocket_urlpatterns = [
    # this url enables creating conversation,messages and viewing all message
    path("ws/estate_chats/<estate_id>/<conversation_name>/", ChatConsumer.as_asgi()),
]
