# Generated by Django 4.1.5 on 2023-01-15 15:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0020_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("5445dd91-5f3f-4429-814e-122862025432"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("6b82577c-4e89-4c9f-94e9-348d2af1cd21"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
