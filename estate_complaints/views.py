from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from estate_complaints.serializers import EstateComplaintSerializer
from estate_users.models import EstateUser
from estates.utils import get_estate, get_estate_user
from users.permissions import LoggedInPermission
from .tasks import (
    send_new_complaint_to_super_admin_task,
    send_new_complaint_to_receiver_task,
)


class EstateComplaintListCreateAPIView(ListCreateAPIView):
    """ "
    This class is meant to list , create  complaint
    """

    serializer_class = EstateComplaintSerializer
    permission_classes = [LoggedInPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "reason",
        "receivers",
        "message",
        "case_id",
    ]

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        # Get the queryset of all the complaint for the current user as the receiver
        queryset = self.filter_queryset(estate.estatecomplaint_set.all())
        if estate_user.user_type == "RESIDENT":
            queryset = self.filter_queryset(queryset.filter(estate_user=estate_user))
        elif estate_user.user_type == "EXTERNAL":
            queryset = self.filter_queryset(queryset.filter(estate_user=estate_user))
        elif estate_user.user_type == "ADMIN":
            # That means he was invited, so he cant see all complaint but on the once addressed to hime
            if estate_user.invited:
                # get the estate complaint for the user category
                if estate_user.user_category:
                    queryset = self.filter_queryset(
                        queryset.filter(recivers=estate_user.user_category)
                    )

        # complaint status
        status = self.request.query_params.get("status")

        if status == "PENDING":
            queryset = self.filter_queryset(queryset.filter(status="PENDING"))
        elif status == "RESOLVED":
            queryset = self.filter_queryset(queryset.filter(status="RESOLVED"))
        return queryset

    def create(self, request, *args, **kwargs):
        estate_id = request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estate_complaint = serializer.save(estate=estate, estate_user=estate_user)
        user = self.request.user
        # send complaint to superadmin  of project
        send_new_complaint_to_super_admin_task.delay(
            case_id=estate_complaint.case_id,
            estate_name=estate_complaint.estate.name,
            estate_id=estate_complaint.estate.estate_id,
            complaint_title=estate_complaint.title,
            senders_name=f"{user.first_name} - {user.last_name} ",
            complaint_reason=estate_complaint.reason,
            complaint_message=estate_complaint.message,
            complaint_status=estate_complaint.status,
        )
        # send complaint to the  main admin and also list off all the receivers
        send_new_complaint_to_receiver_task.delay(
            email=estate.owner.email,
            first_name=estate.owner.first_name,
            last_name=estate.owner.last_name,
            case_id=estate_complaint.case_id,
            estate_name=estate_complaint.estate.name,
            estate_id=estate_complaint.estate.estate_id,
            complaint_title=estate_complaint.title,
            senders_name=f"{user.first_name} - {user.last_name} ",
            complaint_reason=estate_complaint.reason,
            complaint_message=estate_complaint.message,
            complaint_status=estate_complaint.status,
        )
        # send the complaint to all the receivers and exclude the admin
        all_estate_users_receivers = EstateUser.objects.filter(
            estate=estate, status="ACTIVE", user_category=estate_complaint.receivers
        ).exclude(user=estate.owner)

        # loop through all the receivers
        for estate_user_receiver in all_estate_users_receivers:
            # send to the receiver set
            send_new_complaint_to_receiver_task.delay(
                email=estate_user_receiver.user.email,
                first_name=estate_user_receiver.user.first_name,
                last_name=estate_user_receiver.user.last_name,
                case_id=estate_complaint.case_id,
                estate_name=estate_complaint.estate.name,
                estate_id=estate_complaint.estate.estate_id,
                complaint_title=estate_complaint.title,
                senders_name=f"{user.first_name} - {user.last_name} ",
                complaint_reason=estate_complaint.reason,
                complaint_message=estate_complaint.message,
                complaint_status=estate_complaint.status,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class EstateComplaintRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to retrieve a complaint , update the complaint , and also delete the complaint
    """

    serializer_class = EstateComplaintSerializer
    permission_classes = [LoggedInPermission]
    lookup_field = "pk"

    def get_queryset(self):
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        queryset = estate.estatecomplaint_set.all()

        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        #  before creating an estate utility we have to make sure the user is an admin in the estate
        estate = instance.estate
        create_by_estate_user = instance.estate_user

        update_by_estate_user = get_estate_user(estate=estate, user=self.request.user)

        # check if the user have access to update this complaint
        if update_by_estate_user.user_type != "ADMIN":
            if update_by_estate_user != create_by_estate_user:
                if instance.receivers == update_by_estate_user.user_type:
                    return Response(
                        {
                            "error": "You dont have the permission to update this complaint"
                        },
                        status=400,
                    )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(update_by=update_by_estate_user)
        instance.update_time = timezone.now()
        instance.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  before creating an estate utility we have to make sure the user is an admin in the estate
        estate = instance.estate
        create_by_estate_user = instance.estate_user

        update_by_estate_user = get_estate_user(estate=estate, user=self.request.user)

        # check if the user have access to update this complaint
        if update_by_estate_user.user_type != "ADMIN":
            if update_by_estate_user != create_by_estate_user:
                if instance.receivers == update_by_estate_user.user_type:
                    return Response(
                        {
                            "error": "You dont have the permission to update this complaint"
                        },
                        status=400,
                    )

        self.perform_destroy(instance)
        return Response(status=204)
