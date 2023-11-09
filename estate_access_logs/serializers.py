from rest_framework import serializers

from estate_access_logs.models import EstateAccessLog, WAYBILL_TYPE
from estate_users.models import GENDER_CHOICES
from estate_users.serializers import EstateUserLittleInfoSerializer
from django.utils import timezone


class EstateAccessLogSerializer(serializers.ModelSerializer):
    estate_user = EstateUserLittleInfoSerializer(read_only=True)
    updated_by = EstateUserLittleInfoSerializer(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EstateAccessLog
        fields = [
            "id",
            "estate_user",
            "updated_by",
            "estate",
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "from_date",
            "to_date",
            "access",
            "access_type",
            "category",
            "access_code",
            "status",
            "verified_time",
            "timestamp",
            # add this new
            "vehicle_number",
            "waybill_type",
            "item_type",
            "access_log_type",
            "gender",
            "quantity",
        ]
        read_only_fields = [
            "estate_user",
            "updated_by",
            "access_code",
            "id",
            "estate",
            "access",
            "verified_time",
            "status",
            "timestamp",
        ]

    def get_status(self, obj: EstateAccessLog):
        if obj.to_date:
            if obj.to_date > timezone.now():
                return "ENTRY"
            return "EXIT"
        return ""

    def validate_from_date(self, from_date):
        #  when updating the start date could be none so i have to prepare for it
        # if from_date:
        #     if from_date < timezone.now():
        #         raise serializers.ValidationError(
        #             "An error occurred . Please the arrival and departure time must be greater than current time "
        #         )
        return from_date

    def validate(self, attrs):
        to_date = attrs.get("to_date")
        from_date = attrs.get("from_date")
        if from_date and to_date:
            if to_date < from_date:
                raise serializers.ValidationError(
                    "Invalid date. Arrival time cannot be greater than departure time"
                )
        return attrs


class EstateAccessLogVerifySerializer(serializers.Serializer):
    access_code = serializers.CharField(max_length=250)


class EstateAccessLogModifySerializer(serializers.Serializer):
    access = serializers.CharField(max_length=250)
    access_code = serializers.CharField(max_length=250)


class EstateAccessLogWaybillCreateSerializer(serializers.Serializer):
    receivers_name = serializers.CharField(max_length=250)
    item_type = serializers.CharField(max_length=250, required=False)  # just some text
    vehicle_number = serializers.CharField(
        max_length=250, required=False, allow_null=True
    )  # just some text
    waybill_type = serializers.ChoiceField(choices=WAYBILL_TYPE)
    quantity = serializers.IntegerField(required=False, allow_null=True)


EXIT_TYPE = (
    ("VEHICLE", "VEHICLE"),
    ("CLIENT", "CLIENT"),
    ("PEDESTRIAN", "PEDESTRIAN"),
    ("HOUSEHOLD_ITEMS", "HOUSEHOLD_ITEMS"),
)


class EstateAccessLogExitPassCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=250)
    exit_type = serializers.ChoiceField(choices=EXIT_TYPE)
    vehicle_number = serializers.CharField(
        max_length=250,
        required=False,
        allow_null=True,
    )  # just some text
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    exit_date = serializers.DateTimeField()
