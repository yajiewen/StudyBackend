"""study URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),   #account 应用路由到account中的urls再次路由
    path('orders/', include('orders.urls')),    # 应用路由到orders中的urls再次路由
    path('evaluate/',include('evaluate.urls')), # 应用路由到evaluate中的urls再次路由
    path('classinfo/',include('classinfo.urls')), # 应用路由到classinfo中的urls再次路由
    path('verify/',include('verify.urls')),  #路由到verify中的urls再次路由
]
