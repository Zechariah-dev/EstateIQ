# Generated by Django 4.1.5 on 2023-01-13 12:50

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_chats", "0011_alter_conversation_id_alter_message_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("e8c1e114-61fa-4b5a-bdee-68b43f778d0c"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("66c1d322-ce57-45c9-8a25-dcd32b60e5ad"),
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]