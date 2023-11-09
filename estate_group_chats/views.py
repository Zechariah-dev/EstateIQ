from django.http import Http404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from estates.utils import get_estate, get_estate_user
from .models import GroupConversation, GroupMessage
from estate_chats.paginators import MessagePagination

from .serializers import GroupMessageSerializer, GroupConversationSerializer
from users.permissions import LoggedInPermission


class GroupConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    this list the conversations of the logged-in user
    """
    serializer_class = GroupConversationSerializer
    queryset = GroupConversation.objects.none()
    lookup_field = "name"
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        #  filter the conversation created by the superuser
        queryset = GroupConversation.objects.filter(
            is_super_user=True
        )
        return queryset

    def get_serializer_context(self):
        """this enables adding the context to a serializer"""
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        return {"request": self.request, "estate_user": estate_user}


class GroupMessageViewSet(ListModelMixin, GenericViewSet):
    """"
    Returns
    """
    serializer_class = GroupMessageSerializer
    queryset = GroupMessage.objects.none()
    pagination_class = MessagePagination
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        group_conversation_name = self.request.GET.get("group_conversation_name")
        queryset = (
            GroupMessage.objects.filter(
                conversation__name__contains=group_conversation_name,
            )
            .order_by("-timestamp")
        )
        return queryset
