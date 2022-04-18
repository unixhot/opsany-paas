#! /usr/bin/python3
# -*- coding: utf8 -*-
import requests
import json
from grafana_api.grafana_face import GrafanaFace
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse

try:
    from default_monitor_dashboard_dict import request_dict as monitor_request_dict
    from default_host_dashboard_dict import request_dict as host_request_dict
except:
    pass


class InitData:
    # 导航分组
    NAV_GROUP = {
        "group_name": "自动化运维",
        "nav_list": [
            {
                "nav_name": "Zabbix监控",
                "nav_url": "/o/monitor/",
                "describe": "兼容Zabbix监控平台",
                "group_name": "自动化运维",
                "icon_name": "monitor.png"
            }
        ]
    }


class ZabbixApi:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
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
                "user": self.username,
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
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
                    "alias": zabbix_api_username,
                    "passwd": zabbix_api_password,
                    "type": 3,
                    "usrgrps": [
                        {
                            "usrgrpid": admin_group_id
                        }
                    ]
                },
                "auth": self.session,
                "id": 1
            }
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
                    "userid": user_id,
                    "passwd": new_password
                },
                "auth": self.session,
                "id": 1
            }
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
            if a.json().get("result"):
                user_id_list = [user_obj.get("userid") for user_obj in a.json().get("result") if
                                user_obj.get("alias") == "Admin"]
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
            res = session.post(self.url, data=json.dumps(body), verify=False)
            if res.json().get("result"):
                return res.json().get("result")["hostids"][0]
            else:
                return None


class BkApi:
    def __init__(self, bk_token, paas_domain):
        self.token = bk_token
        self.session = requests.Session()
        self.url = paas_domain
        # self.url = "http://demo.opsany.com"
        self.session.headers.update({'referer': paas_domain})
        self.csrfmiddlewaretoken = self.get_csrftoken()

    def get_csrftoken(self):
        API = "/login/"
        URL = self.url + API
        resp = self.session.get(URL, verify=False)
        if resp.status_code == 200:
            return resp.cookies["bklogin_csrftoken"]
        return None

    def update_user_info(self, user_id, user_info):
        API = "/login/accounts/user/{}/".format(user_id)
        self.session.cookies["bk_token"] = self.token
        headers = {
            "X-CSRFToken": self.csrfmiddlewaretoken
        }
        URL = self.url + API
        resp = self.session.put(URL, data=user_info, verify=False, headers=headers)
        if resp.status_code == 200:
            if resp.json().get("result"):
                return "更新成功", True
            return resp.json().get("message"), False
        return "服务器错误", False


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

    def create_controller(self, create_data):
        # TEST DATA  /t/ -> /o/
        API = "/o/control/api/control/v0_1/controller/"
        url = self.paas_domain + API
        res = self.session.post(url, json=create_data, verify=False)
        if res.status_code == 200:
            if str(res.json().get("code", "")) == "200":
                # API请求成功
                return True, "控制器创建成功"
            else:
                # API请求失败
                return False, res.json().get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)

    def create_grafana_api_token(self, create_data):
        # TEST DATA  /t/ -> /o/
        API = "/o/monitor/api/monitor/v0_1/api/grafana/v0_2/grafana/"
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

    def import_zabbix(self):
        # TEST DATA  /t/ -> /o/
        API = "/o/control/api/control/v0_1/import-zabbix/"
        url = self.paas_domain + API
        res = self.session.post(url, json={}, verify=False)
        data = res.json()
        if res.status_code == 200:
            if str(data.get("code", "")) == "200":
                # API请求成功
                return True, data.get("data", "操作成功")
            else:
                # API请求失败
                return False, data.get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)

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

    def create_controller_zabbix(self, create_data):
        # TEST DATA  /t/ -> /o/
        API = "/o/control/api/control/v0_1/controller-init/"
        url = self.paas_domain + API
        res = self.session.post(url, json=create_data, verify=False)
        if res.status_code == 200:
            if str(res.json().get("code", "")) == "200":
                # API请求成功
                return True, "Zabbix集成创建成功"
            else:
                # API请求失败
                return False, res.json().get("message")
        else:
            # 连接API失败
            return False, "API连接不成功，请检查API地址{}".format(url)


