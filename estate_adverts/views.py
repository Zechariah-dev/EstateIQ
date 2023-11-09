from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.permissions import LoggedInPermission
from .models import EstateAdvertisement, EstateAnnouncement, EstateReminder
from .serializers import EstateAdvertisementSerializer, EstateAnnouncementSerializer, EstateReminderSerializer


class EstateAdvertisementViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = EstateAdvertisementSerializer
    permission_classes = [LoggedInPermission]
    queryset = EstateAdvertisement.objects.all()
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class EstateAnnouncementViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = EstateAnnouncementSerializer
    permission_classes = [LoggedInPermission]
    queryset = EstateAnnouncement.objects.all()
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class EstateReminderViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = EstateReminderSerializer
    permission_classes = [LoggedInPermission]
    queryset = EstateReminder.objects.all()
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return Response({"error": "Not a staff user"})
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)
