#!/usr/bin/env python3
# coding:utf8

import json

import requests
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, verify_code="", env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({"referer": paas_domain})
        self.session.verify = False
        self.run_env = "o" if env == "prod" else "t"
        self.username = username
        self.password = password
        self.login_url = self.paas_domain + "/login/api/v3/login/"
        self.status, self.token, self.csrfmiddlewaretoken = self.login(verify_code)

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

    def reset_login_sort(self):
        try:
            API = self.paas_domain + "/{}/rbac/api/rbac/v0_1/auth-admin-sort/".format(self.run_env)
            res = self.session.post(API)
            try:
                res_json = res.json()
            except:
                return False, res.content.decode()
            if res.status_code == 200 and res_json.get("code") == 200:
                return True, res_json.get("message")
        except Exception as e:
            return False, "Api error, error info: {}".format(str(e))


def run(options):
    run_env = options.run_env if options.run_env else "prod"
    api_object = OpsAnyApi(
        options.domain,
        options.paas_username,
        options.paas_password,
        options.verify_code or "",
        run_env
    )

    api_object.reset_login_sort()


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.add_argument("--verify_code", help="OpsAny verify_code.", required=False)
    parameter.add_argument("--run_env", help="Run env", required=False)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

"""
# 重置登录方式(当全部启用的登录方式无法使用, 可以重置全部登录方式!)
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD}
"""
