# Generated by Django 4.1.5 on 2023-01-15 13:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0015_alter_user_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("9670d180-8676-4a66-b32e-ff334d7a2456"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
