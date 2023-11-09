from django.db import models
import uuid
from estate_users.models import ESTATE_USER_TYPE


# Create your models here.


class EstateAdvertisement(models.Model):
    """this shows list of advert that could be shown in the estate dashboard """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    business_name = models.CharField(max_length=250,blank=True,null=True)
    image = models.ImageField(upload_to="advert_image")
    description = models.TextField()
    phone_number = models.CharField(blank=True, null=True,max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)


class EstateAnnouncement(models.Model):
    """this shows list of announce ment that could be shown in the estate dashboard """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="announcement_image")
    description = models.TextField()
    announcement_date = models.DateTimeField()
    recipients = models.CharField(max_length=50, choices=ESTATE_USER_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)


class EstateReminder(models.Model):
    """this shows list of reminders that could be shown in the estate dashboard """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="reminders_image")
    description = models.TextField()
    reminder_date = models.DateTimeField()
    recipients = models.CharField(max_length=50, choices=ESTATE_USER_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)
