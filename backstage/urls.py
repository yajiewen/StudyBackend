from django.urls import path
from .views import *

urlpatterns = [
    path('login/',admin_login),
    path('badaccountlist/',admin_get_bad_accounts),
    path('deljunkmail/',admin_del_account),
]