# Generated by Django 4.1.5 on 2023-08-18 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_adverts', '0005_estateadvertisement_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='estateadvertisement',
            name='business_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
