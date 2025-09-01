# -*- coding: utf-8 -*-
from django.urls import path
from django.urls import include


urlpatterns = [
    path('', include('blueapps.account.urls')),
]
