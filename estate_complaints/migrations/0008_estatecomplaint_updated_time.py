# Generated by Django 4.1.5 on 2023-08-18 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_complaints', '0007_alter_estatecomplaint_receivers'),
    ]

    operations = [
        migrations.AddField(
            model_name='estatecomplaint',
            name='updated_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]