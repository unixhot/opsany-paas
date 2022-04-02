#! /usr/bin/python3
# -*- coding: utf8 -*-
"""
执行前请执行
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany/uploads/workbench/icon/
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany-paas/paas-ce/paas/paas/media/applogo/
"""


import time

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class InitData:
    # 导航分组
    NAV_GROUP = {
        "group_name": "应用管理",
        "nav_list": [
            {
                "nav_name": "应用平台",
                "nav_url": "/o/devops/",
                "describe": "应用DevOps平台",
                "group_name": "应用管理",
                "icon_name": "devops.png"
            },
            {
                "nav_name": "流水线",
                "nav_url": "/o/pipeline/",
                "describe": "流水线编排",
                "group_name": "应用管理",
                "icon_name": "pipeline.png"
            },
            {
                "nav_name": "持续部署",
                "nav_url": "/o/deploy/",
                "describe": "部署编排灵活",
                "group_name": "应用管理",
                "icon_name": "deploy.png"
            },
        ]
    }


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

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code == 200:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):
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

    def workbench_add_nav(self):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data = InitData()
            nav_data = data.NAV_GROUP
            nav_data.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps(nav_data), verify=False)
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


def start(paas_domain, username, password):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)

    # 初始化工作台导航目录
    add_nav_status, add_nav_data = run_obj.workbench_add_nav()
    print("[SUCCESS] add nav success") if add_nav_status else print(
        "[ERROR] add nav error, error info: {}".format(add_nav_data))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain
    username = options.username
    password = options.password
    start(domain, username, password)


# python init-ce-devops.py --domain https://www.opsany_url.cn --username opsany_username  --password opsany_password
