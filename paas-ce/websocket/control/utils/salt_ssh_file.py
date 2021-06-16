# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

import urllib.request
import urllib.parse
import json
import requests
import ssl
import os, stat, re

from config import ROSTER_FILE_URL
from config import SALT_SSH_FILE_URL
from control.utils.encryption import PasswordEncryption


ssl._create_default_https_context = ssl._create_unverified_context


class SaltAPI(object):
    __token_id = ''

    def __init__(self, url, user, passwd):
        self.__url = url
        self.__user = user
        self.__password = passwd
        self.__token_id = self.get_token_id()
        # print(self.__token_id)

    def get_token_id(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        
        try:
            # obj = urllib.parse.urlencode(params).encode('utf-8')
            url = str(self.__url) + '/login'
            # req = urllib.request.Request(url, obj, verify=False)
            # opener = urllib.request.urlopen(req, timeout=2)
            # content = json.loads(opener.read())
            res_token = requests.post(url, json=params, timeout=2, verify=False)
            # print("res_token", res_token.json())
            content = res_token.json()
            token_id = content['return'][0]['token']
        except Exception as e:
            print(e)
            return 0
        return token_id

    def post_request(self, data, prefix='/', timeout=None):
        url = str(self.__url) + prefix
        headers = {'X-Auth-Token': self.__token_id, 'Content-type': 'application/json'}
        try:
            # 解析成json
            data = bytes(json.dumps(data), 'utf8')
            req = urllib.request.Request(url, data, headers)
            opener = urllib.request.urlopen(req, timeout=timeout)
            content = json.loads(opener.read())
        except Exception as e:
            return print(str(e))
        return content

    def list_all_key(self):
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]['data']['return']
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def delete_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        content = self.post_request(params, timeout=10)
        # print("content", content)
        if isinstance(content, dict):
            return content['return'][0]['data']['success']
        else:
            return {"status": False, "message": "salt api error : " + content if content else ''}

    def accept_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        content = self.post_request(params, timeout=10)
        # print("content", content)
        if isinstance(content, dict):
            return content['return'][0]['data']['return']
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def ping_check(self, node_name):
        params = {'client': 'local', 'tgt': node_name, 'fun': 'test.ping'}
        content = self.post_request(params, timeout=10)
        # print("content", content)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def reject_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.reject', 'match': node_name}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]['data']['success']
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def remote_noarg_execution(self, tgt, fun, types="tgt_type"):
        # Execute commands without parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, types: 'list'}
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            ret = content['return'][0][tgt]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_noarg_execution(tgt, fun, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def remote_noarg_execution_notgt(self, tgt, fun, types="tgt_type"):
        # Execute commands without parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, types: 'list'}
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_noarg_execution_notgt(tgt, fun, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def remote_execution(self, tgt, fun, arg, types="tgt_type"):
        # Command execution with parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            ret = content['return'][0][tgt]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_execution(tgt, fun, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def remote_execution_notgt(self, tgt, fun, arg, types="tgt_type"):
        # Command execution with parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_execution_notgt(tgt, fun, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def shell_remote_execution(self, tgt, arg, timeout=None, types="tgt_type"):
        # Shell command execution with parameters
        # Changed in version 2017.7.0: Renamed from expr_form to tgt_type
        params = {'client': 'local', 'tgt': tgt, 'fun': 'cmd.run', "arg": arg, types: 'list'}
        print(params)
        content = self.post_request(params, timeout=timeout)
        if isinstance(content, dict):
            print(content)
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.shell_remote_execution(tgt, arg, timeout=60, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def ssh_shell_remote_execution(self, tgt, arg, types="tgt_type"):
        # 暂时不用
        # Shell command execution with parameters
        # Changed in version 2017.7.0: Renamed from expr_form to tgt_type
        params = {'client': 'ssh', 'tgt': tgt, 'fun': 'test.ping', 'arg': arg, types: 'list'}
        print(params)
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            print(content)
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.shell_remote_execution(tgt, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def shell_remote_execution_sync(self, tgt, arg, types="tgt_type"):
        # 暂时不用
        # Shell command execution with parameters
        # Changed in version 2017.7.0: Renamed from expr_form to tgt_type

        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'cmd.run', 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout=1200)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.shell_remote_execution(tgt, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def grain(self, tgt, arg):
        # Grains.item
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.item', 'arg': arg}
        content = self.post_request(params, timeout=30)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def grains(self, tgt):
        # Grains.items
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.items'}
        content = self.post_request(params, timeout=30)
        if isinstance(content, dict):
            return {"status": True, "message": "", "data": content['return'][0]}
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    # def target_remote_execution(self, tgt, fun, arg):
    #     # Use targeting for remote execution
    #     params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'nodegroup'}
    #     content = self.post_request(params)
    #     if isinstance(content, dict):
    #         jid = content['return'][0]['jid']
    #         return jid
    #     else:
    #         return {"status": False, "message": "Salt API Error : " + content}

    def deploy(self, tgt, arg):
        # Module deployment
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
        return self.post_request(params, timeout=10)

    def async_deploy(self, tgt, arg):
        # Asynchronously send a command to connected minions
        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]['jid']
        else:
            return {"status": False, "message": "salt api error : " + content if content else ''}

    def target_deploy(self, tgt, arg, types="tgt_type"):
        # Based on the list forms deployment
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            try:
                ret = content.get("return")[0]
                # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
                if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                    return self.target_deploy(tgt, arg, types="expr_form")
                return ret
            except Exception as e:
                return {"status": False, "message": str(e)}
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def pillar_items(self, tgt, arg=[], types="tgt_type"):
        # Get pillar item
        if arg:
            params = {'client': 'local', 'tgt': tgt, 'fun': 'pillar.item', 'arg': arg, types: 'list'}
        else:
            params = {'client': 'local', 'tgt': tgt, 'fun': 'pillar.items', 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            try:
                ret = content.get("return")[0]
                # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
                if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                    return self.pillar_items(tgt, arg=[], types="expr_form")
                return ret
            except Exception as e:
                return {"status": False, "message": str(e)}
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def jobs_list(self):
        # Get Cache Jobs Default 24h '''
        url = self.__url + '/jobs/'
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        try:
            opener = urllib.request.urlopen(req)
            content = json.loads(opener.read())
        except Exception as e:
            return str(e)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def jobs_info(self, arg):
        # Get Job detail info '''
        url = self.__url + '/jobs/' + arg
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        try:
            opener = urllib.request.urlopen(req)
            content = json.loads(opener.read())
        except Exception as e:
            return str(e)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def stats(self):
        # Expose statistics on the running CherryPy server
        url = self.__url + '/stats'
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib.request.Request(url, headers=headers)
        try:
            opener = urllib.request.urlopen(req)
            content = json.loads(opener.read())
        except Exception as e:
            return str(e)
        if isinstance(content, dict):
            return content
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def runner_status(self, arg):
        # Return minion status
        params = {'client': 'runner', 'fun': 'manage.' + arg}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def runner(self, arg):
        # Return minion status
        params = {'client': 'runner', 'fun': arg}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def events(self):
        # SSE get job info '''
        url = self.__url + '/events'
        headers = {'X-Auth-Token': self.__token_id}
        req = requests.get(url, stream=True, headers=headers)
        return req

    def hook(self, tag=""):
        # Fire an event in Salt with a custom event tag and data
        url = self.__url + '/hook/' + tag
        headers = {'X-Auth-Token': self.__token_id}
        # data = json.dumps({"gitfs": "update"})
        # data = bytes(data, 'utf8')
        req = urllib.request.Request(url, headers=headers, method="POST")
        try:
            opener = urllib.request.urlopen(req)
            content = json.loads(opener.read())
        except Exception as e:
            return str(e)
        if isinstance(content, dict):
            return content
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def network(self, tgt=""):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'network.netstat'}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def filestats(self, tgt="", arg="/etc/shadow"):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'file.stats', 'arg': arg}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}

    def psinfo(self, tgt=""):
        # params = {'client': 'local', 'tgt': tgt, 'fun': 'ps.psaux', 'arg': '.*'}
        params = {'client': 'local', 'tgt': tgt, 'fun': 'cmd.run', 'arg': 'ps -auxwww'}
        content = self.post_request(params, timeout=10)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content if content else ''}


