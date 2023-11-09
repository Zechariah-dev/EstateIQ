from django.contrib.auth import get_user_model
from rest_framework import serializers

from estate_chats.models import Message, Conversation
from estate_users.models import EstateUser
from estate_users.serializers import EstateUserLittleInfoSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    from_user = EstateUserLittleInfoSerializer(read_only=True)
    to_user = EstateUserLittleInfoSerializer(read_only=True)
    conversation_name = serializers.SerializerMethodField()
    id= serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation_name",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
        )
        read_only_fields = [
            "id",
            "timestamp",
        ]

    def get_conversation_name(self, obj):
        return str(obj.conversation.name)

    def get_id(self,obj):
        return str(obj.id)


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "name", "other_user", "last_message")

    def get_last_message(self, obj):
        """
        this get the last message sent from the conversation

        """
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        """
        this enables getting the other user of a message using the id of the user from the
        conversation name
        :param obj:
        :return:
        """
        estate_user_ids = obj.name.split("__")
        context = {}
        for estate_user_id in estate_user_ids:
            if estate_user_id != self.context["estate_user"].id:
                # This is the other participant
                other_user = EstateUser.objects.get(id=estate_user_id)
                return EstateUserLittleInfoSerializer(other_user, context=context).data
