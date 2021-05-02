from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.core.mail import BadHeaderError,send_mail
from smtplib import SMTPDataError #被当成垃圾邮件后发送失败的excpt
from django.core.exceptions import ObjectDoesNotExist
import json
from orders import models
import time
import datetime
from django.utils import timezone
from django.forms.models import model_to_dict
#######################订单状态定义######################
UN_PAID = 0 # 未发布的订单
PAID = 1    #已付款 
TAKEOVER = 2 #订单已接手
COMPLETE = 3 #订单已完成
NEGOTIATE_REFUND = 4 #协商退款中
REFUND_SUCCESS = 5 #退款成功
CANCELD = 6 #订单已取消
CUSTOMET_INTERVEN = 7 #客服介入中
APPLY_COMPLETE = 8 #申请订单完成
#########################用户动作#######################
BOSS_ASK_REFUND = 1
BOSS_CANCEL_REFUND = 0

WORKER_AGREE_REFUND = 1
WORKER_DENY_REFUND = 2

WORKER_ASK_COMPLETE = 1
BOSS_AGREEE_COMPLETE = 1

NOT_EVALUATE = 0 #订单为评价
EVALUATED = 1 #订单已经评价

# Create your views here.
"""
------创建订单------
------首先判断是不是post请求，不是返回bad request，是则从cookie判断用户是否已经登录，未登录则返回相应的信息，
------登录则进行cookie中的email与前端提交的email比较，不相同则返回不合法请求，若相同则提取前端发送的订单信息后，
------判断金额是否正确，正确则向订单表里面添加一条订单信息并返回相应信息，否则返回Illegal total_money
前端请求方法：POST
请求中的cookie
数据类型：form-data
    邮箱 uemail:
    执教年级 oteaching_grade:
    执教学科 oteaching_subjects:
    订单单价 ohourly_money:
    订单总价 ototal_money:
    教学时长 oteaching_time:
    老板称呼 oboss_name:
    老板电话 oboss_phone_number:
    老板qq微 oboss_qq_wei:
    老板额外要求 oboss_require:  可以为空，其上其它字段不可以为空

api:127.0.0.1:8080/orders/creatorder/
后端返回值:
未登录时
{
    "is_login": "yes",
    "is_add_order": "yes",
    "order_token": "ya1617978805773496"
}
登录时且创建订单成功
{
    "is_login": "no",
    "is_add_order": "no",
    "order_token": ""
}
"""
def boss_create_order(request):
    if request.method == 'POST':
        #从cookie获取登录状态
        is_login = request.COOKIES.get('is_login')
        #从cookie获取邮箱号
        usr_email = request.COOKIES.get('uemail')
        #获取发单者邮箱
        order_boss_email = request.POST.get('uemail')

        response_data = {
            'is_login':'no',
            'is_add_order':'no',
            'order_token':''
        }
        #判断登录状态
        if is_login:
            response_data['is_login'] = 'yes'
            #判断cookie中的email 与 前端发送的boss_email是否一致(为了再次确认发单者是登录的那个人,防止恶意软件发单)
            if usr_email == order_boss_email:
                #开始向订单表中添加一条订单信息
                #生成订单号
                #token = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
                #order_token = token.replace('-','').replace(' ','').replace(':','')
                usr_name = amodels.Table.objects.get(usr_email = usr_email).usr_name
                order_token =usr_name[0:2]+str(round(time.time() * 1000000)) #得到订单号
                order_start_time = timezone.now() #订单创建时间
                order_status = UN_PAID #待付款状态
                order_teaching_grade = request.POST.get('oteaching_grade') #执教年级
                order_teaching_subjects = request.POST.get('oteaching_subjects') #执教学科
                order_hourly_money = request.POST.get('ohourly_money') #订单每小时多少钱
                order_teaching_time = request.POST.get('oteaching_time') #教学时长
                order_total_money = request.POST.get('ototal_money') #订单总的金额
                order_boss_name = request.POST.get('oboss_name') #老板称呼
                order_boss_phone_number = request.POST.get('oboss_phone_number') #老板电话
                order_boss_qq_wei = request.POST.get('oboss_qq_wei') #老板qq或微信
                order_boss_require = request.POST.get('oboss_require') #老板特殊要求
                

                if (order_token and order_start_time and order_teaching_grade and order_teaching_subjects and 
                    order_hourly_money and order_teaching_time and order_total_money and order_boss_name and 
                    order_boss_phone_number and order_boss_qq_wei): #这些信息不可以为空 
                    #向数据库订单表里面添加一条订单信息
                    #核算一下总金额防止信息被恶意篡改
                    if float(order_hourly_money) * float(order_teaching_time) == float(order_total_money):
                        response_data['order_token'] = order_token
                        models.Table.objects.create (order_token=order_token,order_boss_email=order_boss_email,order_start_time=order_start_time,
                        order_status=order_status,order_teaching_grade=order_teaching_grade,order_teaching_subjects=order_teaching_subjects,
                        order_hourly_money=order_hourly_money,order_teaching_time=order_teaching_time,order_total_money=order_total_money,
                        order_boss_name=order_boss_name,order_boss_phone_number=order_boss_phone_number,order_boss_qq_wei=order_boss_qq_wei,
                        order_boss_require=order_boss_require
                        )
                        response_data['is_add_order'] = 'yes'
                        return JsonResponse(response_data)
                    else:
                        return HttpResponse('Illegal total_money')
                    
                else:
                    return HttpResponse('Illegal update information')

            else:
                return HttpResponse('Illegal request')
        else:
            return JsonResponse(response_data) #未登录返回登录状态
    else:
        return HttpResponse('Bad request',status= 500)

"""
------发单者修改订单(修改未付款订单)------ 订单付款后不可修改
------首先判断是不是post请求，不是返回bad request，是则从cookie判断用户是否已经登录，未登录则返回相应的信息，
------登录则进行cookie中的email与前端提交的email比较，不相同则返回不合法请求，若相同则提取前端发送的订单信息后，
------判断金额是否正确，正确则向订单表跟新订单信息并返回相应信息，否则返回Illegal total_money
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:
    邮箱 uemail:
    执教年级 oteaching_grade:
    执教学科 oteaching_subjects:
    订单单价 ohourly_money:
    教学时长 oteaching_time:
    订单总价 ototal_money:
    老板称呼 oboss_name:
    老板电话 oboss_phone_number:
    老板qq微 oboss_qq_wei:
    老板额外要求 oboss_require:  可以为空，其上其它字段不可以为空

api:127.0.0.1:8080/orders/updateorder/
后端返回值:
未登录时
{
    "is_login": "no",
    "is_update_order": "no"
}
登录时且创建订单成功
{
    "is_login": "yes",
    "is_update_order": "yes"
}
"""

