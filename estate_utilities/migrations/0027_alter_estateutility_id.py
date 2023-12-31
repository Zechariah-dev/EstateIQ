# Generated by Django 4.1.5 on 2023-01-20 10:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0026_alter_estateutility_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estateutility",
            name="id",
            field=models.UUIDField(
                default=uuid.UUID("29de218b-d889-470a-9de8-89094ccc1b95"),
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
