from django.urls import path
from .views import * #导入evaluate view.py中的function

urlpatterns =[
    path('evaluatelist/',get_evaluate_list), #获取待评价的订单列表
    path('evaluateworker/',evaluate_worker), #老板对员工评价
    path('evaluatecontent/<str:evaluated_usr_email>/',get_evaluate_content), #获取员工评价表
]