# Generated by Django 4.1.5 on 2023-01-12 10:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Conversation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.UUID("02565a65-f1cf-4121-8858-f66245209d49"),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.UUID("1aea6e72-6c26-4d87-a76e-3585dddc454d"),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("content", models.CharField(max_length=512)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("read", models.BooleanField(default=False)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="estate_chats.conversation",
                    ),
                ),
            ],
        ),
    ]
