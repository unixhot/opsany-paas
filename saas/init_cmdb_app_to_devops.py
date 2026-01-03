#!/usr/bin/env python3
# coding:utf8
"""
将资源平台应用数据同步至应用平台，默认同步或更新业务、应用和服务，可重复执行
"""
import json

import requests
import sys
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    def init_cmdb_to_devops(self):
        API = self.paas_domain + "/o/devops/api/devops/v0_1/sync_cmdb_yw/"
        try:
            # 用于初次创建用户
            json_data = {"sync_type": "init"}
            res = self.session.post(API, json=json_data)
            try:
                res_data = res.json()
            except Exception as e:
                return "失败", res.content.decode()
            if res.status_code == 200 and res_data.get("code") == 200:
                return "成功", res_data.get("data")
            return "失败", res_data.get("message")
        except Exception as e:
            print("Api error, error info: {}, api url: {}.".format(str(e), API))
            return "错误", str(e)


def run(options):
    api_object = OpsAnyApi(
        options.domain,
        options.paas_username,
        options.paas_password,
    )
    status, message = api_object.init_cmdb_to_devops()
    print("资源平台应用数据导入应用平台{}：{}".format(status, message))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

"""
python3 init_cmdb_app_to_devops.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD}
"""
