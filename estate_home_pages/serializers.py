from rest_framework import serializers

from estate_home_pages.models import WaitList


class WaitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitList
        fields = [
            "email"
        ]