class GrafanaBasicApi:
    """
    ("admin", "admin", "dev.opsany.cn/grafana")
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
            res = requests.post(url, json={"name": "opsany_monitor", "role": "Admin"}, verify=False)
            if res.json().get("key"):
                return True, res.json().get("key")
            else:
                return False, res.json().get("message")
        except Exception as e:
            return False, str(e)


class GrafanaBearerApi:
    """
    ("eyJrIjoiR3ZZZGxjbmZ6N0NybEowWEZ4RVJiRDgwYWVyb0RYcTMiLCJuIjoiYXBpa2V5MSIsImlkIjoxfQ==", "dev.opsany.cn/grafana")
    """

    def __init__(self, api_token, grafana_url, zabbix_api_password):
        self.grafana_api_obj = GrafanaFace(auth=api_token, host=grafana_url, protocol="https", verify=False)
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
                return True, res.get("datasource").get("name")
            else:
                return False, ""
        except Exception as e:
            return False, str(e)

    def import_dashboard(self, request_json):
        try:
            res = self.grafana_api_obj.dashboard.update_dashboard(request_json)
            if res.get("status", "") == "success":
                return True, "import success"
            else:
                return False, "import error"
        except Exception as e:
            return False, str(e)


class Run:
    def __init__(self, paas_domain, private_ip, paas_username, paas_password, zabbix_ip, zabbix_password, grafana_ip,
                 grafana_password, modify_zabbix_password, zabbix_api_password, modify_grafana_password):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.grafana_ip = grafana_ip if grafana_ip else self.handle_domain(private_ip)
        self.grafana_password = grafana_password if grafana_password else default_grafana_password
        self.basic_grafana_obj = GrafanaBasicApi("admin", self.grafana_password, "{}/grafana".format(self.grafana_ip))
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.zabbix_ip = zabbix_ip if zabbix_ip else self.handle_domain(private_ip)
        self.zabbix_password = zabbix_password if zabbix_password else default_zabbix_password
        self.zabbix_api_password = zabbix_api_password if zabbix_api_password else default_zabbix_api_password
        self.zabbix_api_username = default_zabbix_api_username
        self.data_source_name = default_data_source_name
        self.modify_zabbix_password = modify_zabbix_password if modify_zabbix_password else default_modify_zabbix_password
        self.modify_grafana_password = modify_grafana_password
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

    def init_zabbix(self):
        try:
            status = True
            default_zabbix_username = "Admin"
            try:
                zabbix_api_url = "http://" + self.zabbix_ip + ":8006/api_jsonrpc.php"
                zabbix_obj = ZabbixApi(default_zabbix_username, self.zabbix_password, zabbix_api_url)
            except:
                zabbix_api_url = "http://" + self.private_ip + ":8006/api_jsonrpc.php"
                zabbix_obj = ZabbixApi(default_zabbix_username, self.zabbix_password, zabbix_api_url)
            # 创建用户
            group_id = zabbix_obj.get_admin_user_group_id()
            if group_id:
                create_user_status = zabbix_obj.create_admin_user(group_id, self.zabbix_api_username,
                                                                  self.zabbix_api_password)
                if not create_user_status:
                    status = False
                    return status, "创建初始化用户失败，用户可能已经存在"
            else:
                status = False
                return status, "用户名密码验证失败"
            update_host_res = zabbix_obj.update_base_host_info(10084, self.private_ip)
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
                bearer_grafana_obj = GrafanaBearerApi(
                    grafana_api_token,
                    "{}/grafana".format(self.private_ip),
                    self.zabbix_api_password
                )
                create_data_source_status, create_data_source_name_or_message = bearer_grafana_obj.create_data_source(
                    "http://{}:8006/api_jsonrpc.php".format(self.private_ip), self.zabbix_api_username, self.data_source_name
                )
                if create_data_source_status:
                    import_monitor_status, import_monitor_message = bearer_grafana_obj.import_dashboard(
                        monitor_request_dict)
                    if not import_monitor_status:
                        print("[ERROR] Import default monitor dashboard error: {}".format(import_monitor_message))
                    else:
                        print("[SUCCESS] Import default monitor dashboard success")
                    import_host_status, import_host_message = bearer_grafana_obj.import_dashboard(host_request_dict)
                    if not import_host_status:
                        print("[ERROR] Import default host dashboard error: {}".format(import_host_message))
                    else:
                        print("[SUCCESS] Import default host dashboard success")
                    if self.modify_grafana_password:
                        update_password_status, update_password_message = self.basic_grafana_obj.update_password(
                            self.modify_grafana_password)
                        if not update_password_status:
                            print("[ERROR] Update grafana password error: {}".format(update_password_message))
                        else:
                            print("[SUCCESS] Update grafana password success")
                    return True, "[SUCCESS] Init Grafana success", grafana_api_token
                else:
                    return False, "[ERROR] Create data source error: {}".format(create_data_source_name_or_message), \
                           grafana_api_token
        except Exception as e:
            return False, str(e), ""

    def init_monitor(self, api_token):
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

    def sync_dashboard(self):
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.sync_dashboard()
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def import_zabbix(self):
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.import_zabbix()
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def create_controller_zabbix(self):
        controller_dict = {
            "name": self.data_source_name,
            "description": self.data_source_name,
            "built_in": True,
            "default": True,
            "zabbix_url": "http://" + self.zabbix_ip + ":8006/api_jsonrpc.php",
            "zabbix_username": self.zabbix_api_username,
            "zabbix_password": self.modify_zabbix_password,
        }
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.create_controller_zabbix(controller_dict)
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def workbench_add_nav(self):
        data = InitData()
        nav_data = data.NAV_GROUP
        return self.opsany_api_obj.workbench_add_nav(nav_data)


def start(paas_domain, private_ip, paas_username, paas_password, zabbix_ip, zabbix_password, grafana_ip,
          grafana_password, modify_zabbix_password, zabbix_api_password, modify_grafana_password=None):
    run_obj = Run(paas_domain, private_ip, paas_username, paas_password, zabbix_ip, zabbix_password, grafana_ip,
                  grafana_password, modify_zabbix_password, zabbix_api_password, modify_grafana_password)
    # 初始化Zabbix
    init_zabbix_status, init_zabbix_message = run_obj.init_zabbix()
    if init_zabbix_status:
        init_grafana_status, init_grafana_message, grafana_api_token = run_obj.init_grafana()
        print(init_grafana_message)
        sync_dashboard_status, sync_dashboard_status_message = run_obj.sync_dashboard()
        print("[SUCCESS] Sync dashboard success") if sync_dashboard_status else \
            print("[ERROR] Sync dashboard error, error info: {}".format(sync_dashboard_status_message))
        # 创建Zabbix
        create_controller_zabbix_status, create_controller_zabbix_message = run_obj.create_controller_zabbix()
        print("[SUCCESS] Create controller zabbix success") if create_controller_zabbix_status else \
            print("[ERROR] Create controller zabbix error, error info: {}".format(create_controller_zabbix_message))

        # 管控主机导入zabbix
        import_zabbix_status, import_zabbix_status_message = run_obj.import_zabbix()
        print("[SUCCESS] import agent zabbix success") if import_zabbix_status else \
            print("[ERROR] import agent zabbix error, error info: {}".format(import_zabbix_status_message))

        # 初始化工作台导航目录
        add_nav_status, add_nav_data = run_obj.workbench_add_nav()
        print("[SUCCESS] add nav success") if add_nav_status else print(
            "[ERROR] add nav error, error info: {}".format(add_nav_data))

        print("[SUCCESS] ALL success")
    else:
        print("[ERROR] Init zabbix error, error info: {}".format(init_zabbix_message))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.add_argument("--zabbix_ip", help="Zabbix Host IP.", required=False)
    parameter.add_argument("--zabbix_password", help="Zabbix Admin Password.", required=False)
    parameter.add_argument("--zabbix_api_password", help="Zabbix Api User Password.", required=False)
    parameter.add_argument("--grafana_ip", help="Grafana Host IP.", required=False)
    parameter.add_argument("--grafana_password", help="Grafana Admin Password.", required=False)
    parameter.add_argument("--modify_zabbix_password", help="Modify Zabbix Admin Password.", required=False)
    # parameter.add_argument("--modify_grafana_password", help="Modify Grafana Admin Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    default_data_source_name = "内置Zabbix Server"
    default_paas_username = "admin"
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
        options.grafana_ip,
        options.grafana_password,
        options.modify_zabbix_password,
        options.zabbix_api_password,
        # options.modify_grafana_password
    )

# python3 init-ce-monitor.py \
# --domain 192.168.56.11 \
# --private_ip 192.168.56.11 \
# --paas_username admin \
# --paas_password 123456.coM \
# --zabbix_ip 192.168.56.11 \
# --zabbix_password OpsAny@2020 \
# --grafana_ip 192.168.56.11 \
# --grafana_password OpsAny@2020
