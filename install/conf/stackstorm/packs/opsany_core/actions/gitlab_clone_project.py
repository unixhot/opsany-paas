from lib import base_action
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GitlabCloneProject(base_action.OpsAnyCoreRestAPI):
    def run(
            self,
            host_list,
            project_dir,
            project_url,
            api_token,
            depth=None,
            project_branch="master"):
        project_url_split = project_url.split("//")
        if len(project_url_split) != 2:
            return False, {"error": "project_url error"}
        api_token_url = "{http}//oauth2:{api_token}@{url}".format(
            http=project_url_split[0], api_token=api_token, url=project_url_split[-1])
        print("depth", depth)
        try:
            depth = int(depth)
        except Exception as e:
            depth = None
        if not depth:
            command = "cd {project_dir} && git clone -b {project_branch} {api_token_url}".format(
                project_dir=project_dir, project_branch=project_branch, api_token_url=api_token_url)
        else:
            command = "cd {project_dir} && git clone --depth {depth} -b {project_branch} {api_token_url}".format(
                project_dir=project_dir, depth=depth, project_branch=project_branch, api_token_url=api_token_url)
        print("command", command)
        status, requests_id = self.run_shell(host_list, command)
        if not status:
            return False, {
                "success": [],
                "error": {
                    "message": "Error: {}".format(str(requests_id))
                }
            }
        return self.get_return(requests_id)
