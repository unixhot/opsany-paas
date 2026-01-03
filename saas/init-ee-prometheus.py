#! /usr/bin/python3
# -*- coding: utf8 -*-


import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class OpsAnyApi:
    def __init__(self, paas_domain, username, password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({"referer": paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.username = username
        self.password = password
        self.login_url = self.paas_domain + "/login/api/v3/login/"
        self.status, self.token, self.csrfmiddlewaretoken = self.login()

    def login(self, verify_code=""):
        try:
            json_data = {"username": self.username, "password": self.password, "verify_code": verify_code,
                         "auth_type": "1"}
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
    def init_control_prometheus(self, prom_dict):
        try:
            CONTROL_API = "/o/control//api/control/v0_1/controller-prom-init/"
            CONTRO_URL = self.paas_domain + CONTROL_API
            response = self.session.put(url=CONTRO_URL, data=json.dumps(prom_dict), verify=False)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("code") != 200:
                    return False, json_data.get("message")
                return True, response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return True, res.get("data") or res.get("message")
            else:
                return False, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return False, str(e)


def start(paas_domain, username, password, prom_dict):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)

    # 1. 初始化管控平台Prometheus相关服务
    status, message = run_obj.init_control_prometheus(prom_dict)
    print("[SUCCESS] Init Control Prometheus Success.") if status else print(
        "[ERROR] Init Control Prometheus Error, error info: {}".format(str(message)))


def add_parameter():
    parameter = argparse.ArgumentParser("init-ee-prometheus")
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--local_ip", help="local_ip prometheus consul alertmanager server ip.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--prom_username", help="Prometheus username.", required=True)
    parameter.add_argument("--prom_password", help="Prometheus password.", required=True)
    parameter.add_argument("--consul_token", help="Consul token.", required=True)
    parameter.add_argument("--alertmanager_username", help="Alertmanager username.", required=True)
    parameter.add_argument("--alertmanager_password", help="Alertmanager Password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain  # 域名
    local_ip = options.local_ip  # 内网地址
    username = options.username  # 平台用户名
    password = options.password  # 平台密码
    prom_username = options.prom_username  # Prometheus服务用户名
    prom_password = options.prom_password  # Prometheus服务密码
    consul_token = options.consul_token  # Consul服务token
    alertmanager_username = options.alertmanager_username  # Alertmanager服务用户名
    alertmanager_password = options.alertmanager_password  # Alertmanager服务密码

    prom_dict = {
        "name": "内置Prometheus",
        "description": "",
        "data_type": "init",
        "default": True,
        "prom_url": f"http://{local_ip}:9090",
        "prom_username": prom_username,
        "prom_password": prom_password,
        "consul_url": f"http://{local_ip}:8500",
        "consul_password": consul_token,
        "alertmanager_url": f"http://{local_ip}:9093",
        "alertmanager_username": alertmanager_username,
        "alertmanager_password": alertmanager_password,
        "basic_auth": True,
        "consul_basic_auth": True,
        "alertmanager_basic_auth": True,
    }

    start(f"https://{domain}", username, password, prom_dict=prom_dict)

"""
1. 执行init-ee-prometheus.py脚本，需要部署社区版OpsAny并成功部署Prometheus服务，Consul服务，Alertmanager服务
2. 执行init-ee-prometheus.py脚本，需要检测管控平台服务是否正常，Grafana服务是否正常

python3 init-ee-prometheus.py --domain 192.168.56.11 --local_ip 10.0.0.73 --username admin --password 123456 --prom_username  admin --prom_password OpsAny@2024  --consul_token OpsAny@2024 --alertmanager_username admin --alertmanager_password OpsAny@2024
"""
