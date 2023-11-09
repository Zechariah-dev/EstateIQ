from rest_framework import serializers

from estate_adverts.models import EstateAdvertisement, EstateAnnouncement, EstateReminder
from django.utils import timezone


class EstateAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateAdvertisement
        fields = "__all__"


class EstateAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateAnnouncement
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("announcement_date"):
            if attrs.get("announcement_date") < timezone.now():
                raise serializers.ValidationError("announcement date must be greater than current date")
        return attrs


class EstateReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateReminder
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("reminder_date"):
            # 2023-02-05T9:10:00
            if attrs.get("reminder_date") < timezone.now():
                raise serializers.ValidationError("reminder date must be greater than current date")
        return attrs
