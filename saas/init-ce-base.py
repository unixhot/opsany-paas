import os

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


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

    def update_user_info(self, user_id, user_info):
        API = "/login/accounts/user/{}/".format(user_id)
        self.session.cookies["bk_token"] = self.token
        headers = {
            "X-CSRFToken": self.csrfmiddlewaretoken
        }
        URL = self.paas_domain + API
        resp = self.session.put(URL, data=user_info, verify=False, headers=headers)
        if resp.status_code == 200:
            if resp.json().get("result"):
                return "更新成功", True
            return resp.json().get("message"), False
        return "服务器错误", False

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

    def init_celery_queue(self, queue):
        API = "/o/control/api/control/v0_1/celery-queue-init/"
        url = self.paas_domain + API
        res = self.session.post(url, json={"init_data_list": queue}, verify=False)
        try:
            res_data = res.json()
        except Exception:
            return False, "后台任务初始化中 API连接不成功，请检查API地址{}".format(res.content.decode())
        if res.status_code == 200:
            if str(res_data.get("code", "")) == "200":
                return True, "后台任务初始化成功！"
            else:
                return False, res_data.get("message")
        else:
            return False, "后台任务初始化中 API连接不成功，请检查API地址{}".format(url)


class Run:
    def __init__(self, paas_domain, private_ip, paas_username, paas_password, proxy_url, proxy_public_url, proxy_token):
        self.paas_domain = self.handle_domain(paas_domain)
        self.private_ip = self.handle_domain(private_ip)
        self.paas_username = paas_username if paas_username else default_paas_username
        self.paas_password = paas_password if paas_password else default_paas_password
        self.opsany_api_obj = OpsAnyApi("https://" + self.paas_domain, self.paas_username, self.paas_password)
        self.proxy_url = proxy_url
        self.proxy_public_url = proxy_public_url
        self.proxy_token = proxy_token

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
        controller_dict_v2 = {
            "name": "默认控制器",
            "type": "本地",
            # TEST DATA 8011 -> 8005
            "proxy_url": self.proxy_url,
            "proxy_public_url": self.proxy_public_url,
            "proxy_token": self.proxy_token,
        }
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.create_controller_salt(controller_dict_v2)
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
        message, status = self.opsany_api_obj.update_user_info(user_id_or_error_message, user_info)
        return status, message

    def init_celery_queue(self):
        saas_queue = [
            ("统一权限", "rbac", "celery", "1"),
            ("工作台", "workbench", "celery", "2"),
            ("资源平台", "cmdb", "celery", "3"),
            ("管控平台", "control", "celery", "4"),
            ("作业平台", "job", "celery", "5"),
            ("基础监控", "monitor", "celery", "6"),
            ("云管平台", "cmp", "celery", "7"),
            ("堡垒机", "bastion", "celery", "8"),
            ("应用平台", "devops", "celery", "9"),
            ("制品仓库", "repo", "celery", "17"),
            ("流水线", "pipeline", "celery", "17"),
            ("持续部署", "deploy", "celery", "18"),
        ]
        if self.opsany_api_obj.token:
            status, message = self.opsany_api_obj.init_celery_queue(saas_queue)
            if status:
                return True, message
            else:
                return False, message
        else:
            return False, "OpsAny平台认证失败"


def start(paas_domain, private_ip, paas_username, paas_password, proxy_url, proxy_public_url, proxy_token):
    run_obj = Run(paas_domain, private_ip, paas_username, paas_password, proxy_url, proxy_public_url, proxy_token)
    # 创建控制器
    create_controller_status, create_controller_message = run_obj.create_controller_salt()
    print("[SUCCESS] Create controller success") if create_controller_status else \
        print("[ERROR] Create controller error, error info: {}".format(create_controller_message))

    # 更新用户admin用户信息
    update_admin_user_info_status, update_admin_user_info_message = run_obj.update_admin_user()
    print("[SUCCESS] Update admin user info success") if update_admin_user_info_status else \
        print("[ERROR] Update admin user info error, error info: {}".format(update_admin_user_info_message))

    # 更新管控后台任务
    init_queue_status, init_queue_info_message = run_obj.init_celery_queue()
    print("[SUCCESS] Init Control Celery Queue info success") if init_queue_status else \
        print("[ERROR] Init Control Celery Queue info error, error info: {}".format(init_queue_info_message))
    print("[SUCCESS] ALL complete")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--private_ip", help="Required parameters.", required=True)
    parameter.add_argument("--proxy_url", help="Required parameters.", required=True)
    parameter.add_argument("--proxy_public_url", help="Required parameters.", required=True)
    parameter.add_argument("--proxy_token", help="Required parameters.", required=True)
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
        options.paas_password,
        options.proxy_url,
        options.proxy_public_url,
        options.proxy_token,
    )


"""
# 初始化 用户 控制器 任务队列
python3 init-ce-base.py --domain 192.168.56.11 --private_ip 192.168.56.11 --paas_username admin --paas_password Ops525df452 --proxy_url https://192.168.56.11:8011 --proxy_public_url https://192.168.56.11:8011 --proxy_token ed4158dfd-85df-956d-985d-58d98er41fr5

"""

