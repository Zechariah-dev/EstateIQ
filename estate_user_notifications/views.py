from django.shortcuts import render, redirect

# Create your views here.
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from estates.utils import get_estate, get_estate_user
from users.permissions import LoggedInPermission
from .models import SuperAdminNotification, EstateUserNotification
from .serializers import EstateUserNotificationSerializer, SuperAdminNotificationSerializer


class EstateUserNotificationListAPIView(ListAPIView):
    """
    this list all the notifications available for a user in that particular estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = EstateUserNotificationSerializer

    def get_queryset(self):
        # get the estate_id pass in the params
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)

        # This only shows notifications that are not read to the user
        queryset = self.filter_queryset(estate_user.estateusernotification_set.filter(read=False))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EstateUserNotificationRetrieveAPIView(RetrieveAPIView):
    """
    This is used to retrieve the notification detail and mark it as read
    """
    queryset = EstateUserNotification.objects.all()
    permission_classes = [LoggedInPermission]
    lookup_field = "id"
    serializer_class = EstateUserNotificationSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # make the notification read
        instance.read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return redirect(instance.redirect_url)


class SuperAdminNotificationListAPIView(ListAPIView):
    """
    this list all the notifications available for a user in that particular estate
    """
    permission_classes = [LoggedInPermission]
    serializer_class = SuperAdminNotificationSerializer
    queryset = SuperAdminNotification.objects.filter(read=False)

    def get_queryset(self):
        # get the estate_id pass in the params

        # This only shows notifications that are not read to the user
        queryset = self.filter_queryset(self.queryset.all())
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SuperAdminNotificationRetrieveAPIView(RetrieveAPIView):
    """
    This is used to retrieve the notification detail and mark it as read
    """
    queryset = SuperAdminNotification.objects.all()
    permission_classes = [LoggedInPermission]
    lookup_field = "id"
    serializer_class = SuperAdminNotificationSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # make the notification read
        instance.read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return redirect(instance.redirect_url)
