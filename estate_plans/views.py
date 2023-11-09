import json
from datetime import timedelta

from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_plans.models import Plan, EstateTransaction, EstateSubscription
from estate_plans.serializers import PlanSerializer, InitializeEstateTransaction, EstateTransactionSerializer, \
    EstateSubscriptionSerializer, EstateSubscriptionModifySerializer
from estate_plans.utils import create_json_of_months_for_twelve
from estates.utils import get_estate, check_admin_access_estate, generateTransactionRef, get_estate_user
from users.permissions import LoggedInPermission, LoggedInStaffPermission, NotLoggedInPermission
from django.utils import timezone


class PlanCreateAPIView(CreateAPIView):
    """Create a new plan for users and can only be created by the staff members"""
    serializer_class = PlanSerializer
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    queryset = Plan.objects.all()


class PlanListAPIView(ListAPIView):
    """
    List all  plan types, and you don't have to be authenticated to access this url
    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [NotLoggedInPermission]


class PlanAnalyTicsAPIView(APIView):
    """
    This is used to get all the analy tics for the past 12 motns on the three plan
    """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]

    def get(self, request, *args, **kwargs):
        json_data = create_json_of_months_for_twelve()
        data = json.loads(json_data)
        for item in data:
            free_plan_count = EstateSubscription.objects.filter(
                plan__plan_type="FREE", timestamp__lte=item["end_date"]).count()
            essentiaL_plan_count = EstateSubscription.objects.filter(
                plan__plan_type="ESSENTIAL", timestamp__lte=item["end_date"]).count()
            standard_plan_count = EstateSubscription.objects.filter(
                plan__plan_type="STANDARD", timestamp__lte=item["end_date"]).count()
            premium_plan_count = EstateSubscription.objects.filter(
                plan__plan_type="PREMIUM", timestamp__lte=item["end_date"]).count()
            item["FREE"] = free_plan_count
            item["ESSENTIAL"] = essentiaL_plan_count
            item["STANDARD"] = standard_plan_count
            item["PREMIUM"] = premium_plan_count
        return Response(data, status=200)


class PlanRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    This deletes the  plan, create a new on or update it .
    Note: I require it should be updated but not deleted base on some users might have subscribed to what
    you would like to delete
    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    # will check if the user is staff on the update and destroy function below
    permission_classes = [LoggedInPermission]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        # update the plan
        instance = self.get_object()
        # status before it was updated
        old_status = instance.status
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to update this plan"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # update the plan status if the status which was provided is not equals the user current one
        if old_status == "ACTIVE" and serializer.validated_data.get(
                "status") == "INACTIVE":
            if not instance.deactivate_plan():
                #  if the plan was not deactivated then I changed it back to what it was
                _ = instance.status == "INACTIVE"
                instance.save()
                return Response({"error": "Error updating plan status"}, status=400)
        if old_status == "INACTIVE" and serializer.validated_data.get(
                "status") == "ACTIVE":
            if not instance.activate_plan():
                #  if the plan was not activated then I changed it back to what it was
                _ = instance.status == "ACTIVE"
                instance.save()
                return Response({"error": "Error updating plan status"}, status=400)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete the plan
        instance = self.get_object()
        # check if the user is staff
        if not request.user.is_staff:
            return Response({"error": "You dont have permission to delete this plan"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


class EstateTransactionListAPIView(ListAPIView):
    """
    this returns all the transaction made by the admins in an estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateTransactionSerializer
    queryset = EstateTransaction.objects.all()

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        queryset = self.filter_queryset(estate.estatetransaction_set.all())
        return queryset

    def list(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InitializeEstateSubscriptionAPIView(APIView):
    """
    this enables us to view an estate current subscription and only the admin of the estate
    is allowed to view it
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        """
        this initializes the subscription and also adds new transaction reference
        :param request:
        :return:
        """
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        serializer = InitializeEstateTransaction(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        plan_id = serializer.validated_data.get("plan_id")
        plan = Plan.objects.filter(id=plan_id).first()
        if not plan:
            return Response({"error": "Plan does not exists"})
        estate_transaction = EstateTransaction.objects.create(
            plan=plan,
            status="PENDING",
            transaction_reference=generateTransactionRef(EstateTransaction, "plan"),
            payment_type=serializer.validated_data.get("payment_type"),
            estate=estate,
            estate_user=estate_user,
        )
        return Response(EstateTransactionSerializer(instance=estate_transaction).data, status=201)


class SuperAdminEstateTransactionListAPIView(ListAPIView):
    """
    this returns all the transaction made by the admin on behalf of th estate
    """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    serializer_class = EstateTransactionSerializer
    queryset = EstateTransaction.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "estate_user__user_type",
        "estate_user__user__first_name",
        "estate_user__user__last_name",
        "status",
        "transaction_reference",
        "payment_type", ]


class SuperAdminEstateSubscriptionListAPIView(ListAPIView):
    """
    this returns all the transaction made by the admin on behalf of the estate
    and can only be seen by the super admin
    """
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    serializer_class = EstateSubscriptionSerializer
    queryset = EstateSubscription.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "estate__name",
        "status",
        "plan__plan_type",
    ]

    def get_queryset(self):
        queryset = self.filter_queryset(self.queryset.all())
        EstateSubscription.objects.filter(plan__plan_type="", due_date__gt=timezone.now())

        # Get the active and inactive subscription
        plan_status = self.request.query_params.get("plan_status")
        if plan_status == "ACTIVE":
            queryset = queryset.exclude(plan__plan_type="FREE").filter(due_date__gt=timezone.now())
        elif plan_status == "INACTIVE":
            # Get the inactive subscription
            queryset = queryset.filter(
                Q(due_date__lt=timezone.now()) | Q(due_date__isnull=True)
            )
        elif plan_status == "PENDING":
            # Get the pending subscription
            queryset = queryset.filter(status="PENDING")
        return queryset


class EstateSubscriptionAPIView(APIView):
    """
    this shows the current subscription of an estate
    """
    permission_classes = [LoggedInPermission]

    def get(self, request):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        # Check if the estate have a subscription
        if not EstateSubscription.objects.filter(estate=estate).first():
            free_plan, created = Plan.objects.get_or_create(
                price=0, plan_type="FREE", status="ACTIVE")
            # Create the estate subscription or just get it
            estate_subscription, created = EstateSubscription.objects.get_or_create(
                estate=estate,
                plan=free_plan, )
            estate.estatesubscription = estate_subscription
        serializer = EstateSubscriptionSerializer(instance=estate.estatesubscription)
        return Response(serializer.data, status=200)


class EstateSubscriptionModifyAPIView(APIView):
    """This is used to modify the estate subscription to active, inactive, pending or something else"""
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]

    def post(self, request):
        """
        You have to be a super admin to be able to access this endpoint
        """
        serializer = EstateSubscriptionModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estate_id = serializer.validated_data.get("estate_id")
        status = serializer.validated_data.get("status")

        estate = get_estate(estate_id=estate_id)

        estate_subscription = estate.estatesubscription
        estate_subscription.status = status

        if estate_subscription.plan.plan_type != "FREE":
            estate_subscription.paid_date = timezone.now()
            estate_subscription.due_date = timezone.now() + timedelta(days=365)
            estate_subscription.save()
        return Response({"message": "Successfully modified the estate Subscription "}, status=200)
