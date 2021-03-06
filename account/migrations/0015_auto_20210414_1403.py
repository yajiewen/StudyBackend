# Generated by Django 3.1.7 on 2021-04-14 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20210411_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evalu_table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluated_usr_email', models.CharField(max_length=100)),
                ('evaluate_usr_name', models.CharField(max_length=100)),
                ('evaluate_content', models.CharField(max_length=300)),
                ('evaluate_score', models.IntegerField(default=5)),
            ],
        ),
        migrations.AlterField(
            model_name='table',
            name='usr_email',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
