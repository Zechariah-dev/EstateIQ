from rest_framework import serializers

from estate_complaints.models import EstateComplaint
from estate_users.serializers import (
    EstateUserSerializer,
    EstateUserLittleInfoSerializer,
)


class EstateComplaintSerializer(serializers.ModelSerializer):
    """
    this serializer is used to list ,create and update the estate complaint and can be used
    by any user type
    """

    estate_user = EstateUserLittleInfoSerializer(read_only=True)
    updated_by = EstateUserLittleInfoSerializer(read_only=True)

    class Meta:
        model = EstateComplaint
        fields = [
            "id",
            "estate",
            "estate_user",
            "title",
            "reason",
            "case_id",
            "receivers",
            "message",
            "status",
            "updated_time",
            "updated_by",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "estate",
            "estate_user",
            "updated_time",
            "case_id",
            "updated_by",
            "timestamp",
        ]
