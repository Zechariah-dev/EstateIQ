from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import EstateIQLoginAPIView, RequestEmailLinkAPIView, VerifyEmailAPIView, \
    EstateIQRegisterAPIView, UserChangePasword, RequestEmailOTPAPIView, ForgotPasswordWithOTPAPIView, \
    EstateIQGoogleLoginAPIView, EstateIQFacebookLoginAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("estate_home_pages.urls")),
    path("api/v1/estates/", include("estates.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/estate_utilities/", include("estate_utilities.urls")),
    path("api/v1/estate_plans/", include("estate_plans.urls")),
    path("api/v1/estate_webhooks/", include("estate_webhooks.urls")),
    path("api/v1/estate_users/", include("estate_users.urls")),
    path("api/v1/estate_chats/", include("estate_chats.urls")),
    path("api/v1/estate_complaints/", include("estate_complaints.urls")),
    path("api/v1/estate_access_logs/", include("estate_access_logs.urls")),
    path("api/v1/estate_adverts/", include("estate_adverts.urls")),
    path("api/v1/estate_group_chats/", include("estate_group_chats.urls")),
    path("api/v1/estate_user_notifications/", include("estate_user_notifications.urls")),
]

# The authentication urls which contains login, register, request otp and verify account
auth_urlpatterns = [
    path("api/v1/auth/login/", EstateIQLoginAPIView.as_view(), name="estate_iq_login"),
    path("api/v1/auth/registration/", EstateIQRegisterAPIView.as_view(), name="estate_iq_register"),
    path("api/v1/auth/google_login/", EstateIQGoogleLoginAPIView.as_view(), name="google_login"),
    path("api/v1/auth/facebook_login/", EstateIQFacebookLoginAPIView.as_view(), name="facebook_login"),
    #  requesting otp via email
    path("api/v1/auth/request_email_link/", RequestEmailLinkAPIView.as_view(), name="estate_iq_request_otp"),
    #  verify account with the otp passed on posted data
    path("api/v1/auth/verify_account/", VerifyEmailAPIView.as_view(), name="estate_iq_verify_account"),
    path("api/v1/auth/set_password/", UserChangePasword.as_view(), name="set_password"),
    path("api/v1/auth/request_otp/", RequestEmailOTPAPIView.as_view(), name="estate_iq_request_otp"),
    path("api/v1/auth/forgot_password/", ForgotPasswordWithOTPAPIView.as_view(), name="forgot_password"),
]

urlpatterns += auth_urlpatterns

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)