def boss_update_order(request):
    if request.method == 'POST':
        #从cookie获取登录状态
        is_login = request.COOKIES.get('is_login')
        #从cookie获取邮箱号
        usr_email = request.COOKIES.get('uemail')
        #获取修改订单者邮箱
        order_boss_email = request.POST.get('uemail')

        response_data = {
            'is_login':'no',
            'is_update_order':'no',
        }
        #判断登录状态
        if is_login:
            response_data['is_login'] = 'yes'
            #判断cookie中的email 与 前端发送的boss_email是否一致(为了再次确认发单者是登录的那个人,防止恶意软件改单)
            if usr_email == order_boss_email:
                #获取新的订单信息
                order_token =request.POST.get('otoken') #得到订单号
                order_teaching_grade = request.POST.get('oteaching_grade') #执教年级
                order_teaching_subjects = request.POST.get('oteaching_subjects') #执教学科
                order_hourly_money = request.POST.get('ohourly_money') #订单每小时多少钱
                order_teaching_time = request.POST.get('oteaching_time') #教学时长
                order_total_money = request.POST.get('ototal_money') #订单总的金额
                order_boss_name = request.POST.get('oboss_name') #老板称呼
                order_boss_phone_number = request.POST.get('oboss_phone_number') #老板电话
                order_boss_qq_wei = request.POST.get('oboss_qq_wei') #老板qq或微信
                order_boss_require = request.POST.get('oboss_require') #老板特殊要求
                

                if (order_token and order_teaching_grade and order_teaching_subjects and 
                    order_hourly_money and order_teaching_time and order_total_money and order_boss_name and 
                    order_boss_phone_number and order_boss_qq_wei): #这些信息不可以为空 
                    #向数据库修改订单信息
                    #核算一下总金额防止信息被恶意篡改
                    if float(order_hourly_money) * float(order_teaching_time) == float(order_total_money):
                        tab_obj = models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email,order_status=UN_PAID)
                        if tab_obj.exists():
                            tab_obj.update(order_teaching_grade=order_teaching_grade,order_teaching_subjects=order_teaching_subjects,
                            order_hourly_money=order_hourly_money,order_teaching_time=order_teaching_time,order_total_money=order_total_money,
                            order_boss_name=order_boss_name,order_boss_phone_number=order_boss_phone_number,order_boss_qq_wei=order_boss_qq_wei,
                            order_boss_require=order_boss_require)
                    
                            response_data['is_update_order'] = 'yes'
                            return JsonResponse(response_data)
                        else:
                            return HttpResponse('The order cannot be modified or the information does not match')
                    else:
                        return HttpResponse('Illegal total_money')
                    
                else:
                    return HttpResponse('Illegal update information')

            else:
                return HttpResponse('Illegal request') #cookie 中的email与发单者的email不一致
        else:
            return JsonResponse(response_data) #未登录返回登录状态
    else:
        return HttpResponse('Bad request',status= 500)

"""
------发单者发布订单(付款)------ 订单付款后不可修改
------判断是不是post请求，不是返回相应信息，是则查找要付款的订单，若查找到则付款，付款成功返回相应信息，
------钱不够返回相应信息，若为查找到相应订单，返回相应信息
前端请求方法：POST
cookie
数据类型：form-data
    邮箱 uemail:
    订单号 otoken:


api:127.0.0.1:8080/orders/payorder/
后端返回值:
付款成功
{
    "order_exist": "yes",
    "order_status": 1,
    "is_payed": "yes",
    "payed_money": 500.0,
    "lack_money": "no"
}
付款失败(已付款或者为查找到订单)
{
    "order_exist": "no",
    "order_status": 1,
    "is_payed": "no",
    "payed_money": 0,
    "lack_money": "no"
}

"""
#import sys
#sys.path.append('..')
from account import models as amodels
def boss_pay_order(request):
    if request.method == 'POST':
        order_boss_email = request.POST.get('uemail') #获取boss邮箱
        order_token = request.POST.get('otoken') #获取订单号
        usr_email = request.COOKIES.get('uemail') #获取cookie中的邮箱
        response_data = {
            'order_exist':'no',
            'order_status':'',
            'is_payed':'no',
            'payed_money':0,
            'lack_money':'no',
        }
        if order_boss_email == usr_email:
            #获取订单状态
            try:
                response_data['order_status'] = models.Table.objects.get(order_token=order_token).order_status
            except ObjectDoesNotExist:
                return JsonResponse(response_data)

            if models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email,order_status=UN_PAID).exists(): #查找对应的未付款订单
                #开始扣钱
                response_data['order_exist'] = 'yes'
                
                usr_coin = amodels.Table.objects.get(usr_email=order_boss_email).usr_coin
                order_price = models.Table.objects.get(order_token=order_token,order_boss_email=order_boss_email,order_status=UN_PAID).order_total_money

                if usr_coin < order_price:
                    response_data['lack_money'] = 'yes'
                    return JsonResponse(response_data)
                else:
                    usr_coin = usr_coin - order_price
                    amodels.Table.objects.filter(usr_email=order_boss_email).update(usr_coin=usr_coin) #修改coin
                    models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email,order_status=0).update(order_status=PAID) #修改订单状态
                    response_data['is_payed'] = 'yes'
                    response_data['payed_money'] = order_price
                    response_data['order_status'] = models.Table.objects.get(order_token=order_token).order_status  #获取订单状态
                    return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('Bad request',status=500)

