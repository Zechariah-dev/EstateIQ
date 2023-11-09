import datetime

from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_users.models import EstateUserProfile
from estates.utils import get_estate, get_estate_user
from users.permissions import LoggedInPermission, LoggedInStaffPermission
from users.utils import date_filter_queryset
from .models import EstateAccessLog
from .serializers import (
    EstateAccessLogSerializer,
    EstateAccessLogVerifySerializer,
    EstateAccessLogModifySerializer,
    EstateAccessLogWaybillCreateSerializer,
    EstateAccessLogExitPassCreateSerializer,
)
from .tasks import send_access_code_task


class EstateAccessLogListCreateAPIView(ListCreateAPIView):
    serializer_class = EstateAccessLogSerializer
    permission_classes = [LoggedInPermission]
    queryset = EstateAccessLog.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "first_name",
        "last_name",
    ]

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        # Get the queryset of all the accesslog for the current user as the receiver
        queryset = self.filter_queryset(estate.estateaccesslog_set.all())
        if estate_user.user_type == "EXTERNAL":
            queryset = self.filter_queryset(queryset.filter(updated_by=estate_user))
        elif estate_user.user_type == "RESIDENT":
            queryset = self.filter_queryset(queryset.filter(estate_user=estate_user))

        # access log  status ( could be ENTRY OR EXIT)
        status = self.request.query_params.get("status")
        if status == "ENTRY":
            queryset = self.filter_queryset(queryset.filter(to_date__gt=timezone.now()))
        elif status == "EXIT":
            queryset = self.filter_queryset(queryset.filter(to_date__lt=timezone.now()))
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        estate_id = request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        if estate_user.status == "INACTIVE":
            return Response(
                {"error": "Your account is currently inactive."}, status=400
            )
        if not estate_user.gate_pass:
            # Check if the user has permission to create gate pass
            return Response(
                {"error": "You dont have permission to create gate pass"}, status=400
            )
        # the estate user profile
        estate_user_profile = EstateUserProfile.objects.filter(
            estate_user=estate_user
        ).first()
        if estate_user_profile:
            if not estate_user_profile.address:
                return Response(
                    {
                        "error": "Set home address in profile page before generating access code."
                    },
                    status=400,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estate_access_log = serializer.save(estate_user=estate_user, estate=estate)

        if estate_user_profile:
            estate_access_log.address = estate_user_profile.address
            estate_access_log.save()
        return Response(serializer.data, status=201)


class SuperAdminEstateAccessLogListAPIView(ListAPIView):
    serializer_class = EstateAccessLogSerializer
    permission_classes = [LoggedInPermission & LoggedInStaffPermission]
    queryset = EstateAccessLog.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "first_name",
        "last_name",
    ]

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        # Get the queryset of all the accesslog for the current user as the receiver
        queryset = self.filter_queryset(estate.estateaccesslog_set.all())
        # access log  status ( could be ENTRY OR EXIT)
        status = self.request.query_params.get("status")
        if status == "ENTRY":
            queryset = self.filter_queryset(queryset.filter(to_date__gt=timezone.now()))
        elif status == "EXIT":
            queryset = self.filter_queryset(queryset.filter(to_date__lt=timezone.now()))
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset


class EstateAccessLogVerificationAPIView(APIView):
    permission_classes = [LoggedInPermission]

    def post(self, request):
        """
        this is used to verify the access log of a user in an estate
        :param self:
        :param request:
        :return:
        """
        serializer = EstateAccessLogVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_code = serializer.validated_data.get("access_code")

        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        estate_access_log = estate.estateaccesslog_set.filter(
            access_code__icontains=access_code
        ).first()

        if not estate_access_log:
            return Response({"error": "Access code not valid"}, status=400)

        # # check date if the access code is valid
        # if not estate_access_log.to_date:
        #     return Response(
        #         {"error": "Access log expired, does not have to_date"}, status=400
        #     )

        # # check date if the access code is valid
        # if estate_access_log.to_date < timezone.now():
        #     return Response({"error": "Access log expired"}, status=400)

        # check if it has been updated before
        if estate_access_log.updated_by:
            access = f"{estate_access_log.access}".lower()
            accessToUse = "granted" if access == "grant" else "declined"
            return Response(
                {"error": f"This access code has been used and {accessToUse}"}
            )
        return Response(
            EstateAccessLogSerializer(instance=estate_access_log).data, status=200
        )


