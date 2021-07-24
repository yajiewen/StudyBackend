from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from backstage import models
from account import models as amodels
from verify import models as vmodels
from orders import models as omodels
import json
import datetime
import os
import zipfile
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import BadHeaderError,send_mail
from smtplib import SMTPDataError #被当成垃圾邮件后发送失败的excpt
from orders.views import APPLY_COMPLETE
from orders.views import COMPLETE
from orders.views import BOSS_AGREEE_COMPLETE
from account.views import Email_VERIFIED
from account.views import FUND_TEACHER_PAID
NOT_VERIFY = 0 #邮箱未验证
apply_review =0 #申请审核
application_passed = 1 #认证通过
application_unpassed = 2 #申请不通过

CERTIFICATE_VERIFIED = 1 #学籍已认证
IDENTITY_VERIFIED = 1 #身份已认证
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
            try:
                tab_obj = amodels.Table.objects.get(usr_email= usr_email,usr_verify= NOT_VERIFY)
                time_now = datetime.datetime.now()
                if (time_now - tab_obj.usr_account_add_time).total_seconds() >24 * 3600:
                    print('shi la ji zhang hao ')
                    #开始删除垃圾账号
                    tab_obj.delete()
                    response_data['is_delet'] = 'yes'   
            except ObjectDoesNotExist:
                print('get account failed')

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
api:https://127.0.0.1:8081/backstage/ilist/
后端返回:
{
    "is_login": "yes",
    "is_get": "yes",
    "identity_num": 1,
    "identity_list": [
        {
            "usr_email": "1193184604@qq.com",
            "usr_identity_imgurl1": "http://127.0.0.1/Identity/1193184604idenimg1.jpg",
            "usr_identity_imgurl2": "http://127.0.0.1/Identity/1193184604idenimg2.jpg"
        }
    ]
}
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
            #获取需要审核的条目信息
            identi_info_list = vmodels.Table.objects.filter(usr_identity_status = apply_review).values(
                'usr_email',
                'usr_identity_imgurl1',
                'usr_identity_imgurl2',
            )
            identi_info_list = list(identi_info_list)
            response_data['is_get'] = 'yes'
            response_data['identity_list'].extend(identi_info_list)
            response_data['identity_num'] = len(identi_info_list)
            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
------获取学籍验证条目信息------
方法:get
参数:
    cookies
