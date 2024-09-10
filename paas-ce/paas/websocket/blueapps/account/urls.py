# -*- coding: utf-8 -*-
from django.conf.urls import url

from blueapps.account import views

app_name = 'account'

urlpatterns = [
    url(r'^healthz/$', views.healthz, name="healthz"),
]
