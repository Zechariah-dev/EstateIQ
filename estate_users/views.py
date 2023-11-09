import json
import random
import string
import time

from rest_framework import parsers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_access_logs.models import EstateAccessLog
from estate_plans.utils import create_json_of_months_for_twelve
from estate_users.models import EstateUser
from estate_users.serializers import EstateUserProfileDetailSerializer, EstateUserProfileUpdateSerializer, \
    ResidentInviteEstateUserSerializer, AdminInviteEstateUserSerializer, EstateUserSerializer, \
    ModifyEstateUserSerializer, EstateUserBulkUploadSerializer, EstateUserProfileUpdateProfileImageSerializer, \
    ResidentMobileInviteEstateUserSerializer
from estate_users.tasks import send_created_estate_user, send_user_account_activated, estate_user_bulk_upload
from estate_users.utils import create_estate_user, create_user, read_csv_file_return_data
from estates.utils import get_estate, get_estate_user, check_admin_access_estate, check_user_access_estate
from users.permissions import LoggedInPermission
from users.utils import date_filter_queryset


class AdminEstateUserListAPIView(ListAPIView):
    """
    this is used by the admin to accessed all the users in an estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUserSerializer
    queryset = EstateUser.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user_type",
        "user_category",
    ]

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        #  first check for the user is part of the estate users before he would be able to create the utility
        if not check_user_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        queryset = self.filter_queryset(estate.estateuser_set.all())
        user_type = self.request.query_params.get("user_type")
        user_category = self.request.query_params.get("user_category")
        if user_type == "ADMIN":
            queryset = self.filter_queryset(estate.estateuser_set.filter(user_type="ADMIN"))
        elif user_type == "RESIDENT":
            queryset = self.filter_queryset(estate.estateuser_set.filter(user_type="RESIDENT"))
        elif user_type == "EXTERNAL":
            queryset = self.filter_queryset(estate.estateuser_set.filter(user_type="EXTERNAL"))

        # Check for the user category
        if user_category == "SECURITY":
            queryset = self.filter_queryset(estate.estateuser_set.filter(user_category="SECURITY"))
        elif user_category == "VENDOR":
            queryset = self.filter_queryset(estate.estateuser_set.filter(user_category="VENDOR"))

        # check for date
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
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


class ResidentEstateUserListAPIView(ListAPIView):
    """"
    This is accessed by the resident to get his family_member more of like individuals invited by him"""
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUserSerializer
    queryset = EstateUser.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user_category",
    ]

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        #  first check for the user is part of the estate users before he would be able to create the utility
        if not check_user_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        queryset = self.filter_queryset(estate.estateuser_set.filter(created_by=estate_user))
        user_category = self.request.query_params.get("user_category")
        if user_category == "DOMESTIC_STAFF":
            queryset = self.filter_queryset(queryset.filter(user_category="DOMESTIC_STAFF"))
        elif user_category == "FAMILY_MEMBER":
            queryset = self.filter_queryset(queryset.filter(user_category="FAMILY_MEMBER"))
        return queryset


class UserEstateUserListAPIView(ListAPIView):
    """
    this is used to list all the estate user tied to a user account
    """
    serializer_class = EstateUserSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        return EstateUser.objects.filter(user=self.request.user)


class EstateUserDetailAPIView(APIView):
    """
    This is used to view the full detail of a user
    """
    permission_classes = [LoggedInPermission]

    def get(self, request):
        """
        Get the full detail of the user
        :param request:
        :return:
        """
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        estate_user_profile = estate_user.estate_user_profile
        if estate_user_profile:
            # Get the estate for estate user
            serializer = EstateUserProfileDetailSerializer(instance=estate_user_profile)
            return Response(serializer.data, status=200)
        else:
            return Response({"error": "An error occurred"}, status=200)


class EstateUserProfileUpdateAPIView(APIView):
    """
    User update api view enables you to update the user api
    """
    permission_classes = [LoggedInPermission]

    def put(self, request):
        """Update a user profile base on the data passed also we used related name to access
        the user profile
        """
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        estate_user_profile = estate_user.estate_user_profile
        if not estate_user_profile:
            return Response({"error": "An error occurred."}, status=400)
        serializer = EstateUserProfileUpdateSerializer(
            instance=estate_user_profile,
            data=self.request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # add the estate type
        if estate_user.user_type == "ADMIN":
            estate_type = serializer.validated_data.get("estate_type")
            if estate_type:
                estate.estate_type = estate_type
                estate.save()
        return Response(
            status=200,
            data={"message": "successfully updated user profile",
                  "data": EstateUserProfileDetailSerializer(estate_user_profile).data
                  })


class ResidentInviteEstateUserAPIView(APIView):
    """
    this is used by residents to invite other residents to the estate or staff
    ,external and more, but they cant invite someone above their own current stat
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        """
        this is used to invite users to the app by the resident

        """
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        # check if the estate user is an external
        if estate_user.user_type == "EXTERNAL":
            return Response({"error": "You dont have permission to invite user"}, status=400)
        if estate_user.status != "ACTIVE":
            return Response(
                {"error": "Your account is currently inactive. Please wait till account has been activated"},
                status=400)

        if estate_user.user_category == "FAMILY_MEMBER" or estate_user.user_category == "DOMESTIC_STAFF":
            return Response({
                "error": "You dont have permission to invite a resident"
            }, status=400)

        serializer = ResidentInviteEstateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        email = serializer.validated_data.get('email')
        mobile = serializer.validated_data.get('mobile')
        user_category = serializer.validated_data.get('user_category')
        # Generate random strings in ten letters
        password = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=10))

        new_user = create_user(first_name=first_name,
                               last_name=last_name, email=email,
                               mobile=mobile, password=password)
        if not new_user:
            return Response({"error": "An error occurred creating user"}, status=400)
        # Create the estate user under the estate
        new_estate_user = create_estate_user(
            estate=estate,
            created_by_user=estate_user,
            user=new_user,
            user_category=user_category,
            user_type="RESIDENT",
            address=None,
            status="INACTIVE",
            relationship=None,
            designation=None
        )
        if not new_estate_user:
            return Response({"error": "this user is already an existing user."}, status=400)
        # Send the user a message on the account created
        send_created_estate_user.delay(
            estate_name=estate.name,
            user_category=user_category,
            first_name=first_name, last_name=last_name,
            email=email, mobile=mobile, password=password,
            user_type=new_estate_user.user_type,
            inverter_user_type=estate_user.user_type,
            inviter_first_name=estate_user.user.first_name,
            inviter_last_name=estate_user.user.last_name
        )
        return Response({"message": "Resident Successfully added"}, status=201)


