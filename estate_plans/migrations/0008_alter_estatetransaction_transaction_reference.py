# Generated by Django 4.1.5 on 2023-01-15 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estate_plans", "0007_estatetransaction_estate_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estatetransaction",
            name="transaction_reference",
            field=models.CharField(blank=True, max_length=250, null=True, unique=True),
        ),
    ]
