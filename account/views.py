from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.core.mail import BadHeaderError,send_mail
from django.core.exceptions import ObjectDoesNotExist
from smtplib import SMTPDataError #被当成垃圾邮件后发送失败的excpt
#from django.core.exceptions import ObjectDoesNotExist,  #导入查找异常
import json
from account import models
from threading import Thread
# Create your views here.
###########################找老师价格#################
FUND_TEACHER_PAID = 1
FUND_TEACHER_NOT_PAID = 0
FUNF_TEACHER_PRICE = 10 #购买找老师价格


CERTIFICATE_VERIFIED = 1
IDENTITY_VERIFIED = 1

"""
------注册功能------
------接收前端发送的账号 密码 用户名 ，判断前端是不是POST方法的请求，不是则返回bad request，如果是则判断账号和用户名是否已经存在，
------若都不存在则向数据库表account_table中添加一条用户信息，返回对应数据，否则返回相应数据
前端请求方法：POST
数据类型：form-data
    账号 uemail:
    密码 upassword:
    用户名 uname:
api:127.0.0.1:8080/account/add/
后端返回值:
{
    "uemail_exist": "yes",
    "uname_exist": "yes",
    "is_add": "no"
}
"""
def usr_add(request): #创建账号
    if request.method == 'POST':
        usr_email = request.POST.get('uemail')
        usr_password = request.POST.get('upassword')
        usr_name = request.POST.get('uname')
        
        response_data = {'uemail_exist':'',
                         'uname_exist':'',
                         'is_add':'no',
                         'is_send_verify':'no'
        }
        #查找账号是否存在
        if models.Table.objects.filter(usr_email=usr_email).exists():
            response_data['uemail_exist']='yes'
        else:
            response_data['uemail_exist']='no'
        #查找用户名是否存在
        if models.Table.objects.filter(usr_name=usr_name).exists():
            response_data['uname_exist']='yes'
        else:
            response_data['uname_exist']='no'
        #账号不存在用户名不存在则添加账号
        if response_data['uname_exist']=='no' and response_data['uemail_exist']=='no':
            tab_obj = models.Table.objects.create(usr_email=usr_email,usr_password=usr_password,usr_name=usr_name)
            response_data['is_add']='yes'
            #发送验证邮件
            subject = 'Edu account verify'
            message = 'https://127.0.0.1:8080/account/emailverify/'+usr_email+'/'
            from_email = 'eudtocher@163.com'
            recept_email =[usr_email]  #接收可以有多个人
            
            try:
                send_mail(subject,message,from_email,recept_email) #发送邮件
                response_data['is_send_verify'] = 'yes'
            except (BadHeaderError,SMTPDataError):
                print('邮件发送失败')

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)


"""
------登录功能------
------接收前端发送的账号和密码，判断是不是POST请求，不是则返回bad request，是则首先判断账号是否已经验证，
------未验证则返回相应数据，已经验证则判断账号免密是否正确，正确则设置分别设置键为uemail:账号 和 is_login:True的COOKIE 
------用于保存用户状态,同时返回相应数据，账号密码不匹配返回相应数据
前端请求方法：POST
数据类型：form-data
    账号 uemail:
    密码 upassword:
api:127.0.0.1:8080/account/login/
后端返回值:Httpresponse
{"is_login": "yes", "is_verify": "yes"}
若登录成功同时在浏览器设置了两个cookie uname: 和is_login: is_login 存活时间3600秒 max_age 按照秒计算
"""
def usr_login(request): #登录功能
    if request.method == 'POST':
        usr_email = request.POST.get('uemail')
        usr_password = request.POST.get('upassword')
        response_data = {'is_login':'no',
                         'is_verify':'no'
        }

        if models.Table.objects.filter(usr_email=usr_email,usr_verify=1).exists(): #判断邮箱是否已经验证
            response_data['is_verify']='yes'
        else:

            return JsonResponse(response_data)
        if models.Table.objects.filter(usr_email=usr_email,usr_password=usr_password).exists():
            response_data['is_login']='yes'
            response_data = HttpResponse(json.dumps(response_data)) #必须要json.dumps 否则前端收不到键的值
            response_data.set_cookie('uemail',usr_email, secure=True) #设置usr_email COOKIE
            response_data.set_cookie('is_login',True,max_age=3600*6, secure=True) #设置是否登录的 COOKIE

            ##设置cookie samesite属性值为 none 避免跨域找不到cookie
            response_data.cookies['uemail']['samesite'] = 'none'
            response_data.cookies['is_login']['samesite'] = 'none'
            return response_data
        else: #账号密码不匹配返回相应数据

            return JsonResponse(response_data)

    else:
        return HttpResponse('Bad request',status=500)

