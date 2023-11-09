# Generated by Django 4.1.5 on 2023-02-02 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("estate_utilities", "0032_estateutilitypenalty"),
    ]

    operations = [
        migrations.AddField(
            model_name="estateutilitypenalty",
            name="estate_utility",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="estate_utilities.estateutility",
            ),
        ),
        migrations.AddField(
            model_name="estateutilitypenalty",
            name="revoke",
            field=models.CharField(default="EMERGENCY_SERVICE", max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="estateutilitypenalty",
            name="unpaid_in",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="estateutilitypenalty",
            name="unpaid_period",
            field=models.CharField(default="WEEK", max_length=250),
            preserve_default=False,
        ),
    ]
