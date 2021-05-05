from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from backstage import models
from account import models as amodels
from verify import models as vmodels
import json
import datetime

NOT_VERIFY = 0
# Create your views here.
"""
------管理员登录------
请求方法:post
参数:
    account 账号
    password 密码
api:https://127.0.0.1:8081/backstage/login/
后端返回值:
{
    "is_login": "yes"
}
        携带键为account 和is_admin_login 的cookie
"""
def admin_login(request):
    if request.method == 'POST':
        usr_account = request.POST.get('account')
        usr_password = request.POST.get('password')
        response_data = {
            'is_login':'no',
        }
        #查找账号
        if models.Table.objects.filter(usr_account=usr_account,usr_password=usr_password).exists():
            response_data['is_login'] = 'yes'

            response_data = HttpResponse(json.dumps(response_data))  #必须要json.dumps 否则前端收不到键的值
            response_data.set_cookie('account',usr_account,secure=True)
            response_data.set_cookie('is_admin_login',True,max_age=3600*6,secure=True)
            response_data.cookies['account']['samesite'] = 'none'
            response_data.cookies['is_admin_login']['samesite'] = 'none'
            return response_data

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)



"""
------获取超过24小时为验证的账号------
请求方法:get
参数:
    cookies
api:https://127.0.0.1:8081/backstage/badaccountlist/
后端返回值: 
{
    "is_login": "yes",
    "bad_account_list": [
        {
            "usr_email": "973178360@qq.com",
            "usr_account_add_time": "2021-05-03 11:59:20",
            "usr_verify": 0,
            "how_long": 47.16
        }
    ],
    "account_num": 1
}
"""
def admin_get_bad_accounts(request):
    if request.method == 'GET':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'bad_account_list':[],
            'account_num':0,
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'
            account_list = amodels.Table.objects.filter(usr_verify= NOT_VERIFY).values('usr_email','usr_account_add_time','usr_verify')
            account_list = list(account_list) 
            #把未验证时间超过24小时的加入bad account list
            time_now = datetime.datetime.now()
            for account in account_list:
                if (time_now - account['usr_account_add_time']).total_seconds() >24 * 3600:   #.seconds 只计算小时分钟秒 部分之间的时间差 要使用total_seconds()
                    #向字典中加入距离账号创建时间
                    account['how_long'] = round((time_now - account['usr_account_add_time']).total_seconds() / 3600 ,2)  #转化为小时候保留两位小数
                    account['usr_account_add_time'] = account['usr_account_add_time'].strftime('%Y-%m-%d %H:%M:%S') #时间转化为字符串
                    response_data['bad_account_list'].append(account)
                    response_data['account_num'] +=1

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
------后台管理员删除垃圾账号------
方法:post
参数
    cookies
    uemail 垃圾账号邮箱
api:https://127.0.0.1:8081/backstage/deljunkmail/
后端返回值:
{
    "is_login": "yes",
    "is_delet": "yes"
}

"""
def admin_del_account(request):
    if request.method == 'POST':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_delet':'no',
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        usr_email = request.POST.get('uemail')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'
            #判断删除的账号是不是垃圾账号
            tab_obj = amodels.Table.objects.get(usr_email= usr_email,usr_verify= NOT_VERIFY)
            time_now = datetime.datetime.now()
            if (time_now - tab_obj.usr_account_add_time).total_seconds() >24 * 3600:
                print('shi la ji zhang hao ')
                #开始删除垃圾账号
                tab_obj.delete()
                response_data['is_delet'] = 'yes'   
            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('bad request',status = 500)

"""
------获取身份验证条目信息------
方法:get
参数:
    cookies
后端返回:

"""
def admin_get_identity_list(request):
    if request.method == 'GET':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_get':'no',
            'identity_num':0,
            'identity_list':[],
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)