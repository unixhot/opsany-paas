from lib import base_action
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ControlRunScript(base_action.OpsAnyCoreRestAPI):


    def run(self, host_list, script_url, script_arg="", timeout=1800):
        status, requests_id = self.run_script(host_list, script_url, script_arg, timeout)
        if not status:
            return False, {
                "success": [],
                "error": {
                    "message": "Error: {}".format(str(requests_id))
                }
            }
        return self.get_return(requests_id)
