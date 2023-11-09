from rest_framework import serializers

from estate_user_notifications.models import EstateUserNotification, SuperAdminNotification


class EstateUserNotificationSerializer(serializers.ModelSerializer):
    """
    This serializer is used to list all available
     notification for a user that are not being read
    """
    detail_uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EstateUserNotification
        fields = [
            "id",
            "notification_type",
            "detail_uri",
            "redirect_url",
            "message",
            "read",
            "timestamp",
        ]

    def get_detail_uri(self, obj: EstateUserNotification):
        return obj.get_absolute_url()


class SuperAdminNotificationSerializer(serializers.ModelSerializer):
    """
    This serializer is used to list all available
     notification for a user that are not being read
    """
    detail_uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SuperAdminNotification
        fields = [
            "id",
            "notification_type",
            "detail_uri",
            "redirect_url",
            "message",
            "read",
            "timestamp",
        ]
    def get_detail_uri(self, obj: SuperAdminNotification):
        return obj.get_absolute_url()