"""
------注销功能------
删除用户携带的cookie并返回相应信息
前端请求方法：POST
数据类型：用户请求携带的cookie

api:127.0.0.1:8080/account/logout/
后端返回值:Httpresponse
{"is_logout": "yes"}
"""

def usr_logout(request):
    if request.method =='POST':
        #从cookie获取用户邮箱
        usr_email = request.COOKIES.get('uemail')
        #从cookie获取用户登录状态
        is_login = request.COOKIES.get('is_login')
        response_data = {
            'is_logout':'yes',
        }

        response_data = HttpResponse(json.dumps(response_data))
        for cookie_name in request.COOKIES:
            print(cookie_name)
            #response_data.delete_cookie(cookie_name) #客户端删除cookie 因为samesite问题不可用

            response_data.set_cookie('uemail','', secure=True) #设置usr_email COOKIE
            response_data.set_cookie('is_login','',max_age=0, secure=True) #设置是否登录的 COOKIE

            ##设置cookie samesite属性值为 none 避免跨域找不到cookie
            response_data.cookies['uemail']['samesite'] = 'none'
            response_data.cookies['is_login']['samesite'] = 'none'
        return response_data
    else:
        return HttpResponse('Bad request',status= 500)


"""
------发送验证邮件功能------
------接收前端发送的账号，判断是不是POST请求，不是则返回bad request，若是则判断该账号是否已经在数据库中，若不存在返回相应数据，
------若存在则向该用户发送验证邮件，并返回相应数据
前端请求方法：POST
数据类型：form-data
    账号 uemail:
api:127.0.0.1:8080/account/sendverify/
后端返回值:
{
    "is_send_verify": "yes",
    "uemail_exist": "yes"
}
"""
def usr_send_verify_email(request):
    if request.method == 'POST':
        usr_email = request.POST.get('uemail')

        response_data = {'is_send_verify':'no',
                         'uemail_exist':'no'
        }

        subject = 'Edu account verify'
        message = 'https://127.0.0.1:8080/account/emailverify/'+usr_email+'/'
        from_email = 'eudtocher@163.com'
        recept_email =[usr_email]  #接收可以有多个人
        #如果接收邮件不空且在数据库中已经添加了该邮件账号则发送验证邮件,且邮件为验证
        if usr_email and models.Table.objects.filter(usr_email=usr_email,usr_verify =0 ).exists():
            try:
                send_mail(subject,message,from_email,recept_email) #发送邮件
                response_data['is_send_verify'] = 'yes'
                response_data['uemail_exist'] = 'yes'
                return JsonResponse(response_data)

            except (BadHeaderError,SMTPDataError):
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)  #邮件名在数据库不存在则返回相应数据

    else:
        return HttpResponse('Bad request',status=500)

"""
------验证邮箱确认功能------（该功能无需前端参与）
------接收用户邮箱中发送来的验证请求，首先判断该邮箱在数据库中是否存在，若不存在则返回'unknow request',status=500
------若存在则判断是否已经激活，若已经激活返回相应数据，若未激活则激活该账号后返回相应数据
客户请求方法：GET
api:127.0.0.1:8080/account/emailverify/验证邮箱/
后端返回值:
usr_email+'is verified now!'
usr_email+" is verified , Please don't repeat the verification"
'unknow request',status=500
"""
def usr_email_verify(request,usr_email):
    response_data=''
    if models.Table.objects.filter(usr_email=usr_email).exists(): #判断邮箱是否存在避免被恶意请求

        if models.Table.objects.filter(usr_email=usr_email,usr_verify=1).exists(): #判断是否已经激活过
            response_data = usr_email+" is verified , Please don't repeat the verification"
        else:
            models.Table.objects.filter(usr_email=usr_email).update(usr_verify=1) #若没有激活则激活
            response_data = usr_email+'is verified now!'
        return HttpResponse(response_data)
    else:
        return HttpResponse('unknow request',status=500)  #用户名不存在返回unknow request

    
