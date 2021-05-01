# Generated by Django 3.1.7 on 2021-05-01 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_remove_table_usr_education'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='usr_now_City_County',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='table',
            name='usr_now_province',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='table',
            name='usr_real_City_County',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='table',
            name='usr_real_age',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='table',
            name='usr_real_clan',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='table',
            name='usr_real_province',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='table',
            name='usr_real_name',
            field=models.CharField(default='', max_length=50),
        ),
    ]