# -*- coding: utf-8 -*-
import requests
import settings
import json


class OpsAnyRbacUserAuth(object):
    APP_CODE = "rbac"
    APP_SECRET = "8a628f06-ed28-4d60-8ce8-458ae52efb6a"
    BK_URL = "{}://{}".format(settings.HTTP_SCHEMA, settings.PAAS_INNER_DOMAIN)
    ACCESS_TOKEN = "opsany-esb-auth-token-9e8083137204"

    def __init__(self, username, password=""):
        self.username = username
        self.password = password

    def check_users(self):
        API = "/api/c/compapi/rbac/user_auth/"
        url = self.BK_URL + API
        req = {
            "bk_app_code": self.APP_CODE,
            "bk_app_secret": self.APP_SECRET,
            "bk_access_token": self.ACCESS_TOKEN,
            "username": self.username,
            "password": self.password,
        }
        res = requests.post(url, json=req, headers={"Cookie": "bk_token=None"}, verify=False)
        data = res.json().get("data")
        if data:
            return data.get("auth_status"), data
        return False, {}

    def get_user_google_auth_status(self):
        API = "/api/c/compapi/rbac/get_user_google_auth_status/"
        req = {
            "bk_app_code": self.APP_CODE,
            "bk_app_secret": self.APP_SECRET,
            "bk_access_token": self.ACCESS_TOKEN,
            "username": self.username
        }
        url = self.BK_URL + API
        response = requests.get(url, params=req, headers={"Cookie": "bk_token=None"}, verify=False)
        end_data = json.loads(response.text)
        if end_data.get("result"):
            end_data = end_data.get("data")
            return end_data
        return "4"

    def check_google_verify_code(self, verify_code):
        API = "/api/c/compapi/rbac/check_google_verify_code/"
        req = {
            "bk_app_code": self.APP_CODE,
            "bk_app_secret": self.APP_SECRET,
            "bk_access_token": self.ACCESS_TOKEN,
            "username": self.username,
            "verify_code": verify_code
        }
        url = self.BK_URL + API
        response = requests.post(url, data=req, headers={"Cookie": "bk_token=None"}, verify=False)
        end_data = json.loads(response.text)
        if end_data.get("result"):
            end_data = end_data.get("data")
            return end_data
        return False


