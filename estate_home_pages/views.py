from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from users.permissions import NotLoggedInPermission
from .models import WaitList
from .serializers import WaitListSerializer  # Create your views here.
from .tasks import send_waitlist_added_task, send_super_admin_waitlist_added_task


class WaitListCreateView(ListCreateAPIView):
    permission_classes = [NotLoggedInPermission]
    serializer_class = WaitListSerializer
    queryset = WaitList.objects.all()
    throttle_scope = 'monitor'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        send_waitlist_added_task.delay(serializer.validated_data.get("email"))
        send_super_admin_waitlist_added_task.delay(serializer.validated_data.get("email"))
        return Response(serializer.data, status=201)


def home_page(request):
    return render(request, 'HomePage/home.html')