class ModifyEstateAccessLogAPIView(APIView):
    permission_classes = [LoggedInPermission]

    def post(self, request):
        """
        this is used to modify an access control to grant or revoked
        :param request:
        :return:
        """
        serializer = EstateAccessLogModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data.get("access")
        access_code = serializer.validated_data.get("access_code")

        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        estate_access_log = estate.estateaccesslog_set.filter(
            access_code=access_code
        ).first()
        if not estate_access_log:
            return Response({"error": "Access code does not exist"}, status=400)
        if estate_user.user_type == "RESIDENT":
            if estate_user != estate_access_log.estate_user:
                return Response(
                    {"error": "You dont have access to modify the access log"},
                    status=400,
                )
        # update the access
        estate_access_log.access = access
        # update the update by
        estate_access_log.updated_by = estate_user
        estate_access_log.verified_time = timezone.now()
        estate_access_log.save()

        if estate_access_log.access == "REVOKE":
            send_access_code_task.delay(
                estate_access_log.estate_user.user.email,
                estate_access_log.estate_user.user.first_name,
                estate_access_log.estate_user.user.last_name,
                "denied",
                estate_access_log.first_name,
                estate_access_log.last_name,
            )
        else:
            send_access_code_task.delay(
                estate_access_log.estate_user.user.email,
                estate_access_log.estate_user.user.first_name,
                estate_access_log.estate_user.user.last_name,
                "granted",
                estate_access_log.first_name,
                estate_access_log.last_name,
            )
        return Response({"message": "Successfully modified"}, status=200)


class EstateAccessLogWaybillCreateView(CreateAPIView):
    """
    this is used to create waybill access log
    """

    serializer_class = EstateAccessLogWaybillCreateSerializer
    permission_classes = [LoggedInPermission]

    def create(self, request, *args, **kwargs):
        estate_id = request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        if estate_user.status == "INACTIVE":
            return Response(
                {"error": "Your account is currently inactive."}, status=400
            )
        estate_user_profile = EstateUserProfile.objects.filter(
            estate_user=estate_user
        ).first()
        if estate_user_profile:
            if not estate_user_profile.address:
                return Response(
                    {
                        "error": "Set home address in profile page before generating access code."
                    },
                    status=400,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receivers_name = serializer.validated_data.get("receivers_name")
        item_type = serializer.validated_data.get("item_type")
        waybill_type = serializer.validated_data.get("waybill_type")
        quantity = serializer.validated_data.get("quantity")
        vehicle_number = serializer.validated_data.get("vehicle_number")

        # create the access log
        names = receivers_name.split(" ")
        first_name = names[0]
        last_name = ""
        if len(names) > 1:
            last_name = names[1]

        estate_access_log = EstateAccessLog.objects.create(
            estate_user=estate_user,
            estate=estate,
            first_name=first_name,
            last_name=last_name,
            address=estate_user_profile.address,
            access_type="ONE_TIME",
            category="OTHERS",
            vehicle_number=vehicle_number,
            waybill_type=waybill_type,
            item_type=item_type,
            quantity=quantity,
            access_log_type="WAYBILL",
        )
        #  serialize the data
        serializer = EstateAccessLogSerializer(instance=estate_access_log)
        return Response(serializer.data, status=201)


class EstateAccessLogExitPassCreateView(CreateAPIView):
    """
    this is used to create waybill access log
    """

    serializer_class = EstateAccessLogExitPassCreateSerializer
    permission_classes = [LoggedInPermission]

    def create(self, request, *args, **kwargs):
        estate_id = request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        if estate_user.status == "INACTIVE":
            return Response(
                {"error": "Your account is currently inactive."}, status=400
            )
        estate_user_profile = EstateUserProfile.objects.filter(
            estate_user=estate_user
        ).first()
        if estate_user_profile:
            if not estate_user_profile.address:
                return Response(
                    {
                        "error": "Set home address in profile page before generating access code."
                    },
                    status=400,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        full_name = serializer.validated_data.get("full_name")
        exit_type = serializer.validated_data.get("exit_type")
        vehicle_number = serializer.validated_data.get("vehicle_number")

        gender = serializer.validated_data.get("gender")
        exit_date = serializer.validated_data.get("exit_date")

        # create the access log
        names = full_name.split(" ")
        first_name = names[0]
        last_name = ""
        if len(last_name) > 1:
            last_name = names[1]

        estate_access_log = EstateAccessLog.objects.create(
            estate_user=estate_user,
            estate=estate,
            first_name=first_name,
            last_name=last_name,
            address=estate_user_profile.address,
            access_type="ONE_TIME",
            category=exit_type,
            vehicle_number=vehicle_number,
            access_log_type="BUSINESS",
            gender=gender,
            to_date=exit_date,
        )
        #  serialize the data
        serializer = EstateAccessLogSerializer(instance=estate_access_log)
        return Response(serializer.data, status=201)
