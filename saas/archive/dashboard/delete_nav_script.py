"""
脚本说明：为Saas应用添加Nav导航

执行说明：
    python delete_nav_script.py --paas_domain [paas_domain]
                                --paas_username [paas_username]
                                --paas_password [paas_password]
                                --run_env [run_env]
    例：python delete_nav_script.py --paas_domain https://domain
                                   --paas_username admin
                                   --paas_password admin
                                   --run_env dev

参数说明：
    paas_domain          必填
    paas_username        必填
    paas_password        必填
    run_env              非必填

Paas账号说明：
    必须要有工作台权限

第三方依赖：
    requests==2.25.0
"""
import json
import argparse
import requests
import sys

# 去除本地python3 windows环境报错
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, run_env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.username = username
        self.password = password
        self.run_env = run_env
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

    def get_target_nav_id(self):
        try:
            API = "/{}/workbench/api/workbench/v0_1/nav/".format("t" if self.run_env == "dev" else "o")
            url = self.paas_domain + API
            data = {}
            response = self.session.get(url, data=json.dumps(data), verify=False)
            res = response.json().get("data")
            if res:
                for _res in res:
                    if _res.get("nav_url") == "/{}/workbench/#/bigScreen/bigScreenList".format(
                            "t" if self.run_env == "dev" else "o"
                    ):
                        return _res.get("id")
                raise Exception("Not find target nav id.")
            raise Exception(response.json().get("message", ""))
        except Exception as e:
            print("Add nav info error, error info: {}".format(str(e)))
            sys.exit(1)

    def delete_nav_info(self):
        try:
            API = "/{}/workbench/api/workbench/v0_1/nav/".format("t" if self.run_env == "dev" else "o")
            url = self.paas_domain + API
            data = {
                "id": self.get_target_nav_id()
            }
            response = self.session.delete(url, data=json.dumps(data), verify=False)
            if response.json().get("code") == 200:
                return "Delete success."
            raise Exception(response.json().get("message", ""))
        except Exception as e:
            print("Delete nav error, error info: {}".format(str(e)))
            sys.exit(1)


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--paas_domain", help="Paas domain.", required=True)
    parameter.add_argument("--paas_username", help="Paas username.", required=True)
    parameter.add_argument("--paas_password", help="Paas password.", required=True)
    parameter.add_argument("--run_env", help="Run env.", required=False, default="prod")
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    paas_domain = options.paas_domain
    paas_username = options.paas_username
    paas_password = options.paas_password
    run_env = options.run_env
    res = OpsAnyApi(paas_domain, paas_username, paas_password, run_env)
    info = res.delete_nav_info()
    print(info)
