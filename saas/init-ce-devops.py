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
    NAV_GROUP = [
        {
            "group_name": "DevOps",
            "group_language": {
                "chinese_simplified": "DevOps",
                "chinese_traditional": "DevOps",
                "english": "DevOps"
            },
            "nav_list": [
                {
                    "nav_name": "应用平台",
                    "nav_code": "devops",
                    "nav_url": "/o/devops/",
                    "describe": "应用DevOps平台",
                    "nav_describe_language": {
                        "chinese_simplified": "应用DevOps平台",
                        "chinese_traditional": "應用DevOps平台",
                        "english": "DevOps Platform"
                    },
                    "group_name": "应用管理",
                    "icon_name": "devops.png",
                    "nav_language": {
                        "chinese_simplified": "应用平台",
                        "chinese_traditional": "應用平台",
                        "english": "Devops"
                    },
                },
                {
                    "nav_name": "流水线",
                    "nav_code": "pipeline",
                    "nav_url": "/o/pipeline/",
                    "describe": "流水线编排",
                    "nav_describe_language": {
                        "chinese_simplified": "流水线编排",
                        "chinese_traditional": "流水線编排",
                        "english": "Pipeline Orchestration"
                    },
                    "group_name": "应用管理",
                    "icon_name": "pipeline.png",
                    "nav_language": {
                        "chinese_simplified": "流水线",
                        "chinese_traditional": "流水線",
                        "english": "Pipeline"
                    },
                },
                {
                    "nav_name": "持续部署",
                    "nav_code": "deploy",
                    "nav_url": "/o/deploy/",
                    "describe": "部署编排灵活",
                    "nav_describe_language": {
                        "chinese_simplified": "部署编排灵活",
                        "chinese_traditional": "部署編排靈活",
                        "english": "Deployment Orchestration"
                    },
                    "group_name": "应用管理",
                    "icon_name": "deploy.png",
                    "nav_language": {
                        "chinese_simplified": "持续部署",
                        "chinese_traditional": "持續部署",
                        "english": "Deploy"
                    },
                },
                {
                    "nav_name": "制品仓库",
                    "nav_code": "repo",
                    "nav_url": "/o/repo/",
                    "describe": "应用制品仓库",
                    "nav_describe_language": {
                        "chinese_simplified": "应用制品仓库",
                        "chinese_traditional": "應用建置成品倉庫",
                        "english": "Application Repository"
                    },
                    "group_name": "应用管理",
                    "icon_name": "repo.png",
                    "nav_language": {
                        "chinese_simplified": "制品仓库",
                        "chinese_traditional": "制品仓库",
                        "english": "Repo"
                    },
                },
            ]
        }
    ]
    
    # 初始化业务树
    DEFAULT_BUSINESS_TREE = [
            {
                "BUSINESS_name": "default",
                "BUSINESS_VISIBLE_NAME": "默认分组",
                "BUSINESS_STATUS": "已上线",
                "BUSINESS_ID": "default",
                "BUSINESS_COMMENT": " <p>默认分组</p>",
                "children": [
                    {
                        "APPLICATION_name": "default",
                        "APPLICATION_VISIBLE_NAME": "默认应用",
                        "APPLICATION_STATUS": "运行中",
                        "APPLICATION_ID": "default",
                        "APPLICATION_COMMENT": " <p>默认应用</p>",
                        "children": [
                            {
                                "SERVICE_name": "default",
                                "SERVICE_VISIBLE_NAME": "默认服务",
                                "SERVICE_STATUS": "运行中",
                                "SERVICE_COMMENT": " <p>默认服务</p>",
                            }
                        ]
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
        self.username = username
        self.password = password
        self.login_url = self.paas_domain + "/login/api/v3/login/"
        self.status, self.token, self.csrfmiddlewaretoken = self.login()

    def login(self, verify_code=""):
        try:
            json_data = {"username": self.username, "password": self.password, "verify_code": verify_code, "auth_type": "1"}
            resp = self.session.post(self.login_url, data=json.dumps(json_data), verify=False)
            try:
                res_json = resp.json()
                if resp.status_code != 200:
                    return False, res_json, ""
                bk_token = (res_json.get("data") or {}).get("bk_token")
                code = res_json.get("code")
                message = res_json.get("message")
                if bk_token:
                    return True, bk_token, resp.cookies.get("bklogin_csrftoken")
                elif code != 200:
                    return False, message, ""
                else:
                    return False, res_json, ""
            except Exception as e:
                return False, str(resp.content.decode()), ""
        except Exception as e:
            return False, str(e), ""

    def workbench_add_nav(self):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav-v2/"
            # NAV_API = "/api/workbench/v0_1/update-nav-v2/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data = InitData()
            nav_data = data.NAV_GROUP
            for nav in nav_data:
                nav.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps({"group_list": nav_data}), verify=False)
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

    def init_default_business_tree(self):
        """应用平台初始化应用分组应用和服务"""
        try:
            INIT_URL = "/o/devops//api/devops/v0_1/init-business/"
            NAV_GROUP_URL = self.paas_domain + INIT_URL

            data = InitData()
            nav_data = {"business_list": data.DEFAULT_BUSINESS_TREE}
            
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
    
    # 初始化默认应用
    init_app_status, init_app_data = run_obj.init_default_business_tree()
    print("[SUCCESS] init default application success: {}".format(init_app_data)) if init_app_status else print(
        "[ERROR] init default application error, error info: {}".format(init_app_data))


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
# python init-ce-devops.py --domain http://192.168.0.11:8004 --username opsany_username  --password opsany_password
