from django.urls import path
from .views import * #导入orders view.py中的function

urlpatterns =[
    path('creatorder/',boss_create_order), #创建订单1
    path('updateorder/',boss_update_order), #发单者修改订单(未付款的单可以修改)2
    path('payorder/',boss_pay_order), #发单者为订单付款3
    path('wtakeover/',worker_take_over_order), #老师接单4
    path('bcancelorder/',boss_cancel_order), #发单者取消订单（创建但是未付款，已付款但是未接手的单）5
    path('brefundorder/',boss_refund_order), #发单者申请退款6
    path('bcancelrefund/',boss_cancel_refund), #发单者取消申请退款7
    path('wcancelorder/',worker_cancel_order), #员工取消接单（扣除保证金）8
    path('wagreerefund/',worker_agree_refund), #员工同意退款9 
    path('wdenyrefund/',worker_deny_refund), #员工拒绝退款10
    path('waskok/',worker_ask_complete), #员工申请结单11
    path('bagreeok/',boss_agree_complete), #老板同意结单12
    path('wtakelist/<str:usr_email>/',get_take_order_info), #获取员工接单列表 13
    path('breleaselist/<str:usr_email>/',get_release_order_info), #获取老板发单表 14
    path('ordertotake/<str:order_teaching_grade>/<str:order_teaching_subjects>/',get_order_to_take), #获取待接的单，当没有过滤的时候 年级=no  科目=no 有过滤写相应的值 15 
    path('sendclassreminder/',send_class_reminder), #发送上课邮件提醒
]