# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
"""  # noqa

import requests
import json

import settings
try:
    from config import APP_CODE, SECRET_KEY, BK_URL, DEFAULT_LANGUAGE
    from bastion.utils.constants import IP_PATTERN, PRIVATE_IP_PATTERN
except Exception as e:
    raise Exception("导包错误：", str(e))


class EsbApi(object):
    def __init__(self, token=None, language=DEFAULT_LANGUAGE):
        self.token = token if token else ""
        self.app_code = APP_CODE
        self.app_secret = SECRET_KEY
        self.url = BK_URL
        self.headers = {
            "Cookie": "bk_token={}; opsany_language={}".format(self.token, language)
        }

    def get_user_info(self):
        API = "/api/c/compapi/v2/bk_login/get_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_token": self.token
        }
        URL = self.url + API
        response = requests.get(url=URL, params=req, headers=self.headers, verify=False)
        end_data = json.loads(response.text)
        dt = {}
        if end_data.get("result"):
            dt["phone"] = end_data.get("data").get("phone")
            dt["username"] = end_data.get("data").get("bk_username")
            dt["email"] = end_data.get("data").get("email")
            dt["ch_name"] = end_data.get("data").get("chname")
            dt["role"] = end_data.get("data").get("bk_role")
        return dt
