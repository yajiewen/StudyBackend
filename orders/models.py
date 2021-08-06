from django.db import models
from django.utils import timezone
# Create your models here.
class Table(models.Model): #进行中的订单放在这个表（状态为这些的表放在这里0:待发布(待发单者付款) 1:待接单(已付款) 2:已接单 4:协商退款 7.客服介入）
    #订单基础信息
    order_token = models.CharField(max_length=100,primary_key=True) #订单号
    order_boss_email = models.CharField(max_length=200) #发单者
    order_worker_email = models.CharField(max_length=200) #接单者
    order_start_time = models.DateTimeField(auto_now_add=True) #订单创建时间 auto_now_add 设置为创建时间，之后修改对象时不再更新
    order_accept_time = models.DateTimeField(default=timezone.now) #订单接单时间时间
    order_complet_time = models.DateTimeField(default=timezone.now) #订单完成时间
    order_end_time = models.DateTimeField(auto_now=True) #订单结束时间 auto_now 每次修改对象时自动更新时间
    order_status = models.IntegerField(default=0) #订单状态(0:待发布(待发单者付款) 1:待接单(已付款) 2:已接单 3:订单完成 4:协商退款中 5.退款成功 6.订单已取消 7.客服介入 8.订单申请完成中)
    order_is_worker_ask_complet = models.IntegerField(default=0) #(0:未申请完成订单 1:申请完成订单)
    order_is_boss_agree_complet = models.IntegerField(default=0) #(0:未处理 1:同意完成订单)
    order_is_boss_ask_refund = models.IntegerField(default=0) #(0:未申请退款 1:申请退款)
    order_refund_reason = models.CharField(max_length=500)  #退款原因
    order_is_worker_agree_refund = models.IntegerField(default=0) #(0:未处理 1:同意退款 2.拒绝退款)
    order_refund_money = models.FloatField(default=0) #发单者申请退款金额
    #订单需求信息
    order_teaching_grade = models.CharField(max_length=200) #学生年级
    order_teaching_subjects = models.CharField(max_length=200) #所学科目
    order_hourly_money = models.FloatField() #订单每小时多少钱
    order_teaching_time = models.IntegerField() #教学时长
    order_total_money = models.FloatField() #订单总的金额
    order_worker_earnest_money = models.FloatField(default=10) #接单者保证金
    order_boss_name = models.CharField(max_length=200) #老板名字
    order_boss_phone_number = models.CharField(max_length=11) #老板电话
    order_boss_qq_wei = models.CharField(max_length=200) #老板微信或qq
    order_boss_require = models.CharField(max_length=500) #老板的额外需求
    order_worker_name = models.CharField(max_length=200) #老师名字
    order_worker_phone_number = models.CharField(max_length=11) #老师电话
    order_worker_qq_wei = models.CharField(max_length=200) #老师微信或qq
    order_is_evalute = models.IntegerField(default=0) #(0:未评价 1 已评价)
    #27项
class Table1(models.Model): #结束的订单放在这个表（状态为这些的表放在这里 3:完成 5.退款成功 6.订单已取消）
    #订单基础信息
    order_token = models.CharField(max_length=100,primary_key=True) #订单号
    order_boss_email = models.CharField(max_length=200) #发单者
    order_worker_email = models.CharField(max_length=200) #接单者
    order_start_time = models.DateTimeField(default=timezone.now) #订单创建时间 auto_now_add 设置为创建时间，之后修改对象时不再更新
    order_accept_time = models.DateTimeField(default=timezone.now) #订单接单时间时间
    order_complet_time = models.DateTimeField(default=timezone.now) #订单完成时间
    order_end_time = models.DateTimeField(auto_now=True) #订单结束时间 auto_now 每次修改对象时自动更新时间
    order_status = models.IntegerField(default=0) #订单状态( 3:完成  5.退款成功 6.订单已取消  )
    order_is_worker_ask_complet = models.IntegerField(default=0) #(0:未申请完成订单 1:申请完成订单)
    order_is_boss_ask_refund = models.IntegerField(default=0) #(0:未申请退款 1:申请退款)
    order_refund_reason = models.CharField(max_length=500)  #退款原因
    order_is_boss_agree_complet = models.IntegerField(default=0) #(0:未处理 1:同意完成订单 )
    order_is_worker_agree_refund = models.IntegerField(default=0) #(0:未处理 1:同意退款 2.拒绝退款)
    order_refund_money = models.FloatField(default=0) #发单者申请退款金额
    #订单需求信息
    order_teaching_grade = models.CharField(max_length=200) #学生年级
    order_teaching_subjects = models.CharField(max_length=200) #所学科目
    order_hourly_money = models.FloatField() #订单每小时多少钱
    order_teaching_time = models.IntegerField() #教学时长
    order_total_money = models.FloatField() #订单总的金额
    order_worker_earnest_money = models.FloatField(default=10) #接单者保证金
    order_boss_name = models.CharField(max_length=200) #老板名字
    order_boss_phone_number = models.CharField(max_length=11) #老板电话
    order_boss_qq_wei = models.CharField(max_length=200) #老板微信或qq
    order_boss_require = models.CharField(max_length=500) #老板的额外需求
    order_worker_name = models.CharField(max_length=200) #老师名字
    order_worker_phone_number = models.CharField(max_length=11) #老师电话
    order_worker_qq_wei = models.CharField(max_length=200) #老师微信或qq
    order_is_evalute = models.IntegerField(default=0) #(0:未评价 1 已评价)

    # 隐藏订单 (0 未隐藏 1 已经隐藏)
    worker_hide_order = models.IntegerField(default=0) 
    boss_hide_order = models.IntegerField(default=0)