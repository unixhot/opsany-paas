import argparse
import json

import requests
import urllib3

urllib3.disable_warnings()


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

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code in [200, 400]:
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
            return ""
        except:
            return False

    def batch_import_pipeline(self):
        """批量导入流水线"""
        try:
            NAV_API = "/o/pipeline//api/pipeline/v0_1/batch-import-pipeline/"
            # NAV_API = "/api/pipeline/v0_1/batch-import-pipeline/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data_json = json.dumps({"jobs": jobs})
            response = self.session.post(url=NAV_GROUP_URL, data=data_json, verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)


def start(paas_domain, username, password):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)

    # 批量导入流水线
    status, add_data = run_obj.batch_import_pipeline()
    if status:
        print("[SUCCESS] batch import pipeline success")
        success = add_data[0]
        error = add_data[1]
        print("导入成功 {} 条，失败 {} 条".format(len(success), len(error)))
        for i in range(0, len(error)):
            print(i, ".", error[i])
        print("导入成功 {} 条，失败 {} 条".format(len(success), len(error)))
        print("[SUCCESS] batch import pipeline success")
    else:
        print("[ERROR] batch import pipeline, error info: {}".format(add_data))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="OpsAny URL.", required=True)
    parameter.add_argument("--paas_username", help="OpsAny Username.", required=False)
    parameter.add_argument("--paas_password", help="OpsAny Password.", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    """
    a = {
        "OpsAny": [
            {
                "env": "uat",
                "script_name": "tianyi",
                "startswith": "Uat环境-",
                "job_name_list": ["HUXINGQI-uat1", "HUXINGQI-uat2"],
            },
            {
                "env": "pro",
                "script_name": "ali",
                "startswith": "Pro环境-",
                "job_name_list": ["HUXINGQI-pro1", "HUXINGQI-pro2"],
            }
        ]
    }
    """
    jobs = {}

    parameter = add_parameter()
    options = parameter.parse_args()
    start(
        options.domain,
        options.paas_username,
        options.paas_password,
    )

"""
python3 pipeline_batch_import.py --domain https://demo.opsany.com --paas_username admin --paas_password 123456
python pipeline_batch_import.py --domain http://192.168.0.13:8012 --paas_username huxingqi --paas_password 123456
"""
