from django.http import Http404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from estates.utils import get_estate, get_estate_user
from .models import Conversation, Message
from .paginators import MessagePagination

from .serializers import MessageSerializer, ConversationSerializer
from users.permissions import LoggedInPermission


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    this list the conversations of the logged-in user
    """
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        #  filter the conversation base on conversation name that contains the user id
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)

        estate_user = get_estate_user(estate=estate, user=self.request.user)

        queryset = Conversation.objects.filter(
            name__contains=estate_user.id
        )
        return queryset

    def get_serializer_context(self):
        """this enables adding the context to a serializer"""
        estate_id = self.request.query_params.get("estate_id")
        estate = get_estate(estate_id=estate_id)
        estate_user = get_estate_user(estate=estate, user=self.request.user)
        return {"request": self.request, "estate_user": estate_user}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MessageViewSet(ListModelMixin, GenericViewSet):
    """"
    Returns
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        # check if the current user has access but if the user is a staff he has access to viewing the messages
        # notice I had to convert the user id to string that's because the id is currently a uuid
        if not str(self.request.user.id) in conversation_name.split("__") or self.request.user.is_staff is False:
            #  it raises an error if the user is not in this conversation
            raise Http404
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.id,
            )
            .filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset
