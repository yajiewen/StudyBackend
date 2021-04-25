from django.db import models

# Create your models here.
class Table(models.Model):
    usr_email = models.CharField(max_length=100,primary_key=True) #用户名
    usr_password = models.CharField(max_length=200) #登录密码
    usr_verify = models.IntegerField(default=0) #用户验证  0 未验证 1 验证
    usr_name = models.CharField(max_length=200) #昵称
    usr_age = models.IntegerField(default=0) #年龄
    usr_sex = models.CharField(max_length=10) #性别
    usr_major  = models.CharField(max_length=100,default='') #专业
    usr_school =  models.CharField(max_length=100) #毕业学校
    usr_teaching_subjects = models.CharField(max_length=200) #执教学科
    usr_teaching_grade = models.CharField(max_length=200) #执教年级
    usr_experience = models.CharField(max_length=500) #个人经历
    usr_coin = models.FloatField(default=0) #学币
    usr_credit = models.FloatField(default=0) #信用
    usr_phone_number = models.CharField(max_length=11) #手机号码

    #认证信息
    usr_real_name =models.CharField(max_length=100)  #用户真是姓名
    use_graduation_certificate_no = models.CharField(max_length=50)  #用户毕业证书编号
    use_certificate_verify = models.IntegerField(default=0) #证书是否已经验证 0 未验证 1 已经验证

    #购买赵老师模块
    usr_is_paid_fundteacher = models.IntegerField(default=0) #是否开通找老师模块 0 未开通 1 已经开通

