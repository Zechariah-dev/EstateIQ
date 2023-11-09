import uuid

from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone

from users.models import User

STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE"),
    ("PENDING", "PENDING"),
)

ESTATE_TYPE = (
    ("PUBLIC_RESIDENTIAL_HOUSING_SCHEME", "PUBLIC_RESIDENTIAL_HOUSING_SCHEME"),
    ("PRIVATE_ESTATE", "PRIVATE_ESTATE"),
    ("CORPORATE_RESIDENTIAL_ESTATE", "CORPORATE_RESIDENTIAL_ESTATE"),
    ("MIXED_PRIVATE_BUSINESSES", "MIXED_PRIVATE_BUSINESSES"),
)


class Estate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    estate_id = models.CharField(max_length=250, unique=True)
    estate_type = models.CharField(max_length=250, blank=True, null=True)
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    logo = models.ImageField(upload_to="logo", blank=True, null=True)
    address = models.CharField(max_length=250)
    status = models.CharField(max_length=250, default="PENDING")
    state = models.CharField(max_length=250, blank=True, null=True)
    lga = models.CharField(max_length=250)
    accept_terms_and_condition = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)


def pre_save_generate_estate_id(sender, instance: Estate, *args, **kwargs):
    """this generates a unique estate id which gas not been used and add it to the estate
    currently being created"""
    # Using local import
    from estates.utils import create_unique_estate_id

    if instance:
        if not instance.estate_id:
            instance.estate_id = create_unique_estate_id(Estate)
            # Save it
            instance.save()


post_save.connect(pre_save_generate_estate_id, sender=Estate)


class EstateZone(models.Model):
    """
    This is used for zone within an estate
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)


class EstateStreet(models.Model):
    """
    These are the list of street available to an estate
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    estate_zone = models.ForeignKey(EstateZone, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)
