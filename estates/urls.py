from django.urls import path

from .views import EstateListCreateAPIView, EstateZoneListCreateAPIView, EstateStreetListCreateAPIView, \
    SuperAdminEstateListCreateAPIView, SuperAdminEstateRetrieveUpdateDestroyAPIView, EstateNotLoggedinDetailAPIView, \
    EstateDetailAPIView, EstateCreatStreetWithoutZoneListCreateView, EstateZoneRetrieveUpdateDestroyView, \
    EstateStreetRetrieveUpdateDestroyView, EstateUpdateLogoView

urlpatterns = [
    path("", EstateListCreateAPIView.as_view(), name="estates"),
    path("estate_info/<str:estate_id>/", EstateNotLoggedinDetailAPIView.as_view(), name="estate_info"),
    path("estate_detail/<str:estate_id>/", EstateDetailAPIView.as_view(), name="estate_detail"),
    path("super_admin/", SuperAdminEstateListCreateAPIView.as_view(), name="super_admin_estates"),
    path("super_admin/<str:estate_id>/", SuperAdminEstateRetrieveUpdateDestroyAPIView.as_view(),
         name="super_admin_estates_detail"),
    path("estates_zone/", EstateZoneListCreateAPIView.as_view(), name="estates_zone"),
    path("estates_street/", EstateStreetListCreateAPIView.as_view(), name="estates_street"),
    path("estates_street_no_zone/", EstateCreatStreetWithoutZoneListCreateView.as_view(),
         name="estates_street_no_zone"),
    path("estates_zone/<str:pk>/", EstateZoneRetrieveUpdateDestroyView.as_view(),
         name="estates_street_det"),
    path("estates_street/<str:pk>/", EstateStreetRetrieveUpdateDestroyView.as_view(),
         name="estates_street_det"),
    path("estate_update_logo/", EstateUpdateLogoView.as_view(),
         name="estate_update_logo"),

]
