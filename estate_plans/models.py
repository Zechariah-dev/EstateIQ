import uuid

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from estate_users.models import EstateUser
from estates.models import Estate
from datetime import timedelta

SUBSCRIPTION_PLAN_TYPE = (
    ("FREE", "FREE"),
    ("ESSENTIAL", "ESSENTIAL"),
    ("STANDARD", "STANDARD"),
    ("PREMIUM", "PREMIUM"),
)

STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE"),
)


class Plan(models.Model):
    """The plan is used by the estate in which and estate subscribe to"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField(blank=True,null=True)
    plan_type = models.CharField(choices=SUBSCRIPTION_PLAN_TYPE, unique=True, max_length=250)
    status = models.CharField(max_length=250, choices=STATUS, default="ACTIVE")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def activate_plan(self):
        """this activates a  plan if it is not activate"""
        self.plan_status = "ACTIVE"
        self.save()
        return True

    def deactivate_plan(self):
        """this deactivates a  plan if it is not activated, and it returns bool if it was successful or
        not """
        self.plan_status = "INACTIVE"
        self.save()
        return True


PAYMENT_TYPE = (
    ("FLUTTERWAVE", "FLUTTERWAVE"),
    ("PAYSTACK", "PAYSTACK"),
    ("BANK", "BANK"),
)
TRANSACTION_STATUS = (
    ('PENDING', 'PENDING'),
    ('FAILED', 'FAILED'),
    ('SUCCESS', 'SUCCESS'),
)


class EstateTransaction(models.Model):
    """
    this contains info about an estate transaction list of all payment made and the plan the transaction
    was made for
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate_user = models.ForeignKey(EstateUser, on_delete=models.SET_NULL, blank=True, null=True)
    estate = models.ForeignKey(Estate, on_delete=models.SET_NULL, blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=250, choices=TRANSACTION_STATUS, default="PENDING")
    transaction_reference = models.CharField(max_length=250, blank=True, null=True, unique=True)
    payment_type = models.CharField(choices=PAYMENT_TYPE, blank=True, null=True, max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def update_estate_subscription(self):
        """
        this is used to update an estate subscription with the current transaction
        :return:
        """
        # Only update if the transaction status is success
        if self.status == "SUCCESS":
            # Get or create the estate
            estate_subscription, created = EstateSubscription.objects.get_or_create(estate=self.estate)
            # Set the plan
            estate_subscription.plan = self.plan
            estate_subscription.status = "ACTIVE"
            due_date = timezone.now() + timedelta(days=365)
            estate_subscription.due_date = due_date
            estate_subscription.payment_type = self.payment_type
            estate_subscription.paid_date = timezone.now()
            estate_subscription.save()


class EstateSubscription(models.Model):
    """
    This is the estate subscription
    by default it uses the free subscription for an estate which reduces the number of permission the estate have
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.OneToOneField(Estate, on_delete=models.CASCADE)
    status = models.CharField(max_length=250, choices=STATUS)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    payment_type = models.CharField(choices=PAYMENT_TYPE, blank=True, null=True, max_length=250)
    account_name = models.CharField(max_length=250, blank=True, null=True)
    # The bank and account number is only used if the admin would like to update
    # if the user paid through bank
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    account_number = models.CharField(max_length=15, blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)


def post_save_create_free_estate_subscription(sender, instance: Estate, *args, **kwargs):
    """
    This creates the owner as part of the estate user and as an admin
    and also create a free estate_subscription for an estate
    :return:
    """
    free_plan, created = Plan.objects.get_or_create(
        price=0, plan_type="FREE", status="ACTIVE")
    if instance:
        # If the estate subscription does not exist I need to create one
        estate_subscription = EstateSubscription.objects.filter(estate=instance).first()
        if not estate_subscription:
            # Create the estate subscription or just get it
            EstateSubscription.objects.get_or_create(
                estate=instance,
                plan=free_plan, )


post_save.connect(post_save_create_free_estate_subscription, sender=Estate)
