# Generated by Django 4.1.5 on 2023-01-12 11:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0004_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("7add4cdf-c8c8-493b-beba-e2988cdef43b"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("27844b6e-cda1-4de9-befe-600097abd181"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
