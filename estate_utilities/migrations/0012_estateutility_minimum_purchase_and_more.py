# Generated by Django 4.1.5 on 2023-01-13 12:50

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0011_alter_estateutility_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="estateutility",
            name="minimum_purchase",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("057ca4bd-8eef-4636-b4ff-dafab14b3701"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="estateutilitysubscription",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("b4594496-3108-4db6-a926-9d9b55288f6d"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
