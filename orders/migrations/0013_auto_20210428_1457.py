# Generated by Django 3.1.7 on 2021-04-28 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_auto_20210428_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='order_refund_reason',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='table1',
            name='order_refund_reason',
            field=models.CharField(max_length=500),
        ),
    ]
