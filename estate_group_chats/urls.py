from .views import GroupMessageViewSet, GroupConversationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# conversation route
router.register("group_conversations", GroupConversationViewSet)
urlpatterns = router.urls
#  message route
router.register("group_messages", GroupMessageViewSet)
# add the messages users to the urlpatterns
urlpatterns += router.urls
