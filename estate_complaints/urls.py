from django.urls import path

from .views import EstateComplaintListCreateAPIView, EstateComplaintRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", EstateComplaintListCreateAPIView.as_view(), name="estate_complaint"),
    path("<str:pk>/", EstateComplaintRetrieveUpdateDestroyAPIView.as_view(),
         name="estate_complaint_retrieve_update_destroy"),
]