"""
------员工接单------ 
------判断是不是post请求，不是返回相应信息，是则判断是否登录未登录则返会相应信息 登录则判断是不是自己接自己的单
------不是则查找订单（接单必须是PAID 已经发布的单），查找成功,开始扣除保证金，钱不够则返回相应信息，否则扣出保证金后接单修改相应信息，否则返回相应信息
前端请求方法：POST
浏览器cookie
数据类型：form-data
    老板邮箱 bemail:
    订单号 otoken:
    ###老师信息不能为空
    老师名字 wname:
    老师电话 wphone_number:
    老师微信或qq wwei_qq :

api:127.0.0.1:8080/orders/wtakeover/
后端返回值:
{
    "is_login": "yes",
    "order_exist": "yes",
    "is_take_over": "yes",
    "is_lack_eranest_money": "no",
    "is_self_take": "no"
}
"""
def worker_take_over_order(request):
    if request.method == 'POST':
        order_worker_email = request.COOKIES.get('uemail')
        is_login = request.COOKIES.get('is_login')
        order_boss_email = request.POST.get('bemail')
        order_token = request.POST.get('otoken')
        #获取老师信息
        order_worker_name = request.POST.get('wname')
        order_worker_phone_number = request.POST.get('wphone_number')
        order_worker_qq_wei = request.POST.get('wwei_qq')

        response_data ={
            'is_login':'no',
            'order_exist':'no',
            'is_take_over':'no',
            'is_lack_eranest_money':'no',
            'is_self_take':'no',
        }
        if is_login and order_worker_email != order_boss_email: #不可以字节接自己的单
            response_data['is_login'] = 'yes'
            if models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email,order_status=PAID).exists(): #接单必须是已经发布的单
                #更新订单信息
                response_data['order_exist'] = 'yes'
                if order_worker_name and order_worker_phone_number and order_worker_qq_wei:
                    #接单者支付保证金
                    tab_obj=''
                    try:
                        tab_obj = amodels.Table.objects.get(usr_email=order_worker_email)
                    except ObjectDoesNotExist:
                        return JsonResponse(response_data)
                    
                    worker_coin = tab_obj.usr_coin
                    order_worker_earnest_money = models.Table.objects.get(order_token=order_token,order_boss_email=order_boss_email,order_status=PAID).order_worker_earnest_money

                    if worker_coin - order_worker_earnest_money >= 0:
                        #钱够支付保证金则开始扣钱
                        worker_coin = worker_coin - order_worker_earnest_money
                        amodels.Table.objects.filter(usr_email=order_worker_email).update(usr_coin=worker_coin)
                        response_data['is_lack_eranest_money'] = 'no'
                        #扣钱后跟新订单信息
                        models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email).update(
                        order_worker_email=order_worker_email,
                        order_status=TAKEOVER,
                        order_accept_time=timezone.now(),
                        order_worker_name=order_worker_name,
                        order_worker_phone_number=order_worker_phone_number,
                        order_worker_qq_wei=order_worker_qq_wei)
                        response_data['is_take_over'] = 'yes'
                        #给老板发送接单信息
                        tab_obj1=''
                        try:
                            tab_obj1 = models.Table.objects.get(order_token=order_token,order_boss_email=order_boss_email,order_status=TAKEOVER)
                        except ObjectDoesNotExist:
                            print('order get error!')
                        subject = 'Edu 您的订单被接手'
                        message = tab_obj1.order_boss_email+ '你的订单:' + tab_obj1.order_token + '\n'+tab_obj1.order_teaching_subjects +'\n' +str(tab_obj1.order_total_money)+'元'+'已被接单者：'+tab_obj1.order_worker_email+'接单！'
                        from_email = 'eudtocher@163.com'
                        recept_email =[tab_obj1.order_boss_email]  #接收可以有多个人

                        try:
                            send_mail(subject, message, from_email, recept_email)
                        except (BadHeaderError,SMTPDataError):
                            print('send email falied')

                        return JsonResponse(response_data)
                    else:
                        response_data['is_lack_eranest_money'] = 'yes'
                        return JsonResponse(response_data)
                else:
                    return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            if order_worker_email == order_boss_email:
                response_data['is_login'] = 'yes'
                response_data['is_self_take'] = 'yes'
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)

"""
------员工取消接单------ （取消的单子要是已经接手的，同时要扣除保证金）

前端请求方法：POST
cookie数据
数据类型：form-data
    订单号 otoken:


api:127.0.0.1:8080/orders/wcancelorder/
后端返回值:
{
    "is_login": "yes",
    "is_order_cancel": "yes",
    "order_status": 1
}
"""
def worker_cancel_order(request):
    if request.method == 'POST':
        is_login = request.COOKIES.get('is_login')
        order_worker_email = request.COOKIES.get('uemail')
        order_token = request.POST.get('otoken')
        response_data = {
            'is_login':'no',
            'is_order_cancel':'no',
            'order_status':'',
        }
        tab_obj =''
        if is_login and order_token and order_worker_email:
            response_data['is_login'] = 'yes'
            try:
                tab_obj = models.Table.objects.get(order_token=order_token,order_worker_email=order_worker_email)
                response_data['order_status'] = tab_obj.order_status
            except:
                print('Can not get order info')

            if models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=TAKEOVER).exists():
                #更新订单信息
                models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=TAKEOVER).update(
                    order_status=PAID,
                    order_worker_email=''
                )
                response_data['is_order_cancel'] = 'yes'
                response_data['order_status'] = PAID

                #给老板发送订单被取消的邮件邮件
                subject = 'Edu 对方取消接单'
                message = tab_obj.order_boss_email+ '你的订单:' + tab_obj.order_token + '\n'+tab_obj.order_teaching_subjects +'\n' +str(tab_obj.order_total_money)+'元'+'已被接单者：'+tab_obj.order_worker_email+'取消！'
                from_email = 'eudtocher@163.com'
                recept_email =[tab_obj.order_boss_email]  #接收可以有多个人

                try:
                    send_mail(subject, message, from_email, recept_email)
                except (BadHeaderError,SMTPDataError):
                    print('send email falied')
                

                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('Bad request',status =500)


"""
------用户(boss)取消发单()------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息，若已登录则比对cookie中的email和
------前端提交的email 账号，相同则进行取消订单操作，不相同返回相应信息；取消订单操作先看该订单是否存在，不存在返回相应信息，存在则
------看订单状态，订单状态为0，则修改订单状态为6后向order_table2中添加这条订单信息同时删除其在order_table中的相应条目，若订单状态为1，
------则先退回coin后，修改订单状态为6,向order_table2中添加这条订单信息同时删除其在order_table中的相应条目，最后返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data
    邮箱 uemail:
    订单号 otoken:

api:127.0.0.1:8080/orders/bcancelorder/
后端返回值:
{
    "is_login": "yes",
    "order_exist": "yes",
    "order_status": 6,
    "is_order_cancel": "yes",
    "coin_refund": 0
}
"""
def boss_cancel_order(request):
    if request.method == 'POST':
        #从cookie获取登录状态
        is_login = request.COOKIES.get('is_login')
        #从cookie获取用户邮箱
        usr_email = request.COOKIES.get('uemail')
        #获取前端提交的用户邮箱
        order_boss_email = request.POST.get('uemail')
        #获取订单号
        order_token = request.POST.get('otoken')

        response_data = {
            'is_login':'no',
            'order_exist':'no',
            'order_status':'',
            'is_order_cancel':'no',
            'coin_refund':0,
        }
        #判断cookie中的email 与 前端发送的boss_email是否一致(为了再次确认发单者是登录的那个人,防止恶意软件取消单)
        if is_login and usr_email == order_boss_email:
            response_data['is_login'] = 'yes'
            tab_obj = ''
            try:
                tab_obj = models.Table.objects.get(order_token=order_token,order_boss_email=order_boss_email)
                response_data['order_exist'] = 'yes'
            except ObjectDoesNotExist:
                return HttpResponse('Order get error')
            
            if tab_obj.order_status == UN_PAID:
                #把该订单放入order_table1
                models.Table1.objects.create(
                    order_token = tab_obj.order_token,
                    order_boss_email = tab_obj.order_boss_email,
                    order_worker_email = tab_obj.order_worker_email,
                    order_start_time = tab_obj.order_start_time,
                    order_accept_time = tab_obj.order_accept_time,
                    order_complet_time = tab_obj.order_complet_time,
                    order_end_time = tab_obj.order_end_time,
                    order_status =CANCELD,
                    order_is_worker_ask_complet = tab_obj.order_is_worker_ask_complet,
                    order_is_boss_agree_complet = tab_obj.order_is_boss_agree_complet,
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
                    order_is_evalute = tab_obj.order_is_evalute,
                )
                #删除order_table中的原订单
                models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email).delete()

                response_data['order_status'] = CANCELD
                response_data['is_order_cancel'] = 'yes'
                return JsonResponse(response_data)
            else:
                if tab_obj.order_status == PAID:
                    #退回coin
                    usr_coin = amodels.Table.objects.get(usr_email=usr_email).usr_coin #获取用户原来coin
                    usr_coin = usr_coin +tab_obj.order_total_money #计算最后的coin
                    amodels.Table.objects.filter(usr_email=usr_email).update(usr_coin=usr_coin) #更新用户coin
                    response_data['coin_refund'] = tab_obj.order_total_money
                    #把该订单放入order_table1
                    models.Table1.objects.create(
                        order_token = tab_obj.order_token,
                        order_boss_email = tab_obj.order_boss_email,
                        order_worker_email = tab_obj.order_worker_email,
                        order_start_time = tab_obj.order_start_time,
                        order_accept_time = tab_obj.order_accept_time,
                        order_complet_time = tab_obj.order_complet_time,
                        order_end_time = tab_obj.order_end_time,
                        order_status =CANCELD,
                        order_is_worker_ask_complet = tab_obj.order_is_worker_ask_complet,
                        order_is_boss_agree_complet = tab_obj.order_is_boss_agree_complet,
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
                        order_is_evalute = tab_obj.order_is_evalute,
                    )
                    #删除order_table中的原订单
                    models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email).delete()

                    response_data['order_status'] = CANCELD
                    response_data['is_order_cancel'] = 'yes'
                    return JsonResponse(response_data)
                else:
                    response_data['order_status'] = tab_obj.order_status
                    return JsonResponse(response_data)
                
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)


