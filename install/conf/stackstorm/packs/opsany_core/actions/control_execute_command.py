from lib import base_action

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ControlRunCommand(base_action.OpsAnyCoreRestAPI):
    def run(self, host_list, shell_command):
        status, requests_id = self.run_shell(host_list, shell_command)
        if not status:
            return False, {
                "success": [],
                "error": {
                    "message": "Error: {}".format(str(requests_id))
                }
            }
        return self.get_return(requests_id)
