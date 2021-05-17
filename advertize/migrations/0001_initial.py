# Generated by Django 3.1.7 on 2021-05-17 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Table_user',
            fields=[
                ('usr_email', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('usr_group_name', models.CharField(default='', max_length=10)),
                ('pr_first_grade', models.BigIntegerField(default=0)),
                ('pr_second_grade', models.BigIntegerField(default=0)),
                ('pr_third_grade', models.BigIntegerField(default=0)),
                ('pr_fourth_grade', models.BigIntegerField(default=0)),
                ('pr_fifth_grade', models.BigIntegerField(default=0)),
                ('pr_sixth_grade', models.BigIntegerField(default=0)),
                ('ju_first_grade', models.BigIntegerField(default=0)),
                ('ju_second_grade', models.BigIntegerField(default=0)),
                ('ju_third_grade', models.BigIntegerField(default=0)),
                ('hi_first_grade', models.BigIntegerField(default=0)),
                ('hi_second_grade', models.BigIntegerField(default=0)),
                ('hi_third_grade', models.BigIntegerField(default=0)),
                ('chinese_class', models.BigIntegerField(default=0)),
                ('math_class', models.BigIntegerField(default=0)),
                ('english_class', models.BigIntegerField(default=0)),
                ('moral_class', models.BigIntegerField(default=0)),
                ('art_class', models.BigIntegerField(default=0)),
                ('science_class', models.BigIntegerField(default=0)),
                ('music_class', models.BigIntegerField(default=0)),
                ('pr_programming_class', models.BigIntegerField(default=0)),
                ('history_class', models.BigIntegerField(default=0)),
                ('geography_class', models.BigIntegerField(default=0)),
                ('biology_class', models.BigIntegerField(default=0)),
                ('information_tech_class', models.BigIntegerField(default=0)),
                ('physics_class', models.BigIntegerField(default=0)),
                ('chemistry_class', models.BigIntegerField(default=0)),
                ('politics_class', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Table_user_group',
            fields=[
                ('usr_group_name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('pr_first_grade', models.BigIntegerField(default=0)),
                ('pr_second_grade', models.BigIntegerField(default=0)),
                ('pr_third_grade', models.BigIntegerField(default=0)),
                ('pr_fourth_grade', models.BigIntegerField(default=0)),
                ('pr_fifth_grade', models.BigIntegerField(default=0)),
                ('pr_sixth_grade', models.BigIntegerField(default=0)),
                ('ju_first_grade', models.BigIntegerField(default=0)),
                ('ju_second_grade', models.BigIntegerField(default=0)),
                ('ju_third_grade', models.BigIntegerField(default=0)),
                ('hi_first_grade', models.BigIntegerField(default=0)),
                ('hi_second_grade', models.BigIntegerField(default=0)),
                ('hi_third_grade', models.BigIntegerField(default=0)),
                ('chinese_class', models.BigIntegerField(default=0)),
                ('math_class', models.BigIntegerField(default=0)),
                ('english_class', models.BigIntegerField(default=0)),
                ('moral_class', models.BigIntegerField(default=0)),
                ('art_class', models.BigIntegerField(default=0)),
                ('science_class', models.BigIntegerField(default=0)),
                ('music_class', models.BigIntegerField(default=0)),
                ('pr_programming_class', models.BigIntegerField(default=0)),
                ('history_class', models.BigIntegerField(default=0)),
                ('geography_class', models.BigIntegerField(default=0)),
                ('biology_class', models.BigIntegerField(default=0)),
                ('information_tech_class', models.BigIntegerField(default=0)),
                ('physics_class', models.BigIntegerField(default=0)),
                ('chemistry_class', models.BigIntegerField(default=0)),
                ('politics_class', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Table_user_world',
            fields=[
                ('global_name', models.CharField(default='global_map', max_length=10, primary_key=True, serialize=False)),
                ('pr_first_grade', models.BigIntegerField(default=0)),
                ('pr_second_grade', models.BigIntegerField(default=0)),
                ('pr_third_grade', models.BigIntegerField(default=0)),
                ('pr_fourth_grade', models.BigIntegerField(default=0)),
                ('pr_fifth_grade', models.BigIntegerField(default=0)),
                ('pr_sixth_grade', models.BigIntegerField(default=0)),
                ('ju_first_grade', models.BigIntegerField(default=0)),
                ('ju_second_grade', models.BigIntegerField(default=0)),
                ('ju_third_grade', models.BigIntegerField(default=0)),
                ('hi_first_grade', models.BigIntegerField(default=0)),
                ('hi_second_grade', models.BigIntegerField(default=0)),
                ('hi_third_grade', models.BigIntegerField(default=0)),
                ('chinese_class', models.BigIntegerField(default=0)),
                ('math_class', models.BigIntegerField(default=0)),
                ('english_class', models.BigIntegerField(default=0)),
                ('moral_class', models.BigIntegerField(default=0)),
                ('art_class', models.BigIntegerField(default=0)),
                ('science_class', models.BigIntegerField(default=0)),
                ('music_class', models.BigIntegerField(default=0)),
                ('pr_programming_class', models.BigIntegerField(default=0)),
                ('history_class', models.BigIntegerField(default=0)),
                ('geography_class', models.BigIntegerField(default=0)),
                ('biology_class', models.BigIntegerField(default=0)),
                ('information_tech_class', models.BigIntegerField(default=0)),
                ('physics_class', models.BigIntegerField(default=0)),
                ('chemistry_class', models.BigIntegerField(default=0)),
                ('politics_class', models.BigIntegerField(default=0)),
            ],
        ),
    ]
