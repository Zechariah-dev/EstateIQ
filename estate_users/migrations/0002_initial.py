# Generated by Django 4.1.5 on 2023-01-12 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("estates", "0001_initial"),
        ("estate_users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="estateuser",
            name="estate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="estates.estate"
            ),
        ),
    ]
