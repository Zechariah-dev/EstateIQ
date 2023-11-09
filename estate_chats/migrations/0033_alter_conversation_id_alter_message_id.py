# Generated by Django 4.1.5 on 2023-01-26 19:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0032_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("db9ebdf5-4260-4e5c-9065-ca3f42cf90a7"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("b3aa1968-6fe4-499f-ac7b-a413982d80dc"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
