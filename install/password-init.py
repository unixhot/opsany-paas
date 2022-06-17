"""
执行说明：python password-init.py --username [Username] --password [Password] --new_password [New Password]
        --verify_code [Verify_code]
参数说明：
username         必填      当前面用户名
passowrd         必填      当前密码
new_password     必填      新的密码
verify_code      非必填    如果您开启了MFA则该参数为必填
第三方依赖：requests==2.25.0
"""
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
        if resp.status_code == 200:
            return resp.cookies["bklogin_csrftoken"]
        return None

    def login(self, verify_code=""):
        API = "/login/api/login/"
        URL = self.url + API
        login_form = {
            'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
            'username': self.username,
            'password': self.password,
            'verify_code': verify_code,
        }
        resp = self.session.post(URL, data=login_form, verify=False)
        if resp.status_code == 200 and resp.json().get("code") == 200:
            return True, ""
        return False, ""

    def set_new_password(self, password):
        API = "/login/accounts/user/password/"
        URL = self.url + API
        req = {
            "new_password": password,
        }
        res = self.session.put(URL, data=json.dumps(req), verify=False)
        try:
            flag = res.json().get("result")
            message = res.json().get("message")
            if not flag:
                return message.split(": ")[-1], flag
            else:
                return message, flag
        except Exception:
            return "Modify password error.", False


# 增加脚本参数
def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--paas_domain", help="Required parameters.", required=True)
    parameter.add_argument("--username", help="Admin user username.", default="admin", required=True)
    parameter.add_argument("--password", help="Admin user password.", default="admin", required=True)
    parameter.add_argument("--new_password", help="Admin user password.", default="admin", required=True)
    parameter.add_argument("--verify_code", help="Verify code.", default="", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    paas_domain = options.paas_domain
    username = options.username
    password = options.password
    new_password = options.new_password
    verify_code = options.verify_code if options.verify_code else ""
    bk_api = BkApi(paas_domain, username, password)
    status, res = bk_api.login(verify_code)
    print(status, res)
    if status:
        res, status = bk_api.set_new_password(new_password)
        if status:
            print("Set new password success, new password: {}".format(new_password))
        else:
            print("Set new password error, error info: {}".format(res))
    else:
        print("Login error, please check your username or password")
