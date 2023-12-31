# Generated by Django 4.1.5 on 2023-01-12 10:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("estate_plans", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Estate",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.UUID("7cb15042-f984-42b3-9bb6-032eca336649"),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("estate_id", models.CharField(max_length=250, unique=True)),
                ("name", models.CharField(max_length=250)),
                ("country", models.CharField(max_length=250)),
                ("address", models.CharField(max_length=250)),
                ("state", models.CharField(max_length=250)),
                ("lga", models.CharField(max_length=250)),
                ("accept_terms_and_condition", models.BooleanField(default=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="EstateSubscription",
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
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")],
                        max_length=250,
                    ),
                ),
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
                    "transaction_id",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                (
                    "account_name",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("bank_name", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "account_number",
                    models.CharField(blank=True, max_length=15, null=True),
                ),
                ("paid_date", models.DateTimeField(blank=True, null=True)),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "estate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="estates.estate"
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="estate_plans.plan",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="estate",
            name="estate_subscription",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="estate_subscriptions",
                to="estates.estatesubscription",
            ),
        ),
    ]
