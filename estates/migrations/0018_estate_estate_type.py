# Generated by Django 4.1.5 on 2023-08-18 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estates', '0017_estate_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='estate',
            name='estate_type',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
