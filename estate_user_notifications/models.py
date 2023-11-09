import uuid

from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse

from estate_adverts.models import EstateReminder, EstateAdvertisement, EstateAnnouncement
from estate_user_notifications.tasks import create_notification_for_reminder, create_notification_for_advert, \
    create_notification_for_announcement
from estate_users.models import EstateUser
from estates.models import Estate

NOTIFICATION_TYPE = (
    ("MESSAGE", "MESSAGE"),
    ("ADVERT", "ADVERT"),
    ("REMINDER", "REMINDER"),
    ("ALERT", "ALERT"),
    ("ANNOUNCEMENT", "ANNOUNCEMENT"),
)


class EstateUserNotification(models.Model):
    """
    this creates notification for all estate users in an estate
    When an advert is created, reminder, new message,
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # The estate user that have the notification
    estate_user = models.ForeignKey(EstateUser, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE)
    # Url to direct the user on every notification
    redirect_url = models.URLField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def get_absolute_url(self):
        return reverse("estate_user_notifications_detail", kwargs={"id": self.id})


def post_save_create_notification_for_reminder(sender, instance, *args, **kwargs):
    """
    This creates a  notification for all estate user for a new reminder
    """
    if instance:
        create_notification_for_reminder.delay(message=f"{instance.title}")


post_save.connect(post_save_create_notification_for_reminder, sender=EstateReminder)


def post_save_create_notification_for_advert(sender, instance, *args, **kwargs):
    """
    This creates a  notification for all estate user for a new advert
    """
    if instance:
        create_notification_for_advert.delay(message=f"{instance.title}")


post_save.connect(post_save_create_notification_for_advert, sender=EstateAdvertisement)


def post_save_create_notification_for_announcement(sender, instance, *args, **kwargs):
    """
    This creates a  notification for all estate user for a new announcement
    """
    if instance:
        create_notification_for_announcement.delay(message=f"{instance.title}")


post_save.connect(post_save_create_notification_for_announcement, sender=EstateAnnouncement)

SUPER_ADMIN_NOTIFICATION_TYPE = (
    ("ESTATE_CREATED", "ESTATE_CREATED"),
    ("MESSAGE", "MESSAGE"),
)


class SuperAdminNotification(models.Model):
    """
    This contains list of notifications to be shown to the superadmin only
    like new estate was created , estate subscription failed and more
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Url to direct the user on every notification
    redirect_url = models.URLField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    notification_type = models.CharField(max_length=50, choices=SUPER_ADMIN_NOTIFICATION_TYPE)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def get_absolute_url(self):
        return reverse("super_admin_notifications_detail", kwargs={"id": self.id})


def post_save_create_notification_for_estate_created(sender, instance, *args, **kwargs):
    """
    This creates a  notification for  new estate_created
    """
    if instance:
        notification, created = SuperAdminNotification.objects.get_or_create(
            message=f"{instance.name}-{instance.estate_id}",
            notification_type="ESTATE_CREATED"
        )
        notification.redirect_url = "https://estate-iq.netlify.app/superadmin/estate/"
        notification.save()


post_save.connect(post_save_create_notification_for_estate_created, sender=Estate)
