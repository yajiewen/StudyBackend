from django.shortcuts import render,HttpResponse
from django.http import JsonResponse


# Create your views here.

"""
------获取小学年级,课程信息
api : 127.0.0.1:8080/classinfo/primaryschool/
请求方法 GET
数据类型 无
数据内容无
后端返回内容:
{
    "grades": [
        "一年级",
        "二年级",
        "三年级",
        "四年级",
        "五年级",
        "六年级"
    ],
    "classes": [
        "语文",
        "数学",
        "英语",
        "思想品德",
        "美术",
        "科学",
        "音乐",
        "小学编程"
    ]
}
"""
def get_primary_school_info(request):
    if request.method == 'GET':
        #设置小学信息
        response_data = {
            'grades': ['一年级','二年级','三年级','四年级','五年级','六年级'],
            'classes': ['语文','数学','英语','思想品德','美术','科学','音乐','小学编程',],
        }
        return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)

"""
------获取初中年级,课程信息
api : 127.0.0.1:8080/classinfo/juniorschool/
请求方法 GET
数据类型 无
数据内容无
后端返回内容:
{
    "grades": [
        "初一",
        "初二",
        "初三"
    ],
    "classes": [
        "语文",
        "数学",
        "英语",
        "历史",
        "地理",
        "生物",
        "思想品德",
        "音乐",
        "美术",
        "信息技术",
        "物理",
        "化学"
    ]
}
"""
def get_junior_school_info(request):
    if request.method == 'GET':
        #设置初中信息
        response_data = {
            'grades': ['初一','初二','初三'],
            'classes': ['语文','数学','英语','历史','地理','生物','思想品德','音乐','美术','信息技术','物理','化学']
        }

        return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status=500)

"""
------获取高中年级,课程信息
api : 127.0.0.1:8080/classinfo/highschool/
请求方法 GET
数据类型 无
数据内容无
后端返回内容:
{
    "grades": [
        "高一",
        "高二",
        "高三"
    ],
    "classes": [
        "语文",
        "数学",
        "英语",
        "物理",
        "化学",
        "生物",
        "地理",
        "历史",
        "政治"
    ]
}
}
"""

def get_high_school_info(request):
    if request.method == 'GET':
        #设置初中信息
        response_data = {
            'grades': ['高一','高二','高三'],
            'classes': ['语文','数学','英语','物理','化学','生物','地理','历史','政治']
        }

        return JsonResponse(response_data)
    else:
        return HttpResponse('Bad request',status=500)