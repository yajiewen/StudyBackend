# Generated by Django 3.1.7 on 2021-05-05 09:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_table_usr_identity_verify'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='usr_account_add_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
