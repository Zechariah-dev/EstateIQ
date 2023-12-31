# Generated by Django 4.1.5 on 2023-01-12 11:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0005_alter_estateutility_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("474b3c70-d79e-41cf-9fd4-eb9bcbf2fa71"),
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
                default=uuid.UUID("e7a0c7bf-b171-44b5-9015-bac7195fb74c"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
