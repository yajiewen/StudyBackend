from django.shortcuts import render,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from advertize import models
from django.forms.models import model_to_dict
from account import models as amodels
from orders import models as omodels
import random
from functools import reduce
#全局画像字段名
Global_Name = 'global_map'
PAID = 1
#数据库字段对应字典
grade_dict = {
    '一年级':'pr_first_grade',
    '二年级':'pr_second_grade',
    '三年级':'pr_third_grade',
    '四年级':'pr_fourth_grade',
    '五年级':'pr_fifth_grade',
    '六年级':'pr_sixth_grade',
    '初一':'ju_first_grade',
    '初二':'ju_second_grade',
    '初三':'ju_third_grade',
    '高一':'hi_first_grade',
    '高二':'hi_second_grade',
    '高三':'hi_third_grade',
}
class_dict = {
    '语文':'chinese_class',
    '数学':'math_class',
    '英语':'english_class',
    '思想品德':'moral_class',
    '美术':'art_class',
    '科学':'science_class',
    '音乐':'music_class',
    '小学编程':'pr_programming_class',
    '历史':'history_class',
    '地理':'geography_class',
    '生物':'biology_class',
    '物理':'physics_class',
    '化学':'chemistry_class',
    '信息技术':'information_tech_class',
    '政治':'politics_class',
}

map_pattern ={
    '语文':'chinese_class',
    '数学':'math_class',
    '英语':'english_class',
    '思想品德':'moral_class',
    '美术':'art_class',
    '科学':'science_class',
    '音乐':'music_class',
    '小学编程':'pr_programming_class',
    '历史':'history_class',
    '地理':'geography_class',
    '生物':'biology_class',
    '物理':'physics_class',
    '化学':'chemistry_class',
    '信息技术':'information_tech_class',
    '政治':'politics_class',
    '一年级':'pr_first_grade',
    '二年级':'pr_second_grade',
    '三年级':'pr_third_grade',
    '四年级':'pr_fourth_grade',
    '五年级':'pr_fifth_grade',
    '六年级':'pr_sixth_grade',
    '初一':'ju_first_grade',
    '初二':'ju_second_grade',
    '初三':'ju_third_grade',
    '高一':'hi_first_grade',
    '高二':'hi_second_grade',
    '高三':'hi_third_grade',
}

Weight_value = 100
# Create your views here.

"""
------纪录用户查看的订单------
方法:post
数据类型 form-data
参数:
   uemail 用户邮箱
   grade 执教年级
   subjects 科目信息(以;为分界,最后一个后面没有;)
   takeorder (yes no)
api: https://127.0.0.1:8081/advertize/upmaps/
后端返回值:
{
    "is_ok": "yes"
}

"""
def get_two_maps(request):
    if request.method == 'POST':
        usr_email = request.POST.get('uemail') #获取用户邮箱
        subject_list = request.POST.get('subjects') #获取课程名称
        tgrade = request.POST.get('grade') #获取执教年级
        is_takeorder = request.POST.get('takeorder') #获取是否是接单按钮的传送
        increase_num = 1
        if is_takeorder == 'yes': #是接单动作则权重增加50
            increase_num = 50

        response_data = {
            'is_ok':'no'
        }
        #邮箱和科目不空开始
        if usr_email and subject_list and tgrade:
            subject_list = subject_list.split(';')
            print(subject_list)
            #获取用户画像和世界画像
            user_map = '' #用户画像
            user_world_map = '' #世界画像
            
            #用户画像不存在则创建用户画像
            if not models.Table_user.objects.filter(usr_email = usr_email).exists():
                models.Table_user.objects.create(usr_email = usr_email)
                print('created usr map')
            else:
                user_map = models.Table_user.objects.filter(usr_email=usr_email)
            #获取世界画像
            #世界画像不存在则创建世界画像
            if not models.Table_user_world.objects.filter(map_name = Global_Name).exists():
                models.Table_user_world.objects.create(map_name = Global_Name)
                print('create world map')
            else:
                user_world_map = models.Table_user_world.objects.filter(map_name =Global_Name)

            #获取画像字典
            user_map_dict = user_map.values()[0]
            user_world_map_dict = user_world_map.values()[0]

            #更新用户画像执教年级内容
            models.Table_user.objects.filter(usr_email = usr_email).update(
                **{ grade_dict[tgrade]:user_map_dict[grade_dict[tgrade]] + increase_num }
            )
            #更新世界画像执教年级内容
            models.Table_user_world.objects.filter(map_name =Global_Name).update(
                **{ grade_dict[tgrade]:user_world_map_dict[grade_dict[tgrade]] + increase_num }
            )

            #更新用户画像和世界画像的执教科目
            for subject in subject_list:
                user_map.update(
                    **{ class_dict[subject]: user_map_dict[class_dict[subject]] +increase_num }
                )
                user_world_map.update(
                    **{ class_dict[subject]:user_world_map_dict[class_dict[subject]] + increase_num}
                )
            response_data['is_ok'] = 'yes'

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)


