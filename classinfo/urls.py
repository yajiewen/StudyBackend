from django.urls import path
from .views import *

urlpatterns = [
        path('primaryschool/',get_primary_school_info), #获取小学年级,课表信息
        path('juniorschool/',get_junior_school_info), #获取初中年级,课表信息
        path('highschool/',get_high_school_info), #获取高中年级,课表信息
]