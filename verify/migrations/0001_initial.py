# Generated by Django 3.1.7 on 2021-05-03 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('usr_email', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('usr_identity_imgurl1', models.CharField(max_length=100)),
                ('usr_identity_imgurl2', models.CharField(max_length=100)),
                ('usr_student_imgurl1', models.CharField(max_length=100)),
                ('usr_student_imgurl2', models.CharField(max_length=100)),
            ],
        ),
    ]