class SaltSshBase(object):
    def __init__(self, master: dict):
        self.master_url1 = master.get("api1")
        self.master_url2 = master.get("api2")
        self.username1 = master.get("username1")
        self.username2 = master.get("username2")
        self.password1 = master.get("password1")
        self.password2 = master.get("password2")
        self.state1 = master.get("state1")
        self.state2 = master.get("state2")
        self.salt = self.test_saltapi()
        self.download_base_url1 = self.get_download_base_url(self.master_url1)
        self.download_base_url2 = self.get_download_base_url(self.master_url2)

    # 获取下载地址
    def get_download_base_url(self, api:str):
        """
        https://xxx.xx.xxx.xx:xxxx
        http://xxx.xx.xxx.xx:xxxx
        """
        lt = api.split(":")
        s = ""
        if len(lt) >= 3:
            s += lt[1][2:]
            return s
        else:
            return s

    # 测试控制器API
    def test_saltapi(self):
        self.salt_obj_1 = SaltAPI(self.master_url1, self.username1, self.password1)
        url_token_1 = self.salt_obj_1.get_token_id()

        self.salt_obj_2 = SaltAPI(self.master_url2, self.username2, self.password2)
        url_token_2 = self.salt_obj_2.get_token_id()
        if isinstance(url_token_1, str):
            self.state1 = True
            
            if isinstance(url_token_2, str):
                self.state2 = True
            else:
                self.state2 = False
            return self.salt_obj_1
        self.state1 = False
        if isinstance(url_token_2, str):
            self.state2 = True
        else:
            self.state2 = False
        return self.salt_obj_2

    # 重启
    def restart_salt(self, new_data):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        # file_name = ROSTER_FILE_URL
        # file_name = "/opt/dev-paas/paas-agent/paas_agent/apps/projects/control/code/control/static/salt/roster.yaml"
        # command = "salt-ssh --roster-file={} '{}' state.sls agent.restart".format(file_name, name)
        # command = "salt-ssh '{}' state.sls agent.restart".format(name)

        ssh_type = new_data.get("ssh_type")
        name = new_data.get("name")
        username = new_data.get("username")
        password = self.decrypt_password(new_data.get("password"))

        restart_command = "/usr/local/opsany-agent/agent.sh restart all"
        if ssh_type != "key":  # 判定是否是秘钥
            command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r '{}'".format(username, password, name, restart_command)

        else:
            pri_key_file = SALT_SSH_FILE_URL + "/" + name
            command = "salt-ssh -i '{}' --priv={} -r '{}'".format(name, pri_key_file, restart_command)
        if not isinstance(self.salt, bool):
            respones = self.salt.shell_remote_execution("master-local", command)
            end = "salt-minion: started" in respones.get("master-local", "")
            return end
        return False

    # 卸载
    def uninstall_salt(self, new_data):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        # file_name = ROSTER_FILE_URL
        # file_name = "/opt/dev-paas/paas-agent/paas_agent/apps/projects/control/code/control/static/salt/roster.yaml"
        # command = "salt-ssh --roster-file={} '{}' state.sls agent.uninstall".format(file_name, name)
        # command = "salt-ssh '{}' state.sls agent.uninstall".format(name)

        ssh_type = new_data.get("ssh_type")
        name = new_data.get("name")
        username = new_data.get("username")
        password = self.decrypt_password(new_data.get("password"))
        # 获取当前agent的控制IP
        ip = new_data.get("ip")

        if self.state1:
            DOWENLOAD_BASE_URL = self.download_base_url1
        else:
            if self.state2:
                re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
                c = re.findall(re_rule, ip)
                if len(c) > 0:
                    DOWENLOAD_BASE_URL = self.download_base_url2
                else:
                    DOWENLOAD_BASE_URL = self.download_base_url1
            else:
                DOWENLOAD_BASE_URL = self.download_base_url1
        if DOWENLOAD_BASE_URL:

            uninstall_command = "curl -s --insecure -o /usr/local/agent-install.sh http://{}/uploads/agent/agent-install.sh " \
                                "&& /bin/bash /usr/local/agent-install.sh remove {} {}".format(DOWENLOAD_BASE_URL, DOWENLOAD_BASE_URL, name)

            if ssh_type != "key":  # 判定是否是秘钥
                command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r '{}'".format(username, password, name, uninstall_command)
            else:
                pri_key_file = SALT_SSH_FILE_URL + "/" + name
                command = "salt-ssh -i '{}' --priv={} -r '{}'".format(name, pri_key_file, uninstall_command)
            if not isinstance(self.salt, bool):
                respones = self.salt.shell_remote_execution("master-local", command)
                end = "{}:\n    ----------\n    retcode:\n        0\n".format(name) in respones.get("master-local")
                return end
        return False

    # 停止服务
    def stop_salt(self, new_data):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        # file_name = ROSTER_FILE_URL
        # file_name = "/opt/dev-paas/paas-agent/paas_agent/apps/projects/control/code/control/static/salt/roster.yaml"
        # command = "salt-ssh --roster-file={} '{}' -r systemctl stop salt-minion".format(file_name, name)

        ssh_type = new_data.get("ssh_type")
        name = new_data.get("name")
        username = new_data.get("username")
        password = self.decrypt_password(new_data.get("password"))

        stop_command = "/usr/local/opsany-agent/agent.sh stop all"

        if ssh_type != "key":  # 判定是否是秘钥
            command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r '{}'".format(username, password, name, stop_command)
        else:
            pri_key_file = SALT_SSH_FILE_URL + "/" + name
            command = "salt-ssh -i '{}' --priv={} -r '{}'".format(name, pri_key_file, stop_command)
        if not isinstance(self.salt, bool):
            respones = self.salt.shell_remote_execution("master-local", command)
            end = "{}:\n    ----------\n    retcode:\n        0\n".format(name) in respones.get("master-local")
            return end
        return False

    # 删除
    def delete_salt(self, new_data):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        # file_name = ROSTER_FILE_URL
        # file_name = "/opt/dev-paas/paas-agent/paas_agent/apps/projects/control/code/control/static/salt/roster.yaml"
        # command = "salt-ssh --roster-file={} '{}' state.sls agent.remove".format(file_name, name)
        # command = "salt-ssh '{}' state.sls agent.remove".format(name)
        ssh_type = new_data.get("ssh_type")
        name = new_data.get("name")
        username = new_data.get("username")
        password = self.decrypt_password(new_data.get("password"))
        ip = new_data.get("ip")

        # 获取当前agent的控制IP
        if self.state1:
            DOWENLOAD_BASE_URL = self.download_base_url1
        else:
            if self.state2:
                re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
                c = re.findall(re_rule, ip)
                if len(c) > 0:
                    DOWENLOAD_BASE_URL = self.download_base_url2
                else:
                    DOWENLOAD_BASE_URL = self.download_base_url1
            else:
                DOWENLOAD_BASE_URL = self.download_base_url1
        if DOWENLOAD_BASE_URL:
            delete_command = "curl -s --insecure -o /usr/local/agent-install.sh http://{}/uploads/agent/agent-install.sh " \
                            "&& /bin/bash /usr/local/agent-install.sh remove {} {}".format(DOWENLOAD_BASE_URL, DOWENLOAD_BASE_URL, name)

            if ssh_type != "key":  # 判定是否是秘钥
                command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r '{}'".format(username, password, name, delete_command)

            else:
                pri_key_file = SALT_SSH_FILE_URL + "/" + name
                command = "salt-ssh -i '{}' --priv={} -r '{}'".format(name, pri_key_file, delete_command)
            # command = "salt-ssh --no-host-keys '{}' -r '{}'".format(name, delete_command)
            if not isinstance(self.salt, bool):
                respones = self.salt.shell_remote_execution("master-local", command)
                end = "{}:\n    ----------\n    retcode:\n        0\n".format(name) in respones.get("master-local")
                return end
        return False

    # 安装
    def install_salt(self, new_data):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        # file_name = ROSTER_FILE_URL
        # command = "salt-ssh --roster-file={} '{}' state.sls agent.install".format(file_name, name)
        # command = "salt-ssh '{}' state.sls agent.install".format(name)
        ssh_type = new_data.get("ssh_type")
        name = new_data.get("name")
        username = new_data.get("username")
        password = self.decrypt_password(new_data.get("password"))
        ip = new_data.get("ip")
        if self.state1:
            DOWENLOAD_BASE_URL = self.download_base_url1
        else:
            if self.state2:
                re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
                c = re.findall(re_rule, ip)
                if len(c) > 0:
                    DOWENLOAD_BASE_URL = self.download_base_url2
                else:
                    DOWENLOAD_BASE_URL = self.download_base_url1
            else:
                DOWENLOAD_BASE_URL = self.download_base_url1
        # if ip:
        #     DOWENLOAD_BASE_URL = self.master_url1.rsplit(":", 1)[0]
        # else:
        #     DOWENLOAD_BASE_URL = self.master_url2.rsplit(":", 1)[0]
        if DOWENLOAD_BASE_URL:
            install_command = "curl -s --insecure -o /usr/local/agent-install.sh http://{}/uploads/agent/agent-install.sh " \
                              "&& /bin/bash /usr/local/agent-install.sh install {} {}".format(DOWENLOAD_BASE_URL, DOWENLOAD_BASE_URL, name)
            if ssh_type != "key":  # 判定是否是秘钥
                command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r '{}'".format(username, password, name, install_command)
            else:
                pri_key_file = SALT_SSH_FILE_URL + "/" + name
                command = "salt-ssh -i '{}' --priv={} -r '{}'".format(name, pri_key_file, install_command)
            if not isinstance(self.salt, bool):
                respones = self.salt.shell_remote_execution("master-local", command)
                if respones.get("master-local"):
                    return "{}:\n    ----------\n    retcode:\n        0\n".format(name) in respones.get("master-local")
                return False
            return False
        return False

    # 新建roster文件
    def pass_key(self, new: dict):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"

        import fcntl
        file_name = ROSTER_FILE_URL
        ip = new.get("ip")
        name = new.get("name")
        username = new.get("username")
        password = self.decrypt_password(new.get("password"))
        ssh_type = new.get("ssh_type")
        port = new.get("ssh_port", "22")
        if ip.startswith("http://") or ip.startswith("https://"):
            ip = ip.split("//")[-1]
        flag = False
        with open(file_name, "a+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.seek(0)
            lt = f.readlines()
            if name + ":\n" in lt:
                flag = True
                a = lt.index(name + ":\n")
                lt[a] = name + ":\n"
                lt[a + 1] = "  host: {}\n".format(ip)
                lt[a + 2] = "  user: {}\n".format(username)
                lt[a + 3] = "  port: {}\n".format(port)
                # lt[a + 4] = "  sudo: {}\n".format("True")
            else:
                f.write(name + ":\n")
                f.write("  host: {}\n".format(ip))
                f.write("  user: {}\n".format(username))
                f.write("  port: {}\n".format(port))
                # f.write("  sudo: {}\n".format("True"))
        if flag:
            with open(file_name, "w+") as f:
                f.writelines(lt)
        # command = "salt-ssh -i --roster-file={} --key-deploy --user='{}' --passwd='{}' '{}' -r 'uptime'".format(
        if ssh_type != "key":
            command = "salt-ssh -i --user='{}' --passwd='{}' '{}' -r 'uptime'".format(username, password, name)
        else:
            file_url = SALT_SSH_FILE_URL + "/" + name
            private_key_data = new.get('ssh_key_info').get('private_key')
            with open(file_url, "w+") as f:
                f.write(private_key_data)
            # 设置秘钥文件权限为600
            os.chmod(file_url, stat.S_IRUSR | stat.S_IWUSR)
            command = "salt-ssh -i --priv={} {} -r 'uptime'".format(file_url, name)
        if not isinstance(self.salt, bool):
            respones = self.salt.shell_remote_execution("master-local", command, timeout=60)
            end = "retcode:\n        0\n" in respones.get("master-local", "")
            return end
        return False

    def delete_ssh_key(self, new):
        # file_name = BASE_DIR + "/static/salt/roster.yaml"
        import fcntl
        name = new.get("name")
        username = new.get("username")
        password = self.decrypt_password(new.get("password"))
        file_name = ROSTER_FILE_URL
        flag = False
        with open(file_name, 'a+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.seek(0)
            lt = f.readlines()
            a = (name + ":\n")
            if a in lt:
                flag = True
                b = lt.index(name + ":\n")
                lt[b] = ""
                lt[b + 1] = ""
                lt[b + 2] = ""
                lt[b + 3] = ""
                # lt[b + 4] = ""
        if flag:
            with open(file_name, "w+") as f:
                f.writelines(lt)
        command = "salt-ssh -i --user='{}' --passwd='{}' '{}' test.ping".format(username, password, name)
        # ========================删除SSHKEY文件==========================
        try:
            file_path = SALT_SSH_FILE_URL + "/" + name
            os.remove(file_path)
        except:
            pass
        if not isinstance(self.salt, bool):
            respones = self.salt.shell_remote_execution("master-local", command, timeout=60)
            end = "[ERROR   ]" in respones.get("master-local", "")
            return end
        return False

    def decrypt_password(self, password):
        if password:
            new_password = PasswordEncryption().decrypt(password)
            return new_password
        return ""

dt = {
    "ip": "182.92.194.96",
    "name": "www.womaiyun.com",
    "username": "root",
    "password": "OPSX@1018.com"
}

dt1 = {
    "ip": "118.31.7.172",
    "name": "www.yukinoneko.com",
    "username": "root",
    "password": "873515490Qq"
}

master = {
    "name": "Local-Master",
    "api1": "https://123.56.111.149:8011",
    "api2": "https://123.56.111.149:8012",
    "username1": "saltapi",
    "username2": "saltapi",
    "password1": "123456.coM",
    "password2": "123456.coM",
    "state1": True,
    "state2": False
}
master2 = {
    "name": "Local-Master",
    "api1": "https://106.15.50.194:8011",
    "api2": "https://106.15.50.194:8012",
    "username1": "saltapi",
    "username2": "saltapi",
    "password1": "123456.coM",
    "password2": "123456.coM",
    "state1": True,
    "state2": False
}

Master = {
    'id': 1,
    'name': '分组12',
    'type': '静态',
    'api1': 'https://123.56.111.149:8011',
    'api2': 'https://123.56.111.149:8012',
    'username1': 'saltapi',
    'username2': 'saltapi',
    'password1': '123456.coM',
    'password2': '123456.coM',
    'port1': '8011',
    'port2': '8012',
    'state1': True,
    'state2': True,
    'count': 3
}

import datetime

agent = {
    'id': 472,
    'ip': '124.70.31.19',
    'name': 'guan-demo',
    'show_name': '测试',
    'username': 'root',
    'system_type': 'Linux',
    'ssh_port': '22',
    'control_type': 'Agent',
    'agent_state': 'SSH连接中',
    'key_url': '',
    'update_time': datetime.datetime(2020, 9, 18, 15, 45, 5, 40653),
    'platform': 'control',
    'controller_name': 'Local-Master',
    'controller_id': 1,
    'zabbix_agent_state': '未连接',
    'zabbix_host_id': None,
    'add_type': ''
}

master_test = {
    "name": "Local-Master",
    "api1": "https://106.38.96.142:8011",
    "api2": "https://192.168.178.253:8011",
    "username1": "saltapi", 
    "username2": "saltapi", 
    "password1": "123456.coM", 
    "password2": "123456.coM", 
    "port1": "", 
    "port2": "", 
    "state1": False,
    "state2": False,
    "zabbix_username": "",
    "zabbix_password": "",
    "zabbix_url": "",
    "zabbix_state": False,
    "count": 1
    }


def proccess_grains(grains_data, model_code, host_name, ip=None):
    """ new_data 增加 model_code + "_HOSTNAME"""
    all_data = grains_data.get("data")
    data = all_data.get(host_name)

    selinux = data.get("selinux", None)
    dns = data.get("dns", None)
    if dns:
        dns = dns.get("nameservers")
    else:
        dns = ""
    if selinux:
        selinux = str(selinux.get("enabled")).lower()
    else:
        selinux = ""

    re_internal_ip_tmp_list = data.get("ip4_interfaces").keys()
    internal_ip = list()
    for each in re_internal_ip_tmp_list:
        reg_netcard = re.compile(r'^(eth|ens|enp|bond|Tencent VirtIO Ethernet Adapter)[\d]+', re.M)
        netcard = reg_netcard.search(each)
        if netcard:
            tmp_ip = data.get("ip4_interfaces").get(netcard.group())
            internal_ip.append(tmp_ip[0] if tmp_ip else '')

    if data.get("os") == "Windows":
        
        ip = data.get("fqdn_ip4")[-1] if data.get("fqdn_ip4") else ''

    re_rule = "^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
    c = re.findall(re_rule, ip)

    new_data = {
        "data": {
            model_code + "_HOSTNAME": data.get("fqdn"),
            model_code + "_INTERNAL_IP": internal_ip[0] if internal_ip else ip,
            model_code + "_PUBLIC_IP": '' if len(c) > 0 else ip,
            model_code + "_MEMORY": data.get("mem_total"),
            model_code + "_SWAP": data.get("swap_total"),
            model_code + "_CPU_MODEL": data.get("cpu_model"),
            model_code + "_CPU_NUM": data.get("num_cpus"),
            model_code + "_CPU_ARCH": data.get("cpuarch"),
            model_code + "_OS": data.get("os"),
            model_code + "_OS_TYPE": data.get("kernel"),
            model_code + "_OS_FAMILY": data.get("os_family"),
            model_code + "_OS_ARCH": data.get("osarch"),
            model_code + "_OS_RELEASE": data.get("osrelease"),
            model_code + "_SELINUX": selinux,
            model_code + "_KERNEL_RELEASE": data.get("kernelrelease"),
            model_code + "_BIOS_RELEASEDATA": data.get("biosreleasedate"),
            model_code + "_BIOS_VERSION": data.get("biosversion"),
            model_code + "_NAME_SERVER": dns,
            model_code + "_CPU_FLAGS": data.get("cpu_flags"),
            model_code + "_AGENT_VERSION": data.get("saltversion"),
            model_code + "_AGENT_PATH": data.get("saltpath"),
            model_code + "_SERIAL_NUMBER": data.get("serialnumber"),
            model_code + "_PRODUCT_NAME": data.get("productname"),
            model_code + "_VIRTUAL": data.get("virtual"),
            model_code + "_MANUFACTURER": data.get("manufacturer"),
            model_code + "_AGENT_STATE": "Agent运行中",
        },
        "pk_name": model_code + "_name",
        "pk_value": host_name,
        "model_code": model_code,
        "import_type": "Agent采集",
        "position": "zc"
    }
    # 如果云主机就采集实例名
    if model_code == "CLOUD_SERVER":
        new_data["data"][model_code + "_INSTANCE_ID"] = host_name
    # 如果不是云主机 需要存入唯一标识  字段名为名称
    if model_code != "CLOUD_SERVER":
        new_data["data"][model_code + "_name"] = host_name
    # 如果是Windows不采集fqdn (_HOSTNAME)
    # if data.get("os") not in "Windows":
    #     new_data["data"][model_code + "_HOSTNAME"] = data.get("fqdn")
    return new_data



# if __name__ == '__main__':
#     a = SaltAPI("https://106.15.50.194:8011", "saltapi", "123456.coM")
    # c = a.ping_check("opsany-windows-server")
    # c = a.grains("xiaoguan")
    # c = a.accept_key("xiaoguan")
    # print(c)
    # a = SaltSshBase(master2)
    # print(a.salt.shell_remote_execution("master-local", "salt-run manage.status"))
    # a.install_salt("dev.opsany.cn")

