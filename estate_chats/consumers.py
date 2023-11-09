import json
import uuid
from uuid import UUID

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.serializers import ListSerializer

from estate_chats.serializers import MessageSerializer

from estate_chats.models import Conversation, Message
from estate_users.models import EstateUser
from estates.models import Estate

User = get_user_model()


# Note: You might notice we are always converting the user.id to string
# and that is because the user.id is a UUID and  UUID cant be serialized
# So we need to convert it to string and also the conversation__name will be converted
# to string since it was created by adding two uuid which makes it a uuid also

class UUIDEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, list):
            return [self.default(item) for item in obj]
        elif isinstance(obj, ListSerializer):
            return [self.default(item) for item in obj]
        return super().default(obj)


def get_or_create_conversation(estate_user, name):
    """
    :param estate_user: The logged-in estate_user
    :param name: user1_id__user2__id
    :return: conversation
    """
    #  filter base on the conversation
    conversation = Conversation.objects.filter(name=name)
    if conversation.exists():
        #  this returns the conversation
        return conversation.first()
    estate_user_ids = name.split("__")
    #  Get all the user conversations in which the logged-in user is in the conversation
    estate_user_conversation_qs = Conversation.objects.filter(name__icontains=str(estate_user.id))
    #  if the user conversation exists
    if estate_user_conversation_qs.exists():
        for estate_user_id in estate_user_ids:
            # use the order user id
            if estate_user_id != str(estate_user.id):
                conversation_qs = estate_user_conversation_qs.filter(name__icontains=estate_user_id)
                if conversation_qs.exists():
                    return conversation_qs.first()

    # if the conversation does not exist from the above then we create a new one
    conversation, created = Conversation.objects.get_or_create(name=name)
    return conversation


def get_estate_with_id(estate_id):
    """
    this uses the estate id to get the estate
    :param estate_id:
    :return:
    """
    estate = Estate.objects.filter(estate_id=estate_id).first()
    if not estate:
        return None
    return estate


def get_estate_user_with_estate(estate: Estate, user: User):
    """
    :param estate: The estate
    :param user: The user
    :return: estate_user
    """
    estate_user = estate.estateuser_set.filter(user=user).first()
    if not estate_user:
        return None
    return estate_user


