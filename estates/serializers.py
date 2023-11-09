from django.utils import timezone
from rest_framework import serializers

from estate_access_logs.models import EstateAccessLog
from estates.models import Estate, EstateZone, EstateStreet
from users.serializers import UserSerializer


class EstateSerializer(serializers.ModelSerializer):
    """
    this serializer is used to list an estate, create the estate and also update the estate
    """
    days_left = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estate
        fields = [
            "id",
            "owner",
            "estate_id",
            "name",
            "country",
            "address",
            "logo",
            "estate_type",
            "status",
            "state",
            "lga",
            "accept_terms_and_condition",
            "days_left",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "owner",
            "estate_id",
            "status",
            "days_left",
            "timestamp",
        ]

    def get_days_left(self, obj: Estate):
        from estate_plans.models import EstateSubscription
        from estate_plans.models import Plan

        # The estate subscription
        estate_subscription = EstateSubscription.objects.filter(estate=obj).first()
        if not estate_subscription:
            # Get or create free plan
            free_plan, created = Plan.objects.get_or_create(
                price=0, plan_type="FREE", status="ACTIVE")
            # Create the estate subscription or just get it
            estate_subscription, created = EstateSubscription.objects.get_or_create(
                estate=obj,
                plan=free_plan, )

        if estate_subscription.plan.plan_type == "FREE":
            return "Currently on Free Subscription"
        due_date = estate_subscription.due_date

        if not due_date:
            return "Due date Not Set"
        if due_date < timezone.now():
            return "Subscription Expired"
        due_date = timezone.now() - due_date
        return due_date


class EstateZoneSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = EstateZone
        fields = "__all__"


class EstateMultipleSerializer(serializers.Serializer):
    names = serializers.CharField(max_length=2000)


class EstateStreetSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = EstateStreet
        fields = "__all__"


