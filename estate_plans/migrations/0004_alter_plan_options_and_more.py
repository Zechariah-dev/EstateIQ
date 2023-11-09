# Generated by Django 4.1.5 on 2023-01-15 13:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estates", "0011_estatezone"),
        ("estate_plans", "0003_alter_estatesubscription_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="plan",
            options={"ordering": ("-timestamp",)},
        ),
        migrations.RenameField(
            model_name="estatesubscription",
            old_name="transaction_id",
            new_name="transaction_ref",
        ),
        migrations.CreateModel(
            name="EstateTransaction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("amount", models.FloatField(default=0)),
                (
                    "payment_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("FLUTTERWAVE", "FLUTTERWAVE"),
                            ("PAYSTACK", "PAYSTACK"),
                            ("BANK", "BANK"),
                        ],
                        max_length=250,
                        null=True,
                    ),
                ),
                (
                    "transaction_reference",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PENDING", "PENDING"),
                            ("FAILED", "FAILED"),
                            ("SUCCESS", "SUCCESS"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "estate",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="estates.estate"
                    ),
                ),
            ],
        ),
    ]
