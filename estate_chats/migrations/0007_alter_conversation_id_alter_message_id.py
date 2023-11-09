# Generated by Django 4.1.5 on 2023-01-12 11:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0006_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("c8add890-f161-4fdd-a725-adb4d52e525a"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("7fa1b5c4-daba-4d13-9f48-c7495893b4b3"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]