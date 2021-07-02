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


class ZabbixApi:
    def __init__(self, username, password, url):
        self.username = username
        self.passworld = password
        self.url = url
        self.session = self.login()

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
                "password": self.passworld
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
                admin_group_id_list = [obj.get("usrgrpid") for obj in a.json().get("result") if obj.get("name") == "Zabbix administrators"]
                return admin_group_id_list[0] if admin_group_id_list else None
            else:
                return None
        return None

    def create_admin_user(self, admin_group_id):
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
                    "alias": "zabbixapi",
                    "passwd": "OpsAny@2020",
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
                user_id_list = [user_obj.get("userid") for user_obj in a.json().get("result") if user_obj.get("alias") == "Admin"]
                admin_user_id = user_id_list[0] if user_id_list else None
                return admin_user_id
            else:
                return None
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
    def __init__(self, paas_domain):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        # TEST DATA  guoyuchen -> admin
        self.username = "admin"
        # TEST DATA  123456.coM -> admin
        self.password = "admin"
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


class GrafanaBasicApi:
    """
    ("admin", "admin", "dev.opsany.cn/grafana")
    """
    def __init__(self, username, password, grafana_url):
        self.username = username
        self.password = password
        self.grafana_url = grafana_url
        self.grafana_api_obj = GrafanaFace(auth=(self.username, self.password), host=grafana_url, protocol="https", verify=False)
        self.link_status = self.test_ping()

    def test_ping(self):
        try:
            self.grafana_api_obj.admin.stats()
            return True
        except:
            return False

    def update_password(self):
        admin_user_data = self.grafana_api_obj.user.get_actual_user()
        admin_user_id = admin_user_data.get("id")
        status = self.grafana_api_obj.admin.change_user_password(admin_user_id, "OpsAny@2020")
        if status.get("message", "") == "User password updated":
            return True, status.get("message", "")
        else:
            return False, status.get("message", "")

    def create_token_key(self):
        # 需要使用requests去做
        try:
            url = "https://{}:{}@{}/api/auth/keys".format(self.username, self.password, self.grafana_url)
            # TEST DATA apikey1 -> opsany
            res = requests.post(url, json={"name": "opsany", "role": "Admin"}, verify=False)
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
    def __init__(self, api_token, grafana_url):
        self.grafana_api_obj = GrafanaFace(auth=api_token, host=grafana_url, protocol="https", verify=False)
        self.link_status = self.test_ping()

    def test_ping(self):
        try:
            self.grafana_api_obj.dashboard.get_home_dashboard()
            return True
        except Exception as e:
            return False

    def create_data_source(self, zabbix_api):
        try:
            data_source_dict = {
                'orgId': 1,
                'name': 'Zabbix',
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
                    'username': 'zabbixapi',
                    'password': 'OpsAny@2020'
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
    def __init__(self, paas_domain, private_ip, deploy_type):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.deploy_type = deploy_type
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain)
        self.basic_grafana_obj = GrafanaBasicApi("admin", "admin", "{}/grafana".format(self.paas_domain if self.paas_domain
                                                                                      else self.private_ip))

    def handle_domain(self, domain: str):
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

    def create_controller(self):
        controller_dict = {
            "name": "默认控制器",
            "type": "本地",
            # TEST DATA 8011 -> 8005
            "api1": "https://{}:8005".format(self.paas_domain) if self.paas_domain else "",
            "api2": "https://{}:8005".format(self.private_ip) if self.private_ip else "",
            "username1": "saltapi",
            "username2": "saltapi",
            # TEST DATA 123456.coM -> OpsAny@2020
            "password1": "OpsAny@2020",
            "password2": "OpsAny@2020",
            "port1": "",
            "port2": "",
            "zabbix_url": "http://" + self.paas_domain + ":8006/api_jsonrpc.php",
            "zabbix_username": "zabbixapi",
            "zabbix_password": "OpsAny@2020",
        }
        if self.opsany_api_obj.token:
            status, message = OpsAnyApi("https://" + self.paas_domain).create_controller(controller_dict)
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def init_zabbix(self):
        try:
            status = True
            default_zabbix_username = "Admin"
            default_zabbix_password = "zabbix"
            zabbix_api_url = "http://" + self.paas_domain + ":8006/api_jsonrpc.php"
            zabbix_obj = ZabbixApi(default_zabbix_username, default_zabbix_password, zabbix_api_url)
            # 创建用户
            group_id = zabbix_obj.get_admin_user_group_id()
            if group_id:
                create_user_status = zabbix_obj.create_admin_user(group_id)
                if not create_user_status:
                    status = False
                    return status, "创建初始化用户失败"
            else:
                status = False
                return status, "用户名密码验证失败"
            # 修改admin用户密码
            admin_user_id = zabbix_obj.get_admin_user_id()
            update_password_status = zabbix_obj.update_user_password(admin_user_id, "OpsAny@2020")
            if not update_password_status:
                status = False
                return status, "更新Admin用户密码失败"
            return status, ""
        except Exception as e:
            return False, str(e)

    def init_grafana(self):
        try:
            if self.basic_grafana_obj.link_status:
                create_token_status, create_token_key_or_message = self.basic_grafana_obj.create_token_key()
                if create_token_status:
                    grafana_api_token = create_token_key_or_message
                else:
                    return False, "[ERROR] Create api token error: {}".format(create_token_key_or_message), ""
            else:
                return False, "[ERROR] Link grafana error, please check username or password", ""
            if grafana_api_token:
                bearer_grafana_obj = GrafanaBearerApi(grafana_api_token, "{}/grafana".format(self.paas_domain
                                                                            if self.paas_domain else self.private_ip))
                create_data_source_status, create_data_source_name_or_message = bearer_grafana_obj.create_data_source(
                        "http://{}:8006/api_jsonrpc.php".format(self.paas_domain if self.paas_domain else self.private_ip))
                if create_data_source_status:
                    # return True, "[SUCCESS] Create data source success", grafana_api_token
                    import_monitor_status, import_monitor_message = bearer_grafana_obj.import_dashboard(monitor_request_dict)
                    if not import_monitor_status:
                        print("[ERROR] Import default monitor dashboard error: {}".format(import_monitor_message))
                    else:
                        print("[SUCCESS] Import default monitor dashboard success")
                    import_host_status, import_host_message = bearer_grafana_obj.import_dashboard(host_request_dict)
                    if not import_host_status:
                        print("[ERROR] Import default host dashboard error: {}".format(import_host_message))
                    else:
                        print("[SUCCESS] Import default host dashboard success")
                    update_password_status, update_password_message = self.basic_grafana_obj.update_password()
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
                "url": "{}/grafana".format(self.paas_domain if self.paas_domain else self.private_ip),
                "api_key": api_token,
            }
            if self.opsany_api_obj.token:
                status, message = OpsAnyApi("https://" + self.paas_domain).create_grafana_api_token(api_token_dict)
                if status:
                    return True, message
                else:
                    return False, message
            else:
                return False, "OpsAny平台认证失败"
        return False, "没有获取到有效key"

    def sync_dashboard(self):
        if self.opsany_api_obj.token:
            status, message = OpsAnyApi("https://" + self.paas_domain).sync_dashboard()
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"

    def update_admin_user(self):
        bk_token = self.opsany_api_obj.token
        usename, user_id_or_error_message = self.opsany_api_obj.get_admin_user_id()
        if not usename:
            return False, user_id_or_error_message
        user_info = {
            "username": "admin",
            "chname": "管理员",
            "phone": "12345678910",
            "email": "123456@qq.com",
            "role": 1
        }
        message, status = BkApi(bk_token, "https://" + self.paas_domain).update_user_info(user_id_or_error_message, user_info)
        return status, message


