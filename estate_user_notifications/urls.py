from django.urls import path

from estate_user_notifications.views import EstateUserNotificationListAPIView, SuperAdminNotificationListAPIView, \
    EstateUserNotificationRetrieveAPIView,SuperAdminNotificationRetrieveAPIView

urlpatterns = [
    path("estate_users/", EstateUserNotificationListAPIView.as_view(), name="estate_user_notifications"),
    path("estate_users/<str:id>/", EstateUserNotificationRetrieveAPIView.as_view(),
         name="estate_user_notifications_detail"),
    path("superadmin/", SuperAdminNotificationListAPIView.as_view(), name="super_admin_notifications"),
    path("superadmin/<str:id>/", SuperAdminNotificationRetrieveAPIView.as_view(), name="super_admin_notifications_detail")
]
