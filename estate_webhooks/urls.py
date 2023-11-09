from django.urls import path

from .views import WebhookAPIView

urlpatterns = [
    path("", WebhookAPIView.as_view(), name="estates"),
]
