# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
"""  # noqa

import requests
import json
import logging

import settings
try:
    from config import APP_CODE, SECRET_KEY, BK_URL, DEFAULT_LANGUAGE
    from bastion.utils.constants import IP_PATTERN, PRIVATE_IP_PATTERN
except Exception as e:
    raise Exception("导包错误：", str(e))

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app_logging = logging.getLogger("app")


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
        try:
            # 添加超时防止请求一直挂起（原代码无 timeout 可能导致 ASGI worker 线程阻塞）
            response = requests.get(url=URL, params=req, headers=self.headers, verify=False, timeout=10)
        except requests.Timeout:
            app_logging.error("[ESB] get_user_info timeout for token: %s", str(self.token)[:8])
            return {}
        except requests.RequestException as e:
            app_logging.error("[ESB] get_user_info request failed: %s", e)
            return {}
        end_data = json.loads(response.text)
        dt = {}
        if end_data.get("result"):
            dt["phone"] = end_data.get("data").get("phone")
            dt["username"] = end_data.get("data").get("bk_username")
            dt["email"] = end_data.get("data").get("email")
            dt["ch_name"] = end_data.get("data").get("chname")
            dt["role"] = end_data.get("data").get("bk_role")
        return dt
