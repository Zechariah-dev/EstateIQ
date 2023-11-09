# Generated by Django 4.1.5 on 2023-02-01 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_users", "0012_alter_estateuser_user_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="estateuser",
            name="emergency_service",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="estateuser",
            name="gate_pass",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="estateuser",
            name="on_to_one_message",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="estateuser",
            name="utility_portal",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="estateuser",
            name="user_category",
            field=models.CharField(
                choices=[
                    ("OTHERS", "OTHERS"),
                    ("STAFF", "STAFF"),
                    ("HOUSEHOLD", "HOUSEHOLD"),
                    ("VENDOR", "VENDOR"),
                    ("SECURITY", "SECURITY"),
                    ("HEAD_OF_SECURITY", "HEAD_OF_SECURITY"),
                    ("FINANCIAL_SECURITY", "FINANCIAL_SECURITY"),
                    ("PRESIDENT", "PRESIDENT"),
                    ("VICE_PRESIDENT", "VICE_PRESIDENT"),
                ],
                default="OTHERS",
                max_length=50,
            ),
        ),
    ]