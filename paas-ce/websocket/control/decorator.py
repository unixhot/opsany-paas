# -*- coding: utf-8 -*-
import requests
import json
import datetime
from django.db import transaction
from .models import UserInfo
from config import APP_CODE, BK_URL, SECRET_KEY


def user_sync(func):
    def wrapped_function(obj, request, **kwargs):
        print("request", request.COOKIES)
        all_user_list = get_all_users(request)

        """
        phone username email ch_name role
        """
        temp_user_list = []
        for each_user in all_user_list:

            used_field = {}
            used_field["phone"] = each_user.get("phone")
            used_field["username"] = each_user.get("bk_username")
            used_field["email"] = each_user.get("email")
            used_field["ch_name"] = each_user.get("chname")
            used_field["role"] = each_user.get("bk_role")

            if not UserInfo.objects.filter(username=each_user["bk_username"]).count():
                UserInfo.objects.create(**used_field)
            else:
                obj_user = UserInfo.objects.select_for_update().filter(username=each_user["bk_username"])
                with transaction.atomic():
                    obj_user.update(**used_field)
            temp_user_list.append(used_field["username"])

        local_all_users = UserInfo.objects.all()
        # print("local_all_users", local_all_users)
        deleted_user_list = []
        for each in local_all_users:
            if each.username not in temp_user_list:
                deleted_user_list.append(each.username)
        UserInfo.objects.filter(username__in=deleted_user_list).delete()
        return func(obj, request, **kwargs)
            
    return wrapped_function


def get_all_users(request):
    host = BK_URL
    bk_token = request.COOKIES.get('bk_token')
    # self.bk_token = "9lDBNOxzXjqJ5BH3QpfxcA2HG7eAjfDkmVivxaHtWpA"
    headers = {"Accept":"application/json"}
    params = {
        "bk_app_code": APP_CODE,
        "bk_app_secret": SECRET_KEY,
        "bk_token": bk_token,
    }
    print("bk_token", params, bk_token, host)
    url = "/api/c/compapi/v2/bk_login/get_all_users/"
    res = requests.get(host + url, params=params, headers=headers, verify=False)
    user_list = json.loads(res.content)["data"]
    return user_list