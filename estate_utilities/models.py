import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete, post_delete
from django.utils import timezone

from estate_users.models import EstateUser
from estate_utilities.tasks import remove_penalty_not_existing_on_utility_penalty
from estates.models import Estate

User = settings.AUTH_USER_MODEL

PAYMENT_FREQUENCY = (
    ("MONTHLY", "MONTHLY"),
    ("QUARTERLY", "QUARTERLY"),
    ("HALF_YEARLY", "HALF_YEARLY"),
    ("YEARLY", "YEARLY"),
)

COLLECTION_TYPE = (
    ("MANDATORY", "MANDATORY"),
    ("NOT_MANDATORY", "NOT_MANDATORY"),
)

# The expired part is used for the subscription class
STATUS = (
    ("PENDING", "PENDING"),
    ("FAILED", "FAILED"),
    ("SUCCESS", "SUCCESS"),
    ("EXPIRED", "EXPIRED"),
)
PAYMENT_TYPE = (
    ("FLUTTERWAVE", "FLUTTERWAVE"),
    ("PAYSTACK", "PAYSTACK"),
    ("BANK", "BANK"),
)

TRANSACTION_TYPE = (
    ('CREDIT', 'CREDIT'),
    ('DEBIT', 'DEBIT')
)
TRANSACTION_STATUS = (
    ('PENDING', 'PENDING'),
    ('FAILED', 'FAILED'),
    ('SUCCESS', 'SUCCESS'),
)

COLLECTION_TARGET = (
    ('RESIDENT', 'RESIDENT'),
    ('EXTERNAL', 'EXTERNAL'),
)


class EstateUtility(models.Model):
    """
    This utility enables estates to be owners to create collection in which
    resident of an estate pays for
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # The utility was created by this estate user
    staff = models.ForeignKey(EstateUser, on_delete=models.SET_NULL, blank=True, null=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    payment_frequency = models.CharField(choices=PAYMENT_FREQUENCY, max_length=50)
    minimum_purchase = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    account_name = models.CharField(max_length=250, blank=True, null=True)
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    account_number = models.CharField(max_length=15, blank=True, null=True)
    collection_type = models.CharField(choices=COLLECTION_TYPE, max_length=50)
    collection_target = models.CharField(choices=COLLECTION_TARGET, max_length=50, blank=True, null=True)
    due_date = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-timestamp',)


class UtilityTransaction(models.Model):
    """
    the transaction is tied to a user
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    estate_user = models.ForeignKey(EstateUser, on_delete=models.CASCADE)
    estate_utility = models.ForeignKey(EstateUtility, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    payment_type = models.CharField(max_length=250, choices=PAYMENT_TYPE, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    message = models.CharField(max_length=400, blank=True, null=True)
    status = models.CharField(max_length=50, choices=TRANSACTION_STATUS, blank=True, null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    paid_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f"{self.estate_user} -- {self.amount}"


UNPAID_PERIOD_CHOICE = (
    ("WEEK", "WEEK"),
    ("MONTH", "MONTH"),
    ("YEAR", "YEAR"),
)


class EstateUtilityPenalty(models.Model):
    """
    this is used to create penalty by preventing some users to access some stuff who have
    not paid for a utility
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    estate_utility = models.ForeignKey(EstateUtility, on_delete=models.CASCADE, blank=True, null=True)
    unpaid_in = models.IntegerField()
    unpaid_period = models.CharField(max_length=250)
    revoke = models.CharField(max_length=250)
    timestamp = models.DateTimeField(default=timezone.now)

    @property
    def revoke_list(self):
        try:
            revoke_list = self.revoke.split(",")
        except:
            revoke_list = []
        return revoke_list


def pre_modify_user_penalty_permission_after_delete(sender, instance: EstateUtilityPenalty, *args, **kwargs):
    """
    If the penalty permission is deleted this modifies the estate user
     that are affected to go back to the way they were
    """
    if instance:
        for item in instance.revoke:
            if item == "ON_TO_ONE_MESSAGE":
                instance.estate.estateuser_set.update(on_to_one_message=True)
            elif item == "UTILITY_PORTAL":
                instance.estate.estateuser_set.update(utility_portal=True)
            elif item == "EMERGENCY_SERVICE":
                instance.estate.estateuser_set.update(emergency_service=True)
            elif item == "GATE_PASS":
                instance.estate.estateuser_set.update(gate_pass=True)

    remove_penalty_not_existing_on_utility_penalty.delay()


post_delete.connect(pre_modify_user_penalty_permission_after_delete, sender=EstateUtilityPenalty)