"""
------用户(boss)申请退款(单子被接1小时内可以退单，超过一小时则协商退单,TAKEOVER 和 APPLY_COMPLETE 才可以申请退款)------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息，若已登录则比对cookie中的email和
------前端提交的email 账号，相同则进行退款操作,退款时判断订单接手时间是否超过1小时，未超过则直接根据boss退款额给双方退款，员工包括退回保证金，订单接手时间超过
------一小时则修改订单状态为协商退款，以及修改其它相应内容后给接单者发送退款邮件提醒
前端请求方法：POST
请求中的cookie
数据类型：form-data
    邮箱 uemail:
    订单号 otoken:
    退款金额 remoney:
    退款原因 reason:

api:127.0.0.1:8080/orders/brefundorder/
后端返回值:
超时返回结果
{
    "is_login": "yes",
    "order_exist": "yes",
    "order_status": 4,
    "is_order_refund": "doing",
    "is_time_out": "yes",
    "coin_refund": 0
}
未超时返回结果
{
    "is_login": "yes",
    "order_exist": "yes",
    "order_status": 6,
    "is_order_refund": "yes",
    "is_time_out": "no",
    "coin_refund": 100.0
}
"""

def boss_refund_order(request):
    if request.method == 'POST':
        #从cookie获取登录状态
        is_login = request.COOKIES.get('is_login')
        #从cookie获取用户邮箱
        usr_email = request.COOKIES.get('uemail')
        #获取前端提交的用户邮箱
        order_boss_email = request.POST.get('uemail')
        #获取订单号
        order_token = request.POST.get('otoken')
        #获取退款金额
        order_refund_money = float(request.POST.get('remoney'))
        #获取退款原因
        order_refund_reason = request.POST.get('reason')
        print (order_refund_reason)
        response_data = {
            'is_login':'no',
            'order_exist':'no',
            'order_status':'',
            'is_order_refund':'no',
            'is_time_out':'no',
            'coin_refund':0,
        } 
        if usr_email and order_boss_email and order_token and order_refund_money:
            #判断cookie中的email 与 前端发送的boss_email是否一致(为了再次确认发单者是登录的那个人,防止恶意软件取消单)
            if is_login and usr_email == order_boss_email:
                response_data['is_login'] = 'yes'
                tab_obj = ''

                try:
                    tab_obj = models.Table.objects.get(order_token=order_token,order_boss_email=order_boss_email)
                    response_data['order_exist'] = 'yes'
                    response_data['order_status'] = tab_obj.order_status
                except ObjectDoesNotExist:
                    return HttpResponse('Order get error')

                #判断订单状态是不是已接手 或申请完成
                if tab_obj.order_status == TAKEOVER or tab_obj.order_status == APPLY_COMPLETE:
                    #获取订单接收时间
                    order_accept_time = tab_obj.order_accept_time#datetime.datetime.strptime(str(tab_obj.order_accept_time),'%Y-%m-%d %H:%M:%S')
                    #获取当前时间
                    time_now = datetime.datetime.now()

                    #两个时间相减看是不是超过了一小时,未超时直接退款
                    if (time_now - order_accept_time).seconds <= 3600:
                        if tab_obj.order_status == TAKEOVER:
                            #把该订单放入order_table1  26 项 有意向earnest monry不用写
                            models.Table1.objects.create(
                                order_token = tab_obj.order_token,
                                order_boss_email = tab_obj.order_boss_email,
                                order_worker_email = tab_obj.order_worker_email,
                                order_start_time = tab_obj.order_start_time,
                                order_accept_time = tab_obj.order_accept_time,
                                order_complet_time = tab_obj.order_complet_time,
                                order_end_time = tab_obj.order_end_time,
                                order_status =CANCELD,#-----------
                                order_is_worker_ask_complet = tab_obj.order_is_worker_ask_complet,
                                order_is_boss_agree_complet = tab_obj.order_is_boss_agree_complet,
                                order_is_boss_ask_refund = BOSS_ASK_REFUND,#----------------
                                order_refund_reason = order_refund_reason, #----------------
                                order_is_worker_agree_refund = tab_obj.order_is_worker_agree_refund,
                                order_refund_money = order_refund_money,#-----------------
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
                            #删除order_table中的原订单
                            models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email).delete()
                            response_data['order_status'] = CANCELD

                            #退回老板coin
                            boss_coin = amodels.Table.objects.get(usr_email=order_boss_email).usr_coin #获取老板当前coin
                            #校验退款金额
                            if order_refund_money <= tab_obj.order_total_money and order_refund_money >= 0:
                                boss_coin = boss_coin + order_refund_money
                                amodels.Table.objects.filter(usr_email=order_boss_email).update(usr_coin=boss_coin) #更老板coin
                            else:
                                return HttpResponse('Illigal refund money')

                            #退回员工coin
                            worker_coin = amodels.Table.objects.get(usr_email=tab_obj.order_worker_email).usr_coin #获取员工coin
                            #校验退款金额
                            if order_refund_money <= tab_obj.order_total_money and order_refund_money >= 0:
                                worker_coin = worker_coin + (tab_obj.order_total_money - order_refund_money) + tab_obj.order_worker_earnest_money#得到退回老板后剩余的coin，包括保证金
                                amodels.Table.objects.filter(usr_email=tab_obj.order_worker_email).update(usr_coin=worker_coin) #更老板coin
                                #给老师发送提醒邮件
                                subject = 'Edu 订单申请退款'
                                message = tab_obj.order_worker_email + '你有一笔订单已被取消，'+'退回对方金额:'+str(order_refund_money)+'你得到报酬:'+str(tab_obj.order_total_money - order_refund_money)+'保证金:'+str(tab_obj.order_worker_earnest_money)
                                from_email = 'eudtocher@163.com'
                                recept_email =[tab_obj.order_worker_email]  #接收可以有多个人

                                try:
                                    send_mail(subject, message, from_email, recept_email)
                                except (BadHeaderError,SMTPDataError):
                                    print('send email falied')
                            else:
                                return HttpResponse('Illigal refund money')

                            response_data['coin_refund'] = order_refund_money
                            response_data['is_order_refund'] = 'yes'

                            return JsonResponse(response_data)
                        else:
                            return JsonResponse(response_data)        
                    else: #超时则修改订单状态，给老师发邮件提醒有退款申请
                        response_data['is_time_out'] = 'yes'
                        response_data['order_status'] = NEGOTIATE_REFUND
                        response_data['is_order_refund'] = 'doing'

                        #更新订单信息
                        models.Table.objects.filter(order_token=order_token,order_boss_email=order_boss_email).update(
                        order_is_boss_ask_refund=BOSS_ASK_REFUND,
                        order_refund_money=order_refund_money,
                        order_status=NEGOTIATE_REFUND,
                        order_refund_reason= order_refund_reason,)

                        #给老师发送提醒邮件
                        subject = 'Edu 订单申请退款'
                        message = tab_obj.order_worker_email + '你有一笔订单申请退款请前往处理'
                        from_email = 'eudtocher@163.com'
                        recept_email =[tab_obj.order_worker_email]  #接收可以有多个人
                        print(tab_obj.order_worker_email)

                        try:
                            send_mail(subject, message, from_email, recept_email)
                        except (BadHeaderError,SMTPDataError):
                            print('send email falied')
                        
                        return JsonResponse(response_data)
                else:
                    return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)


