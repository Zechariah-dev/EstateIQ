from rest_framework import serializers

from estate_plans.models import Plan, PAYMENT_TYPE, EstateTransaction, EstateSubscription
from estate_users.serializers import EstateUserSerializer

from estate_plans.models import STATUS as ESTATE_SUBSCRIPTION_STATUS


class PlanSerializer(serializers.ModelSerializer):
    """
    this serializer is used to list , create , update a subscription
    """

    class Meta:
        model = Plan
        fields = [
            "id",
            "price",
            "description",
            "plan_type",
            "status",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "timestamp",
        ]


class InitializeEstateTransaction(serializers.Serializer):
    """
    this is used to initialize a transaction on subscription for an estate
    """
    # the plan the user wants to subscribe to
    plan_id = serializers.UUIDField(required=True)
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE)

    def validate(self, attrs):
        plan = Plan.objects.filter(id=attrs.get("plan_id")).first()
        if not plan:
            raise serializers.ValidationError("Plan with this ID does not exist")
        if plan.status == "INACTIVE":
            raise serializers.ValidationError("Plan is currently inactive try subscribing to another plan")
        return attrs


class EstateTransactionSerializer(serializers.ModelSerializer):
    """
    This enables to get info about all the transaction made by an estate
    """
    plan = PlanSerializer(read_only=True)
    estate = serializers.SerializerMethodField(read_only=True)
    estate_user = EstateUserSerializer(read_only=True)

    class Meta:
        model = EstateTransaction
        fields = [
            "id",
            "estate",
            "estate_user",
            "plan",
            "status",
            "transaction_reference",
            "payment_type",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "estate",
            "estate_user",
            "plan",
            "timestamp",
        ]

    def get_estate(self, obj: EstateSubscription):
        # using local import just because I need this in the admin
        from estates.serializers import EstateSerializer
        estate = obj.estate
        return EstateSerializer(estate).data


class EstateSubscriptionSerializer(serializers.ModelSerializer):
    """
    this serializer is used to get the active subscription of an estate
    """
    plan = PlanSerializer(read_only=True)
    estate = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EstateSubscription
        fields = [
            "id",
            "estate",
            "status",
            "plan",
            "payment_type",
            "account_name",
            "bank_name",
            "account_number",
            "paid_date",
            "due_date",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "estate",
            "timestamp",
        ]

    def get_estate(self, obj: EstateSubscription):
        # using local import just because I need this in the admin
        from estates.serializers import EstateSerializer
        estate = obj.estate
        return EstateSerializer(estate).data


class EstateSubscriptionModifySerializer(serializers.Serializer):
    """
    this is used to modify an estate subscription
    """
    estate_id = serializers.CharField(max_length=250)
    status = serializers.ChoiceField(choices=ESTATE_SUBSCRIPTION_STATUS)