api:https://127.0.0.1:8081/backstage/slist/
后端返回:
{
    "is_login": "yes",
    "is_get": "yes",
    "student_num": 1,
    "student_list": [
        {
            "usr_email": "1193184604@qq.com",
            "usr_student_imgurl1": "http://127.0.0.1/Studentstatus/1193184604stuimg1.jpg",
            "usr_student_imgurl2": "http://127.0.0.1/Studentstatus/1193184604stuimg2.jpg"
        }
    ]
}
"""
def admin_get_student_list(request):
    if request.method == 'GET':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_get':'no',
            'student_num':0,
            'student_list':[],
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'
            #获取需要审核的条目信息
            identi_info_list = vmodels.Table.objects.filter(usr_student_status = apply_review).values(
                'usr_email',
                'usr_student_imgurl1',
                'usr_student_imgurl2',
            )
            identi_info_list = list(identi_info_list)
            #加入学校和专业信息
            for student in identi_info_list:
                tab_obj = amodels.Table.objects.get(usr_email=student['usr_email'])
                student['school'] = tab_obj.usr_school
                student['major'] = tab_obj.usr_major
                response_data['student_list'].append(student)
                
            response_data['is_get'] = 'yes'
            response_data['student_num'] = len(identi_info_list)
            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
------身份认证审核------
方法:post
参数:
    cookies
    uemail 审核的用户邮箱
    status 审核结果 ()
api:https://127.0.0.1:8081/backstage/iverify/
后端返回:
{
    "is_login": "yes",
    "is_deal": "yes"
}
"""
def admin_verify_identity(request):
    if request.method == 'POST':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_deal':'no',
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        usr_email = request.POST.get('uemail')
        usr_identity_status = int(request.POST.get('status'))

        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'
            tab_obj = ''
            try:
                tab_obj = vmodels.Table.objects.get(usr_email = usr_email) #获取信息
            except ObjectDoesNotExist:
                print('get info failed')

            if usr_identity_status == application_passed: #审核通过
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
                iverify_folder_path = os.path.join(os.path.join(base_path,'Imgfolder'),'Identity')
                iverify_zipfolder_path =os.path.join(iverify_folder_path,'identityzipfolder') #在Identity文件夹下面增加一个zip文件夹
                if not os.path.exists(iverify_zipfolder_path): #文件夹不存在则创建
                    os.makedirs(iverify_zipfolder_path)
                    print(iverify_zipfolder_path)
                
                #压缩文件名
                zipfile_name = usr_email.split('@')[0] + 'iimg.zip'
                with zipfile.ZipFile(os.path.join(iverify_zipfolder_path,zipfile_name),'w') as imgziper:
                    imgziper.write(tab_obj.usr_identity_imgpath1) #压入第一张身份证图片
                    imgziper.write(tab_obj.usr_identity_imgpath2) #压入第二张身份证图片
                    zipfile.ZipFile.close(imgziper)
                #删除原来文件
                if os.path.exists(tab_obj.usr_identity_imgpath1):
                    os.remove(tab_obj.usr_identity_imgpath1)
                if os.path.exists(tab_obj.usr_identity_imgpath2):
                    os.remove(tab_obj.usr_identity_imgpath2)

                #更新用户信息为身份认证通过
                amodels.Table.objects.filter(usr_email = usr_email).update(usr_identity_verify= IDENTITY_VERIFIED)
                #更新认证状态
                vmodels.Table.objects.filter(usr_email = usr_email).update(usr_identity_status= application_passed)

                response_data['is_deal'] = 'yes'
            
            elif usr_identity_status == application_unpassed: #审核不通过
                #删除原来文件
                if os.path.exists(tab_obj.usr_identity_imgpath1):
                    os.remove(tab_obj.usr_identity_imgpath1)
                if os.path.exists(tab_obj.usr_identity_imgpath2):
                    os.remove(tab_obj.usr_identity_imgpath2)
                
                response_data['is_deal'] = 'yes'
                #更新认证状态
                vmodels.Table.objects.filter(usr_email = usr_email).update(usr_identity_status= application_unpassed)

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
------学籍认证审核------
方法:post
参数:
    cookies
    uemail 审核的用户邮箱
    status 审核结果 ()
