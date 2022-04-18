import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse
from grafana_api import GrafanaFace


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

    def create_controller_salt(self, create_data):
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
    def __init__(self, paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.grafana_password = grafana_password if grafana_password else default_grafana_password
        self.grafana_change_password = grafana_change_password
        self.grafana_ip = self.handle_domain(private_ip)
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain, self.paas_username, self.paas_password)
        self.basic_grafana_obj = GrafanaBasicApi("admin", self.grafana_password, "{}/grafana".format(self.grafana_ip))


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

    def create_controller_salt(self):
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
            "port2": ""
        }
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.create_controller_salt(controller_dict)
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


def start(paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password=None):
    run_obj = Run(paas_domain, private_ip, paas_username, paas_password, grafana_password, grafana_change_password)
    # 创建控制器
    create_controller_status, create_controller_message = run_obj.create_controller_salt()
    print("[SUCCESS] Create controller success") if create_controller_status else \
        print("[ERROR] Create controller error, error info: {}".format(create_controller_message))

    init_grafana_status, init_grafana_message, grafana_api_token = run_obj.init_grafana()
    if init_grafana_status:
        # 创建api_token至OpsAny管控
        create_api_token_status, create_api_token_message = run_obj.init_control_grafana_server(grafana_api_token)
        print("[SUCCESS] Create api token success") if create_api_token_status else \
            print("[ERROR] Create api token error, error info: {}, Api token: {}".format(create_api_token_message,
                                                                                     grafana_api_token))
    else:
        print("[ERROR] Init Grafana error, error info: {}".format(init_grafana_message))

    # 更新用户admin用户信息
    update_admin_user_info_status, update_admin_user_info_message = run_obj.update_admin_user()
    print("[SUCCESS] Update admin user info success") if update_admin_user_info_status else \
        print("[ERROR] Update admin user info error, error info: {}".format(update_admin_user_info_message))
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
        options.grafana_change_password
    )

# python3 init-ce-base.py --domain 192.168.56.11 --private_ip 192.168.56.11 --paas_username admin --paas_password 123456.coM --grafana_password grafana_password --grafana_change_password new_password

