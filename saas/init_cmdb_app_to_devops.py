#!/usr/bin/env python3
# coding:utf8
"""
将资源平台应用数据同步至应用平台，默认同步或更新业务、应用和服务，可重复执行
"""

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
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()

    def get_csrftoken(self):  # sourcery skip: do-not-use-bare-except
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code in [200, 400]:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):  # sourcery skip: do-not-use-bare-except
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
