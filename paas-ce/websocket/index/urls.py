"""
Copyright © 2012-2020 OpsAny. All Rights Reserved. 河南我买云信息技术有限公司版权所有
""" # noqa
from django.urls import path
from index.views import *

urlpatterns = [
    path(r"", vue),
    path("swagger/", swagger_editor)
]