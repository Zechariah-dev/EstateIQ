import json

from channels.generic.websocket import JsonWebsocketConsumer

from estate_chats.consumers import get_estate_with_id, get_estate_user_with_estate, UUIDEncoder, \
    user_has_user_type
from estate_group_chats.models import GroupConversation, GroupMessage
from estate_group_chats.serializers import GroupMessageSerializer
from asgiref.sync import async_to_sync


class GroupChatConsumer(JsonWebsocketConsumer):
    """
    this consumer is used between multiple users in an estate
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.estate_id = None
        self.user = None
        self.chat_user_type = None
        self.group_conversation = None
        self.group_conversation_name = None
        self.estate = None
        self.estate_user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        # this could be resident or admin or external
        self.chat_user_type = (
            f"{self.scope['url_route']['kwargs']['chat_user_type']}"
        )

        # the chat_user_type has to be one of the if statement
        if self.chat_user_type != "admin":
            if self.chat_user_type != "resident":
                if self.chat_user_type != "external":
                    # Disconnect the endpoint
                    if self.chat_user_type != "every_one":
                        self.disconnect(code=1014)

        self.estate_id = (
            f"{self.scope['url_route']['kwargs']['estate_id']}"
        )
        # Get the estate with the estate id in our database
        self.estate = get_estate_with_id(estate_id=self.estate_id)
        if not self.estate:
            # If the estate does not exist I then disconnect
            self.send_json(
                {
                    "type": "error",
                    "message": "Estate does not exist",
                }
            )
            self.disconnect(code=1014)

        self.group_conversation_name = f"{self.estate_id}_{self.chat_user_type}"
        # Get the estate user
        self.estate_user = get_estate_user_with_estate(estate=self.estate, user=self.user)

        # Check if the estate_user would have access to this chat_user_type
        if self.estate_user.user_type != "ADMIN":
            if self.chat_user_type != "every_one":
                if f"{self.chat_user_type}".upper() != self.estate_user.user_type:
                    self.send_json(
                        {
                            "type": "error",
                            "message": "You dont have access to connect ",
                        }
                    )
                    self.disconnect(code=1014)

        # Get or create the conversation
        group_conversation, created = GroupConversation.objects.get_or_create(
            name=self.group_conversation_name
        )
        # Set the group conversation
        self.group_conversation = group_conversation

        # set the channel name
        async_to_sync(self.channel_layer.group_add)(
            str(self.group_conversation_name),
            self.channel_name,
        )

        # show list of online users
        self.send_json(
            {
                "type": "online_user_list",
                "estate_users": [str(estate_user.id) for estate_user in self.group_conversation.online.all()],
            }
        )

        # send and event to every one on this conversation that this logged-in user just join
        async_to_sync(self.channel_layer.group_send)(
            str(self.group_conversation_name),
            {
                "type": "user_join",
                "estate_user_id": str(self.estate_user.id),
            },
        )

        # add the current user online users
        self.group_conversation.online.add(self.estate_user)

        #  this shows the last ten message on the conversation
        messages = self.group_conversation.group_mesages.all().order_by("-timestamp")[:50]
        message_count = self.group_conversation.group_mesages.all().count()

        self.send_json(
            {
                "type": "last_50_messages",
                "messages": self.encode_json(GroupMessageSerializer(messages, many=True).data),
                "has_more": message_count > 5,
            }
        )

    def disconnect(self, code):
        # Check if the users is authenticated and if he is  then I remove the user
        # from online users in the Conversation
        # Check if the users is authenticated and if he is  then I remove the user
        # from online users in the Conversation
        if self.user.is_authenticated:
            # send the leave event to the room
            if self.estate_user in self.group_conversation.online.all():
                self.group_conversation.online.remove(self.estate_user)
            async_to_sync(self.channel_layer.group_send)(
                str(self.group_conversation_name),
                {
                    "type": "user_leave",
                    "estate_user_id": str(self.estate_user.id),
                },
            )
        return super().disconnect(code)

    def receive_json(self, content, **kwargs):
        #  this receives json is used to receive any echo from the front end
        message_type = content["type"]

        if message_type == "typing":
            #  this is to let the other user knows you are typing
            async_to_sync(self.channel_layer.group_send)(
                str(self.group_conversation_name),
                {
                    "type": "typing",
                    "estate_user_id": str(self.estate_user.id),
                    "typing": content["typing"],
                },
            )

        if message_type == "chat_message":
            #  this is used to create message
            message = GroupMessage.objects.create(
                from_user=self.estate_user,
                content=content["message"],
                group_conversation=self.group_conversation,
            )

            async_to_sync(self.channel_layer.group_send)(
                str(self.group_conversation_name),
                {
                    "type": "chat_message_echo",
                    "estate_user_id": str(self.estate_user.id),
                    "message": self.encode_json(GroupMessageSerializer(message).data),
                },
            )
        if message_type == "all_messages":
            messages = self.group_conversation.group_mesages.all().order_by("-timestamp")
            # read all messages
            async_to_sync(self.channel_layer.group_send)(
                str(self.group_conversation_name),
                {
                    "type": "all_messages",
                    "all_messages": self.encode_json(GroupMessageSerializer(messages, many=True).data),
                },
            )

        return super().receive_json(content, **kwargs)

    def chat_message_echo(self, event):
        self.send_json(event)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)

    def typing(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def online_user_list(self, event):
        self.send_json(event)

    def all_messages(self, event):
        self.send_json(event)

    def error(self, event):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content):
        #  this  class method is created if you want to encode a json
        return json.dumps(content, cls=UUIDEncoder)


class SuperGroupChatConsumer(JsonWebsocketConsumer):
    """
    this consumer is used between multiple users in an estate
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.chat_user_type = None
        self.group_conversation = None
        self.group_conversation_name = None
        self.estate_user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            # If the user is not authenticated I disconnect
            self.disconnect(code=1014)

        self.accept()
        # this could be resident or admin or external
        self.chat_user_type = (
            f"{self.scope['url_route']['kwargs']['chat_user_type']}"
        )

        # the chat_user_type has to be one of the if statement
        if self.chat_user_type != "admin":
            if self.chat_user_type != "resident":
                if self.chat_user_type != "external":
                    # Disconnect the endpoint
                    if self.chat_user_type != "every_one":
                        self.disconnect(code=1014)

        self.group_conversation_name = f"superadmin_{self.chat_user_type}"

        # Get or create the conversation
        group_conversation, created = GroupConversation.objects.get_or_create(
            name=self.group_conversation_name,
            is_super_user=True
        )
        self.group_conversation = group_conversation

        # Check if the estate_user would have access to this chat_user_type
        if not self.user.is_superuser:
            # if the user is not a staff
            if not self.user.is_staff:
                # if the chat_user_type is not every one
                if self.chat_user_type != "every_one":
                    if not user_has_user_type(user=self.user, user_type=f"{self.chat_user_type}".upper()):
                        self.send_json(
                            {
                                "type": "error",
                                "message": "You dont have access to connect to this",
                            }
                        )
                        self.disconnect(code=1014)

        # set the channel name
        async_to_sync(self.channel_layer.group_add)(
            str(self.group_conversation_name),
            self.channel_name,
        )

        #  this shows the last ten message on the conversation
        messages = self.group_conversation.group_mesages.all().order_by("-timestamp")[:50]
        message_count = self.group_conversation.group_mesages.all().count()

        self.send_json(
            {
                "type": "last_50_messages",
                "messages": self.encode_json(GroupMessageSerializer(messages, many=True).data),
                "has_more": message_count > 5,
            }
        )

    def disconnect(self, code):
        # Check if the users is authenticated
        # Check if the user is one of the staff
        return super().disconnect(code)

    def receive_json(self, content, **kwargs):
        #  this receives json is used to receive any echo from the front end
        message_type = content.get("type")

        if message_type == "chat_message":
            #  this is used to create message
            if not self.user.is_superuser:
                if not self.user.is_staff:
                    # If the user is not a staff I disconnect
                    self.send_json(
                        {
                            "type": "error",
                            "messages": "You don't have access to send message",
                        }
                    )

            if self.user.is_staff or self.user.is_superuser:
                # Only a super can create message in here
                message = GroupMessage.objects.create(
                    is_super_user=True,
                    content=content.get("message"),
                    group_conversation=self.group_conversation,
                )

                async_to_sync(self.channel_layer.group_send)(
                    str(self.group_conversation_name),
                    {
                        "type": "chat_message_echo",
                        "is_super_user": True,
                        "message": self.encode_json(GroupMessageSerializer(message).data),
                    },
                )
        if message_type == "all_messages":
            messages = self.group_conversation.group_mesages.all().order_by("-timestamp")
            # read all messages
            async_to_sync(self.channel_layer.group_send)(
                str(self.group_conversation_name),
                {
                    "type": "all_messages",
                    "all_messages": self.encode_json(GroupMessageSerializer(messages, many=True).data),
                },
            )
        return super().receive_json(content, **kwargs)

    def chat_message_echo(self, event):
        self.send_json(event)

    def typing(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def online_user_list(self, event):
        self.send_json(event)

    def all_messages(self, event):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content):
        #  this  class method is created if you want to encode a json
        return json.dumps(content, cls=UUIDEncoder)
