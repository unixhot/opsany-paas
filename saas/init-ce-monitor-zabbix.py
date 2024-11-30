#! /usr/bin/python3
# -*- coding: utf8 -*-
import os
import sys

import requests
import json
from grafana_api.grafana_face import GrafanaFace
import urllib3
from urllib3.exceptions import ConnectTimeoutError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class ZabbixApi:
    def __init__(self, username, password, url, zabbix_version):
        self.username = username
        self.password = password
        self.url = url
        self.zabbix_version = zabbix_version
        self.session = self.login()
        self.link_status = self.test_link()

    def test_link(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        body = {
            "jsonrpc": "2.0",
            "method": "apiinfo.version",
            "params": [],
            "id": 1
        }
        a = session.post(self.url, data=json.dumps(body), verify=False)
        if a.status_code == 200:
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return ""
        return ""

    def login(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        body = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                # "user": self.username,  通过版本决定参数
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
        if self.zabbix_version in ["6.4", "7.0"]:
            body["params"]["username"] = self.username
        else:  # 5.0  6.0
            body["params"]["user"] = self.username
        a = session.post(self.url, data=json.dumps(body), verify=False)
        if a.status_code == 200:
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return ""
        return ""

    def get_admin_user_group_id(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "usergroup.get",
                "params": {

                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                admin_group_id_list = [obj.get("usrgrpid") for obj in a.json().get("result") if
                                       obj.get("name") == "Zabbix administrators"]
                return admin_group_id_list[0] if admin_group_id_list else None
            else:
                return None
        return None

    def create_admin_user(self, admin_group_id, zabbix_api_username, zabbix_api_password):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "user.create",
                "params": {
                    # "username": zabbix_api_username,  通过版本决定参数
                    "passwd": zabbix_api_password,
                    # "roleid": 3,
                    # "type": 3,
                    "usrgrps": [
                        {
                            "usrgrpid": admin_group_id
                        }
                    ]
                },
                "auth": self.session,
                "id": 1
            }
            if self.zabbix_version in ["6.0", "6.4", "7.0"]:
                body["params"]["username"] = zabbix_api_username
                body["params"]["roleid"] = 3
            else:  # 5.0
                body["params"]["alias"] = zabbix_api_username
                body["params"]["type"] = 3
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def update_user_password(self, user_id, new_password):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "user.update",
                "params": {
                    "userid": str(user_id),
                    # "passwd": new_password
                },
                "auth": self.session,
                "id": 1
            }
            if self.zabbix_version in ["6.4", "7.0"]:
                body["params"]["current_passwd"] = self.password
                body["params"]["passwd"] = new_password
            else:  # 5  6
                body["params"]["passwd"] = new_password
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")
            else:
                return None
        return None

    def get_admin_user_id(self):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "user.get",
                "params": {
                    "output": "extend"
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            username_key = "username" if self.zabbix_version in ["7.0", "6.4", "6.0"] else "alias"  # 5.0
            if a.json().get("result"):
                user_id_list = [user_obj.get("userid") for user_obj in a.json().get("result") if
                                user_obj.get(username_key) == "Admin"]
                admin_user_id = user_id_list[0] if user_id_list else None
                return admin_user_id
            else:
                return None
        return None

    def _get_hostinterface_by_hostids(self, hostid):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            body = {
                "jsonrpc": "2.0",
                "method": "hostinterface.get",
                "params": {
                    # "output": ["interfaceid", "hostid"],
                    "hostids": hostid
                },
                "auth": self.session,
                "id": 1
            }
            a = session.post(self.url, data=json.dumps(body), verify=False)
            if a.json().get("result"):
                return a.json().get("result")[0]
            else:
                return None
        return None

    def update_base_host_info(self, host_id, ip):
        session = requests.session()
        session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })
        if self.session:
            interface_dict = self._get_hostinterface_by_hostids(host_id) or dict()
            interfaceid = interface_dict.get("interfaceid", "")
            body = {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": host_id,
                    "host": default_zabbix_host_name,
                    "name": default_zabbix_host_name,
                    "templates": [
                        # {"templateid": "10047"},
                        # {"templateid": "10343"}
                    ],
                    "interfaces": [
                        {
                            "interfaceid": interfaceid,
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": ip,
                            "dns": "",
                            "port": "10050",
                        }
                    ]
                },
                "auth": self.session,
                "id": 1
            }
            if self.zabbix_version in ["6.0", "6.4", "7.0"]:
                body["params"]["templates"] = [{"templateid": "10047"}, {"templateid": "10343"}]
            else:  # 5.0
                body["params"]["templates"] = [{"temp_id": "10047"}, {"temp_id": "10343"}]
            res = session.post(self.url, data=json.dumps(body), verify=False)
            if res.json().get("result"):
                return res.json().get("result")["hostids"][0]
            else:
                return None


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
            if resp.status_code in [200, 400]:
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

    def sync_dashboard(self):
        # TEST DATA  /t/ -> /o/
        API = "/o/monitor/api/monitor/v0_1/api/grafana/v0_2/dashboard/?data_type=list"
        url = self.paas_domain + API
        res = self.session.get(url, verify=False)
        if res.status_code == 200:
            if str(res.json().get("code", "")) == "200":
                # API请求成功
                return True, "同步Dashboard成功"
            else:
                # API请求失败
                return False, res.json().get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)

    def get_admin_user_id(self):
        API = "/login/api/v2/get_batch_users/"
        URL = self.paas_domain + API
        data = {
            "bk_username_list": [self.username],
            "bk_token": self.token
        }
        response = self.session.post(url=URL, data=json.dumps(data), verify=False)
        data = response.json()
        if data.get("result"):
            return data.get("data").get(self.username).get("bk_username"), data.get("data").get(self.username).get("id")
        else:
            return None, "获取用户ID失败"

    def create_controller_zabbix(self, create_data):
        # TEST DATA  /t/ -> /o/
        API = "/o/control/api/control/v0_1/controller-init/"
        url = self.paas_domain + API
        res = self.session.post(url, json=create_data, verify=False)
        if res.status_code == 200:
            if str(res.json().get("code", "")) == "200":
                # API请求成功
                return True, res.json().get("data", "")
            else:
                # API请求失败
                return False, res.json().get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)


