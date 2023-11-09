from django.urls import path

from .views import EstateUserProfileUpdateAPIView, EstateUserDetailAPIView, ResidentInviteEstateUserAPIView, \
    AdminInviteEstateUserAPIView, AdminEstateUserListAPIView, ResidentEstateUserListAPIView, UserEstateUserListAPIView, \
    ModifyEstateUserAPIView, EstateUserAnalyticsAPIView, EstateUserBulkUploadAPIView, \
    EstateUserUpdateProfileImageAPIView, ResidentMobileInviteEstateUserAPIView

urlpatterns = [
    path("admin_list/", AdminEstateUserListAPIView.as_view(), name="admin_list"),
    path("resident_list/", ResidentEstateUserListAPIView.as_view(), name="resident_list"),
    path("user_list/", UserEstateUserListAPIView.as_view(), name="user_list"),
    path("estate_user_profile_update/", EstateUserProfileUpdateAPIView.as_view(), name="profile_update"),
    path("estate_user_detail/", EstateUserDetailAPIView.as_view(), name="user_detail"),
    path("resident_invite/", ResidentInviteEstateUserAPIView.as_view(), name="resident_invite"),
    path("resident_invite_mobile/", ResidentMobileInviteEstateUserAPIView.as_view(), name="resident_invite_mobile"),
    path("admin_invite/", AdminInviteEstateUserAPIView.as_view(), name="admin_invite"),
    path("modify_user/", ModifyEstateUserAPIView.as_view(), name="modify_estate_user"),
    path("estate_user_analytics/", EstateUserAnalyticsAPIView.as_view(), name="estate_user_analytics"),
    path("estate_user_bulk_upload/", EstateUserBulkUploadAPIView.as_view(), name="estate_user_bulk_upload"),
    path("estate_user_profile_image_update/", EstateUserUpdateProfileImageAPIView.as_view(),
         name="estate_user_profile_image_update"),
]
