# Generated by Django 4.1.5 on 2023-01-12 10:53

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("40a2fafe-3e13-4190-b1dc-5c5289efd0de"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="estateutilitysubscription",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("73809ca2-8a62-40b7-b135-9ade95f59384"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
