# Generated by Django 4.1.5 on 2023-01-12 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("estates", "0008_remove_estate_estate_subscription_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="EstateSubscription",
        ),
    ]