class SuperAdminEstateCreateSerializer(serializers.Serializer):
    """
    This serializer is used to create an estate by the superuser and also create a user with the info provided if the
    user email does not exist
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    mobile = serializers.CharField(max_length=250)
    estate_name = serializers.CharField(max_length=250)
    estate_address = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=250)


class EstateDetailSerializer(serializers.ModelSerializer):
    """
    this contains all the detail of an estate
    """
    owner = UserSerializer(read_only=True)
    users_data = serializers.SerializerMethodField(read_only=True)
    estate_admins = serializers.SerializerMethodField(read_only=True)
    days_left = serializers.SerializerMethodField(read_only=True)
    subscription = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estate
        fields = [
            "id",
            "owner",
            "estate_id",
            "name",
            "country",
            "address",
            "status",
            "state",
            "lga",
            "logo",
            "estate_type",
            "accept_terms_and_condition",
            "timestamp",
            "subscription",
            "days_left",
            "estate_admins",
            "users_data",
        ]
        read_only_fields = [
            "id",
            "owner",
            "status",
            "timestamp",
            "estate_admins",
            "days_left",
            "users_data",
        ]

    def get_users_data(self, obj: Estate):
        active_residents = obj.estateuser_set.filter(user_type="RESIDENT", status="ACTIVE").count()
        in_active_residents = obj.estateuser_set.filter(user_type="RESIDENT", status="INACTIVE").count()
        all_residents = active_residents + in_active_residents

        active_externals = obj.estateuser_set.filter(user_type="EXTERNAL", status="ACTIVE").count()
        in_active_externals = obj.estateuser_set.filter(user_type="EXTERNAL", status="INACTIVE").count()
        all_externals = active_externals + in_active_externals

        active_admins = obj.estateuser_set.filter(user_type="ADMIN", status="ACTIVE").count()
        in_active_admins = obj.estateuser_set.filter(user_type="ADMIN", status="INACTIVE").count()
        all_admins = active_admins + in_active_admins

        active_family_members = obj.estateuser_set.filter(user_category="FAMILY_MEMBER", status="ACTIVE").count()
        in_active_family_members = obj.estateuser_set.filter(user_category="FAMILY_MEMBER", status="INACTIVE").count()
        all_family_members = active_family_members + in_active_family_members

        active_vendors = obj.estateuser_set.filter(user_category="VENDOR", status="ACTIVE").count()
        in_active_vendors = obj.estateuser_set.filter(user_category="VENDOR", status="INACTIVE").count()
        all_vendors = active_vendors + in_active_vendors

        active_securities = obj.estateuser_set.filter(user_category="SECURITY", status="ACTIVE").count()
        in_active_securities = obj.estateuser_set.filter(user_category="SECURITY", status="INACTIVE").count()
        all_securities = active_securities + in_active_securities

        all_visitors = EstateAccessLog.objects.filter(estate=obj).count()
        in_active_visitors = EstateAccessLog.objects.filter(estate=obj, access="REVOKE").count()
        active_visitors = EstateAccessLog.objects.filter(estate=obj, access="GRANT").count()

        return {
            "active_residents": active_residents,
            "in_active_residents": in_active_residents,
            "active_externals": active_externals,
            "in_active_externals": in_active_externals,
            "active_admins": active_admins,
            "in_active_admins": in_active_admins,
            "active_family_members": active_family_members,
            "in_active_family_members": in_active_family_members,
            "active_vendors": active_vendors,
            "in_active_vendors": in_active_vendors,
            "active_securities": active_securities,
            "in_active_securities": in_active_securities,
            "all_residents": all_residents,
            "all_externals": all_externals,
            "all_admins": all_admins,
            "all_family_members": all_family_members,
            "all_vendors": all_vendors,
            "all_securities": all_securities,
            "all_visitors": all_visitors,
            "in_active_visitors": in_active_visitors,
            "active_visitors": active_visitors,
        }

    def get_estate_admins(self, obj: Estate):
        # import it locally
        from estate_users.serializers import EstateUserSerializer

        #  return all the estate users that are admins
        return EstateUserSerializer(
            obj.estateuser_set.filter(user_type="ADMIN", status="ACTIVE"),
            many=True).data

    def get_subscription(self, obj: Estate):
        from estate_plans.models import EstateSubscription
        from estate_plans.models import Plan

        # The estate subscription
        estate_subscription = EstateSubscription.objects.filter(estate=obj).first()
        if not estate_subscription:
            # Get or create free plan
            free_plan, created = Plan.objects.get_or_create(
                price=0, plan_type="FREE", status="ACTIVE")
            # Create the estate subscription or just get it
            estate_subscription, created = EstateSubscription.objects.get_or_create(
                estate=obj,
                plan=free_plan, )
        return estate_subscription.plan.plan_type

    def get_days_left(self, obj: Estate):
        from estate_plans.models import EstateSubscription
        from estate_plans.models import Plan

        # The estate subscription
        estate_subscription = EstateSubscription.objects.filter(estate=obj).first()
        if not estate_subscription:
            # Get or create free plan
            free_plan, created = Plan.objects.get_or_create(
                price=0, plan_type="FREE", status="ACTIVE")
            # Create the estate subscription or just get it
            estate_subscription, created = EstateSubscription.objects.get_or_create(
                estate=obj,
                plan=free_plan, )

        if estate_subscription.plan.plan_type == "FREE":
            return "Currently on Free Subscription"
        due_date = estate_subscription.due_date

        if not due_date:
            return "Due date Not Set"
        if due_date < timezone.now():
            return "Subscription Expired"
        due_date = timezone.now() - due_date
        return due_date


class EstateUpdateSerializer(serializers.ModelSerializer):
    """
    this serializer is used to list an estate, create the estate and also update the estate
    """

    class Meta:
        model = Estate
        fields = [
            "id",
            "name",
            "country",
            "address",
            "status",
            "state",
            "lga",
            "logo",
            "estate_type",
            "accept_terms_and_condition",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "timestamp",
        ]