#boss取消 申请退款
"""
------用户(boss)取消申请退款(在协商退款中的单子可以申请取消退款)------
------首先判断是不是post请求，不是返回相应信息，是则判断从前端获取的信息是否未空，不空则查找相应订单，修改订单状态，返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:

api:127.0.0.1:8080/orders/bcancelrefund/
后端返回值:
{
    "is_login": "yes",
    "is_cancel_refund": "yes",
    "order_status": 2
}
"""
def boss_cancel_refund(request):
    if request.method =='POST':
        #从cookie获取用户登录状态
        is_login = request.COOKIES.get('is_login')
        #从cookie获取用户邮箱
        order_boss_email = request.COOKIES.get('uemail')
        #从前端获取订单号
        order_token = request.POST.get('otoken')
        response_data = {
            'is_login':'no',
            'is_cancel_refund':'no',
            'order_status':'',
        }
        if is_login and order_boss_email and order_token:
            response_data['is_login'] = 'yes'
            if models.Table.objects.filter(order_boss_email=order_boss_email,order_token=order_token,order_status=NEGOTIATE_REFUND).exists():
                order_refund_money = 0
                order_status = TAKEOVER
                order_is_boss_ask_refund = BOSS_CANCEL_REFUND

                #更新订单信息
                models.Table.objects.filter(order_boss_email=order_boss_email,order_token=order_token,order_status=NEGOTIATE_REFUND).update(
                    order_refund_money=order_refund_money,
                    order_status=order_status,
                    order_is_boss_ask_refund=order_is_boss_ask_refund,
                    order_refund_reason ='')
                
                #更新回复信息
                response_data['is_login'] = 'yes'
                response_data['is_cancel_refund'] = 'yes'
                response_data['order_status'] = order_status                
                tab_obj =''
                try:
                    tab_obj = models.Table.objects.get(order_boss_email=order_boss_email,order_token=order_token,order_status=TAKEOVER)
                except ObjectDoesNotExist:
                    print ('Can not get worker email')

                #给老师发送提醒邮件
                subject = 'Edu 订单用户取消申请退款'
                message = tab_obj.order_worker_email + '您的接的订单：'+order_token + '对方已取消退款'
                from_email = 'eudtocher@163.com'
                recept_email =[tab_obj.order_worker_email]  #接收可以有多个人

                try:
                    send_mail(subject, message, from_email, recept_email)
                except (BadHeaderError,SMTPDataError):
                    print('send email falied')
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)
            

"""
------用户(worker)同意退款（只处理协商退款中的单子,老板申请退款不扣除员工保证金）------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息，若已登录则
------查找相应订单，若订单不存在，则返会相应信息，订单存在则分别给老师和老板退钱，然后给老板发短信提示，修改订单
------状态后存入order_table1表中，同时删除order_table表中对应订单，最后返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:

api:127.0.0.1:8080/orders/wagreerefund/
后端返回值:
{
    "is_login": "yes",
    "agree_success": "yes",
    "order_exist": "yes",
    "order_status": 5
}
"""
def worker_agree_refund(request):
    if request.method == 'POST':
        is_login = request.COOKIES.get('is_login')
        order_worker_email = request.COOKIES.get('uemail')
        order_token = request.POST.get('otoken')

        response_data = {
            'is_login':'no',
            'agree_success':'no',
            'order_exist':'no',
            'order_status':''
        }
        tab_obj = '' #存订单信息
        boss_info= ''#存老板信息
        worker_info = ''#存员工信息
        if is_login and order_token and order_worker_email:
            #查找订单
            response_data['is_login'] = 'yes'
            if models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=NEGOTIATE_REFUND).exists():
                #获取订单信息
                try:
                    tab_obj = models.Table.objects.get(order_token=order_token,order_worker_email=order_worker_email,order_status=NEGOTIATE_REFUND)
                    response_data['order_exist'] = 'yes'
                    response_data['order_status'] = tab_obj.order_status
                except ObjectDoesNotExist:
                    print('Get order error')

                order_refund_money = tab_obj.order_refund_money #获取退款钱数
                order_worker_earnest_money = tab_obj.order_worker_earnest_money #获取保证金
                order_total_money = tab_obj.order_total_money #获取订单总金额
                order_boss_email = tab_obj.order_boss_email #获取老板邮箱

                #获取老板信息
                try:
                    boss_info = amodels.Table.objects.get(usr_email = order_boss_email)
                except ObjectDoesNotExist:
                    print('Get boss info error')
                #获取员工信息
                try:
                    worker_info = amodels.Table.objects.get(usr_email = order_worker_email)
                except ObjectDoesNotExist:
                    print('Get worker info error')

                #更新老板的coin
                boss_coin = boss_info.usr_coin + order_refund_money
                amodels.Table.objects.filter(usr_email = order_boss_email).update(usr_coin = boss_coin)
                #更新员工的coin
                worker_coin = worker_info.usr_coin + order_worker_earnest_money + (order_total_money - order_refund_money)
                amodels.Table.objects.filter(usr_email = order_worker_email).update(usr_coin = worker_coin)

                #跟新订单状态
                #在order_table1 订单完成表中加入这个订单
                models.Table1.objects.create(
                    order_token = tab_obj.order_token,
                    order_boss_email = tab_obj.order_boss_email,
                    order_worker_email = tab_obj.order_worker_email,
                    order_start_time = tab_obj.order_start_time,
                    order_accept_time = tab_obj.order_accept_time,
                    order_complet_time = timezone.now(), #----------
                    order_end_time = tab_obj.order_end_time,
                    order_status =REFUND_SUCCESS,#-----------
                    order_is_worker_ask_complet = tab_obj.order_is_worker_ask_complet,
                    order_is_boss_agree_complet = tab_obj.order_is_boss_agree_complet,
                    order_is_boss_ask_refund = tab_obj.order_is_boss_ask_refund,
                    order_refund_reason = tab_obj.order_refund_reason,
                    order_is_worker_agree_refund = WORKER_AGREE_REFUND, #--------
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
                #删除原表信息
                models.Table.objects.filter(order_token=order_token, order_worker_email=order_worker_email).delete()

                response_data['order_status'] = REFUND_SUCCESS
                response_data['agree_success'] = 'yes'


                #给老板发送邮件信息
                subject = 'Edu 订单用户同意您申请的退款'
                message = order_boss_email + '您的接的订单：'+order_token + '对方已同意退款退款' + '退款金额' + str(order_refund_money)
                from_email = 'eudtocher@163.com'
                recept_email =[order_boss_email]  #接收可以有多个人

                try:
                    send_mail(subject, message, from_email, recept_email)
                except (BadHeaderError,SMTPDataError):
                    print('send email falied')

                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)

