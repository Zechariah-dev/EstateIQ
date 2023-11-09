from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
from estate_users.models import EstateUser
from estates.models import Estate

COMPLAINT_STATUS = (
    ("RESOLVED", "RESOLVED"),
    ("PENDING", "PENDING"),
)

COMPLAINT_RECEIVERS = (
    ("CHIEF_SECURITY_OFFICER", "CHIEF_SECURITY_OFFICER"),
    ("FINANCIAL_SECRETARY", "FINANCIAL_SECRETARY"),
    ("ESTATE_MANAGER", "ESTATE_MANAGER"),
    ("EXCOS", "EXCOS"),
)


class EstateComplaint(models.Model):
    """
    this is used by the estate users, resident, external to make complaint on an estate
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    estate_user = models.ForeignKey(
        EstateUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="estate_user",
    )
    title = models.CharField(max_length=250, blank=True, null=True)
    case_id = models.CharField(null=True, blank=True, max_length=10)
    reason = models.CharField(max_length=500)
    receivers = models.CharField(choices=COMPLAINT_RECEIVERS, max_length=50)
    message = models.TextField()
    status = models.CharField(
        max_length=50, choices=COMPLAINT_STATUS, default="PENDING"
    )
    updated_by = models.ForeignKey(
        EstateUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="updated_by",
    )
    updated_time = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def save(self, *args, **kwargs):
        if not self.case_id:
            if self.estate:
                existing_complaints_count = EstateComplaint.objects.filter(
                    estate=self.estate
                ).count()
                self.case_id = f"{existing_complaints_count + 1:03d}"
        super().save(*args, **kwargs)