class GrafanaBearerApi:
    def __init__(self, api_token, grafana_url, zabbix_api_password, timeout=5):
        self.grafana_api_obj = GrafanaFace(auth=api_token, host=grafana_url, protocol="https", verify=False, timeout=timeout)
        self.link_status = self.test_ping()
        self.zabbix_api_password = zabbix_api_password

    def test_ping(self):
        try:
            self.grafana_api_obj.dashboard.get_home_dashboard()
            return True
        except Exception as e:
            return False

    def create_data_source(self, zabbix_api, zabbix_zpi_username, data_source_name):
        try:
            data_source_dict = {
                'orgId': 1,
                'name': data_source_name,
                'type': 'alexanderzobnin-zabbix-datasource',
                'typeLogoUrl': 'public/plugins/alexanderzobnin-zabbix-datasource/img/icn-zabbix-datasource.svg',
                'access': 'proxy',
                'url': zabbix_api,
                'basicAuth': False,
                'isDefault': True,
                'jsonData': {
                    'cacheTTL': '',
                    'disableDataAlignment': False,
                    'timeout': '',
                    'trends': True,
                    'trendsFrom': '',
                    'trendsRange': '',
                    'username': zabbix_zpi_username,
                    'password': self.zabbix_api_password
                },
                'readOnly': False
            }
            res = self.grafana_api_obj.datasource.create_datasource(data_source_dict)
            if res.get("datasource").get("name"):
                return True, "", res.get("datasource", {})
            else:
                return False, "Error", {}
        except Exception as e:
            return False, str(e), {}