"""
------修改密码功能------
------接收前端发送的账号，判断是不是POST请求，不是则返回bad request，若是则判断用户名密码是否匹配，正确则更新密码且返回相应数据，
------若不匹配则返回相应数据
前端请求方法：POST
数据类型：form-data
    账号 uemail:
    密码 upassword
    新密码 unewpassword

api:127.0.0.1:8080/account/newpassword/
后端返回值:
{
    "is_matching": "yes",      #表示用户名与密码是否匹配
    "is_update_password": "yes"
}
"""

def usr_change_password(request):
    if request.method == 'POST':
        usr_email = request.POST.get('uemail')
        usr_password = request.POST.get('upassword')
        usr_newpassword = request.POST.get('unewpassword') #新密码

        response_data = {
            'is_matching':'no',
            'is_update_password':'no'
        }

        if usr_email and usr_password:  #判断用户名和密码是否是空
            if models.Table.objects.filter(usr_email=usr_email,usr_password=usr_password).exists():
                response_data['is_matching'] = 'yes'
                models.Table.objects.filter(usr_email=usr_email,usr_password=usr_password).update(usr_password=usr_newpassword) #设置新密码
                response_data['is_update_password'] = 'yes'
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('Bad request',status= 500)

"""
------向用户邮箱发送找回的密码------
------接收前端发送的账号，判断是不是POST请求，不是则返回bad request，若是则判断邮箱是否存在若邮箱存在则给该邮箱（用户）发送密码
------并给前端返回相应信息，若不存在，则返回相应信息
前端请求方法：POST
数据类型：form-data
    账号 uemail:

api:127.0.0.1:8080/account/sendfindpwd/
后端返回值:
{
    "uemail_exist": "yes",
    "is_send_password": "yes"
}
"""
def usr_find_password(request):
    if request.method == 'POST':
        usr_email = request.POST.get('uemail')
        response_data ={
            'uemail_exist':'no',
            'is_send_password':'no'
        }
        usr_info = ''
        if models.Table.objects.filter(usr_email=usr_email).exists(): #判断邮箱是否存在
            response_data['uemail_exist'] = 'yes'
            #邮件信息
            try:
                usr_info = models.Table.objects.get(usr_email=usr_email) #获取用户信息
            except ObjectDoesNotExist:
                print('get usr_info error')
            usr_password = usr_info.usr_password
            #向用户发送邮件
            subject = 'Eud find password your EDU password'
            message = 'Your password : '+usr_password
            from_email = 'eudtocher@163.com'
            recept_email = [usr_email]

            
            try:
                send_mail(subject,message,from_email,recept_email) #发送邮件
                response_data['is_send_password'] = 'yes'
                
            except (BadHeaderError,SMTPDataError):
                print('send password error')

            return JsonResponse(response_data) #返回响应
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status= 500)

"""
------更新用户信息------
------接收前端发送的账号，判断是不是POST请求，不是则返回bad request，若是则提取cookie中的用户邮箱和登录状态，
------若为未登录则返回相应数据，若为已登录则向数据库提交新的用户数据，返回对应信息
前端请求方法：POST
数据类型：form-data
携带登录时获得的cookie
    年龄 uage:
    性别 usex: B/W
    学历 ueducation:
    毕业学校 uschool:
    执教学科 uteaching_subjects: 多个学科之间用;隔开
    执教年级 uteaching_grade: 多个年级之间用;隔开
    个人经历 uexperience: 

api:127.0.0.1:8080/account/upusrinfo/
后端返回值: 更新成HttpResponse 不成功JosnResponse 
{"is_login": "yes", "is_usrinfo_update": "yes"}
"""

