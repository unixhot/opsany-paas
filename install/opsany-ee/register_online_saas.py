# coding=utf-8
import requests
import argparse
import json

# 去除本地python3 windows环境报错
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BkApi:
    def __init__(self, paas_domain, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.url = paas_domain
        self.session.headers.update({'referer': self.url})
        self.csrfmiddlewaretoken = self.get_csrftoken()

    def get_csrftoken(self):
        API = "/login/"
        URL = self.url + API
        resp = self.session.get(URL, verify=False)
        if resp.status_code in [200, 400]:
            return resp.cookies["bklogin_csrftoken"]
        return None

    def login(self, verify_code=""):
        API = "/login/api/login/"
        URL = self.url + API
        login_form = {
            'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
            'username': self.username,
            'password': self.password,
            'init': "login.init",
            'verify_code': verify_code,
        }
        resp = self.session.post(URL, data=login_form, verify=False)
        if resp.status_code == 200 and resp.json().get("code") == 200:
            return True, ""
        return False, resp.json().get("message")

    def register_online_saas(self, saas_app_code, saas_app_name, saas_app_version, saas_app_secret_key):
        API = "/saas/register-online-saas-app/"
        URL = self.url + API
        req = {
            "saas_file_name": "{}-opsany-{}.tar.gz".format(saas_app_code, saas_app_version),
            "saas_app_code": saas_app_code,
            "saas_app_name": saas_app_name,
            "saas_app_version": saas_app_version,
            "saas_app_secret_key": saas_app_secret_key,
			"csrfmiddlewaretoken": self.csrfmiddlewaretoken
        }
        res = self.session.get(URL, params=req, verify=False)
        try:
            try:
                res_data = res.json()
            except Exception:
                return False, "PAAS服务异常请联系管理员或查看PAAS日志：".format(str(res.content.decode()))
            flag = res_data.get("result")
            message = res_data.get("message")
            if not flag:
                return flag, message
            else:
                return flag, message
        except Exception as e:
            return False, "注册脚本异常请联系管理员：{}".format(str(e))


# 增加脚本参数
def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--paas_domain", help="Required parameters.", required=True)
    parameter.add_argument("--username", help="Admin user username.", default="admin", required=True)
    parameter.add_argument("--password", help="Admin user password.", default="admin", required=True)
    parameter.add_argument("--saas_app_code", help="Saas App Code.", required=True)
    parameter.add_argument("--saas_app_name", help="Saas App Name.", required=True)
    parameter.add_argument("--saas_app_version", help="Saas App Version.", required=True)
    parameter.add_argument("--saas_app_secret_key", help="Saas App Secret Key.", required=True)
    parameter.add_argument("--verify_code", help="Verify code.", default="", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    paas_domain = options.paas_domain
    username = options.username
    password = options.password
    saas_app_code = options.saas_app_code
    saas_app_name = options.saas_app_name
    saas_app_version = options.saas_app_version
    saas_app_secret_key = options.saas_app_secret_key
    verify_code = options.verify_code if options.verify_code else ""
    bk_api = BkApi(paas_domain, username, password)
    status, res = bk_api.login(verify_code)
    if status:
        # res, status = bk_api.set_new_password(password)
        status, res = bk_api.register_online_saas(saas_app_code, saas_app_name, saas_app_version, saas_app_secret_key)
        if status:
            print("Register Online SAAS SUCCESS: {} ".format(saas_app_code))
        else:
            print("Register Online SAAS ERROR, error info: {}".format(res))
    else:
        print("Login ERROR: {}".format(res))


    """
    python register_online_saas.py --paas_domain https://opsany.com --username admin --password admin --saas_app_code rbac --saas_app_name 统一权限 --saas_app_version 1.7.0 --saas_app_secret_key bf4a54e0-a08a-4449-b3f4-1432ddbe4b31
    """