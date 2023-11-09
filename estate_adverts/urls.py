from .views import EstateAdvertisementViewSetsAPIView, EstateAnnouncementViewSetsAPIView, EstateReminderViewSetsAPIView
from rest_framework.routers import DefaultRouter

urlpatterns = [

]
router = DefaultRouter()
router.register(r'adverts', EstateAdvertisementViewSetsAPIView, basename='estate_adverts')
router.register(r'announcement', EstateAnnouncementViewSetsAPIView, basename='estate_announcements')
router.register(r'reminder', EstateReminderViewSetsAPIView, basename='estate_reminder')
urlpatterns += router.urls
