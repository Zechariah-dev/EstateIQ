# Generated by Django 4.1.5 on 2023-01-26 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_users", "0011_estateuser_estate_street_estateuser_estate_zone"),
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
                    ("VENDOR", "VENDOR"),
                    ("SECURITY", "SECURITY"),
                ],
                default="OTHERS",
                max_length=50,
            ),
        ),
    ]
