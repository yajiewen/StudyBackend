from django.shortcuts import render,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from advertize import models
#全局画像字段名
Global_Name = 'global_map'
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
# Create your views here.

"""
------纪录用户查看的订单------
方法:post
数据类型 form-data
参数:
   uemail 用户邮箱
   grade 执教年级
   subjects 科目信息(以;为分界,最后一个后面没有;)
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
            user_map = models.Table_user.objects.filter(usr_email=usr_email)
            #获取世界画像
            #世界画像不存在则创建世界画像
            if not models.Table_user_world.objects.filter(map_name = Global_Name).exists():
                models.Table_user_world.objects.create(map_name = Global_Name)
                print('create world map')
            user_world_map = models.Table_user_world.objects.filter(map_name =Global_Name)

            #获取画像字典
            user_map_dict = user_map.values()[0]
            user_world_map_dict = user_world_map.values()[0]

            #更新用户画像执教年级内容
            models.Table_user.objects.filter(usr_email = usr_email).update(
                **{ grade_dict[tgrade]:user_map_dict[grade_dict[tgrade]] + 1 }
            )
            #更新世界画像执教年级内容
            models.Table_user_world.objects.filter(map_name =Global_Name).update(
                **{ grade_dict[tgrade]:user_world_map_dict[grade_dict[tgrade]] + 1 }
            )

            #更新用户画像和世界画像的执教科目
            for subject in subject_list:
                user_map.update(
                    **{ class_dict[subject]: user_map_dict[class_dict[subject]] +1 }
                )
                user_world_map.update(
                    **{ class_dict[subject]:user_world_map_dict[class_dict[subject]] + 1}
                )
            response_data['is_ok'] = 'yes'

            return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)

