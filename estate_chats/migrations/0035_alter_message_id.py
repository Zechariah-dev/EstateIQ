# Generated by Django 4.1.5 on 2023-01-26 21:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0034_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("d093cbd3-754c-4bb7-b30b-ba468cc3360d"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
