# Generated by Django 4.1.5 on 2023-08-17 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_users', '0017_alter_estateuser_user_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estateuser',
            name='user_category',
            field=models.CharField(choices=[('OTHERS', 'OTHERS'), ('STAFF', 'STAFF'), ('HOUSEHOLD', 'HOUSEHOLD'), ('VENDOR', 'VENDOR'), ('SECURITY', 'SECURITY'), ('HEAD_OF_SECURITY', 'HEAD_OF_SECURITY'), ('FINANCIAL_SECURITY', 'FINANCIAL_SECURITY'), ('PRESIDENT', 'PRESIDENT'), ('VICE_PRESIDENT', 'VICE_PRESIDENT'), ('CHIEF_SECURITY_OFFICER', 'CHIEF_SECURITY_OFFICER'), ('FINANCIAL_SECRETARY', 'FINANCIAL_SECRETARY'), ('ESTATE_MANAGER', 'ESTATE_MANAGER'), ('EXCOS', 'EXCOS')], default='OTHERS', max_length=50),
        ),
    ]
