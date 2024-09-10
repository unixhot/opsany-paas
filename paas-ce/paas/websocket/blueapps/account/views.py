# -*- coding: utf-8 -*-
import datetime
from django.http import JsonResponse, HttpResponse
from django_redis import get_redis_connection
from bastion.models import UserInfo
from blueapps.account.decorators import login_exempt


@login_exempt
def healthz(request):
    code, status, message = 1, "OK", ""
    dic = {"check_mysql": True, "check_redis": True, "check_superuser": True}
    try:
        client = get_redis_connection()  # redis校验
        access_token = client.get("OpsAny")
    except Exception as e:
        dic["check_redis"] = False
        code, status = 0, "ERROR"
        message += "Redis初始化失败 "

    if not UserInfo.objects.filter(username="admin"):  # 校验超级管理员初始化
        dic["check_superuser"] = False
        code, status = 0, "ERROR"
        message += "超级管理员初始化失败 "
    if not message:
        message = "Success"
    if code == 1:
        data = {"code": code, "status": status, "message": message, "time": str(datetime.datetime.now()), "details": dic}
        return JsonResponse(data)
    else:
        data = message
        return HttpResponse(content=data, status=500)
