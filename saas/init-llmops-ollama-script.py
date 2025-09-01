#!/usr/bin/env python3
# coding:utf8
import json

import requests
import sys
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InitData:
    # 导航分组
    NAV_GROUP_LIST = [
        {
            "group_name": "平台管理",
            "group_code": "platform_manager",
            "group_language": {
                "chinese_simplified": "平台管理",
                "chinese_traditional": "平台管理",
                "english": "Platform Management"
            },
            "nav_list": [
                {
                    "nav_name": "大模型开发平台",
                    "nav_code": "llmops",
                    "nav_url": "/o/llmops/",
                    "icon_name": "llmops.png",
                    "icon_url": "uploads/workbench/icon/llmops.png",
                    "describe": "大模型开发平台",
                    "group_name": "平台管理",
                    "nav_language": {
                        "chinese_simplified": "大模型开发平台",
                        "chinese_traditional": "大模型開發平台",
                        "english": "LLMOPS"
                    },
                    "nav_describe_language": {
                        "chinese_simplified": "大模型开发平台",
                        "chinese_traditional": "大模型開發平台",
                        "english": "Large Model Development Platform"
                    }
                }
            ]
        }
    ]


class OpsAnyApi:
    def __init__(self, paas_domain, username, password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()

    def get_csrftoken(self):  # sourcery skip: do-not-use-bare-except
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code in [200, 400]:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):  # sourcery skip: do-not-use-bare-except
        try:
            login_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(self.login_url, data=login_form, verify=False)
            if resp.status_code == 200:
                return self.session.cookies.get("bk_token")
            return ""
        except:
            return False

    def update_or_create_ollama(self, api):
        API = self.paas_domain + "/o/llmops/api/llmops/v0_1/model-provider-init/"
        # API = self.paas_domain + "/api/llmops/v0_1/model-provider-init/"
        unique = "mp-built-in-ollama-1"
        name = "内置Ollama集成"
        create_dict = {"unique": unique, "provider_type": "ollama", "name": name, "api": api, "description": "内置Ollama集成"}
        try:
            res = self.session.post(API, json=create_dict, verify=False)
            try:
                res_json = res.json()
                message = res_json.get("message")
            except Exception:
                return False, res.content.decode()
            if res.status_code == 200 and res_json.get("code") == 200:
                return True, "{}({}), {}".format(name, unique, message)
            return False, message
        except Exception as e:
            return False, str(e)

    def workbench_add_nav(self, nav_group_list):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav-v2/"
            # NAV_API = "/api/workbench/v0_1/update-nav-v2/"
            NAV_GROUP_URL = self.paas_domain + NAV_API
            for nav_group in nav_group_list:
                nav_group.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps({"group_list": nav_group_list}), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)


def run(options):
    api_object = OpsAnyApi(options.domain, options.paas_username, options.paas_password)
    add_type = options.add_type
    if not add_type:
        add_type = "nav"
    if add_type in ["ollama", "all"]:
        status, message = api_object.update_or_create_ollama(options.ollama_api)
        print("初始化Oloama集成{}: {}".format("成功" if status else "失败", message))

    # 初始化工作台导航目录
    if add_type in ["nav", "all"]:
        add_nav_status, add_nav_data = api_object.workbench_add_nav(InitData().NAV_GROUP_LIST)
        print("[SUCCESS] add nav success") if add_nav_status else print(
            "[ERROR] add nav error, error info: {}".format(add_nav_data))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.add_argument("--ollama_api", help="Ollama Api", required=False)
    parameter.add_argument("--add_type", help="ollama or nav or all", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

"""
python3 init-llmops-ollama-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --ollama_api http://192.168.56.11:11434 --add_type all
python3 init-llmops-ollama-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --ollama_api http://192.168.56.11:11434 --add_type ollama
python3 init-llmops-ollama-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --add_type nav
"""