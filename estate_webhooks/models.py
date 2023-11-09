from django.db import models

# Create your models here.
from django.utils import timezone


class Webhook(models.Model):
    """
    this is used to save webhook response before working on it for reference purposes
    """
    data = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-timestamp']
