from django.urls import path
from .views import * #导入account view.py中的function

urlpatterns = [
    path('add/', usr_add), #注册功能 1
    path('login/', usr_login), #登录功能2
    path('logout/',usr_logout), #注销功能3
    path('sendverify/',usr_send_verify_email), #发送验证邮件功能4
    path('emailverify/<str:usr_email>/',usr_email_verify), #验证邮箱确认功能5
    path('newpassword/',usr_change_password), #修改密码功能6
    path('sendfindpwd/',usr_find_password), #向用户邮箱发送找回的密码7
    path('upusrinfo/',usr_upload_info), #上传更新用户信息8
    path('getusrinfo/',usr_get_info), #获取用户信息9
    path('buyteacherfunc/',usr_buy_fund_teacher), #购买找老师模块 10 
    path('getteacherlist/<str:usr_teaching_subjects>/<str:usr_teaching_grade>/',usr_get_teacher_list), #获取老师信息列表 11
    path('getteacherinfo/<str:worker_email>/',usr_get_teacher_info), #获取老师信息
    path('usrtest/',usr_test),  #cookie samesite 问题解决测试 
]