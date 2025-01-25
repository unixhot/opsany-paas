from lib import base_action
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SendMail(base_action.OpsAnyCoreRestAPI):
    def run(self, receiver, subject, text):
        status, message = self.send_mail(receiver, subject, text, 1)
        if not status:
            return False, {"success": [], "error": {"message": message}}
        return True, {"success": {"message": message}, "error": []}
