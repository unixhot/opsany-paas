#! /usr/bin/python3
# -*- coding: utf8 -*-
import requests
import json
import urllib3

from grafana_api import GrafanaFace


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class InitData:
    # 导航分组
    NAV_GROUP_LIST = [
        {
            "group_name": "自动化运维",
            "nav_list": [
                {
                    "nav_name": "基础监控",
                    "nav_url": "/o/monitor/",
                    "describe": "基础监控平台",
                    "group_name": "自动化运维",
                    "icon_name": "monitor.png"
                }
            ],
        },
        {
            "group_name": "平台管理",
            "nav_list": [
                {
                    "nav_name": "可视化平台",
                    "nav_url": "/o/dashboard/",
                    "describe": "运维数据可视化",
                    "group_name": "平台管理",
                    "icon_name": "dashboard.png"
                },
            ],
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

    def workbench_add_nav(self, nav_group_list):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav/"
            NAV_GROUP_URL = self.paas_domain + NAV_API
            for nav_group in nav_group_list:
                nav_group.update({"username": self.username})

            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps(nav_group_list), verify=False)
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

    def create_grafana_api_token(self, create_data):
        # TEST DATA  /t/ -> /o/
        API = "/o/control//api/control/v0_1/grafana/"
        url = self.paas_domain + API
        res = self.session.post(url, json=create_data, verify=False)
        if res.status_code == 200:
            if str(res.json().get("code", "")) == "200":
                # API请求成功
                return True, "API Token 添加成功"
            else:
                # API请求失败
                return False, res.json().get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)


class GrafanaBasicApi:
    """
    ("admin", "admin", "demo.opsany.com/grafana")
    """

    def __init__(self, username, password, grafana_url):
        self.username = username
        self.password = password
        self.grafana_url = grafana_url
        self.grafana_api_obj = GrafanaFace(auth=(self.username, self.password), host=grafana_url, protocol="https",
                                           verify=False)
        self.link_status = self.test_ping()

    def test_ping(self):
        try:
            self.grafana_api_obj.admin.stats()
            return True
        except:
            return False

    def update_password(self, password):
        admin_user_data = self.grafana_api_obj.user.get_actual_user()
        admin_user_id = admin_user_data.get("id")
        status = self.grafana_api_obj.admin.change_user_password(admin_user_id, password)
        if status.get("message", "") == "User password updated":
            return True, status.get("message", "")
        else:
            return False, status.get("message", "")

    def create_token_key(self):
        # 需要使用requests去做
        try:
            url = "https://{}:{}@{}/api/auth/keys".format(self.username, self.password, self.grafana_url)
            # TEST DATA apikey1 -> opsany
            res = requests.post(url, json={"name": "opsany_control", "role": "Admin"}, verify=False)
            if res.json().get("key"):
                return True, res.json().get("key")
            else:
                return False, res.json().get("message")
        except Exception as e:
            return False, str(e)


class Run:
    def __init__(self, paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password=None):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain, self.paas_username, self.paas_password)
        self.grafana_ip = self.handle_domain(private_ip)
        self.grafana_password = grafana_password if grafana_password else default_grafana_password
        self.grafana_change_password = grafana_change_password
        self.basic_grafana_obj = GrafanaBasicApi("admin", self.grafana_password, "{}/grafana".format(self.grafana_ip))

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
        nav_data = data.NAV_GROUP_LIST
        return self.opsany_api_obj.workbench_add_nav(nav_data)

    def init_grafana(self):
        if self.basic_grafana_obj.link_status:
            create_token_status, create_token_key_or_message = self.basic_grafana_obj.create_token_key()
            if create_token_status:
                grafana_api_token = create_token_key_or_message
            else:
                info = "[ERROR] Create api token error: {}".format(create_token_key_or_message)
                return False, info, ""
        else:
            return False, "[ERROR] Link grafana error, please check username or password", ""
        if grafana_api_token:
            if self.grafana_change_password:
                update_password_status, update_password_message = self.basic_grafana_obj.update_password(
                    self.grafana_change_password)
                if not update_password_status:
                    print("[ERROR] Update grafana password error: {}".format(update_password_message))
                else:
                    print("[SUCCESS] Update grafana password success")
            return True, "[SUCCESS] Init Grafana success", grafana_api_token
        else:
            return False, "[ERROR] Create Grafana Token error: {}", ""
        
    def init_control_grafana_server(self, api_token):
        if api_token:
            api_token_dict = {
                "url": "{}/grafana".format(self.paas_domain),
                "api_key": api_token,
            }
            if self.opsany_api_obj.token:
                status, message = self.opsany_api_obj.create_grafana_api_token(api_token_dict)
                if status:
                    return True, message
                else:
                    return False, message
            else:
                return False, "OpsAny平台认证失败"
        return False, "没有获取到有效key"


def start(paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password):
    run_obj = Run(paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password)

    # 初始化工作台导航目录
    add_nav_status, add_nav_data = run_obj.workbench_add_nav()
    print("[SUCCESS] add nav success") if add_nav_status else print(
        "[ERROR] add nav error, error info: {}".format(add_nav_data))
    
    init_grafana_status, init_grafana_message, grafana_api_token = run_obj.init_grafana()
    if init_grafana_status:
        # 创建api_token至OpsAny管控
        create_api_token_status, create_api_token_message = run_obj.init_control_grafana_server(grafana_api_token)
        print("[SUCCESS] Create api token success") if create_api_token_status else \
            print("[ERROR] Create api token error, error info: {}, Api token: {}".format(create_api_token_message,
                                                                                     grafana_api_token))
    else:
        print("[ERROR] Init Grafana error, error info: {}".format(init_grafana_message))

    print("[SUCCESS] ALL success")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.add_argument("--grafana_password", help="Grafana Admin Password.", required=False)
    parameter.add_argument("--grafana_change_password", help="grafana Change Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    default_paas_username = "admin"
    default_paas_password = "admin"
    default_grafana_password = "admin"
    start(
        options.domain,
        options.private_ip,
        options.paas_username,
        options.paas_password,
        options.grafana_password,
        options.grafana_change_password,
    )

# python3 init-ce-monitor.py \
# --domain 192.168.56.11 \
# --private_ip 192.168.56.11 \
# --paas_username admin \
# --paas_password 123456.coM
#  --grafana_password grafana_password
#  --grafana_change_password new_password
