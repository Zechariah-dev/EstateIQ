# Generated by Django 4.1.5 on 2023-09-30 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_access_logs', '0007_estateaccesslog_access_log_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='estateaccesslog',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
