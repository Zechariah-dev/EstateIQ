from rest_framework import serializers

from estate_users.serializers import EstateUserSerializer
from estates.serializers import EstateSerializer
from .models import EstateUtility, UtilityTransaction, PAYMENT_TYPE, EstateUtilityPenalty


class EstateUtilitySerializer(serializers.ModelSerializer):
    """
    this utility serializer is used to create ,list and update a utility
    """
    staff = EstateUserSerializer(read_only=True)

    class Meta:
        model = EstateUtility
        fields = [
            "id",
            "staff",
            "estate",
            "name",
            "price",
            "payment_frequency",
            "minimum_purchase",
            "collection_type",
            "collection_target",
            "account_name",
            "bank_name",
            "account_number",
            "due_date",
            "timestamp",
        ]

        read_only_fields = [
            "id",
            "staff",
            "estate",
            "timestamp",
        ]

    def validate(self, attrs):
        # If the minimum pruchase was passed
        if attrs.get("minimum_purchase"):
            if attrs.get("price") < attrs.get("minimum_purchase"):
                raise serializers.ValidationError("Price must be grater than the minimum price")
        return attrs


class InitializeTransaction(serializers.Serializer):
    """
    this class enables the user to send in date to be used for initializing a transaction
    """
    # the utility_id the user wants to pay for
    utility_id = serializers.UUIDField(required=True)
    # The amount the user is paying for
    amount = serializers.DecimalField(decimal_places=2, max_digits=9)
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE)

    def validate(self, attrs):
        utility = EstateUtility.objects.filter(id=attrs.get("utility_id")).first()
        if not utility:
            raise serializers.ValidationError("Utility ID does not exist")
        if utility.minimum_purchase:
            if utility.minimum_purchase > attrs.get("amount"):
                raise serializers.ValidationError("The amount is less than the minium purchase")
        if utility.collection_type == "MANDATORY":
            if attrs.get("amount") < utility.price:
                raise serializers.ValidationError("The amount is less than the mandatory utility price")
        return attrs


class UtilityTransactionSerializer(serializers.ModelSerializer):
    """
    this is used to list all transactions made on utilities
    """
    estate = EstateSerializer(read_only=True)
    estate_user = EstateUserSerializer(read_only=True)
    estate_utility = EstateUtilitySerializer(read_only=True)

    class Meta:
        model = UtilityTransaction
        fields = [
            "id",
            "estate",
            "estate_user",
            "estate_utility",
            "amount",
            "payment_type",
            "transaction_reference",
            "message",
            "status",
            "purpose",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "estate",
            "estate_user",
            "estate_utility",
            "timestamp",
        ]


REVOKE_CHOICE = ["ON_TO_ONE_MESSAGE", "UTILITY_PORTAL", "EMERGENCY_SERVICE", "GATE_PASS"]


class EstateUtilityPenaltyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    this is used to create penalty for an existing utility
     for the user who are not subscribed to it
    """

    class Meta:
        model = EstateUtilityPenalty
        fields = [
            "id",
            "estate",
            "estate_utility",
            "unpaid_in",
            "unpaid_period",
            "revoke",
            "timestamp",

        ]
        read_only_fields = [
            "id",
            "estate",
        ]

    def validate(self, attrs):
        try:
            if attrs.get("unpaid_in") < 1:
                raise serializers.ValidationError("The unpaid_in must be more than 0")
            revoke_list = attrs.get("revoke").split(",")
            for item in revoke_list:
                if item not in REVOKE_CHOICE:
                    raise serializers.ValidationError(f"{item} not among the revoke list")
        except:
            pass
        return attrs


class EstateUtilityPenaltySerializer(serializers.ModelSerializer):
    """
    this is list and retrieve penalty
    """
    estate_utility = EstateUtilitySerializer(read_only=True)

    class Meta:
        model = EstateUtilityPenalty
        fields = [
            "id",
            "estate",
            "estate_utility",
            "unpaid_in",
            "unpaid_period",
            "revoke",
            "timestamp",

        ]
        read_only_fields = [
            "id",
            "estate",
            "estate_utility",
        ]
