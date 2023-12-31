# Generated by Django 4.1.5 on 2023-02-01 10:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0036_groupconversation_alter_message_id_groupmessage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="groupconversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("03b4b59e-d342-462a-80d2-333875fe0028"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="groupmessage",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("b0a2fd64-0a51-4772-8a77-3aba6d78230a"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("f3bb7152-a658-42e7-a1f3-555fcb4edff7"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