api:https://127.0.0.1:8081/backstage/sverify/
后端返回:
{
    "is_login": "yes",
    "is_deal": "yes"
}
"""
def admin_verify_student(request):
    if request.method == 'POST':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_deal':'no',
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        usr_email = request.POST.get('uemail')
        usr_student_status = int(request.POST.get('status'))

        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'
            tab_obj = ''
            try:
                tab_obj = vmodels.Table.objects.get(usr_email = usr_email) #获取信息
            except ObjectDoesNotExist:
                print('get info failed')

            if usr_student_status == application_passed: #审核通过
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
                sverify_folder_path = os.path.join(os.path.join(base_path,'Imgfolder'),'Studentstatus')
                sverify_zipfolder_path =os.path.join(sverify_folder_path,'studentzipfolder') #在Studentstatus文件夹下面增加一个zip文件夹
                if not os.path.exists(sverify_zipfolder_path): #文件夹不存在则创建
                    os.makedirs(sverify_zipfolder_path)
                    print(sverify_zipfolder_path)
                
                #压缩文件名
                zipfile_name = usr_email.split('@')[0] + 'simg.zip'
                with zipfile.ZipFile(os.path.join(sverify_zipfolder_path,zipfile_name),'w') as imgziper:
                    imgziper.write(tab_obj.usr_student_imgpath1) #压入第一张学生证图片
                    imgziper.write(tab_obj.usr_student_imgpath2) #压入第二张学生证图片
                    zipfile.ZipFile.close(imgziper)
                #删除原来文件
                if os.path.exists(tab_obj.usr_student_imgpath1):
                    os.remove(tab_obj.usr_student_imgpath1)
                if os.path.exists(tab_obj.usr_student_imgpath2):
                    os.remove(tab_obj.usr_student_imgpath2)

                #更新用户信息为身份认证通过
                amodels.Table.objects.filter(usr_email = usr_email).update(use_certificate_verify= CERTIFICATE_VERIFIED)
                #更新认证状态
                vmodels.Table.objects.filter(usr_email = usr_email).update(usr_student_status= application_passed)

                response_data['is_deal'] = 'yes'
            
            elif usr_student_status == application_unpassed: #审核不通过
                #删除原来文件
                if os.path.exists(tab_obj.usr_student_imgpath1):
                    os.remove(tab_obj.usr_student_imgpath1)
                if os.path.exists(tab_obj.usr_student_imgpath2):
                    os.remove(tab_obj.usr_student_imgpath2)
                
                response_data['is_deal'] = 'yes'
                #更新认证状态
                vmodels.Table.objects.filter(usr_email = usr_email).update(usr_student_status= application_unpassed)

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
-----获取申请结单的单(家长超过24小时没有收货的单)-----
方法:get
参数
    cookies
api:https://127.0.0.1:8081/backstage/orderstocomplete/
后端返回值: 
{
    "is_login": "yes",
    "order_list": [
        {
            "order_token": "xm1620290030051132",
            "order_complet_time": "2021-05-14 10:05:26",
            "how_long": 1329.19
        }
    ],
    "order_num": 1
}
"""
def get_orders_to_complete(request):
    if request.method == 'GET':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'order_list':[],
            'order_num':0,
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'

            order_list = omodels.Table.objects.filter(order_status = APPLY_COMPLETE).values('order_token','order_complet_time')
            order_list = list(order_list)
            print(order_list)
        
            #把未验证时间超过24小时的加入bad account list
            time_now = datetime.datetime.now()
            for order in order_list:
                if (time_now - order['order_complet_time']).total_seconds() >360:   #.seconds 只计算小时分钟秒 部分之间的时间差 要使用total_seconds()
                    #向字典中加入距离账号创建时间
                    order['how_long'] = round((time_now - order['order_complet_time']).total_seconds() / 3600 ,2)  #转化为小时候保留两位小数
                    order['order_complet_time'] = order['order_complet_time'].strftime('%Y-%m-%d %H:%M:%S') #时间转化为字符串
                    response_data['order_list'].append(order)
                    response_data['order_num'] +=1


            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request', status = 500)

"""
------客服一键结单------
方法:post
参数
    cookies
api:https://127.0.0.1:8081/backstage/completeorders/
后端返回值:
{
    "is_login": "yes",
    "is_complete": "yes",
    "order_num": 1
}
"""

