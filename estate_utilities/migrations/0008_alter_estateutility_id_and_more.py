# Generated by Django 4.1.5 on 2023-01-12 11:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0007_alter_estateutility_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("9427982b-abef-470a-aee6-2db257887845"),
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
                default=uuid.UUID("a26d7067-ab12-4fcf-a4b2-801b8693be46"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
