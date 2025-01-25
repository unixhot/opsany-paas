from lib import base_action
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SendMessage(base_action.OpsAnyCoreRestAPI):
    def run(self, name, message_title, message_info, task_name, notify_object_list):
        try:
            qw_robot_list = []
            dd_robot_list = []
            enabled_user_dict = {}
            for notify_object in notify_object_list:
                message_type = notify_object.get("type")
                target_value = notify_object.get("target_value")
                checked_message_type = notify_object.get("checked_message_type")
                if checked_message_type:
                    checked_message_type = checked_message_type.replace(",", "")
                if message_type == "1":
                    enabled_user_dict[target_value] = checked_message_type
                elif message_type == "3":
                    qw_robot_list.append(target_value)
                elif message_type == "4":
                    dd_robot_list.append(target_value)

            parameter = "('{}', '{}', '{}', '{}')".format(name, message_title, message_info, task_name)
            alert_info = {
                "step_name": name,
                "message_title": message_title,
                "message_info": message_info,
                "task_name": task_name
            }
            notify_qw_object_list, notify_dd_object_list = [], []
            username_dict = {}
            if qw_robot_list:
                notify_qw_object_list = self.send_robot(20, parameter, ",".join(qw_robot_list), {}, "qw")
            if dd_robot_list:
                notify_dd_object_list = self.send_robot(20, parameter, ",".join(dd_robot_list), {}, "dd")
            for username, checked_message_type_list in enabled_user_dict.items():
                print("subscribe_type", checked_message_type_list, type(checked_message_type_list))
                send_dict = self.send_out_message(20, checked_message_type_list, parameter, username,
                                                  alert_info)
                username_dict[username] = send_dict.get("data") or {}
            end_data = {
                "username_dict": username_dict,
                "notify_qw_object_list": notify_qw_object_list,
                "notify_dd_object_list": notify_dd_object_list
            }
            return True, {"success": {"message": end_data}, "error": []}
        except Exception as e:
            return False, {"success": [], "error": {"message": str(e)}}
