#!/usr/bin/env python3
# coding:utf8
'''
python update_director.py
--domain https://domain
--paas_username guoyuchen
--paas_password ******
--run_env prod/dev  is not required, if not prod, use /t/, or not use /o/
--app_code cmdb cmp
'''

import requests
import sys
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()
        self.run_env = "o" if env == "prod" else "t"

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

    def update_director(self, app_code):
        if app_code == "bastion":
            API = self.paas_domain + "/{}/{}/api/{}/v0_1/sync_user_group/".format(self.run_env, app_code, app_code)
        else:
            API = self.paas_domain + "/{}/{}/api/{}/v0_1/update-director/".format(self.run_env, app_code, app_code)
        try:
            # 用于初次创建用户
            res = self.session.get(API)
            try:
                res.json()
            except:
                print("更新用户失败app_code: ", app_code)
                Exception(res.content.decode())
            if res.status_code == 200 and res.json().get("code") == 200:
                print("Update {} director success.".format(app_code))
                return True
            raise Exception(res.json().get("message"))
        except Exception as e:
            print("Api error, error info: {}, api url: {}.".format(str(e), API))
            # sys.exit(1)


def run(options):
    run_env = options.run_env if options.run_env else "prod"
    api_object = OpsAnyApi(
        options.domain,
        options.paas_username,
        options.paas_password,
        run_env
    )
    app_code = options.app_code
    if isinstance(app_code, list):
        for code in app_code:
            api_object.update_director(code)
    else:
        print("App code error: {}".format(app_code))
        sys.exit(1)


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.add_argument("--run_env", help="Run env", required=False)
    parameter.add_argument("--app_code", help="App code", nargs="+", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

"""
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code auto event k8s prom kbase
"""