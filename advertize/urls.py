from django.urls import path
from .views import *

urlpatterns = [
    path('upmaps/',get_two_maps)
]