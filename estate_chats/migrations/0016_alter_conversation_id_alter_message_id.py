# Generated by Django 4.1.5 on 2023-01-15 13:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0015_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("cdf48956-a6a1-4f67-b4e8-32320db18308"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("f93a5a40-9ce1-411d-9088-5a74f34b049d"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
