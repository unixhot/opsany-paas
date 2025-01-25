#! /usr/bin/python3
# -*- coding: utf8 -*-
"""_summary_

Returns:
    _notion_: 执行前需要确认stackstorm是否部署成功。否则执行失败。

"""

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class StackStormApi:
    def __init__(self, st2_url, st2_username, st2_password, timeout=8):
        self.url = st2_url
        self.username = st2_username
        self.password = st2_password
        self.timeout = timeout
        self.AUTH_TOKENS = "/auth/tokens/"  # 登录 POST
        self.API_KEYS = "/api/v1/apikeys/"  # api key list GET POST

        self.headers = {"accept": "application/json"}

    def get_token(self):
        """Login and get token"""
        try:
            req = requests.session()
            req.auth = (self.username, self.password)
            url = self.url + self.AUTH_TOKENS
            headers = {
                "accept": "application/json"
            }
            res = req.post(url, headers=headers, timeout=self.timeout, verify=False)
            if res.status_code in [200, 201]:
                return True, res.json().get("token")

            else:
                return False, res.json()
        except Exception as e:
            return False, e

    def update_headers(self):
        """update headers token"""
        status, message = self.get_token()
        if not status:
            return self.headers
        return self.headers.update({"x-auth-token": message})

    def create_api_key(self, metadata=None, enabled=True, user="st2admin"):
        """create api key"""
        try:
            url = self.url + self.API_KEYS
            # {"name": "OpsAny-Devops", "used_by": "OpsAny-Devops", "why": "OpsAny Devops StackStorm Service Login header (st2-api-key) Can Not Delete."}
            # api_key = res_dict.get("key", "")
            data_dic = {
                "metadata": metadata if metadata else {},
                "enabled": enabled if enabled else True,
                "user": user
            }
            data_dic = json.dumps(data_dic)
            self.update_headers()
            res = requests.post(url, headers=self.headers, timeout=self.timeout, data=data_dic, verify=False)
            res.encoding = "utf-8"
            if res.status_code == 201:
                return True, res.json()
            else:
                return False, res.json()

        except Exception as e:
            print("create_api_key_error", str(e))
            return False, e


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, st2_url, st2_username, st2_password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({"referer": paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.st2_url = st2_url
        self.st2_api = StackStormApi(st2_url, st2_username, st2_password)
        self.token = self.login()

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code in [200, 400]:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except Exception:
            return ""

    def login(self):
        try:
            login_form = {
                "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
                "username": self.username,
                "password": self.password
            }
            resp = self.session.post(self.login_url, data=login_form, verify=False)
            if resp.status_code == 200:
                return self.session.cookies.get("bk_token")
            return ""
        except Exception:
            return False

    def init_control_st2(self):
        """init devops st2 server"""
        try:
            CONTROL_API = "/o/control//api/control/v0_1/stackstorm/"
            CONTRO_URL = self.paas_domain + CONTROL_API
            metadata = {"name": "OpsAny-Control", "used_by": "OpsAny-Control",
                        "why": "OpsAny Control StackStorm Service Login header (st2-api-key) Can Not Delete."}
            status, api_token = self.st2_api.create_api_key(metadata=metadata, enabled=True)
            # status, api_token = True, {"key": "NzliYTgyMzdlNjM0MjcyYTBiMzY4OWMwMDM2ODdhYTExMDc5MTI3ZmJmMDMzYmQzZjQ4YjRhZTgxYzhlY2YzYg1"}
            if not status:
                return False, api_token
            data = {
                "url": self.st2_url,
                "api_key": api_token.get("key", ""),
            }
            response = self.session.put(url=CONTRO_URL, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                return True, response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return True, res.get("data") or res.get("message")
            else:
                return False, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return False, str(e)


def start(paas_domain, username, password, st2_url, st2_username, st2_password):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password, st2_url=st2_url,
                        st2_username=st2_username, st2_password=st2_password)

    # 1. 初始化应用平台初始化StackStorm服务
    st2_status, st2_message = run_obj.init_control_st2()
    print("[SUCCESS] init devops st2 success.") if st2_status else print(
        "[ERROR] init devops st2 error, error info: {}".format(str(st2_message)))


def add_parameter():
    parameter = argparse.ArgumentParser("init_ce_st2")
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--st2_url", help="StackStorm service url.", required=True)
    parameter.add_argument("--st2_username", help="StackStorm service username.", required=True)
    parameter.add_argument("--st2_password", help="StackStorm service password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain  # 域名
    username = options.username  # 平台用户名
    password = options.password  # s平台密码
    st2_url = options.st2_url  # st2地址
    st2_username = options.st2_username  # st2用户名
    st2_password = options.st2_password  # st2密码
    start(f"https://{domain}", username, password, st2_url=st2_url, st2_username=st2_username, st2_password=st2_password)

"""
1. 部署完应用平台和StackStorm才可以执行此初始化脚本
2. 执行init-ce-st2.py脚本，参数为OpsAny地址用户名密码，St2地址用户名密码

python3 init-ce-st2.py --domain 192.168.56.11 --username admin --password password  --st2_url  http://192.168.56.11:8005 --st2_username st2admin  --st2_password st2_password
"""
