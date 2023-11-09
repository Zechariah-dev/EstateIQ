# Generated by Django 4.1.5 on 2023-01-15 13:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0016_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("11708a1d-8614-467d-949d-437d0a1ca47b"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("88dbf969-e8b7-456f-8637-4213e3711af7"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]