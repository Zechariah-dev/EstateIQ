# Generated by Django 4.1.5 on 2023-07-28 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_access_logs', '0005_estateaccesslog_access_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estateaccesslog',
            name='from_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='estateaccesslog',
            name='to_date',
            field=models.DateTimeField(),
        ),
    ]
