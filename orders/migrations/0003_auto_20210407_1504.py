# Generated by Django 3.1.7 on 2021-04-07 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210407_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='order_boos_require',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='table',
            name='order_worker_email',
            field=models.CharField(max_length=200),
        ),
    ]
