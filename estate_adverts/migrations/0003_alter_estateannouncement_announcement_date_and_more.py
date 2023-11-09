# Generated by Django 4.1.5 on 2023-02-01 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_adverts", "0002_estateannouncement_estatereminder"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateannouncement",
            name="announcement_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="estatereminder",
            name="reminder_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
