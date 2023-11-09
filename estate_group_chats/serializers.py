from rest_framework import serializers

from estate_group_chats.models import GroupMessage, GroupConversation
from estate_users.serializers import EstateUserLittleInfoSerializer


class GroupMessageSerializer(serializers.ModelSerializer):
    """
    this is used for group messages
    """
    from_user = EstateUserLittleInfoSerializer(read_only=True)
    group_conversation = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupMessage
        fields = [
            "id",
            "group_conversation",
            "from_user",
            "content",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "timestamp",
        ]

    def get_group_conversation(self, obj):
        return str(obj.group_conversation.id)

    def get_id(self, obj):
        return str(obj.id)


class GroupConversationSerializer(serializers.ModelSerializer):
    """
    this is used to create group messages which is being seen by
    all users base on the channel name in an estate
    """
    last_message = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupConversation
        fields = [
            "id",
            "name",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "timestamp",
        ]

    def get_last_message(self, obj: GroupConversation):
        """
        this get the last message sent from the conversation

        """
        messages = obj.group_mesages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return GroupMessageSerializer(message).data

    def get_id(self, obj):
        return str(obj.id)