def usr_upload_info(request):
    if request.method == 'POST':
        #从cookie获取用户emial
        usr_email = request.COOKIES.get('uemail')
        #从cookie获取用户登录状态
        is_login = request.COOKIES.get('is_login')
        #获取用户上传的信息
        #年龄
        usr_age = request.POST.get('uage')
        #性别
        usr_sex = request.POST.get('usex')
        #专业
        usr_major = request.POST.get('umajor')
        #毕业学校
        usr_school =request.POST.get('uschool')  
        #执教学科
        usr_teaching_subjects = request.POST.get('uteaching_subjects')
        #执教年级
        usr_teaching_grade = request.POST.get('uteaching_grade')
        #个人经历
        usr_experience = request.POST.get('uexperience')
        #电话号码
        usr_phone_number = request.POST.get('u_phone_number')
        #所在省
        usr_now_province = request.POST.get('u_now_province')
        #坐在市县
        usr_now_city_county = request.POST.get('u_now_city_county')

        response_data = {
            'is_login':'no',
            'is_usrinfo_update':'no'
        }
        if usr_email and is_login: #判断邮箱是否为空 和 是否在登录状态
            response_data['is_login'] = 'yes'
            tab_obj = models.Table.objects.get(usr_email=usr_email)
            if tab_obj.use_certificate_verify != CERTIFICATE_VERIFIED:
                models.Table.objects.filter(usr_email=usr_email).update(
                    usr_age=usr_age,
                    usr_sex=usr_sex,
                    usr_school=usr_school,
                    usr_teaching_subjects=usr_teaching_subjects,
                    usr_teaching_grade=usr_teaching_grade,
                    usr_experience=usr_experience,
                    usr_major=usr_major,
                    usr_phone_number=usr_phone_number,
                    usr_now_province= usr_now_province,
                    usr_now_city_county= usr_now_city_county,)
                response_data['is_usrinfo_update'] = 'yes'
            else:  #已经认证过学籍的账号不可以更改学校和专业
                models.Table.objects.filter(usr_email=usr_email).update(
                    usr_age=usr_age,
                    usr_sex=usr_sex,
                    #usr_school=usr_school,
                    usr_teaching_subjects=usr_teaching_subjects,
                    usr_teaching_grade=usr_teaching_grade,
                    usr_experience=usr_experience,
                    #usr_major=usr_major,
                    usr_phone_number=usr_phone_number,
                    usr_now_province= usr_now_province,
                    usr_now_city_county= usr_now_city_county,)
                response_data['is_usrinfo_update'] = 'yes'

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status =500)

"""
------获取用户信息------
------接收前端发送的账号，判断是不是GET请求，不是则返回bad request，若是则提取cookie中的用户邮箱和登录状态，
------若为已登录则返回用户信息，若未登录则返回相应信息
前端请求方法：POST
数据类型：
    携带登录时获得的cookie

api:127.0.0.1:8080/account/getusrinfo/
后端返回值: 
登录状态返回
{
    "is_login": "yes",
    "uname": "yajie",
    "uemail": "909092921@qq.com",
    "uage": 18,
    "usex": "B",
    "ueducation": "yanjiusheng",
    "uschool": "",
    "uteaching_subjects": "yuwen;shuxue;",
    "uteaching_grade": "chuzhong1;chuzhong3;",
    "uexperience": "good good study",
    "ucoin": 4250.0,
    "ucredit": 0.0,
    "uphone_number": "",
    "is_certificate_verify": 0,  #0表示学历未验证
    "can_fund_teacher": 0  #0 表示未开通赵老师模块
}
未登录状态返回
{
    "is_login": "no"
}
"""
def usr_get_info(request):
    if request.method == 'GET':
        #从cookie获取用户emial
        usr_email = request.COOKIES.get('uemail')
        #从cookie获取用户登录状态
        is_login = request.COOKIES.get('is_login')
        response_data = {
            'is_login':'no',
        }
        if usr_email and is_login: #判断邮箱是否为空 和 是否在登录状态
            response_data['is_login'] = 'yes'
            #从数据库获取用户信息
            tab_obj = models.Table.objects.get(usr_email=usr_email)
            response_data['uname'] = tab_obj.usr_name  #用户昵称
            response_data['uemail'] = tab_obj.usr_email #用户名(邮箱)
            response_data['uage'] = tab_obj.usr_age #年龄
            response_data['usex'] = tab_obj.usr_sex #性别
            response_data['umajor'] = tab_obj.usr_major #专业
            response_data['uschool'] = tab_obj.usr_school #毕业学校
            response_data['uteaching_subjects'] = tab_obj.usr_teaching_subjects #执教学科
            response_data['uteaching_grade'] = tab_obj.usr_teaching_grade #执教年级
            response_data['uexperience'] = tab_obj.usr_experience #个人经历
            response_data['ucoin'] = tab_obj.usr_coin #学币
            response_data['ucredit'] = tab_obj.usr_credit #信用分
            response_data['uphone_number'] = tab_obj.usr_phone_number #电话号码
            response_data['can_fund_teacher'] = tab_obj.usr_is_paid_fundteacher #是否开通赵老师模块
            response_data['u_now_city_county'] = tab_obj.usr_now_city_county #现在所在县市
            response_data['u_now_province'] = tab_obj.usr_now_province #现在所在省
            response_data['is_certificate_verify'] = tab_obj.use_certificate_verify #学历是否验证
            response_data['is_identity_verify'] =tab_obj.usr_identity_verify #是否身份认证

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status= 500)

