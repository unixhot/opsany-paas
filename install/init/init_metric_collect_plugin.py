import os

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class OpsAnyApi:
    def __init__(self, paas_domain, username, password, env="prod"):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.username = username
        self.password = password
        self.init_plugin_url = "/{}/control/api/control/v0_1/init-metric-collect-import/"
        self.run_env = "o" if env == "prod" else "t"
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

    def init_plugin(self, name, json_data):
        api = self.paas_domain + self.init_plugin_url.format(self.run_env)
        try:
            res = self.session.post(api, data=json.dumps(json_data), verify=False)
            try:
                res_data = res.json()
            except Exception as e:
                raise Exception(res.content.decode())
            if res.status_code == 200:
                if res_data.get("code") == 200:
                    return True, res_data.get("message")
            raise Exception(res_data.get("message"))
        except Exception as e:
            return False, "初始化监控插件失败: {}, {}".format(name, str(e))

    def get_plugin_list(self, target_path, file_type=".json"):
        try:
            target_file_dict = {}
            if target_path:
                files = os.listdir(target_path)
                for file in files:
                    if file.lower().endswith(file_type):
                        full_path = os.path.join(target_path, file)
                        with open(full_path, "r", encoding="utf-8") as f:
                            target_file_dict[full_path] = json.loads(f.read())
            if target_file_dict:
                print("Find Metric Collect Plugin: {}, total: {} files, the import will be performed.".format(
                    ", ".join(list(target_file_dict.keys())), len(target_file_dict)))
                return target_file_dict
            else:
                print("Not find valid file.")
                return {}
                # sys.exit(0)
        except Exception as e:
            print("Get target file error, error info: {}".format(str(e)))
            # sys.exit(1)
            return {}


def run(domain, paas_username, paas_password, target_path="./alert-rules"):
    api = OpsAnyApi(domain, paas_username, paas_password)

    # 初始化应用监控告警规则
    plugin_dict = api.get_plugin_list(target_path)
    success, error = 0, 0
    error_message = ""
    for k, v in plugin_dict.items():
        status, message = api.init_plugin(k, v)
        if status: success += 1
        else:
            error += 1
            error_message += f"{k}: {message}\n"
        break
    print(f"初始化指标采集插件结束: 成功: {success} 条!, 失败: {error} 条!")
    if error: print(error_message)


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="Required parameters.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=True)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == "__main__":
    parameter = add_parameter()
    options = parameter.parse_args()
    rules_path = "metric-collect-plugin"
    run(options.domain, options.paas_username, options.paas_password, target_path=rules_path)
    # 初始化 告警规则和通知规则
    # python init_alert_rule.py  --domain https://DOMAIN --paas_username admin --paas_password 123456
