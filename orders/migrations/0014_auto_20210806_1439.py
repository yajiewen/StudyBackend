# Generated by Django 3.1.7 on 2021-08-06 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_auto_20210428_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='table1',
            name='boss_hide_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='table1',
            name='worker_hide_order',
            field=models.IntegerField(default=0),
        ),
    ]
