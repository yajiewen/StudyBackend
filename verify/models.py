from django.db import models

# Create your models here.
class Table(models.Model):
    usr_email = models.CharField(max_length=100,primary_key=True)
    usr_identity_imgurl1 = models.CharField(max_length=100,default='') #身份证正面地址
    usr_identity_imgurl2 = models.CharField(max_length=100,default='') #身份证反面地址
    usr_identity_imgpath1 =  models.CharField(max_length=100,default='') #身份证正面存放地址
    usr_identity_imgpath2 = models.CharField(max_length=100,default='') #身份证反面存放地址
    usr_identity_status = models.IntegerField(default=0) #(0:申请审核 1:审核通过(不可再申请审核)) 不通过删除图片以及数据库条目

    usr_student_imgurl1 = models.CharField(max_length=100,default='') #学生证封面照片地址
    usr_student_imgurl2 = models.CharField(max_length=100,default='') #学生证里面照片地址
    usr_student_imgpath1 = models.CharField(max_length=100,default='') #学生证封面照片存放地址
    usr_student_imgpath2 = models.CharField(max_length=100,default='') #学生证里面照片存放地址

    usr_student_status = models.IntegerField(default=0) #(0:申请审核 1:审核通过(不可再申请审核)) 不通过删除图片以及数据库条目

