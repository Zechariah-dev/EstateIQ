import random
import string

from rest_framework.exceptions import ParseError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_users.tasks import send_created_estate_user
from estate_users.utils import create_user
from estates.models import Estate, EstateZone, EstateStreet
from estates.serializers import EstateSerializer, EstateZoneSerializer, EstateMultipleSerializer, \
    EstateStreetSerializer, SuperAdminEstateCreateSerializer, EstateDetailSerializer, EstateUpdateSerializer
from estates.utils import get_estate, check_admin_access_estate, get_estate_zone, get_estate_user
from users.models import User
from users.permissions import LoggedInPermission, NotLoggedInPermission, LoggedInStaffPermission


class EstateNotLoggedinDetailAPIView(RetrieveAPIView):
    """
    this is used to get the detail of an estate for a user that is not logged in
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = EstateSerializer
    lookup_field = "estate_id"
    queryset = Estate.objects.all()


class EstateDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to get the full detail of an estate and you have to be an admin to get this info
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateSerializer
    lookup_field = "estate_id"
    queryset = Estate.objects.all()

    def retrieve(self, request, *args, **kwargs):
        # Estate
        instance = self.get_object()

        estate_user = get_estate_user(estate=instance, user=self.request.user)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, instance):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = EstateDetailSerializer(instance)
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class EstateListCreateAPIView(ListCreateAPIView):
    """"
    This is used to list create all estate that is tied to a user
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "slug",
    ]

    def get_queryset(self):
        # it filters the company base on the admin of the estate
        user = self.request.user
        queryset = self.filter_queryset(Estate.objects.filter(estateuser__user=user, estateuser__user_type="ADMIN"))
        status = self.request.query_params.get("status")
        if status == "ACTIVE":
            queryset = self.filter_queryset(queryset.filter(status="ACTIVE"))
        elif status == "INACTIVE":
            queryset = self.filter_queryset(queryset.filter(status="INACTIVE"))
        elif status == "PENDING":
            queryset = self.filter_queryset(queryset.filter(status="PENDING"))

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estate_name = serializer.validated_data.get("name")
        if Estate.objects.filter(name__icontains=estate_name).first():
            return Response({"error": "Estate name already exists"}, status=400)

        serializer.save(owner=self.request.user, status="INACTIVE")
        return Response(serializer.data, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EstateSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EstateSerializer(queryset, many=True)
        return Response(serializer.data)


class SuperAdminEstateListCreateAPIView(ListCreateAPIView):
    """"
    This is used to list create all estate that is tied to a user
    """
    permission_classes = [LoggedInStaffPermission & LoggedInPermission]
    serializer_class = EstateSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "name",
        "address",
    ]
    queryset = Estate.objects.all()

    def get_queryset(self):
        queryset = self.filter_queryset(self.queryset)
        status = self.request.query_params.get("status")
        if status == "ACTIVE":
            queryset = self.filter_queryset(queryset.filter(status="ACTIVE"))
        elif status == "INACTIVE":
            queryset = self.filter_queryset(queryset.filter(status="INACTIVE"))
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = SuperAdminEstateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the serialized data
        email = serializer.validated_data.get("email")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        mobile = serializer.validated_data.get("mobile")
        estate_name = serializer.validated_data.get("estate_name")
        estate_address = serializer.validated_data.get("estate_address")
        state = serializer.validated_data.get("state")

        is_new_user = True
        if not User.objects.filter(email=email).exists():
            is_new_user = False

        # Generate random strings in ten letters
        password = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=10))
        # Get or create the user
        user = create_user(email=email, first_name=first_name, last_name=last_name, mobile=mobile, password=password)

        # Create the estate
        estate = Estate.objects.create(
            owner=user,
            name=estate_name,
            address=estate_address,
            status="ACTIVE",
            accept_terms_and_condition=True,
            state=state
        )
        # fixme: send created estate maybe
        if is_new_user:
            # Send the user a message on the account created
            send_created_estate_user(
                estate_name=estate.name,
                user_category="OTHERS",
                first_name=first_name, last_name=last_name,
                email=email, mobile=mobile, password=password,
                user_type="ADMIN",
                inverter_user_type="SUPERADMIN",
                inviter_first_name=user.first_name,
                inviter_last_name=user.last_name
            )
        return Response(EstateSerializer(estate).data, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EstateSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EstateSerializer(queryset, many=True)
        return Response(serializer.data)


class SuperAdminEstateRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this api enables a super admin to be able to get the detail of an estate, delete the estate, update the estate
    """
    serializer_class = EstateSerializer
    permission_classes = [LoggedInStaffPermission & LoggedInPermission]
    lookup_field = "estate_id"
    queryset = Estate.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EstateDetailSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EstateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class EstateZoneListCreateAPIView(ListCreateAPIView):
    """
    this is used to list all zone partaining to an estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateZoneSerializer

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        # Get the list of zone in an estate
        queryset = self.filter_queryset(estate.estatezone_set.all())
        return queryset

    def create(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        serializer = EstateMultipleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        names = serializer.validated_data.get("names").split(",")
        # Create multiple zones
        for item in names:
            EstateZone.objects.create(
                estate=estate,
                name=item,
            )
        return Response(serializer.data, status=201)


class EstateZoneRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    this is used to update the  zone
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateZoneSerializer
    queryset = EstateZone.objects.all()

    def check_if_admin(self, request):
        # Estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        if not check_admin_access_estate(self.request.user, estate):
            return False
        return True

    def update(self, request, *args, **kwargs):
        if not self.check_if_admin(request):
            return Response({"error": "You dont  have the required permission"}, status=400)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.check_if_admin(request):
            return Response({"error": "you dont have the required permission"}, status=400)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class EstateStreetRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    this is used to update the  zone
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateStreetSerializer
    queryset = EstateStreet.objects.all()

    def check_if_admin(self, request):
        # Estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        if not check_admin_access_estate(self.request.user, estate):
            return False
        return True

    def update(self, request, *args, **kwargs):
        if not self.check_if_admin(request):
            return Response({"error": "you dont have the required permission"}, status=400)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.check_if_admin(request):
            return Response({"error": "you dont have the required permission"}, status=400)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class EstateStreetListCreateAPIView(ListCreateAPIView):
    """
    this is used to list all street partaining to an estate under a zone
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = EstateStreetSerializer

    def get_queryset(self):
        estate_zone_id = self.request.query_params.get("estate_zone_id")
        estate_zone = get_estate_zone(estate_zone_id=estate_zone_id)
        # Get the list of zone in an estate
        queryset = self.filter_queryset(estate_zone.estatestreet_set.all())
        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are currently not authenticated"}, status=401)
        # Estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)

        # Estate zone
        estate_zone_id = self.request.query_params.get("estate_zone_id")
        estate_zone = get_estate_zone(estate_zone_id=estate_zone_id)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        serializer = EstateMultipleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        names = serializer.validated_data.get("names").split(",")
        # Create multiple zones
        for item in names:
            EstateStreet.objects.create(
                estate=estate,
                estate_zone=estate_zone,
                name=item,
            )
        return Response(serializer.data, status=201)


class EstateCreatStreetWithoutZoneListCreateView(ListCreateAPIView):
    """
    this is used to create street and list street under an estate with or without zoner
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = EstateStreetSerializer

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        # Get the list of street
        queryset = self.filter_queryset(estate.estatestreet_set.all())
        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are currently not authenticated"}, status=401)
        # Estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)

        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        serializer = EstateMultipleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        names = serializer.validated_data.get("names").split(",")
        # Create multiple zones
        for item in names:
            EstateStreet.objects.create(
                estate=estate,
                name=item,
            )
        return Response({"message": "street added"}, status=201)


class EstateUpdateLogoView(APIView):
    """
    this is used when a user what to update the logo of an estate
    """
    permission_classes = [LoggedInPermission]

    def check_if_admin(self, request):
        # Estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        if not check_admin_access_estate(self.request.user, estate):
            return False
        return True

    def post(self, request):
        # check if user admin
        if not self.check_if_admin(request):
            raise ParseError({"error": "You dont have permission to update this estate"})
        # get the user id
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        serializer = EstateUpdateSerializer(estate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Successfully Update Logo", }, status=200)
