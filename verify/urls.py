from django.urls import path
from .views import *

urlpatterns = [
    path('iverify/',identity_verify), #身份认证应用
    path('sverify/',student_verify), #学籍认证
]