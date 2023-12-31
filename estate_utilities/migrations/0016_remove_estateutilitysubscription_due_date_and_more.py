# Generated by Django 4.1.5 on 2023-01-15 13:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0015_alter_estateutility_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="estateutilitysubscription",
            name="due_date",
        ),
        migrations.RemoveField(
            model_name="estateutilitysubscription",
            name="paid_date",
        ),
        migrations.AddField(
            model_name="utilitytransaction",
            name="due_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="utilitytransaction",
            name="paid_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("4fe42def-c7bc-4533-8fd9-cd7c0c751dae"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="estateutility",
            name="payment_frequency",
            field=models.CharField(
                choices=[
                    ("MONTHLY", "MONTHLY"),
                    ("QUARTERLY", "QUARTERLY"),
                    ("HALF_YEARLY", "HALF_YEARLY"),
                    ("YEARLY", "YEARLY"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="estateutilitysubscription",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("69e124a8-4baf-42fe-bd86-c108d7473508"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="estateutilitysubscription",
            name="status",
            field=models.CharField(
                max_length=50,
                verbose_name=(
                    ("PENDING", "PENDING"),
                    ("FAILED", "FAILED"),
                    ("SUCCESS", "SUCCESS"),
                    ("EXPIRED", "EXPIRED"),
                ),
            ),
        ),
    ]