def complete_orders(request):
    if request.method == 'POST':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'is_complete':'no',
            'order_num':0,
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'

            order_list = omodels.Table.objects.filter(order_status = APPLY_COMPLETE).values('order_token','order_complet_time')
            order_list = list(order_list)
        
            #把未验证时间超过24小时的加入bad account list
            time_now = datetime.datetime.now()
            for order in order_list:
                if (time_now - order['order_complet_time']).total_seconds() >3*24*3600:   #.seconds 只计算小时分钟秒 部分之间的时间差 要使用total_seconds()
                    tab_objf = omodels.Table.objects.filter(order_token=order['order_token'],order_status=APPLY_COMPLETE) #查找订单
                    if tab_objf.exists():
                        tab_obj = omodels.Table.objects.get(order_token=order['order_token'],order_status = APPLY_COMPLETE)
                        order_token = tab_obj.order_token
                        #获取员工coin
                        worker_info = amodels.Table.objects.get(usr_email= tab_obj.order_worker_email)
                        worker_coin = round(worker_info.usr_coin + tab_obj.order_total_money + tab_obj.order_worker_earnest_money,2) # 保留两位小数
                        #更新员工coin
                        amodels.Table.objects.filter(usr_email= tab_obj.order_worker_email).update(usr_coin= worker_coin)
                        #在order_table1表中建立新的订单
                        omodels.Table1.objects.create(
                            order_token = tab_obj.order_token,
                            order_boss_email = tab_obj.order_boss_email,
                            order_worker_email = tab_obj.order_worker_email,
                            order_start_time = tab_obj.order_start_time,
                            order_accept_time = tab_obj.order_accept_time,
                            order_complet_time = timezone.now(), #----------
                            order_end_time = tab_obj.order_end_time,
                            order_status =COMPLETE,#-----------
                            order_is_worker_ask_complet = tab_obj.order_is_worker_ask_complet,
                            order_is_boss_agree_complet = BOSS_AGREEE_COMPLETE, #---------------
                            order_is_boss_ask_refund = tab_obj.order_is_boss_ask_refund,
                            order_refund_reason = tab_obj.order_refund_reason,
                            order_is_worker_agree_refund = tab_obj.order_is_worker_agree_refund, 
                            order_refund_money = tab_obj.order_refund_money,
                            order_teaching_grade = tab_obj.order_teaching_grade,
                            order_teaching_subjects = tab_obj.order_teaching_subjects,
                            order_hourly_money = tab_obj.order_hourly_money,
                            order_teaching_time = tab_obj.order_teaching_time,
                            order_total_money = tab_obj.order_total_money,
                            order_boss_name = tab_obj.order_boss_name,
                            order_boss_phone_number = tab_obj.order_boss_phone_number,
                            order_boss_qq_wei = tab_obj.order_boss_qq_wei,
                            order_boss_require = tab_obj.order_boss_require,
                            order_worker_name = tab_obj.order_worker_name,
                            order_worker_phone_number = tab_obj.order_worker_phone_number,
                            order_worker_qq_wei = tab_obj.order_worker_qq_wei,
                            order_is_evalute= tab_obj.order_is_evalute
                        )
                        #在order_table表中删除该订单
                        tab_objf.delete()
                        response_data['order_num'] +=1
            response_data['is_complete'] = 'yes'
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request', status = 500)

"""
------客服显示注册人数,实名认证人数,老师注册人数,老师人数------
method get
参数 cookies
api:https://127.0.0.1:8081/backstage/stageusrinfo/
后端返回值:

"""
def get_stage_usrinfo(request):
    if request.method == 'GET':
        #获取管理员账号和登录状态
        response_data ={
            'is_login':'no',
            'regs_num':0,
            'id_identified_num':0,
            'teacher_num':0,
            'buy_find_teacher_num':0,
        }

        usr_account = request.COOKIES.get('account')
        is_admin_login = request.COOKIES.get('is_admin_login')
        if is_admin_login and models.Table.objects.filter(usr_account = usr_account).exists(): #登录并且账号存在
            response_data['is_login'] = 'yes'

            # 查询注册人数
            response_data['regs_num'] = amodels.Table.objects.filter(usr_verify = Email_VERIFIED).count()
            # 查询实名认证人数
            response_data['id_identified_num'] = amodels.Table.objects.filter(usr_identity_verify = IDENTITY_VERIFIED).count()
            # 查询老师注册人数
            response_data['teacher_num'] = amodels.Table.objects.filter(usr_identity_verify = IDENTITY_VERIFIED,use_certificate_verify = CERTIFICATE_VERIFIED).count()
            # 查询购买找老师功能的数
            response_data['buy_find_teacher_num'] = amodels.Table.objects.filter(usr_is_paid_fundteacher = FUND_TEACHER_PAID).count()

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)