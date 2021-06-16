# -*- coding: utf-8 -*-
import json
import random
from django.http.response import JsonResponse


class GeetestLibResult:

    def __init__(self):
        self.status = 0
        self.data = ''
        self.msg = ''

    def set_all(self, status, data, msg):
        self.status = status
        self.data = data
        self.msg = msg

    def __str__(self):
        return "GeetestLibResult{{status={0}, data={1}, msg={2}}}".format(self.status, self.data, self.msg)


class GeeTest:
    JSON_FORMAT = "1"
    NEW_CAPTCHA = True
    HTTP_TIMEOUT_DEFAULT = 5
    VERSION = "python-flask:3.1.1"
    GEETEST_CHALLENGE = "geetest_challenge"
    GEETEST_VALIDATE = "geetest_validate"
    GEETEST_SECCODE = "geetest_seccode"

    def __init__(self):
        self.libResult = GeetestLibResult()

    def build_register_result(self):
        challenge = "".join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 32))
        geetest_id = "".join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 32))
        data = json.dumps(
            {"success": 0, "gt": geetest_id, "challenge": challenge, "new_captcha": self.NEW_CAPTCHA})
        self.libResult.set_all(0, data, "")

    def local_init(self):
        self.build_register_result()
        return JsonResponse({
            "code": "200",
            "message": "相关信息信息获取成功",
            "data": json.loads(self.libResult.data),
        })
