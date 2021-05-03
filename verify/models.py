from django.db import models

# Create your models here.
class Table(models.Model):
    usr_email = models.CharField(max_length=100,primary_key=True)
    usr_identity_imgurl1 = models.CharField(max_length=100) #身份证正面地址
    usr_identity_imgurl2 = models.CharField(max_length=100) #身份证反面地址

    usr_student_imgurl1 = models.CharField(max_length=100) #学生证封面照片地址
    usr_student_imgurl2 = models.CharField(max_length=100) #学生证里面照片地址