"""
------用户(worker)拒绝退款（拒绝后订单状态从协商转为客服处理）------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息，若已登录则
------查找相应订单，若订单不存在，则返会相应信息，订单存在则修改订单相应信息后返回相应信息，
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:

api:127.0.0.1:8080/orders/wdenyrefund/
后端返回值:
{
    "is_login": "yes",
    "deny_success": "no",
    "order_exist": "no",
    "order_status": ""
}
"""

def worker_deny_refund(request):
    if request.method == 'POST':
        is_login = request.COOKIES.get('is_login')
        order_worker_email = request.COOKIES.get('uemail')
        order_token = request.POST.get('otoken')

        response_data = {
            'is_login':'no',
            'deny_success':'no',
            'order_exist':'no',
            'order_status':'',
        }

        if is_login and order_token and order_worker_email:
            #查找相应订单
            response_data['is_login'] = 'yes'
            #跟新订单信息
            if models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=NEGOTIATE_REFUND).exists():
                response_data['order_exist'] = 'yes'
                models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=NEGOTIATE_REFUND).update(
                    order_status=CUSTOMET_INTERVEN,
                    order_is_worker_agree_refund=WORKER_DENY_REFUND,
                )
                response_data['deny_success'] = 'yes'
                response_data['order_status'] = CUSTOMET_INTERVEN
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
        
    else:
        return HttpResponse('bad request',status =500)


"""
------用户(worker)申请完成单（只能对订单状态为takeover的订单申请）------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息,用户已经登录
------则查找相应订单，订单存在则修改相应信息后返回相应信息，否则返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:

api:127.0.0.1:8080/orders/waskok/
后端返回值:
{
    "is_login": "yes",
    "ask_success": "yes",
    "order_exist": "yes",
    "order_status": 8
}
"""
def worker_ask_complete(request):
    if request.method =='POST':
        is_login = request.COOKIES.get('is_login')
        order_worker_email = request.COOKIES.get('uemail')
        order_token = request.POST.get('otoken')

        response_data = {
            'is_login':'no',
            'ask_success':'no',
            'order_exist':'no',
            'order_status':'',
        }

        if is_login and order_worker_email and order_token:
            response_data['is_login'] = 'yes'
            tab_objf = models.Table.objects.filter(order_token=order_token,order_worker_email=order_worker_email,order_status=TAKEOVER)
            if tab_objf.exists():
                #更新订单信息
                tab_objf.update(order_status=APPLY_COMPLETE,order_is_worker_ask_complet=WORKER_ASK_COMPLETE,order_complet_time=timezone.now())
                response_data['ask_success'] = 'yes'
                response_data['order_exist'] = 'yes'
                response_data['order_status'] = APPLY_COMPLETE
                #获取订单信息
                tab_obj = models.Table.objects.get(order_token=order_token,order_worker_email=order_worker_email) 
                #给老板发送邮件信息提醒收货
                subject = 'Edu 您的订单已完成请前往确认'
                message = tab_obj.order_boss_email + '您的家教订单：'+order_token + tab_obj.order_teaching_grade + tab_obj.order_teaching_subjects + '已完成,请及时前往确认(未确认则3天后自动确认)' 
                from_email = 'eudtocher@163.com'
                recept_email =[tab_obj.order_boss_email]  #接收可以有多个人

                try:
                    send_mail(subject, message, from_email, recept_email)
                except (BadHeaderError,SMTPDataError):
                    print('send email falied')

                return JsonResponse(response_data)

            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status = 500)


"""
------用户(boss)同意完成单（只能对订单状态为APPLY_COMPLETE的订单同意）------
------判断方法是不是post，不是返回相应信息，是则进行状态信息判断，若用户状态为未登录返回相应信息,用户已经登录
------则查找相应订单，订单存在则给接单者添加coin，把该订单加入order_table1，在order_table删除该订单，否则返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data
    订单号 otoken:

api:127.0.0.1:8080/orders/bagreeok/
后端返回值:
{
    "is_login": "yes",
    "agree_success": "yes",
    "order_exist": "yes",
    "order_status": 3
}

"""