"""
------用后购买找老师模块------（购买过的不可以再次购买,且实名认证过才能买）
------首先判断是不是post请求，是post请求则判断用户是否已经购买过找老师功能，没购买则 购买扣钱且跟新用户购买信息，返回相应信息
------已购买则返回相应信息
前端请求方法：POST
用户携带的cookie
数据类型：

https://127.0.0.1:8081/account/buyteacherfunc/
后端返回值: 
{
    "paid_success": "no",
    "is_identity_verify": "no",
    "is_lack_money": "no"
}
{
    "paid_success": "yes",
    "is_identity_verify": "yes",
    "is_lack_money": "no"
}
"""

def usr_buy_fund_teacher(request):
    if request.method =='POST':
        is_login = request.COOKIES.get('is_login')
        usr_email = request.COOKIES.get('uemail')

        response_data ={
            'paid_success':'no',
            'is_identity_verify':'no',
            'is_lack_money':'no',
        }
        #获取用户信息
        usr_info = ''
        try:
            usr_info = models.Table.objects.get(usr_email= usr_email)
        except ObjectDoesNotExist:
            print('usr_info get error')
        if usr_info.usr_identity_verify == IDENTITY_VERIFIED:  #要实名认证后的才能买
            response_data['is_identity_verify'] = 'yes'
            if usr_info.usr_is_paid_fundteacher == FUND_TEACHER_NOT_PAID: #没购买过才能买
                if usr_info.usr_coin >= FUNF_TEACHER_PRICE:
                    usr_coin = usr_info.usr_coin - FUNF_TEACHER_PRICE
                    models.Table.objects.filter(usr_email= usr_email).update(usr_coin = usr_coin,usr_is_paid_fundteacher=FUND_TEACHER_PAID)

                    response_data['paid_success'] = 'yes'
                    response_data['is_lack_money'] = 'no'
                    return JsonResponse(response_data)
                else:
                    response_data['is_lack_money'] = 'yes'
                    return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status =500)