def start(paas_domain, private_ip):
    run_obj = Run(paas_domain, private_ip, "")
    # 创建控制器
    create_controller_status, create_controller_message = run_obj.create_controller()
    print("[SUCCESS] Create controller success") if create_controller_status else \
        print("[ERROR] Create controller error, error info: {}".format(create_controller_message))
    # 初始化Zabbix
    init_zabbix_status, init_zabbix_message = run_obj.init_zabbix()
    print("[SUCCESS] Init zabbix success") if init_zabbix_status else \
        print("[ERROR] Init zabbix error, error info: {}".format(init_zabbix_message))
    # 初始化Grafana
    init_grafana_status, init_grafana_message, grafana_api_token = run_obj.init_grafana()
    print(init_grafana_message)
    # 更新用户admin用户信息
    update_admin_user_info_status, update_admin_user_info_message = run_obj.update_admin_user()
    print("[SUCCESS] Update admin user info success") if update_admin_user_info_status else \
        print("[ERROR] Update admin user info error, error info: {}".format(update_admin_user_info_message))
    # 创建api_token至OpsAny
    create_api_token_status, create_api_token_message = run_obj.init_monitor(grafana_api_token)
    print("[SUCCESS] Create api token success") if create_api_token_status else \
        print("[ERROR] Create api token error, error info: {}".format(create_api_token_message))
    sync_dashboard_status, sync_dashboard_status_message = run_obj.sync_dashboard()
    print("[SUCCESS] Sync dashboard success") if sync_dashboard_status else \
        print("[ERROR] Sync dashboard error, error info: {}".format(sync_dashboard_status_message))
    print("[SUCCESS] ALL success")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain
    private_ip = options.private_ip
    paas_domain = domain
    private_ip = private_ip
    start(paas_domain, private_ip)