class Run:
    def __init__(self, paas_domain, private_ip, paas_username, paas_password, zabbix_ip, zabbix_password,
                 zabbix_version, grafana_ip, grafana_password, zabbix_api_password, modify_zabbix_password=None):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.grafana_ip = grafana_ip if grafana_ip else self.handle_domain(private_ip)
        self.grafana_password = grafana_password
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.zabbix_ip = zabbix_ip if zabbix_ip else self.handle_domain(private_ip)
        self.zabbix_password = zabbix_password if zabbix_password else default_zabbix_password
        self.zabbix_version = zabbix_version
        self.zabbix_api_password = zabbix_api_password if zabbix_api_password else default_zabbix_api_password
        self.zabbix_api_username = default_zabbix_api_username
        self.data_source_name = default_data_source_name
        self.modify_zabbix_password = modify_zabbix_password
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain, self.paas_username, self.paas_password)
        self.data_source_dict = {}

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

    def init_zabbix(self):
        try:
            status = True
            default_zabbix_username = "Admin"
            try:
                zabbix_api_url = "http://" + self.zabbix_ip + ":8006/api_jsonrpc.php"
                zabbix_obj = ZabbixApi(default_zabbix_username, self.zabbix_password, zabbix_api_url, self.zabbix_version)
            except:
                zabbix_api_url = "http://" + self.private_ip + ":8006/api_jsonrpc.php"
                zabbix_obj = ZabbixApi(default_zabbix_username, self.zabbix_password, zabbix_api_url, self.zabbix_version)
            # 创建用户
            group_id = zabbix_obj.get_admin_user_group_id()
            if group_id:
                create_user_status = zabbix_obj.create_admin_user(group_id, self.zabbix_api_username, self.zabbix_api_password)
                if not create_user_status:
                    status = False
                    return status, "创建初始化用户失败，用户可能已经存在"
            else:
                status = False
                return status, "用户名密码验证失败"
            update_host_res = zabbix_obj.update_base_host_info(default_zabbix_host_id, self.private_ip)
            if not update_host_res:
                print("更新主机失败")
            # 修改admin用户密码
            admin_user_id = zabbix_obj.get_admin_user_id()
            if self.modify_zabbix_password:
                update_password_status = zabbix_obj.update_user_password(admin_user_id, self.modify_zabbix_password)
                if not update_password_status:
                    status = False
                    return status, "更新Admin用户密码失败"
            return status, ""
        except Exception as e:
            return None, str(e)

    def init_grafana(self):
        try:
            auth = ("admin", self.grafana_password)
            try:
                bearer_grafana_obj = GrafanaBearerApi(auth, "{}/grafana".format(self.private_ip), self.zabbix_api_password, 3)
            except (ConnectTimeoutError, Exception) as e:
                bearer_grafana_obj = GrafanaBearerApi(auth, "{}/grafana".format(self.paas_domain), self.zabbix_api_password)
            create_data_source_status, create_data_source_message, create_data_source_dict = bearer_grafana_obj.create_data_source(
                "http://{}:8006/api_jsonrpc.php".format(self.private_ip), self.zabbix_api_username, self.data_source_name
            )
            if create_data_source_status:
                return True, "[SUCCESS] Create data source success", create_data_source_dict
            else:
                return False, f"[ERROR] Create data source error: {create_data_source_message}", {}
        except Exception as e:
            return False, f"[ERROR] Create data source Exception: {e}", {}

    def sync_dashboard(self):
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.sync_dashboard()
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def create_controller_zabbix(self, datasource_dict: dict):
        controller_dict = {
            "name": self.data_source_name,
            "description": self.data_source_name,
            "built_in": True,
            "default": True,
            "zabbix_url": "http://" + self.zabbix_ip + ":8006/api_jsonrpc.php",
            "zabbix_username": self.zabbix_api_username,
            "zabbix_password": self.modify_zabbix_password,
            "version": self.zabbix_version,
            "datasource_id": datasource_dict.get("id", 1),
            "datasource_uid": datasource_dict.get("uid"),
            "datasource_name": datasource_dict.get("name"),
            "datasource_type": datasource_dict.get("type"),
        }
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.create_controller_zabbix(controller_dict)
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"