def boss_agree_complete(request):
    if request.method == 'POST':
        is_login = request.COOKIES.get('is_login')
        order_boss_email = request.COOKIES.get('uemail')
        order_token = request.POST.get('otoken')

        response_data = {
            'is_login':'no',
            'agree_success':'no',
            'order_exist':'no',
            'order_status':'',
        }

        if is_login and order_boss_email and order_token:
            response_data['is_login'] = 'yes'
            #查找订单
            tab_objf = models.Table.objects.filter(order_token=order_token, order_boss_email=order_boss_email, order_status=APPLY_COMPLETE)
            if tab_objf.exists():
                response_data['order_exist'] = 'yes'
                #获取订单信息
                tab_obj = models.Table.objects.get(order_token=order_token, order_boss_email= order_boss_email,order_status = APPLY_COMPLETE)
                #获取员工coin
                worker_info = amodels.Table.objects.get(usr_email= tab_obj.order_worker_email)
                worker_coin = worker_info.usr_coin + tab_obj.order_total_money + tab_obj.order_worker_earnest_money
                #更新员工coin
                amodels.Table.objects.filter(usr_email= tab_obj.order_worker_email).update(usr_coin= worker_coin)

                #在order_table1表中建立新的订单
                models.Table1.objects.create(
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
                response_data['agree_success'] = 'yes'
                response_data['order_status'] = COMPLETE
                #给老师发送结单信息
                subject = 'Edu 您的订单对方已同意结单'
                message = worker_info.usr_email + '您的家教订单：'+order_token + tab_obj.order_teaching_grade + tab_obj.order_teaching_subjects + '已入账' +str(tab_obj.order_total_money)+'元,保证金'+str(tab_obj.order_worker_earnest_money)+ '元' 
                from_email = 'eudtocher@163.com'
                recept_email =[worker_info.usr_email]  #接收可以有多个人
                try:
                    send_mail(subject, message, from_email, recept_email)
                except (BadHeaderError,SMTPDataError):
                    print('send email falied')

                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request ',status = 500)

    
"""
------获取用户接单信息------
------接收前端发送的账号，判断是不是GET请求，不是则返回bad request，若是则提取cookie中的用户邮箱和登录状态，
------若为已登录则读取订单信息然后把时间转化为字符串后返回给前端
前端请求方法：GET
数据类型：
    携带登录时获得的cookie
    url中的用户邮箱
api:127.0.0.1:8080/orders/wtakelist/用户邮箱/
后端返回值: 

{
    "is_login": "yes",
    "is_get_order": "no",
    "order_num": 4,
    "orders": [
        {
            "order_token": "ya1618064944579011",
            "order_boss_email": "909092921@qq.com",
            "order_worker_email": "2447255540@qq.com",
            "order_start_time": "2021-04-10 22:29:04",
            "order_accept_time": "2021-04-10 22:34:06",
            "order_complet_time": "2021-04-10 22:29:04",
            "order_end_time": "2021-04-10 22:29:04",
            "order_status": 2,
            "order_is_worker_ask_complet": 0,
            "order_is_boss_agree_complet": 0,
            "order_is_boss_ask_refund": 0,
            "order_is_worker_agree_refund": 0,
            "order_refund_money": 0.0,
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_worker_earnest_money": 10.0,
            "order_boss_name": "xiaowen",
            "order_boss_phone_number": "13636784990",
            "order_boss_qq_wei": "yajie123321",
            "order_boss_require": "没有",
            "order_worker_name": "文老师",
            "order_worker_phone_number": "15087238233",
            "order_worker_qq_wei": "1193184604",
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062625332581",
            "order_boss_email": "909092921@qq.com",
            "order_worker_email": "2447255540@qq.com",
            "order_start_time": "2021-04-10 21:50:25",
            "order_accept_time": "2021-04-10 21:52:33",
            "order_complet_time": "2021-04-10 21:58:06",
            "order_end_time": "2021-04-10 21:58:06",
            "order_status": 3,
            "order_is_worker_ask_complet": 1,
            "order_is_boss_ask_refund": 0,
            "order_is_boss_agree_complet": 1,
            "order_is_worker_agree_refund": 0,
            "order_refund_money": 0.0,
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_worker_earnest_money": 10.0,
            "order_boss_name": "xiaowen",
            "order_boss_phone_number": "13636784990",
            "order_boss_qq_wei": "yajie123321",
            "order_boss_require": "没有",
            "order_worker_name": "文老师",
            "order_worker_phone_number": "15087238233",
            "order_worker_qq_wei": "1193184604",
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062626354889",
            "order_boss_email": "909092921@qq.com",
            "order_worker_email": "2447255540@qq.com",
            "order_start_time": "2021-04-10 21:50:26",
            "order_accept_time": "2021-04-10 21:52:21",
            "order_complet_time": "2021-04-10 21:57:57",
            "order_end_time": "2021-04-10 21:57:57",
            "order_status": 3,
            "order_is_worker_ask_complet": 1,
            "order_is_boss_ask_refund": 0,
            "order_is_boss_agree_complet": 1,
            "order_is_worker_agree_refund": 0,
            "order_refund_money": 0.0,
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_worker_earnest_money": 10.0,
            "order_boss_name": "xiaowen",
            "order_boss_phone_number": "13636784990",
            "order_boss_qq_wei": "yajie123321",
            "order_boss_require": "没有",
            "order_worker_name": "文老师",
            "order_worker_phone_number": "15087238233",
            "order_worker_qq_wei": "1193184604",
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062627130826",
            "order_boss_email": "909092921@qq.com",
            "order_worker_email": "2447255540@qq.com",
            "order_start_time": "2021-04-10 21:50:27",
            "order_accept_time": "2021-04-10 21:51:54",
            "order_complet_time": "2021-04-10 21:57:41",
            "order_end_time": "2021-04-10 21:57:41",
            "order_status": 3,
            "order_is_worker_ask_complet": 1,
            "order_is_boss_ask_refund": 0,
            "order_is_boss_agree_complet": 1,
            "order_is_worker_agree_refund": 0,
            "order_refund_money": 0.0,
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_worker_earnest_money": 10.0,
            "order_boss_name": "xiaowen",
            "order_boss_phone_number": "13636784990",
            "order_boss_qq_wei": "yajie123321",
            "order_boss_require": "没有",
            "order_worker_name": "文老师",
            "order_worker_phone_number": "15087238233",
            "order_worker_qq_wei": "1193184604",
            "order_is_evalute": 0
        }
    ]
}
"""



def get_take_order_info(request,usr_email):
    if request.method == 'GET':
        is_login = request.COOKIES.get('is_login')
        order_worker_email = request.COOKIES.get('uemail')


        response_data = {
            'is_login':'no',
            'is_get_order':'no',
            'order_num':0,
            'orders':[]
        }

        if is_login and order_worker_email == usr_email:
            response_data['is_login'] = 'yes'
            tab_obj = '' #order_table 表中的订单信息
            tab_obj1 = '' #order_table1 表中的订单信息

            try:
                tab_obj = models.Table.objects.filter(order_worker_email=order_worker_email).order_by('-order_accept_time').values() #value返回 字典键值对 list能把里面的字典提取出来成为字典列表
                tab_obj1 = models.Table1.objects.filter(order_worker_email=order_worker_email).order_by('-order_accept_time').values() #value返回 字典键值对 list能把里面的字典提取出来成为字典列表
            except ObjectDoesNotExist:
                print('ger order error')
            order_info_list = list(tab_obj) #获取订单信息构成的字典列表
            order_info_list1 = list(tab_obj1) #获取订单信息构成的字典列表
            order_info_list.extend(order_info_list1) #两个表的订单表放入一个

            for order in order_info_list: #循环每一个字典， 把datetime 类型转化为字符串
                order['order_start_time'] = order['order_start_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_accept_time'] = order['order_accept_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_complet_time'] = order['order_complet_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_end_time'] = order['order_end_time'].strftime('%Y-%m-%d %H:%M:%S')
            #print(order_info_list)

            response_data['orders'].extend(order_info_list)
            response_data['is_get_order'] = 'yes'
            response_data['order_num'] = len(order_info_list)
            
            return JsonResponse(response_data)

        else:
            return JsonResponse(response_data)

        
    else:
        return HttpResponse('bad request',status = 500)

"""
------获取用户发单信息------
------接收前端发送的账号，判断是不是GET请求，不是则返回bad request，若是则提取cookie中的用户邮箱和登录状态，
------若为已登录则读取订单信息然后把时间转化为字符串后返回给前端
前端请求方法：GET
数据类型：
    携带登录时获得的cookie
    url中的用户邮箱
api:127.0.0.1:8080/orders/breleaselist/用户邮箱/
后端返回值: 
{
    "is_login": "yes",
    "is_get_order": "yes",
    "order_num": 1,
    "orders": [
        {
            "order_token": "ya1618115656504322",
            "order_boss_email": "1193184604@qq.com",
            "order_worker_email": "",
            "order_start_time": "2021-04-11 12:34:16",
            "order_accept_time": "2021-04-11 12:34:16",
            "order_complet_time": "2021-04-11 12:34:16",
            "order_end_time": "2021-04-11 12:34:16",
            "order_status": 0,
            "order_is_worker_ask_complet": 0,
            "order_is_boss_agree_complet": 0,
            "order_is_boss_ask_refund": 0,
            "order_is_worker_agree_refund": 0,
            "order_refund_money": 0.0,
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_worker_earnest_money": 10.0,
            "order_boss_name": "xiaowen",
            "order_boss_phone_number": "13636784990",
            "order_boss_qq_wei": "yajie123321",
            "order_boss_require": "没有",
            "order_worker_name": "",
            "order_worker_phone_number": "",
            "order_worker_qq_wei": "",
            "order_is_evalute": 0
        }
    ]
}
"""
def get_release_order_info(request,usr_email):
    if request.method =='GET':
        is_login = request.COOKIES.get('is_login')
        order_boss_email = request.COOKIES.get('uemail')

        response_data = {
            'is_login':'no',
            'is_get_order':'no',
            'order_num':0,
            'orders':[]
        }

        if is_login and order_boss_email == usr_email:
            response_data['is_login'] = 'yes'

            tab_obj = '' #order_table 表中的订单信息
            tab_obj1 = '' #order_table1 表中的订单信息

            try:
                tab_obj = models.Table.objects.filter(order_boss_email=order_boss_email).order_by('-order_start_time').values() #value返回 字典键值对 list能把里面的字典提取出来成为字典列表
                tab_obj1 = models.Table1.objects.filter(order_boss_email=order_boss_email).order_by('-order_end_time').values() #value返回 字典键值对 list能把里面的字典提取出来成为字典列表
            except ObjectDoesNotExist:
                print('ger order error')
            order_info_list = list(tab_obj) #获取订单信息构成的字典列表
            order_info_list1 = list(tab_obj1) #获取订单信息构成的字典列表
            order_info_list.extend(order_info_list1) #两个表的订单表放入一个

            for order in order_info_list: #循环每一个字典， 把datetime 类型转化为字符串
                order['order_start_time'] = order['order_start_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_accept_time'] = order['order_accept_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_complet_time'] = order['order_complet_time'].strftime('%Y-%m-%d %H:%M:%S')
                order['order_end_time'] = order['order_end_time'].strftime('%Y-%m-%d %H:%M:%S')
            #print(order_info_list)

            response_data['orders'].extend(order_info_list)
            response_data['is_get_order'] = 'yes'
            response_data['order_num'] = len(order_info_list)
            return JsonResponse(response_data)

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)

