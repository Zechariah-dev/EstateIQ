from django.urls import path

from estate_utilities.views import EstateUtilityListCreateAPIView, EstateUtilityRetrieveUpdateDestroyAPIView, \
    UtilityTransactionListAPIView, InitializeUtilityTransaction, EstateUtilityTransactionListAPIView, \
    EstateUtilityPenaltyListCreateAPIView, EstatePenaltyRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", EstateUtilityListCreateAPIView.as_view(), name="estate_utilities"),
    path("<str:id>/", EstateUtilityRetrieveUpdateDestroyAPIView.as_view(), name="estate_utilities"),
    path("utility/transaction/", UtilityTransactionListAPIView.as_view(), name="utility_transaction"),
    path("utility/estate_transaction/", EstateUtilityTransactionListAPIView.as_view(),
         name="estate_utility_transaction"),
    path("utility/initialize/", InitializeUtilityTransaction.as_view(),
         name="initialize_transaction"),
    path("list_create/penalty/", EstateUtilityPenaltyListCreateAPIView.as_view(),
         name="penalty_list_create"),
    path("penalty/<str:pk>/", EstatePenaltyRetrieveUpdateDestroyAPIView.as_view(),
         name="penalty_list_create"),
]