def start(*args):
    run_obj = Run(*args)
    # 初始化Zabbix-创建用户改密码
    init_zabbix_status, init_zabbix_message = run_obj.init_zabbix()
    if not init_zabbix_status:
        print(f"[ERROR] Init zabbix error, error info: {init_zabbix_message}")
        return
    print("[SUCCESS] Init Zabbix User zabbixapi success")
    # 初始化Grafana-录入数据源
    init_grafana_status, init_grafana_message, create_data_source_dict = run_obj.init_grafana()
    print(init_grafana_message)
    if not init_grafana_status:
        return
    # 同步基础监控大屏
    sync_dashboard_status, sync_dashboard_status_message = run_obj.sync_dashboard()
    if not sync_dashboard_status:
        print(f"[ERROR] Sync dashboard error, error info: {sync_dashboard_status_message}")
        return
    print("[SUCCESS] Sync dashboard success")

    # 初始化Zabbix到管控
    create_controller_zabbix_status, create_controller_zabbix_message = run_obj.create_controller_zabbix(create_data_source_dict)
    if not create_controller_zabbix_status:
        print(f"[ERROR] Create controller zabbix error, error info: {create_controller_zabbix_message}")
        return
    print("[SUCCESS] Create controller zabbix success")

    print("[SUCCESS] ALL success")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.add_argument("--zabbix_ip", help="Zabbix Host IP.", required=False)
    parameter.add_argument("--zabbix_password", help="Zabbix Admin Password.", required=False)
    parameter.add_argument("--zabbix_version", help="Zabbix Version Support 5 6 6.4 7.", required=False)
    parameter.add_argument("--grafana_ip", help="Grafana Host IP.", required=False)
    parameter.add_argument("--grafana_password", help="Grafana Admin Password.", required=False)
    parameter.add_argument("--zabbix_api_password", help="Zabbix Api Password Init Control.", required=False)
    parameter.add_argument("--modify_zabbix_password", help="Modify Zabbix Admin Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    default_data_source_name = "内置Zabbix Server"
    default_paas_username = "admin"
    default_zabbix_host_name = "opsany-server"
    default_zabbix_host_id = 10084
    default_zabbix_host_template_list = [
        {"temp_id": "10047", "temp_name": "Zabbix server health"},
        {"temp_id": "10343", "temp_name": "Linux by Zabbix agent active"}
    ]
    default_paas_password = "admin"
    default_zabbix_password = "admin"
    default_grafana_password = "admin"
    default_zabbix_api_password = "OpsAny@2020"
    default_zabbix_api_username = "zabbixapi"
    default_modify_zabbix_password = "OpsAny@2020"
    start(
        options.domain,
        options.private_ip,
        options.paas_username,
        options.paas_password,
        options.zabbix_ip,
        options.zabbix_password,
        options.zabbix_version,
        options.grafana_ip,
        options.grafana_password,
        options.zabbix_api_password,
        options.modify_zabbix_password,
    )

"""
# 不修改Admin的Zabbix密码可以不传modify_zabbix_password
python ../saas/init-ce-monitor-zabbix.py --domain 127.0.0.1 --private_ip 127.0.0.1 --paas_username admin --paas_password OpsYXur628852 --zabbix_ip 127.0.0.1 --zabbix_password zabbix --grafana_ip 127.0.0.1 --grafana_password OpsMEnOL9268 --zabbix_api_password OpsAny@2020 --zabbix_version 6.0

python3 ../saas/init-ce-monitor-zabbix.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password $ADMIN_PASSWORD --zabbix_ip $LOCAL_IP --zabbix_password zabbix --grafana_ip $LOCAL_IP --grafana_password $GRAFANA_ADMIN_PASSWORD --zabbix_api_password OpsAny@2020 --zabbix_version 7.0
"""