"""
------获取已经认证的老师的信息------（实名认证且购买了找老师功能的用户才可以请求）

前端请求方法：GET
用户携带的cookie
数据类型：
    url中的过滤信息

api:127.0.0.1:8080/account/getteacherlist/学历/执教学科/执教年级/
后端返回值: 
{
    "is_login": "yes",
    "is_identity_verify": "yes",
    "is_paid_fund_teacher_fuc": "yes",
    "teacher_num": 1,
    "teacherinfo": [
        {
            "usr_email": "1193184604@qq.com",
            "usr_age": 21,
            "usr_sex": "B",
            "usr_education": "本科", //yishan
            "usr_school": "青岛大学",
            "usr_teaching_subjects": "语文;数学;地理",
            "usr_teaching_grade": "初一;高一",
            "usr_experience": "..........",
            "usr_credit": 0.0,
            "usr_phone_number": ""
        }
    ]
}
"""
def usr_get_teacher_list(request,usr_teaching_subjects,usr_teaching_grade):
    if request.method == 'GET':
        is_login = request.COOKIES.get('is_login')
        usr_email = request.COOKIES.get('uemail')

        response_data ={
            'is_login':'no',
            'is_identity_verify':'no',
            'is_paid_fund_teacher_fuc':'no',
            'teacher_num':0,
            'teacherinfo':[],
        }
        #转化内容便于模糊查询
        if usr_teaching_subjects =='no':
            usr_teaching_subjects = ''
        if usr_teaching_grade == 'no':
            usr_teaching_grade = ''

        #查看用户有没有开通找老师功能和实名认证
        if is_login and usr_email:
            response_data['is_login'] = 'yes'
            if models.Table.objects.filter(usr_email=usr_email,usr_identity_verify = IDENTITY_VERIFIED).exists():
                response_data['is_identity_verify'] = 'yes'
                if models.Table.objects.filter(usr_email = usr_email,usr_is_paid_fundteacher = FUND_TEACHER_PAID).exists() :
                    response_data['is_paid_fund_teacher_fuc'] = 'yes'
                    #开始获取老师信息
                    teacher_info = ''

                    teacher_info = models.Table.objects.filter(use_certificate_verify = CERTIFICATE_VERIFIED, #学籍认证的老师才会出现
                        usr_teaching_subjects__contains = usr_teaching_subjects, #模糊查询执教学科
                        usr_teaching_grade__contains = usr_teaching_grade,      #模糊查询执教年级
                        ).values(
                            'usr_email',
                            'usr_age',
                            'usr_sex',
                            'usr_school',
                            'usr_teaching_subjects',
                            'usr_teaching_grade',
                            'usr_experience',
                            'usr_credit',
                            'usr_phone_number',
                            'usr_identity_verify',
                            'use_certificate_verify',
                        )

                    teacher_info = list(teacher_info)
                    response_data['teacher_num'] = len(teacher_info)
                    response_data['teacherinfo'].extend(teacher_info)

                    return JsonResponse(response_data)

                else:
                    return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)

"""
------查看员工信息(老师信息)------
方法:get
数据:cookies 
      wemail 员工邮箱 
api:https://127.0.0.1:8081/account/getteacherinfo/员工邮箱/
后端返回值:
{
    "is_login": "yes",
    "is_get_info": "yes",
    "worker_info": {
        "usr_age": 21,
        "usr_sex": "男",
        "usr_school": "青岛大学",
        "usr_teaching_subjects": "小学:(思想品德 ) ",
        "usr_teaching_grade": "小学:(三年级 ) ",
        "usr_experience": "在历史前进的逻辑中前进",
        "usr_credit": 0.0,
        "usr_phone_number": "17554251675",
        "usr_identity_verify": 1,
        "use_certificate_verify": 1
    }
}
"""
def usr_get_teacher_info(request,worker_email):
    if request.method == 'GET':
        is_login = request.COOKIES.get('is_login')
        #返回数据
        response_data={
            'is_login':'no',
            'is_get_info':'no',
            'worker_info':{},
        }

        if is_login:
            response_data['is_login'] = 'yes'
            if models.Table.objects.filter(usr_email=worker_email).exists():
                #获取信息
                teacher_info = ''
                teacher_info = models.Table.objects.filter(usr_email=worker_email
                    ).values(
                        'usr_age',
                        'usr_sex',
                        'usr_school',
                        'usr_major',
                        'usr_teaching_subjects',
                        'usr_teaching_grade',
                        'usr_experience',
                        'usr_credit',
                        'usr_phone_number',
                        'usr_identity_verify',
                        'use_certificate_verify',
                    )

                response_data['worker_info'] = list(teacher_info)[0] 
                response_data['is_get_info']='yes'
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)



def usr_test(request): #登录功能
    if request.method == 'GET':

        response_data = {'is_login':'no',
                         'is_verify':'no'
        }


        response_data = HttpResponse(json.dumps(response_data))
        response_data.set_cookie('uemail','2kjhkjh2',secure=True) #设置usr_email COOKIE
        response_data.set_cookie('is_login',True,max_age=3600,secure=True) #设置是否登录的 COOKIE
        response_data.cookies["uemail"]['samesite'] = "none"
        response_data.cookies["is_login"]['samesite'] = "none"

        return response_data

    else:
        return HttpResponse('Bad request',status=500)