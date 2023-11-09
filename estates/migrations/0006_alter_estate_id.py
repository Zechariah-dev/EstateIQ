# Generated by Django 4.1.5 on 2023-01-12 11:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estates", "0005_alter_estate_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estate",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("2a566ea3-e045-4b41-be78-94bad54e9eaf"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]