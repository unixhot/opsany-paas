# coding=utf-8
import requests
import argparse
import json

# 去除本地python3 windows环境报错
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BkApi:
    def __init__(self, paas_domain, username, password, verify_code="", env="prod"):
        self.paas_domain = paas_domain
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.run_env = "o" if env == "prod" else "t"
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

    def register_online_saas(self, saas_app_code, saas_app_name, saas_app_version, saas_app_secret_key, is_update):
        API = "/saas/register-online-saas-app/"
        URL = self.paas_domain + API
        req = {
            "saas_file_name": "{}-opsany-{}.tar.gz".format(saas_app_code, saas_app_version),
            "saas_app_code": saas_app_code,
            "saas_app_name": saas_app_name,
            "saas_app_version": saas_app_version,
            "saas_app_secret_key": saas_app_secret_key,
        }
        if is_update in [1, "1", "true", "True"]:
            req["is_update"] = True
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
    parameter.add_argument("--is_update", help="is update.", default="", required=False)
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
    is_update = options.is_update
    bk_api = BkApi(paas_domain, username, password, verify_code)
    if bk_api.status:
        status, res = bk_api.register_online_saas(saas_app_code, saas_app_name, saas_app_version, saas_app_secret_key, is_update)
        if status:
            message = "{} SUCCESS: {}:{} ".format("Register Online SAAS" if not is_update else "Update SAAS Version", saas_app_code, saas_app_version)
        else:
            message = "{} ERROR, error info: {}".format("Register Online" if not is_update else "Update SAAS Version", res)
        print(message)
    else:
        print("Login ERROR: {}".format(bk_api.token))


    """
    # 注册SAAS
    python register_online_saas.py --paas_domain https://opsany.com --username admin --password admin --saas_app_code repo --saas_app_name 统一权限 --saas_app_version 2.3.0 --saas_app_secret_key bf4a54e0-a08a-4449-b3f4-1431ddbe4b31
    # 更新SAAS版本
    python register_online_saas.py --paas_domain https://opsany.com --username admin --password admin --saas_app_code rbac --saas_app_name 统一权限 --saas_app_version 2.2.2 --saas_app_secret_key bf4a54e0-a08a-4449-b3f4-1431ddbe4b31 --is_update true
    """