def user_has_user_type(user: User, user_type):
    """
    this is used to check if the user has an estate_user with the user_type
    :param user: User
    :param user_type: ADMIN, RESIDENT
    :return: True or False
    """
    estate_user = EstateUser.objects.filter(user=user, user_type=user_type).first()
    if not estate_user:
        return False
    return True


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications. and also used between only two estate users
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.estate_id = None
        self.user = None
        self.conversation_name = None
        self.conversation = None
        self.estate = None
        self.estate_user = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        self.conversation_name = (
            f"{self.scope['url_route']['kwargs']['conversation_name']}"
        )
        self.estate_id = (
            f"{self.scope['url_route']['kwargs']['estate_id']}"
        )
        # Get the estate with the estate id in our database
        self.estate = get_estate_with_id(estate_id=self.estate_id)
        if not self.estate:
            # If the estate does not exist I then disconnect
            self.disconnect(code=1014)

        self.estate_user = get_estate_user_with_estate(estate=self.estate, user=self.user)

        # validate the conversation name
        estate_user_ids = self.conversation_name.split("__")
        #  in here I split the conversation name which is user1_id__user2__id
        # then I check if the ids exists
        for estate_user_id in estate_user_ids:
            estate_user = EstateUser.objects.filter(id=estate_user_id).first()
            if not estate_user:
                # if the user does not exist I disconnect
                self.disconnect(code=1014)
            if estate_user not in self.estate.estateuser_set.all():
                # Disconnect because the user is not part of the estate users
                self.disconnect(code=1014)

        # the get the conversation with the user id passed in the url which is user_id__other_user_id
        self.conversation = get_or_create_conversation(self.estate_user, str(self.conversation_name))
        # update the conversation name if the user_id is user2__id__user1__id
        self.conversation_name = str(self.conversation.name)

        # set the channel name
        async_to_sync(self.channel_layer.group_add)(
            str(self.conversation_name),
            self.channel_name,
        )
        # show list of online users
        self.send_json(
            {
                "type": "online_user_list",
                "estate_users": [str(estate_user.id) for estate_user in self.conversation.online.all()],
            }
        )

        # send and event to every one on this conversation that this logged-in user just join
        async_to_sync(self.channel_layer.group_send)(
            str(self.conversation_name),
            {
                "type": "user_join",
                "estate_user_id": str(self.estate_user.id),
            },
        )

        # add the current user online users
        self.conversation.online.add(self.estate_user)

        #  this shows the last ten message on the conversation
        messages = self.conversation.messages.all().order_by("-timestamp")[:50]
        message_count = self.conversation.messages.all().count()
        self.conversation.messages.filter(read=False).update(read=True)
        self.send_json(
            {
                "type": "last_50_messages",
                "messages": MessageSerializer(messages, many=True).data,
                "has_more": message_count > 5,
            }
        )

    def disconnect(self, code):
        # Check if the users is authenticated and if he is  then I remove the user
        # from online users in the Conversation
        if self.user.is_authenticated:
            # send the leave event to the room
            if self.conversation:
                self.conversation.online.remove(self.estate_user)
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "user_leave",
                    "estate_user_id": str(self.estate_user.id),
                },
            )
        return super().disconnect(code)

    def get_receiver(self):
        #  it uses the id's in the conversation_name to get the receiver id
        estate_user_ids = self.conversation_name.split("__")
        for estate_user_id in estate_user_ids:
            if estate_user_id != str(self.estate_user.id):
                # This is the receiver
                return EstateUser.objects.get(id=estate_user_id)

    def receive_json(self, content, **kwargs):
        #  this receives json is used to receive any echo from the front end
        message_type = content["type"]

        if message_type == "read_messages":
            # the is used to read all messages by the receiver
            messages_to_me = self.conversation.messages.filter(to_user=self.estate_user)
            messages_to_me.update(read=True)

            # Update the unread message count
            unread_count = Message.objects.filter(to_user=self.estate_user, read=False,
                                                  conversation=self.conversation).count()
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "unread_count",
                    "unread_count": unread_count,
                },
            )

        if message_type == "all_messages":
            messages = self.conversation.messages.all().order_by("-timestamp")
            # read all messages
            self.conversation.messages.filter(read=False).update(read=True)
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "all_messages",
                    "all_messages": json.dumps(MessageSerializer(messages, many=True).data, cls=UUIDEncoder),
                },
            )

        if message_type == "typing":
            #  this is to let the other user knows you are typing
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "typing",
                    "estate_user_id": str(self.estate_user.id),
                    "typing": content.get("typing"),
                },
            )

        if message_type == "chat_message":
            #  this is used to create message
            if not self.estate_user.on_to_one_message:
                # if the user doesn't have the permission
                # to send message I" disconnect the connection
                self.disconnect(code=1014)
            message = Message.objects.create(
                from_user=self.estate_user,
                to_user=self.get_receiver(),
                content=content.get("message"),
                conversation=self.conversation,
            )

            if self.conversation.online.count() > 1:
                # If the other user is online then message has been read
                message.read = True

            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "chat_message_echo",
                    "estate_user_id": str(self.estate_user.id),
                    "message": json.dumps(MessageSerializer(message).data, cls=UUIDEncoder),
                },
            )

            # This is a notification in which the receiver could listen to (Same as the chat message echo)
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "new_message_notification",
                    "estate_user_id": str(self.estate_user.id),
                    "message": json.dumps(MessageSerializer(message).data, cls=UUIDEncoder),
                },
            )
        if message_type == "is_online":
            # this returns boolean base on the other user online status
            # this check if the logged-in user count is greater than one the .it shows the other user is not online
            # because right now if it is only one that means the online user is 1
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "is_online",
                    "is_online": self.conversation.online.count() > 1,
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

    def is_online(self, event):
        self.send_json(event)

    def online_user_list(self, event):
        self.send_json(event)

    def all_messages(self, event):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content):
        #  this  class method is created if you want to encode a json
        return json.dumps(content, cls=UUIDEncoder)
