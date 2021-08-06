from django.urls import path
from .views import *

urlpatterns = [
    path('login/',admin_login),
    path('badaccountlist/',admin_get_bad_accounts),
    path('deljunkmail/',admin_del_account),
    path('ilist/',admin_get_identity_list),
    path('slist/',admin_get_student_list),
    path('iverify/',admin_verify_identity),
    path('sverify/',admin_verify_student),
    path('orderstocomplete/',get_orders_to_complete),
    path('completeorders/',complete_orders),
    path('stageusrinfo/',get_stage_usrinfo),
    path('dealorder/',dear_order),
    path('getorderinfo/',get_order_info),
]