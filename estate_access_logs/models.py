from django.db import models

# Create your models here.
from django.db.models.signals import post_save

from estate_users.models import EstateUser, GENDER_CHOICES
from estates.models import Estate
import uuid

ESTATE_ACCESS_LOG_ACCESS = (
    ("GRANT", "GRANT"),
    ("REVOKE", "REVOKE"),
)
# Drop down - One Time Guest, Regular Guest, Artisan, Taxi, Event
ACCESS_LOG_CATEGORY = (
    ("VISITOR", "VISITOR"),
    ("ARTISAN", "ARTISAN"),
    ("TAXI", "TAXI"),
    ("DELIVERY", "DELIVERY"),
    ("EVENT", "EVENT"),
    ("VEHICLE", "VEHICLE"),
    ("CLIENT", "CLIENT"),
    ("PEDESTRIAN", "PEDESTRIAN"),
    ("HOUSEHOLD_ITEMS", "HOUSEHOLD_ITEMS"),
    ("OTHERS", "OTHERS"),
)

ACCESS_TYPE = (
    ("ONE_TIME", "ONE_TIME"),
    ("PERMANENT", "PERMANENT"),
)
WAYBILL_TYPE = (
    ("INBOUND_ITEM", "INBOUND_ITEM"),
    ("OUTBOUND_ITEM", "OUTBOUND_ITEM"),
)

ACCESS_LOG_TYPE = (
    ("PRIVATE", "PRIVATE"),
    ("BUSINESS", "BUSINESS"),
    ("WAYBILL", "WAYBILL"),
)


class EstateAccessLog(models.Model):
    """
    this is the access log of an estate which can be created by a user
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate_user = models.ForeignKey(EstateUser, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name="access_log_created_by")
    estate = models.ForeignKey(Estate, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    from_date = models.DateTimeField(blank=True, null=True)
    to_date = models.DateTimeField(blank=True, null=True)
    access_code = models.CharField(max_length=50)
    access = models.CharField(max_length=50, choices=ESTATE_ACCESS_LOG_ACCESS, blank=True, null=True)
    # the external scanning the access code
    updated_by = models.ForeignKey(EstateUser, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="access_log_updated_by")
    access_type = models.CharField(max_length=255, null=True, blank=True, choices=ACCESS_TYPE, default='ONETIME')
    category = models.CharField(choices=ACCESS_LOG_CATEGORY, max_length=250, blank=True, null=True,
                                default="OTHERS")
    verified_time = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # new fields for waybill
    vehicle_number = models.CharField(max_length=250, blank=True, null=True)
    waybill_type = models.CharField(max_length=255, null=True, blank=True, choices=WAYBILL_TYPE)
    item_type = models.CharField(max_length=250, blank=True, null=True)
    access_log_type = models.CharField(max_length=250, choices=ACCESS_LOG_TYPE, default="PRIVATE")
    gender = models.CharField(max_length=250, choices=GENDER_CHOICES, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']


def pre_save_generate_estate_id(sender, instance: EstateAccessLog, *args, **kwargs):
    """this generates a unique access code which gas not been used and add it to the estate
    currently being created"""
    # Using local import
    from .utils import create_unique_access_code

    if instance:
        if not instance.access_code:
            instance.access_code = create_unique_access_code(EstateAccessLog)
            # Save it
            instance.save()


post_save.connect(pre_save_generate_estate_id, sender=EstateAccessLog)
