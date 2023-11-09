from django.urls import path

from .consumers import GroupChatConsumer,SuperGroupChatConsumer

websocket_urlpatterns = [
    # the chat_user_tpe could be resident , external , admin
    path("ws/estate_group_chats/<estate_id>/<chat_user_type>/", GroupChatConsumer.as_asgi()),
    path("ws/super_admin_group_chats/<chat_user_type>/", SuperGroupChatConsumer.as_asgi()),
]
