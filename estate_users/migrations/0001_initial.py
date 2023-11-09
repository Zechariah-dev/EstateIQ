# Generated by Django 4.1.5 on 2023-01-12 10:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EstateUser",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.UUID("18c70b10-4665-44be-a65b-2e9d8ca51202"),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "user_type",
                    models.CharField(
                        choices=[
                            ("ADMIN", "ADMIN"),
                            ("RESIDENT", "RESIDENT"),
                            ("EXTERNAL", "EXTERNAL"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "user_category",
                    models.CharField(
                        choices=[("OTHERS", "OTHERS"), ("SECURITY", "SECURITY")],
                        default="OTHERS",
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")],
                        max_length=250,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]