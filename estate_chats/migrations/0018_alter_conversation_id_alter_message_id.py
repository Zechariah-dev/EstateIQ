# Generated by Django 4.1.5 on 2023-01-15 15:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0017_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("99512259-9f40-4922-96e4-140cf628cf57"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("8cd9b69e-cd9b-4e42-b486-ef64c3ce4750"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
