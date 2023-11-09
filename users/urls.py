from django.urls import path

from users.views import UserUpdateAPIView, SuperAdminGetUserDetailAPIView, SuperAdminGetUserListAPIView,UserDetailView

urlpatterns = [
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("super_admin_list_users/", SuperAdminGetUserListAPIView.as_view(), name="super_admin_list_users"),
    path("super_admin_user_detail/<str:id>/", SuperAdminGetUserDetailAPIView.as_view(), name="super_admin_user_detail"),
    path("user_detail/", UserDetailView.as_view(), name="user_detail"),
]
