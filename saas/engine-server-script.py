#!/usr/bin/env python3
# coding:utf8
import json

import requests
import sys
import argparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.cookies = None
        self.token = self.login()

        self.token = None

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
            resp = self.session.post(self.login_url, data=login_form, verify=False, headers=self.headers)
            if resp.status_code == 200:
                self.headers.update(self.session.headers)
                self.cookies = dict(self.session.cookies)
                return self.session.cookies.get("bk_token")
            return "", ""
        except:
            return "", ""

    def add_engine_server(self, server_ip, server_port, app_port, server_cate):
        API = self.paas_domain + "/engine/server/"
        try:
            server_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                "server_ip": server_ip,
                "server_port": server_port,
                "app_port": app_port,
                "server_cate": server_cate
            }
            self.headers.update({
                "Origin": self.paas_domain + "/engine/server/",
                "X-CSRFToken": self.csrfmiddlewaretoken,
            })
            self.cookies["bk_csrftoken"] = self.csrfmiddlewaretoken

            res = requests.post(API, data=server_form, headers=self.headers, cookies=self.cookies, verify=False)

            if res.status_code == 200 and res.json().get("code") == 200:
                return True, res.json()
            else:
                return True, res.json()
        except Exception as e:
            s = "Add Engine Server, error info: {}.".format(str(e))
            return False, {'result': False, "message": s}

    def active_engine_server(self, server_id):
        API = self.paas_domain + "/engine/server/active/"
        try:
            server_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                "server_id": server_id
            }
            self.headers.update({
                "Origin": self.paas_domain + "/engine/server/active/",
                "X-CSRFToken": self.csrfmiddlewaretoken,
            })
            self.cookies["bk_csrftoken"] = self.csrfmiddlewaretoken

            res = requests.post(API, data=server_form, headers=self.headers, cookies=self.cookies, verify=False)

            if res.status_code == 200 and res.json().get("code") == 200:
                return True, res.json()
            else:
                return True, res.json()
        except Exception as e:
            s = "Active Engine Server, error info: {}.".format(str(e))
            return False, {'result': False, "message": s}


def run(options):
    # run_env =  "prod"
    run_env =  "dev"
    api_object = OpsAnyApi(
        options.domain,
        options.paas_username,
        options.paas_password,
        run_env
    )
    if options.type == "active":
        status, message = api_object.active_engine_server(options.server_id)
        print(json.dumps(message, ensure_ascii=False))
    else:
        status, message = api_object.add_engine_server(options.server_ip,options.server_port,options.app_port,options.server_cate )
        print(json.dumps(message, ensure_ascii=False))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.add_argument("--server_ip", help="server_ip", required=False)
    parameter.add_argument("--server_port", help="server_port", required=False)
    parameter.add_argument("--app_port", help="app_port", required=False)
    parameter.add_argument("--server_id", help="server_id", required=False)
    parameter.add_argument("--server_cate", help="server_cate(tapp | app)", required=False)
    parameter.add_argument("--type", help="type(add | active)", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(options)

"""
python3 engine-server-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --server_ip 192.168.0.169 --server_port 8081 --app_port 8082 --server_cate tapp --type add
python3 engine-server-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --server_id 2 --type active
"""