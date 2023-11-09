from django.urls import path

from .views import InitializeEstateSubscriptionAPIView, PlanCreateAPIView, PlanListAPIView, \
    PlanRetrieveUpdateDestroyAPIView, EstateTransactionListAPIView, SuperAdminEstateTransactionListAPIView, \
    SuperAdminEstateSubscriptionListAPIView, EstateSubscriptionAPIView, EstateSubscriptionModifyAPIView, \
    PlanAnalyTicsAPIView

urlpatterns = [
    path("", PlanListAPIView.as_view(), name="plan_list"),
    path("create/plan/", PlanCreateAPIView.as_view(), name="plan_create"),
    path("plan/<str:id>/", PlanRetrieveUpdateDestroyAPIView.as_view(), name="plan_retrieve_update_destroy"),
    path("transaction/initialize/", InitializeEstateSubscriptionAPIView.as_view(), name="initialize_transaction"),
    path("transaction/list/", EstateTransactionListAPIView.as_view(), name="transaction_list"),
    path("superadmin_transaction/list/", SuperAdminEstateTransactionListAPIView.as_view(),
         name="superadmin_transaction_list"),
    path("superadmin_subscription/list/", SuperAdminEstateSubscriptionListAPIView.as_view(),
         name="superadmin_subscription_list"),
    path("estate_subscription/", EstateSubscriptionAPIView.as_view(),
         name="estate_subscription"),
    path("modify_subscription/", EstateSubscriptionModifyAPIView.as_view(),
         name="modify_subscription"),
    path("plan_analytics/", PlanAnalyTicsAPIView.as_view(),
         name="modify_subscription"),

]
