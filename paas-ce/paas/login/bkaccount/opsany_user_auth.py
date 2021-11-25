# -*- coding: utf-8 -*-
import requests


class OpsAnyRbacUserAuth(object):
    RBAC_APP_CODE = "rbac"
    RBAC_APP_SECRET = "8a628f06-ed28-4d60-8ce8-458ae52efb6a"
    BK_URL = "https://dev.opsany.cn"
    ACCESS_TOKEN = "opsany-esb-auth-token-9e8083137204"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_users(self):
        API = "/api/c/compapi/rbac/user_auth/"
        url = self.BK_URL + API
        req = {
            "bk_app_code": self.RBAC_APP_CODE,
            "bk_app_secret": self.RBAC_APP_SECRET,
            "bk_access_token": self.ACCESS_TOKEN,
            "username": self.username,
            "password": self.password,
        }
        res = requests.post(url, json=req, headers={"Cookie": "bk_token=None"}, verify=False)
        data = res.json().get("data")
        if data:
            return data.get("auth_status"), data
        return False, {}

if __name__ == '__main__':
    auth_object = OpsAnyRbacUserAuth("guoyuchen@ldap", "123456.coM")
    res = auth_object.check_users()
    print res

