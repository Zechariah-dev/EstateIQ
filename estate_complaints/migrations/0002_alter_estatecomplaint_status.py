# Generated by Django 4.1.5 on 2023-01-31 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_complaints", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estatecomplaint",
            name="status",
            field=models.CharField(
                choices=[("RESOLVED", "RESOLVED"), ("PENDING", "PENDING")],
                default="PENDING",
                max_length=50,
            ),
        ),
    ]
