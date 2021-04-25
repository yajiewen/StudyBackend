from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from orders import models as omodels
from account import models as amodels
from evaluate import models

COMPLETE = 3 #订单已完成

##########################订单评价状态##############
EVALUATED = 1 #订单已经评价
NOT_EVALUATE = 0 #订单未评价
# Create your views here.
#获取需要评价的订单列表

"""
-----获取待评价的订单列表------ 
-----判断请求是不是GET请求，若是get请求则判断是否已经登录，若已经登录则查找该用户发的单子中状态为完成并且未评价的订单
-----然后返回订单信息
前端请求方法：GET
请求中的cookie
数据类型：无
api:127.0.0.1:8080/evaluate/evaluatelist/
后端返回值:
{
    "is_login": "yes",
    "is_get_evaluate_list": "yes",
    "order_num": 5,
    "orders": [
        {
            "order_token": "ya1618043585467574",
            "order_worker_email": "1193184604@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_status": 3,
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062625332581",
            "order_worker_email": "2447255540@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_status": 3,
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062626354889",
            "order_worker_email": "2447255540@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_status": 3,
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618062627130826",
            "order_worker_email": "2447255540@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_status": 3,
            "order_is_evalute": 0
        },
        {
            "order_token": "ya1618122781310268",
            "order_worker_email": "1193184604@qq.com",
            "order_teaching_grade": "一年级",
            "order_teaching_subjects": "数学",
            "order_hourly_money": 100.0,
            "order_teaching_time": 3,
            "order_total_money": 300.0,
            "order_status": 3,
            "order_is_evalute": 0
        }
    ]
}

"""

def get_evaluate_list(request):
    if request.method == 'GET':
        is_login = request.COOKIES.get('is_login')
        order_boss_email = request.COOKIES.get('uemail')

        response_data = {
            'is_login':'no',
            'is_get_evaluate_list':'no',
            'order_num':0,
            'orders':[],
        }

        order_list =''
        if is_login and order_boss_email:
            response_data['is_login'] = 'yes'

            #开始获取状态为已完成的订单列表
            order_list = omodels.Table1.objects.filter(order_boss_email= order_boss_email, order_status = COMPLETE,order_is_evalute =NOT_EVALUATE).values(
                'order_token',
                'order_worker_email',
                'order_teaching_grade',
                'order_teaching_subjects',
                'order_hourly_money',
                'order_teaching_time',
                'order_total_money',
                'order_status',
                'order_is_evalute',
            )
            order_list = list(order_list)

            response_data['is_get_evaluate_list'] = 'yes'
            response_data['orders'].extend(order_list)
            response_data['order_num'] = len(order_list)

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
        
    else:
        return HttpResponse('bad request',status = 500)

"""
-----老板对接单者评价------ 
-----判断请求是不是POST请求，若是POST请求则判断是否已经登录，若已经登录则查找相应订单，查找到则向评价表中添加评价，同时更新订单的评价状态
-----否则返回相应信息
前端请求方法：POST
请求中的cookie
数据类型：form-data (下面字段不可以为空)
    订单号 otoken
    被评价者邮箱 worker_email
    评价内容 content
    评分 score
api:127.0.0.1:8080/evaluate/evaluateworker/
后端返回值:
{
    "is_login": "yes",
    "evalu_success": "yes",
    "is_evaluated": "no",
    "order_exist": "yes"
}
"""
def evaluate_worker(request):
    if request.method == 'POST':
        #获取登录状态和boss邮箱
        is_login = request.COOKIES.get('is_login')
        order_boss_email = request.COOKIES.get('uemail')
        #获取订单号
        order_token = request.POST.get('otoken')
        #获取员工邮箱
        order_worker_email = request.POST.get('worker_email')
        #获取评价内容
        evaluate_content = request.POST.get('content')
        #获取评分
        evaluate_score = request.POST.get('score')

        response_data = {
            'is_login':'no',
            'evalu_success':'no',
            'is_evaluated':'no',
            'order_exist':'no'
        }

        if is_login and order_boss_email:
            response_data['is_login'] = 'yes'
            #判断订单匹配订单相应信息，看是否有符合要求的订单
            if omodels.Table1.objects.filter(
                order_boss_email= order_boss_email,
                order_worker_email= order_worker_email,
                order_token= order_token,
                order_is_evalute=NOT_EVALUATE).exists():

                response_data['order_exist'] = 'yes'
                #获取老板昵称
                evaluate_usr_name = amodels.Table.objects.get(usr_email= order_boss_email).usr_name
                #对老板昵称加密（昵称最后三个显示未*）
                last_three = list(evaluate_usr_name)
                last_three = last_three[-3:]
                last_three = ''.join(last_three)
                print(last_three)
                evaluate_usr_name = evaluate_usr_name.replace(last_three, '***')

                #向评价表添加评价信息
                models.Table.objects.create(
                    order_token= order_token,
                    evaluated_usr_email= order_worker_email,
                    evaluate_usr_name= evaluate_usr_name,
                    evaluate_content= evaluate_content,
                    evaluate_score= evaluate_score)

                #跟新订单信息为已经评价
                omodels.Table1.objects.filter(
                    order_boss_email= order_boss_email,
                    order_token= order_token,
                    order_is_evalute=NOT_EVALUATE).update(order_is_evalute= EVALUATED)

                response_data['evalu_success'] = 'yes'

                return JsonResponse(response_data)

            else:
                #订单评价过不再评价
                response_data['is_evaluated'] = 'yes'
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)

    else:
        return HttpResponse('Bad request',status = 500)

"""
-----查看员工评价信息------ 
-----判断请求是不是GET请求，若是GET请求则判断是否已经登录，若已经登录则获取老师的评价表返回
前端请求方法：GET
请求中的cookie
数据类型：无
url中的员工邮箱

api:127.0.0.1:8080/evaluate/evaluatecontent/员工邮箱/
后端返回值:
{
    "is_login": "yes",
    "is_get_success": "yes",
    "content_num": 5,
    "evalu_content": [
        {
            "evaluate_usr_name": "yajie",
            "evaluate_content": "讲的非常好",
            "evaluate_score": 5
        },
        {
            "evaluate_usr_name": "yajie",
            "evaluate_content": "讲的非常好",
            "evaluate_score": 5
        },
        {
            "evaluate_usr_name": "yajie",
            "evaluate_content": "讲的非常好",
            "evaluate_score": 5
        },
        {
            "evaluate_usr_name": "ya***",
            "evaluate_content": "讲的非常好",
            "evaluate_score": 5
        },
        {
            "evaluate_usr_name": "ya***",
            "evaluate_content": "讲的非常好",
            "evaluate_score": 5
        }
    ]
}
"""

def get_evaluate_content(request,evaluated_usr_email):
    if request.method == 'GET':
        is_login = request.COOKIES.get('is_login')

        response_data = {
            'is_login':'no',
            'is_get_success':'no',
            'content_num':0,
            'evalu_content':[],
        }

        if is_login:
            response_data['is_login'] = 'yes'

            evalu_content = models.Table.objects.filter(evaluated_usr_email= evaluated_usr_email).values(
                'evaluate_usr_name',
                'evaluate_content',
                'evaluate_score',
            )
            response_data['is_get_success'] = 'yes'

            evalu_content = list(evalu_content)
            response_data['content_num'] = len(evalu_content)
            response_data['evalu_content'].extend(evalu_content)
            
            return JsonResponse(response_data)

        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status = 500)