"""
------获取待接单表------
------
前端请求方法：GET
数据类型：

api:127.0.0.1:8080/orders/ordertotake/年级/科目/   当没有过滤的时候 年级=no  科目=no 有过滤写相应的值
后端返回值: 
{
    "is_get": "yes",
    "order_num": 4,
    "orders": [
        {
            "order_token": "ya1618115656504322",
            "order_boss_email": "1193184604@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0
        },
        {
            "order_token": "ya1618122781310268",
            "order_boss_email": "909092921@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0
        },
        {
            "order_token": "ya1618122830075952",
            "order_boss_email": "909092921@qq.com",
            "order_teaching_grade": "三年级",
            "order_teaching_subjects": "语文",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0
        },
        {
            "order_token": "zh1618115903131801",
            "order_boss_email": "1193184604@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0
        }
    ]
}
""" 

def get_order_to_take(request,order_teaching_grade,order_teaching_subjects):
    if request.method =='GET':
        response_data = {
            'is_get':'no',
            'order_num':0,
            'orders':[],
        }
        
        #开始获取订单
        if order_teaching_grade == 'no':
            order_teaching_grade = ''
        if order_teaching_subjects == 'no':
            order_teaching_subjects = ''

        order_list=[]
        teaching_subjects_list = order_teaching_subjects.split(';')

        for subject in teaching_subjects_list: #获取每一个科目的订单
            order_listo = models.Table.objects.values( 
            'order_token',
            'order_boss_email',
            'order_teaching_grade',
            'order_teaching_subjects',
            'order_hourly_money',
            'order_teaching_time',
            'order_total_money',
            'order_boss_require',
            'order_worker_earnest_money',).filter(order_status=PAID,order_teaching_grade__contains=order_teaching_grade,order_teaching_subjects__contains=subject)   #value 返回包含对象具体值的字典的QuerySet 参数为限制哪些字段  模糊匹配
            order_list.extend(list(order_listo))

        response_data['is_get'] = 'yes'
        response_data['order_num'] = len(order_list)
        response_data['orders'].extend(order_list)
    
        return JsonResponse(response_data)
       
    else:
        return HttpResponse('bad request',status =500)



"""
------发送上课通知------
------

前端请求方法：POST
数据类型：form-data
    登录时获得的cookie
    老板邮箱 bemail
    邮件内容 umessage

api:127.0.0.1:8080/orders/sendclassreminder/
后端返回值: 
"""

def send_class_reminder(request):
    if request.method == 'POST':
        is_login = request.COOKIES.get('is_login') #获取登录状态
        order_worker_email = request.COOKIES.get('uemail') #获取员工邮箱
        order_boss_email = request.POST.get('bemail')  #获取老板邮箱
        message = request.POST.get('umessage')  #获取邮件内容

        response_data ={
            'is_login' : 'no',
            'is_send' : 'no',
        }

        if is_login and order_worker_email and order_boss_email:
            response_data ['is_login'] = 'yes'

            #给老板发送邮件信息
            subject = 'Edu 上课提醒'
            from_email = 'eudtocher@163.com'
            recept_email =[order_boss_email]  #接收可以有多个人

            try:
                send_mail(subject, message, from_email, recept_email)
                response_data['is_send'] = 'yes'
            except (BadHeaderError,SMTPDataError):
                print('send email falied')
            
            return JsonResponse(response_data)

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request', status = 500)