"""
------获取推荐列表-----
方法:get
数据类型 
参数:
    cookies
api: https://127.0.0.1:8081/advertize/adverlist/

"""
def get_adver_list(request):
    if request.method == 'GET':
        usr_email = request.COOKIES.get('uemail')
        is_login = request.COOKIES.get('is_login')
        response_data = {
            'is_login':'no',
            'is_get':'no',
            'order_num':0,
            'orders':[],
        }

        if usr_email and is_login: #判断用户名和登录状态
            response_data['is_login'] = 'yes'
            #获取用户画像
            usr_obj = ''
            try:
                usr_obj = models.Table_user.objects.get(usr_email = usr_email)
            except ObjectDoesNotExist:
                models.Table_user.objects.create(usr_email = usr_email)
                print('created usr map')
                usr_obj = models.Table_user.objects.get(usr_email = usr_email)
            usr_map_dict = model_to_dict(usr_obj)
            #获取用户信息用于添加执教年级科目权重
            usr_info = amodels.Table.objects.get(usr_email = usr_email) 
            #创建用户画像表示
            usr_map = {} #用户画像
            for keyvalue in map_pattern.keys():
                usr_map[keyvalue] = usr_map_dict[map_pattern[keyvalue]] 
                #增加用户信息里面的权重
                if keyvalue in usr_info.usr_teaching_subjects or keyvalue in usr_info.usr_teaching_grade: #若个人信息里面有相应的学科或执教年级则给对应的执教学科和年级加上权重
                    usr_map[keyvalue] += Weight_value 

            #获取用户所属的群的画像

            #获取世界画像
            world_obj = ''
            try:
                world_obj = models.Table_user_world.objects.get(map_name = Global_Name)
            except ObjectDoesNotExist:
                models.Table_user_world.objects.create(map_name = Global_Name)
                print('create world map')
                world_obj = models.Table_user_world.objects.get(map_name = Global_Name)
            world_map_dict = model_to_dict(world_obj)
            #创建世界画像表示
            world_map = {} #世界画像
            for keyvalue in map_pattern.keys():
                world_map[keyvalue] = world_map_dict[map_pattern[keyvalue]]

            #print('用户画像')
            #print(usr_map)
            #print('世界画像')
            #print(world_map)

            #用户画像推荐列表-------------------------------------------------
            usr_map = sorted(usr_map.items(), key=lambda x:x[1], reverse=True) #对画像字典排序
            print(usr_map)
            uorderlist = []
            uinterest_grades = [] #最感兴趣的年级
            uinterest_classes = [] #最感兴趣的科目
            ugrade_num = 3 #最感兴趣的几个年级
            uclass_num = 2 #最感兴趣的几个科目
            uorder_num = 100 #最大推荐订单数

            for keyvalue,weightvalue in usr_map: #遍历排序后的字典(元祖列表)
                if keyvalue in grade_dict.keys() and len(uinterest_grades) < ugrade_num : #keyvalue 是年级信息并且感兴趣的年级的列表中元素少于grade_num 则向感兴趣的年级列表中添加年级
                    uinterest_grades.append(keyvalue)
                if keyvalue in class_dict.keys() and len(uinterest_classes) < uclass_num: 
                    uinterest_classes.append(keyvalue)

            print(uinterest_grades)
            print(uinterest_classes)

            for grade in uinterest_grades:
                for subject in uinterest_classes:
                    order_list = omodels.Table.objects.filter(order_status=PAID,order_teaching_grade__contains = grade,order_teaching_subjects__contains = subject).order_by('order_start_time').values(
                        'order_token',
                        'order_start_time',
                        'order_boss_email',
                        'order_teaching_grade',
                        'order_teaching_subjects',
                        'order_hourly_money',
                        'order_teaching_time',
                        'order_total_money',
                        'order_boss_require',
                        'order_worker_earnest_money',
                    ) #按照时间由远到近
                    uorderlist.extend(list(order_list))
                    #限制推荐数量(暂未开放该功能)
            for dictv in uorderlist:
                dictv['order_start_time'] = dictv['order_start_time'].strftime('%Y-%m-%d %H:%M:%S') #把datatime转化为字符串
            print(uorderlist)

            #用户群画像推荐列表-------------------------------------------------
            orderlist2 = []
            ginterest_grades = []
            ginterest_classes = []

            #世界画像推荐列表-------------------------------------------------
            world_map = sorted(world_map.items(), key=lambda x:x[1], reverse=True) #对画像字典排序
            print(world_map)
            worderlist = []
            winterest_grades = [] #最感兴趣的年级
            winterest_classes = [] #最感兴趣的科目
            wgrade_num = 2 #最感兴趣的几个年级
            wclass_num = 2 #最感兴趣的几个科目
            worder_num = 10 #最大推荐订单数

            for keyvalue,weightvalue in world_map: #遍历排序后的字典(元祖列表)
                if keyvalue in grade_dict.keys() and len(winterest_grades) < wgrade_num : #keyvalue 是年级信息并且感兴趣的年级的列表中元素少于grade_num 则向感兴趣的年级列表中添加年级
                    winterest_grades.append(keyvalue)
                if keyvalue in class_dict.keys() and len(winterest_classes) < wclass_num: 
                    winterest_classes.append(keyvalue)
            
            print(winterest_grades)
            print(winterest_classes)

            for grade in winterest_grades:
                for subject in winterest_classes:
                    order_list = omodels.Table.objects.filter(order_status=PAID,order_teaching_grade__contains = grade,order_teaching_subjects__contains = subject).order_by('order_start_time').values(
                        'order_token',
                        'order_start_time',
                        'order_boss_email',
                        'order_teaching_grade',
                        'order_teaching_subjects',
                        'order_hourly_money',
                        'order_teaching_time',
                        'order_total_money',
                        'order_boss_require',
                        'order_worker_earnest_money',
                    )#按照时间由远到近
                    worderlist.extend(list(order_list))
            #限制推荐数量(开放该功能)
            if len(worderlist) >=worder_num:
                worderlist = worderlist[:worder_num] #订单数量大于限制则切片
            
            for dictv in worderlist:
                dictv['order_start_time'] = dictv['order_start_time'].strftime('%Y-%m-%d %H:%M:%S') #把datatime转化为字符串
            print(worderlist)

            #生成返回数据(不可以是自己发的订单,返回的订单中订单号不可以重复)-------------------------------------------------
            raw_order_list = []
            raw_order_list1 = []
            raw_order_list.extend(uorderlist)
            raw_order_list.extend(worderlist)
            #过滤自己发的订单
            for orderinfo in raw_order_list:
                if orderinfo['order_boss_email'] != usr_email:
                    raw_order_list1.append(orderinfo)
            
            #过滤同一个订单
            order_token_list = []
            for orderinfo in raw_order_list1:
                if orderinfo['order_token'] not in order_token_list:
                    order_token_list.append(orderinfo['order_token'])
                    response_data['orders'].append(orderinfo)

            response_data['order_num'] = len(response_data['orders'])
            response_data['is_get'] = 'yes'
            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)    
    else:
        return HttpResponse('bad request',status = 500)