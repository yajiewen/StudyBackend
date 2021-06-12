from django.urls import path
from .views import *

urlpatterns = [
    path('buycoin/',buycoin), #充值coin
    path('check_pay/',check_pay), #微信那边回调访问地址
    path('payoutcome/<str:order_token>/',get_pay_outcome), #前端查询支付结果
]