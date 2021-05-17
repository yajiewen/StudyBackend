from django.db import models

# Create your models here.
#该表用于存放用户画像
class Table_user(models.Model): 
    usr_email = models.CharField(max_length=50,primary_key=True) #用户邮箱
    usr_group_name =  models.CharField(max_length=10,default='') #用户所属的群落名称
    pr_first_grade = models.BigIntegerField(default=0)
    pr_second_grade = models.BigIntegerField(default=0) #小学二年级
    pr_third_grade = models.BigIntegerField(default=0)
    pr_fourth_grade = models.BigIntegerField(default=0)
    pr_fifth_grade = models.BigIntegerField(default=0)
    pr_sixth_grade = models.BigIntegerField(default=0)

    ju_first_grade = models.BigIntegerField(default=0) #初中一年级
    ju_second_grade = models.BigIntegerField(default=0)
    ju_third_grade = models.BigIntegerField(default=0)

    hi_first_grade = models.BigIntegerField(default=0) #高中一年级
    hi_second_grade = models.BigIntegerField(default=0)
    hi_third_grade = models.BigIntegerField(default=0)
    #各科课程
    chinese_class = models.BigIntegerField(default=0) 
    math_class = models.BigIntegerField(default=0)
    english_class = models.BigIntegerField(default=0)
    moral_class = models.BigIntegerField(default=0)
    art_class = models.BigIntegerField(default=0)
    science_class = models.BigIntegerField(default=0)
    music_class = models.BigIntegerField(default=0)
    pr_programming_class = models.BigIntegerField(default=0)
    history_class = models.BigIntegerField(default=0)
    geography_class = models.BigIntegerField(default=0)
    biology_class = models.BigIntegerField(default=0)
    information_tech_class = models.BigIntegerField(default=0)
    physics_class = models.BigIntegerField(default=0)
    chemistry_class = models.BigIntegerField(default=0)
    politics_class = models.BigIntegerField(default=0)

#该表用于存放用户群落画像
class Table_user_group(models.Model): 
    usr_group_name = models.CharField(max_length=10,primary_key=True) #用户群落名称
    pr_first_grade = models.BigIntegerField(default=0)
    pr_second_grade = models.BigIntegerField(default=0) #小学二年级
    pr_third_grade = models.BigIntegerField(default=0)
    pr_fourth_grade = models.BigIntegerField(default=0)
    pr_fifth_grade = models.BigIntegerField(default=0)
    pr_sixth_grade = models.BigIntegerField(default=0)

    ju_first_grade = models.BigIntegerField(default=0) #初中一年级
    ju_second_grade = models.BigIntegerField(default=0)
    ju_third_grade = models.BigIntegerField(default=0)

    hi_first_grade = models.BigIntegerField(default=0) #高中一年级
    hi_second_grade = models.BigIntegerField(default=0)
    hi_third_grade = models.BigIntegerField(default=0)
    #各科课程
    chinese_class = models.BigIntegerField(default=0) 
    math_class = models.BigIntegerField(default=0)
    english_class = models.BigIntegerField(default=0)
    moral_class = models.BigIntegerField(default=0) #思想品德课
    art_class = models.BigIntegerField(default=0) #美术课
    science_class = models.BigIntegerField(default=0)
    music_class = models.BigIntegerField(default=0)
    pr_programming_class = models.BigIntegerField(default=0)
    history_class = models.BigIntegerField(default=0)
    geography_class = models.BigIntegerField(default=0) #地理课
    biology_class = models.BigIntegerField(default=0) #生物课
    information_tech_class = models.BigIntegerField(default=0) #信息技术课
    physics_class = models.BigIntegerField(default=0)
    chemistry_class = models.BigIntegerField(default=0)
    politics_class = models.BigIntegerField(default=0)


#该表用于存世界用户画像
class Table_user_world(models.Model):
    map_name = models.CharField(max_length=10,primary_key=True)  #条目名称为global_map
    pr_first_grade = models.BigIntegerField(default=0)
    pr_second_grade = models.BigIntegerField(default=0) #小学二年级
    pr_third_grade = models.BigIntegerField(default=0)
    pr_fourth_grade = models.BigIntegerField(default=0)
    pr_fifth_grade = models.BigIntegerField(default=0)
    pr_sixth_grade = models.BigIntegerField(default=0)

    ju_first_grade = models.BigIntegerField(default=0) #初中一年级
    ju_second_grade = models.BigIntegerField(default=0)
    ju_third_grade = models.BigIntegerField(default=0)

    hi_first_grade = models.BigIntegerField(default=0) #高中一年级
    hi_second_grade = models.BigIntegerField(default=0)
    hi_third_grade = models.BigIntegerField(default=0)
    #各科课程
    chinese_class = models.BigIntegerField(default=0) 
    math_class = models.BigIntegerField(default=0)
    english_class = models.BigIntegerField(default=0)
    moral_class = models.BigIntegerField(default=0) #思想品德课
    art_class = models.BigIntegerField(default=0) #美术课
    science_class = models.BigIntegerField(default=0)
    music_class = models.BigIntegerField(default=0)
    pr_programming_class = models.BigIntegerField(default=0)
    history_class = models.BigIntegerField(default=0)
    geography_class = models.BigIntegerField(default=0) #地理课
    biology_class = models.BigIntegerField(default=0) #生物课
    information_tech_class = models.BigIntegerField(default=0) #信息技术课
    physics_class = models.BigIntegerField(default=0)
    chemistry_class = models.BigIntegerField(default=0)
    politics_class = models.BigIntegerField(default=0)

