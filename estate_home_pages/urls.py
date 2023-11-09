from django.urls import path

from estate_home_pages.views import home_page, WaitListCreateView

app_name = 'estate_home_pages'
urlpatterns = [
    path('', home_page, name='estate_home_pages'),
    path('api/v1/wait_list/', WaitListCreateView.as_view(), name='wait_list'),

]
