# Generated by Django 4.1.5 on 2023-02-01 10:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estates", "0014_alter_estate_status_estatestreet"),
        ("estate_utilities", "0031_estateutility_collection_target"),
    ]

    operations = [
        migrations.CreateModel(
            name="EstateUtilityPenalty",
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
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "estate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="estates.estate"
                    ),
                ),
            ],
        ),
    ]