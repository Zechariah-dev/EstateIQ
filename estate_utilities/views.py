from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_utilities.models import EstateUtility, UtilityTransaction
from estate_utilities.serializers import EstateUtilitySerializer, UtilityTransactionSerializer, \
    InitializeTransaction, EstateUtilityPenaltySerializer, EstateUtilityPenaltyCreateUpdateSerializer
from estates.utils import check_admin_access_estate, get_estate, get_estate_user, generateTransactionRef
from users.permissions import LoggedInPermission
from users.utils import date_filter_queryset

from django.utils import timezone


class EstateUtilityListCreateAPIView(ListCreateAPIView):
    """
    this list create api view list all utilities using the estate id and also uses
    the estate id to create it .
    Before you can create this you have to be an estate admin or owner
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUtilitySerializer
    queryset = EstateUtility.objects.all()

    def get_queryset(self):
        """
        this filter using the company id passed on the urls to get the leads associated with it
        """
        estate_id = self.request.query_params.get("estate_id")
        queryset = self.filter_queryset(get_estate(estate_id=estate_id).estateutility_set.all())
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        this list all the utilities on an estate
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        #  before creating an estate utility we have to make sure the user is an admin in the estate
        estate_id = request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = EstateUtilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(estate=estate, staff=estate_user)
        return Response(serializer.data, status=201)


class EstateUtilityRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    This class enables you to retrieve an estate utility , update it and also delete
    ,but you must have the required permission
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUtilitySerializer
    queryset = EstateUtility.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        """
        this filter using the company id passed on the urls to get the leads associated with it
        """
        # Get the estate
        estate = get_estate(self.request.query_params.get("estate_id"))
        queryset = self.filter_queryset(estate.estateutility_set.all())
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def update(self, request, *args, **kwargs):
        # Get the estate
        estate = get_estate(estate_id=self.request.query_params.get("estate_id"))
        # Get the estate user
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        # Get the instance we want to update
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(staff=estate_user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Get the estate
        estate = get_estate(estate_id=self.request.query_params.get("estate_id"))
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class UtilityTransactionListAPIView(ListAPIView):
    """
    this list all transaction on utility by a user
    """
    serializer_class = UtilityTransactionSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        queryset = UtilityTransaction.objects.filter(
            estate_user=estate_user, estate=estate)

        # filter base on the utility category provided
        utility_category = self.request.query_params.get("utility_category")
        if utility_category == "PAID":
            queryset = queryset.filter(due_date__gte=timezone.now())
        elif utility_category == "DUE":
            queryset = queryset.filter(due_date__lte=timezone.now())
        return queryset


class EstateUtilityTransactionListAPIView(ListAPIView):
    """
    this list all transaction on utility by a user
    """
    serializer_class = UtilityTransactionSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        utility_transaction = UtilityTransaction.objects.filter(
            estate_user=estate_user, estate=estate)
        return utility_transaction

    def list(self, request, *args, **kwargs):
        # Get the estate
        estate = get_estate(estate_id=self.request.query_params.get("estate_id"))
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InitializeUtilityTransaction(APIView):
    """
    this class is used to initialize the transaction for flutterwave or paystack if the user
    chooses flutterwave or paystack
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)
        serializer = InitializeTransaction(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        utility_id = serializer.validated_data.get("utility_id")
        # let's check if the estate have a utility with the ID provided
        estate_utility = estate.estateutility_set.filter(id=utility_id).first()

        if not estate_user.utility_portal:
            return Response({"error": "You dont have permission to make payment for utility"}, status=400)

        # Check the estate utility collection target
        if estate_utility.collection_target:
            if estate_utility.collection_target != estate_user.user_type:
                return Response({"error": "You are not allowed to pay for the utility"}, status=400)

        if not estate_utility:
            # If the estate utility does not exist
            return Response({"error": "EstateUtility with this estate does not exist"}, status=400)
        # Create the transaction
        transaction = UtilityTransaction.objects.create(
            estate=estate,
            estate_user=estate_user,
            amount=serializer.validated_data.get("amount"),
            payment_type=serializer.validated_data.get("payment_type"),
            message="",
            status="PENDING",
            estate_utility=estate_utility,
            purpose=f"Payment for {estate_utility.name}",
            transaction_reference=generateTransactionRef(UtilityTransaction, "utility")
        )
        serializer = UtilityTransactionSerializer(instance=transaction)
        return Response(serializer.data, status=201)


class EstateUtilityPenaltyListCreateAPIView(ListCreateAPIView):
    """
    this is used to create penalty or list penalty on an estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUtilityPenaltySerializer

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)

        queryset = self.filter_queryset(estate.estateutilitypenalty_set.all())
        return queryset

    def create(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)
        if estate_user.user_type != "ADMIN":
            return Response({"error": "You dont have permission to create penalty"}, status=400)

        serializer = EstateUtilityPenaltyCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estate_utility = serializer.validated_data.get("estate_utility")
        if not estate_utility:
            return Response({"error": "Estate utility ID does not exist"}, status=400)
        if estate_utility.estate != estate:
            return Response({"error": "You dont have access to use this utility"}, status=400)
        serializer.save(estate=estate)
        return Response(serializer.data, status=201)


class EstatePenaltyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to retrieve update and delete an estate penalty
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUtilityPenaltySerializer
    lookup_field = "pk"

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)

        queryset = self.filter_queryset(estate.estateutilitypenalty_set.all())
        return queryset

    def update(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)
        if estate_user.user_type != "ADMIN":
            return Response({"error": "You dont have permission to update penalty"}, status=400)

        instance = self.get_object()
        serializer = EstateUtilityPenaltyCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        estate_utility = serializer.validated_data.get("estate_utility")
        if estate_utility:
            if estate_utility.estate != estate:
                return Response({"error": "You dont have access to use this utility"}, status=400)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        # get the estate_id we would like to initialize a transaction
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate, self.request.user)
        if estate_user.user_type != "ADMIN":
            return Response({"error": "You dont have permission to delete penalty"}, status=400)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)
