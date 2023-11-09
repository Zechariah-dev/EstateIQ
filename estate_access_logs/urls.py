from django.urls import path

from estate_access_logs.views import EstateAccessLogVerificationAPIView, EstateAccessLogListCreateAPIView, \
    ModifyEstateAccessLogAPIView, SuperAdminEstateAccessLogListAPIView, EstateAccessLogExitPassCreateView, \
    EstateAccessLogWaybillCreateView

urlpatterns = [
    path("", EstateAccessLogListCreateAPIView.as_view(), name="estate_access_log"),
    path("waybill_create/", EstateAccessLogWaybillCreateView.as_view(), name="waybill_create"),
    path("exit_pass_create/", EstateAccessLogExitPassCreateView.as_view(), name="exit_pass_create"),
    path("superadmin/", SuperAdminEstateAccessLogListAPIView.as_view(), name="superadmin_estate_access_log"),
    path("verify/", EstateAccessLogVerificationAPIView.as_view(), name="estate_access_log_verify"),
    path("modify/", ModifyEstateAccessLogAPIView.as_view(), name="estate_access_log_modify"),
]
