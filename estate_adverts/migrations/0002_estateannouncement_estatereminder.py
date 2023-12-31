# Generated by Django 4.1.5 on 2023-02-01 13:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_adverts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EstateAnnouncement",
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
                ("title", models.CharField(max_length=250)),
                ("image", models.ImageField(upload_to="announcement_image")),
                ("description", models.TextField()),
                ("announcement_date", models.DateTimeField(auto_now_add=True)),
                (
                    "recipients",
                    models.CharField(
                        choices=[
                            ("ADMIN", "ADMIN"),
                            ("RESIDENT", "RESIDENT"),
                            ("EXTERNAL", "EXTERNAL"),
                        ],
                        max_length=50,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="EstateReminder",
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
                ("title", models.CharField(max_length=250)),
                ("image", models.ImageField(upload_to="reminders_image")),
                ("description", models.TextField()),
                ("reminder_date", models.DateTimeField(auto_now_add=True)),
                (
                    "recipients",
                    models.CharField(
                        choices=[
                            ("ADMIN", "ADMIN"),
                            ("RESIDENT", "RESIDENT"),
                            ("EXTERNAL", "EXTERNAL"),
                        ],
                        max_length=50,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