class ResidentMobileInviteEstateUserAPIView(APIView):
    """
    this is used by residents to invite other residents to the estate or staff
    ,external and more, but they cant invite someone above their own current stat
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        """
        this is used to invite users to the app by the resident

        """
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        # check if the estate user is an external
        if estate_user.user_type == "EXTERNAL":
            return Response({"error": "You dont have permission to invite user"}, status=400)
        if estate_user.status != "ACTIVE":
            return Response(
                {"error": "Your account is currently inactive. Please wait till account has been activated"},
                status=400)

        if estate_user.user_category == "FAMILY_MEMBER" or estate_user.user_category == "DOMESTIC_STAFF":
            return Response({
                "error": "You dont have permission to invite a resident"
            }, status=400)

        serializer = ResidentMobileInviteEstateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        email = serializer.validated_data.get('email')
        mobile = serializer.validated_data.get('mobile')
        user_category = serializer.validated_data.get('user_category')

        profile_image = serializer.validated_data.get("profile_image")
        designation = serializer.validated_data.get("designation")
        address = serializer.validated_data.get("address")
        relationship = serializer.validated_data.get("relationship")

        # Generate random strings in ten letters
        password = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=10))

        new_user = create_user(first_name=first_name,
                               last_name=last_name, email=email,
                               mobile=mobile, password=password)
        if not new_user:
            return Response({"error": "An error occurred creating user"}, status=400)
        # Create the estate user under the estate
        new_estate_user = create_estate_user(
            estate=estate,
            created_by_user=estate_user,
            user=new_user,
            user_category=user_category,
            user_type="RESIDENT",
            address=address,
            status="INACTIVE",
            relationship=designation,
            designation=relationship
        )
        if not new_estate_user:
            return Response({"error": "this user is already an existing user."}, status=400)

        #  update the estate user profile image
        estate_user_profile = new_estate_user.estate_user_profile
        estate_user_profile.profile_image = profile_image
        estate_user_profile.save()

        # Send the user a message on the account created
        send_created_estate_user.delay(
            estate_name=estate.name,
            user_category=user_category,
            first_name=first_name, last_name=last_name,
            email=email, mobile=mobile, password=password,
            user_type=new_estate_user.user_type,
            inverter_user_type=estate_user.user_type,
            inviter_first_name=estate_user.user.first_name,
            inviter_last_name=estate_user.user.last_name
        )
        return Response({"message": "Resident Successfully added"}, status=201)


class AdminInviteEstateUserAPIView(APIView):
    """
    this is only used by the admin of an estate in which he is allowed to invite other estate user
    eg: RESIDENT,EXTERNAL,ADMIN ALSO

    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = AdminInviteEstateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        mobile = serializer.validated_data.get("mobile")
        email = serializer.validated_data.get("email")
        user_type = serializer.validated_data.get("user_type")
        user_category = serializer.validated_data.get("user_category")
        # Generate random strings in ten letters
        password = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=10))
        # Create the Django User
        new_user = create_user(first_name=first_name,
                               last_name=last_name, email=email,
                               mobile=mobile, password=password)
        if not new_user:
            return Response({"error": "An error occurred creating user"}, status=400)
        # Create the estate user under the estate
        new_estate_user = create_estate_user(
            estate=estate,
            created_by_user=estate_user,
            user=new_user,
            user_category=user_category,
            user_type=user_type,
            address=None,
            status="ACTIVE",
            relationship=None,
            designation=None
        )
        if not new_estate_user:
            return Response({"error": "EstateUser already exists or an error occurred. Please try changing the values"},
                            status=400)
        # Send the user a message on the account created
        send_created_estate_user.delay(
            estate_name=estate.name,
            user_category=user_category,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            password=password,
            user_type=new_estate_user.user_type,
            inverter_user_type=estate_user.user_type,
            inviter_first_name=estate_user.user.first_name,
            inviter_last_name=estate_user.user.last_name
        )
        return Response({"message": f"{user_type} Successfully added"}, status=201)


