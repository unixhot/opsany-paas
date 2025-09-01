# -*- coding: utf-8 -*-
from django.urls import path

from blueapps.account import views

app_name = 'account'

urlpatterns = [
    path('healthz/', views.healthz, name="healthz"),
]
