# Generated by Django 4.1.5 on 2023-01-15 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("estate_webhooks", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="webhook",
            old_name="json",
            new_name="data",
        ),
    ]