class ModifyEstateUserAPIView(APIView):
    """
    this class  enables activating and deactivating the estate user which you invited if you are a resident
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        serializer = ModifyEstateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estate_user_id = serializer.validated_data.get("estate_user_id")
        status = serializer.validated_data.get("status")

        modify_user = estate.estateuser_set.filter(id=estate_user_id).first()
        if not modify_user:
            return Response({"error": "The user does not exist"})

        if estate_user.user_type != "ADMIN":
            if modify_user.created_by_user != estate_user:
                return Response({"error": "You dont have access to update the user"})

        if status == "INACTIVE":
            modify_user.status = "INACTIVE"
            modify_user.save()
        elif status == "ACTIVE":
            send_user_account_activated.delay(
                estate_name=estate.name,
                first_name=modify_user.user.first_name,
                email=modify_user.user.email,
            )
            modify_user.status = "ACTIVE"
            modify_user.save()
        return Response(EstateUserSerializer(instance=modify_user).data, status=200)


class EstateUserAnalyticsAPIView(APIView):
    """
    This is used to get all the analy tics for the past 12 motns on the active , incactive users and the uer type
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        # Get the estate
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)

        #  first check for the user is part of the estate admin before he would be able to create the utility
        if not check_admin_access_estate(self.request.user, estate):
            # You have to be an admin of that estate before you would be able to make payment
            return Response({"error": "You dont have permission"}, status=401)
        json_data = create_json_of_months_for_twelve()
        data = json.loads(json_data)
        for item in data:
            admin_count = estate.estateuser_set.filter(
                user_type="ADMIN", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            resident_count = estate.estateuser_set.filter(
                user_type="RESIDENT", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            external_count = estate.estateuser_set.filter(
                user_type="EXTERNAL", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            active_user_count = estate.estateuser_set.filter(
                status="ACTIVE", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            inactive_user_count = estate.estateuser_set.filter(
                status="INACTIVE", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            domestic_staff_count = estate.estateuser_set.filter(
                user_category="DOMESTIC_STAFF", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            family_member_count = estate.estateuser_set.filter(
                user_category="FAMILY_MEMBER", timestamp__range=[estate.timestamp, item["end_date"]]).count()
            visitor_count = EstateAccessLog.objects.filter(estate=estate,
                                                           timestamp__range=[estate.timestamp,
                                                                             item["end_date"]]).count()
            security_count = estate.estateuser_set.filter(
                user_category="SECURITY", timestamp__range=[estate.timestamp, item["end_date"]]).count()

            item["ADMIN"] = admin_count
            item["RESIDENT"] = resident_count
            item["EXTERNAL"] = external_count
            item["ACTIVE_USER"] = active_user_count
            item["INACTIVE_USER"] = inactive_user_count
            item["DOMESTIC_STAFF"] = domestic_staff_count
            item["FAMILY_MEMBER"] = family_member_count
            item["VISITOR"] = visitor_count
            item["SECURITY"] = security_count
        return Response(data, status=200)


class EstateUserBulkUploadAPIView(APIView):
    """
    this is used to make bulk upload with a csv
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        # get the csv
        serializer = EstateUserBulkUploadSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        csv_file = serializer.validated_data.get("csv_file")
        # get the data and the header
        data, errors = read_csv_file_return_data(csv_file)
        # estate bulk upload
        estate_user_bulk_upload.delay(data, estate.id, estate_user.id)
        error_exist = len(errors) != 0
        return Response({"message": "Successfully added user", "error_exist": error_exist, "errors": errors})


class EstateUserUpdateProfileImageAPIView(APIView):
    """
    this is used to update the profile image of the estate user
    """
    permission_classes = [LoggedInPermission]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    def post(self, request):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        estate_user_profile = estate_user.estate_user_profile

        serializer = EstateUserProfileUpdateProfileImageSerializer(
            instance=estate_user_profile,
            data=self.request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=200,
            data={"message": "successfully updated user profile",
                  "data": EstateUserProfileDetailSerializer(estate_user_profile).data
                  })
