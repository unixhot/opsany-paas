from lib import base_action
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class NexusProject(base_action.OpsAnyCoreRestAPI):
    def run(self, host_list, project_dir, download_url, timeout=600):
        status, get_url = self.download_nexus_project(download_url)
        print("get_url", get_url)
        if not status:
            return False, {
                "success": {}, "error": {
                    "message": "download nexus project error({})".format(get_url)}}

        status, requests_id = self.post_file(
            host_list, file_url=get_url, file_path=project_dir)
        if not status:
            return False, {
                "success": [],
                "error": {
                    "message": "Error: {}".format(str(requests_id))
                }
            }
        return self.get_return(requests_id)
