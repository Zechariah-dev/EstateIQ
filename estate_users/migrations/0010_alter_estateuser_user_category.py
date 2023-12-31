# Generated by Django 4.1.5 on 2023-01-20 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_users", "0009_alter_estateuser_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateuser",
            name="user_category",
            field=models.CharField(
                choices=[
                    ("OTHERS", "OTHERS"),
                    ("STAFF", "STAFF"),
                    ("HOUSEHOLD", "HOUSEHOLD"),
                    ("SECURITY", "SECURITY"),
                ],
                default="OTHERS",
                max_length=50,
            ),
        ),
    ]
