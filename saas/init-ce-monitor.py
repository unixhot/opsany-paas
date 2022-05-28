#! /usr/bin/python3
# -*- coding: utf8 -*-
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class InitData:
    # 导航分组
    NAV_GROUP = {
        "group_name": "自动化运维",
        "nav_list": [
            {
                "nav_name": "基础监控",
                "nav_url": "/o/monitor/",
                "describe": "基础监控平台",
                "group_name": "自动化运维",
                "icon_name": "monitor.png"
            }
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
        # TEST DATA  guoyuchen -> admin
        self.username = username
        # TEST DATA  123456.coM -> admin
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

    def workbench_add_nav(self, nav_group):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav/"
            NAV_GROUP_URL = self.paas_domain + NAV_API
            nav_group.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps(nav_group), verify=False)
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


class Run:
    def __init__(self, paas_domain, private_ip, paas_username, paas_password):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain, self.paas_username, self.paas_password)

    def handle_domain(self, domain):
        """
        http://xxx.xxx.xx/
        https://xxx.xxx.xx/
        xxx.xxx.xxx.xxx
        xxxx.xxxx.xxx
        -> xxx.xxx.xxx.xxx
        """
        if domain.startswith("http://") or domain.startswith("https://"):
            domain = domain.split("http://")[-1] if domain.startswith("http://") else domain.split("https://")[-1]
            if len(domain.split("/")) > 1:
                domain = domain.split("/", 1)[0]
                return domain
            else:
                return domain
        else:
            return domain

    def workbench_add_nav(self):
        data = InitData()
        nav_data = data.NAV_GROUP
        return self.opsany_api_obj.workbench_add_nav(nav_data)


def start(paas_domain, private_ip, paas_username, paas_password):
    run_obj = Run(paas_domain, private_ip, paas_username, paas_password)

    # 初始化工作台导航目录
    add_nav_status, add_nav_data = run_obj.workbench_add_nav()
    print("[SUCCESS] add nav success") if add_nav_status else print(
        "[ERROR] add nav error, error info: {}".format(add_nav_data))

    print("[SUCCESS] ALL success")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    default_paas_username = "admin"
    default_paas_password = "admin"
    start(
        options.domain,
        options.private_ip,
        options.paas_username,
        options.paas_password
    )

# python3 init-ce-monitor.py \
# --domain 192.168.56.11 \
# --private_ip 192.168.56.11 \
# --paas_username admin \
# --paas_password 123456.coM
