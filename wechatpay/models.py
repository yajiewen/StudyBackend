from django.db import models
from django.utils import timezone
# Create your models here.
class Table(models.Model):
    order_token = models.CharField(max_length=32,primary_key=True) #订单号
    usr_email = models.CharField(max_length=100) #用邮箱
    coin_num = models.FloatField(default=0) #学币
    order_status = models.IntegerField(default=0) #订单状态(0:充值失败 1:充值成功)
    order_start_time = models.DateTimeField(auto_now_add=True) #订单创建时间 auto_now_add 设置为创建时间