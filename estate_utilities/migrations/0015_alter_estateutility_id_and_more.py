# Generated by Django 4.1.5 on 2023-01-15 10:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        (
            "estate_utilities",
            "0014_remove_estateutilitysubscription_transaction_id_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("3fb08095-e749-4bc6-bbc0-f0a5abb2a726"),
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
                default=uuid.UUID("bd27f9aa-d46f-4e80-a267-de1790e1f299"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
