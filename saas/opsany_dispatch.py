#!/usr/bin/env python3

"""
Send alarms to the OpsAny workbench
Python3
requests==2.23.0
脚本路径 /usr/lib/zabbix/alertscripts(Zabbix配置文件指定脚本目录)
脚本需要可执行权限
"""
import json
import sys

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SendAlertToOpsAny:
    
    def __init__(self, opsany_url, app_code, app_secret):
        self.opsany_url = opsany_url
        self.app_code = app_code
        self.app_secret = app_secret
    
    def send_out_message(self, parameter, operator, temp_id, subscribe_type=None, alert_info=None):
        API = "/api/c/compapi/workbench/post_info_to_user/"
        req = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
            "bk_username": operator,
            "operator": operator,
            "temp_id": temp_id,
            "subscribe_type": subscribe_type,
            "parameter": parameter,
            "alert_info": json.dumps(alert_info),
        }
        URL = self.opsany_url + API
        response = requests.post(url=URL, data=req, verify=False)
        try:
            end_data = response.json()
        except Exception as e:
            raise Exception("发送失败，请检查域名或其他参数是否正确：{}".format(response.content.decode()))

        if end_data.get("code") == 200:
            print("发送状态：{}".format(end_data.get("message")))
            return response.status_code
        else:
            raise Exception("发送失败，请检查参数是否正确：{}".format(end_data))
    
    def send(self, alert_sendto, alert_subject, alert_message):
        parameter = '("""{}""", """{}""")'.format(alert_subject, alert_message)
        alert_info = {
            "alert_subject": alert_subject,
            "alert_message": alert_message,
        }
        return self.send_out_message(parameter, alert_sendto, 7001, alert_info=alert_info)


def main():
    opsany_url = sys.argv[1]
    app_code = sys.argv[2]
    app_secret = sys.argv[3]
    alert_sendto = sys.argv[4]
    alert_subject = sys.argv[5]
    alert_message = sys.argv[6]
    
    if len(sys.argv) != 7:
        mes = "参数异常：OpsAny地址 应用ID 应用TOKEN OpsAny接收人用户名 告警标题 告警内容"
        raise Exception(mes)
    
    if not opsany_url:
        raise Exception("OpsAny地址不能为空")
    
    if "http" not in opsany_url:
        raise Exception("OpsAny地址请添加前缀 http")
    
    if not app_code:
        raise Exception("应用ID不能为空")
    
    if not app_secret:
        raise Exception("应用TOKEN不能为空")
    
    if not alert_sendto:
        raise Exception("接收人不能为空")
    
    if not alert_subject:
        raise Exception("告警标题不能为空")
    
    if not alert_message:
        raise Exception("告警内容不能为空")
    
    SendAlertToOpsAny(opsany_url, app_code, app_secret).send(alert_sendto, alert_subject, alert_message)


if __name__ == '__main__':
    main()
