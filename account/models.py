from django.db import models
from django.utils import timezone
# Create your models here.
class Table(models.Model):
    usr_email = models.CharField(max_length=100,primary_key=True) #用邮箱
    usr_password = models.CharField(max_length=200) #登录密码
    usr_verify = models.IntegerField(default=0) #用户邮箱验证  0 未验证 1 验证
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
    #用户现在所在省市(这些信息可以更改)
    usr_now_province = models.CharField(max_length=50,default='')  #用户现在所在省
    usr_now_city_county = models.CharField(max_length=100,default='') #用户现在所在市县  (过滤主要使用这个字段进行过滤)

    #学籍认证信息
    use_graduation_certificate_no = models.CharField(max_length=50)  #用户毕业证书编号
    use_certificate_verify = models.IntegerField(default=0) #证书是否已经验证 0 未验证 1 已经验证

    #身份认证信息(这些信息不可以更改)
    usr_real_name =models.CharField(max_length=50,default='')  #用户真实姓名
    usr_real_age = models.IntegerField(default=0) #用户真实年龄
    usr_real_clan = models.CharField(max_length=10,default='')  #用户名族
    usr_real_province = models.CharField(max_length=50,default='')  #用户真实省
    usr_real_city_county = models.CharField(max_length=100,default='') #用户真实市县  (过滤主要使用这个字段进行过滤)
    usr_identity_verify = models.IntegerField(default=0) #用户身份认证 0未认证 1 已经认证
    #购买赵老师模块
    usr_is_paid_fundteacher = models.IntegerField(default=0) #是否开通找老师模块 0 未开通 1 已经开通
    #账号创建时间
    usr_account_add_time = models.DateTimeField(auto_now_add=True) # auto_now_add 设置为创建时间，之后修改对象时不再更新


