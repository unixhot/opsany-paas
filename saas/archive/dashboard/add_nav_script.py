"""
脚本说明：为Saas应用添加Nav导航

执行说明：
    python add_nav_script.py --paas_domain [paas_domain]
                             --paas_username [paas_username]
                             --paas_password [paas_password]
                             --config_file_path [config_file_path]
                             --run_env [run_env]
    例：python add_nav_script.py --paas_domain https://domain
                                --paas_username admin
                                --paas_password admin
                                --config_file_path /xx/xxx/xxx/config
                                --run_env dev

参数说明：
    paas_domain          必填
    paas_username        必填
    paas_password        必填
    config_file_path     必填
    run_env              非必填

Paas账号说明：
    必须要有工作台权限

第三方依赖：
    requests==2.25.0
"""
import json
import argparse
import requests
import configparser
import sys

# 去除本地python3 windows环境报错
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, config_file_path, run_env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()
        self.run_env = run_env
        self.config_info = self.get_config(config_file_path)

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code == 200:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):
        try:
            login_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(self.login_url, data=login_form, verify=False)
            if resp.status_code == 200:
                return self.session.cookies.get("bk_token")
            raise Exception("Login error.")
        except:
            print("Login error, please check your domain username password.")
            sys.exit(1)

    def get_config(self, config_file_path):
        read_install_config = configparser.ConfigParser()
        read_install_config.optionxform = lambda option: option
        try:
            read_install_config.read(config_file_path, encoding="utf-8")
            config_dict = dict(read_install_config)
            app_info = config_dict.get("APP_INFO")
            config_info = {}
            for key, value in app_info.items():
                config_info[key] = self.handle_value(value)
            return config_info
        except Exception as e:
            print('Read config file error, error info: {}.'.format(str(e)))
            sys.exit(1)

    def handle_value(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("'") or value.startswith('"'):
                value = value[1:]
            if value.endswith("'") or value.endswith('"'):
                value = value[:-1]
        return value

    def get_nav_group_id(self):
        try:
            API = "/{}/workbench/api/workbench/v0_1/nav-group/".format("t" if self.run_env == "dev" else "o")
            url = self.paas_domain + API
            response = self.session.get(url, verify=False)
            res = response.json().get("data")
            if res:
                group_id = ""
                for info in res:
                    if info.get("group_name") == self.config_info.get("APP_GROUP"):
                        group_id = info.get("id")
                        break
                if group_id:
                    return group_id
                raise Exception("Not find nav group id.")
        except Exception as e:
            print("Get nav group id error, error info: {}".format(str(e)))
            sys.exit(1)

    def upload_nav_icon(self):
        try:
            API = "/{}/workbench/api/workbench/v0_1/nav-icon/".format("t" if self.run_env == "dev" else "o")
            url = self.paas_domain + API
            file = {
                "icon": (
                    '{}.png'.format(self.config_info.get("APP_CODE")),
                    open('{}.png'.format(self.config_info.get("APP_CODE")), 'rb'),
                    'image/png',
                    {}
                )
            }
            response = self.session.post(url, files=file, verify=False)
            res = response.json().get("data")
            if res:
                return res.get("id")
            raise Exception(response.json().get("message", ""))
        except Exception as e:
            print("Upload nav icon error, error info: {}".format(str(e)))
            sys.exit(1)

    def add_nav_info(self):
        try:
            API = "/{}/workbench/api/workbench/v0_1/nav/".format("t" if self.run_env == "dev" else "o")
            url = self.paas_domain + API
            data = {
                "group_id": self.get_nav_group_id(),
                "nav_icon_id": self.upload_nav_icon(),
                "nav_name": self.config_info.get("APP_NAME"),
                "describe": self.config_info.get("APP_DESCRIBE"),
                "target": "_self",
                "nav_url": "/{}/{}/".format("t" if self.run_env == "dev" else "o", self.config_info.get("APP_CODE"))
            }
            response = self.session.post(url, data=json.dumps(data), verify=False)
            res = response.json().get("data")
            if res:
                return "Create app nav info success." if res.get("id") else "Create app nav info error."
            raise Exception(response.json().get("message", ""))
        except Exception as e:
            print("Add nav info error, error info: {}".format(str(e)))
            sys.exit(1)


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--paas_domain", help="Paas domain.", required=True)
    parameter.add_argument("--paas_username", help="Paas username.", required=True)
    parameter.add_argument("--paas_password", help="Paas password.", required=True)
    parameter.add_argument("--config_file_path", help="Config file path.", required=True)
    parameter.add_argument("--run_env", help="Run env.", required=False, default="prod")
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    paas_domain = options.paas_domain
    paas_username = options.paas_username
    paas_password = options.paas_password
    config_file_path = options.config_file_path
    run_env = options.run_env
    res = OpsAnyApi(paas_domain, paas_username, paas_password, config_file_path, run_env)
    info = res.add_nav_info()
    print(info)
