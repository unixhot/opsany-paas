# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import include


urlpatterns = [
    url(r'^', include('blueapps.account.urls')),
]
