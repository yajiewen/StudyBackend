from django.db import models

# Create your models here.
#用户评价表
class Table(models.Model):
    id = models.AutoField(primary_key=True)
    order_token = models.CharField(max_length=200)
    evaluated_usr_email = models.CharField(max_length=100)  #被评价人邮箱
    evaluate_usr_name = models.CharField(max_length=100)  #评价人昵称
    evaluate_content = models.CharField(max_length=300) #评价内容
    evaluate_score = models.FloatField(default=5) #评分(1,2,3,4,5 分)