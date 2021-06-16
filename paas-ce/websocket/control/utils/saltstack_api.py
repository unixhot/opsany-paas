# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

import urllib.request
import urllib.parse
import json
import requests
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class SaltAPI(object):
    __token_id = ''

    def __init__(self, url, user, passwd):
        self.__url = url
        self.__user = user
        self.__password = passwd
        self.__token_id = self.get_token_id()

    def get_token_id(self):
        # user login and get token id
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        url = str(self.__url) + '/login'
        req = urllib.request.Request(url, obj)
        try:
            opener = urllib.request.urlopen(req, timeout=60)
            content = json.loads(opener.read())
            token_id = content['return'][0]['token']
        except Exception as _:
            return _
        return token_id

    def post_request(self, data, timeout=None, prefix='/'):
        url = str(self.__url) + prefix
        headers = {'X-Auth-Token': self.__token_id, 'Content-type': 'application/json'}
        try:
            # 解析成json
            data = bytes(json.dumps(data), 'utf8')
            req = urllib.request.Request(url, data, headers)
            opener = urllib.request.urlopen(req, timeout=timeout)
            content = json.loads(opener.read())
        except Exception as e:
            return str(e)
        return content

    def list_all_key(self):
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]['data']['return']
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def delete_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]['data']['success']
        else:
            return {"status": False, "message": "salt api error : " + content}

    def accept_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]['data']['success']
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def reject_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.reject', 'match': node_name}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]['data']['success']
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def remote_noarg_execution(self, tgt, fun, types="tgt_type"):
        # Execute commands without parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, types: 'list'}
        content = self.post_request(params)
        if isinstance(content, dict):
            ret = content['return'][0][tgt]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_noarg_execution(tgt, fun, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def remote_noarg_execution_notgt(self, tgt, fun, types="tgt_type"):
        # Execute commands without parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, types: 'list'}
        content = self.post_request(params)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_noarg_execution_notgt(tgt, fun, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def remote_execution(self, tgt, fun, arg, types="tgt_type"):
        # Command execution with parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, types: 'list'}
        content = self.post_request(params)
        if isinstance(content, dict):
            ret = content['return'][0][tgt]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_execution(tgt, fun, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def remote_execution_notgt(self, tgt, fun, arg, types="tgt_type"):
        # Command execution with parameters
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, types: 'list'}
        content = self.post_request(params)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.remote_execution_notgt(tgt, fun, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def shell_remote_execution(self, tgt, arg, timeout=None, types="tgt_type"):
        # Shell command execution with parameters
        # Changed in version 2017.7.0: Renamed from expr_form to tgt_type
        params = {'client': 'local', 'tgt': tgt, 'fun': 'cmd.run', 'arg': arg, types: 'list'}
        content = self.post_request(params, timeout)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.shell_remote_execution(tgt, arg, timeout=60, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def shell_remote_execution_sync(self, tgt, arg, types="tgt_type"):
        # Shell command execution with parameters
        # Changed in version 2017.7.0: Renamed from expr_form to tgt_type

        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'cmd.run', 'arg': arg, types: 'list'}
        content = self.post_request(params)
        if isinstance(content, dict):
            ret = content['return'][0]
            # 如果返回结果是空，说明salt可能版本小于2017.7.0的版本，使用次方法处理
            if not ret and types != "expr_form":  # types != "expr_form" 很重要确保最多执行两次，否则肯能发送死循环
                return self.shell_remote_execution(tgt, arg, types="expr_form")
            return ret
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def grain(self, tgt, arg):
        # Grains.item
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.item', 'arg': arg}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def grains(self, tgt):
        # Grains.items
        params = {'client': 'local', 'tgt': tgt, 'fun': 'grains.items'}
        content = self.post_request(params)
        if isinstance(content, dict):
            return {"status": True, "message": "", "data": content['return'][0]}
        else:
            return {"status": False, "message": "Salt API Error : " + content}

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
        return self.post_request(params)

    def async_deploy(self, tgt, arg):
        # Asynchronously send a command to connected minions
        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]['jid']
        else:
            return {"status": False, "message": "salt api error : " + content}

    def target_deploy(self, tgt, arg, types="tgt_type"):
        # Based on the list forms deployment
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, types: 'list'}
        content = self.post_request(params)
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
            return {"status": False, "message": "Salt API Error : " + content}

    def pillar_items(self, tgt, arg=[], types="tgt_type"):
        # Get pillar item
        if arg:
            params = {'client': 'local', 'tgt': tgt, 'fun': 'pillar.item', 'arg': arg, types: 'list'}
        else:
            params = {'client': 'local', 'tgt': tgt, 'fun': 'pillar.items', 'arg': arg, types: 'list'}
        content = self.post_request(params)
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
            return {"status": False, "message": "Salt API Error : " + content}

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
            return {"status": False, "message": "Salt API Error : " + content}

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
        content = self.post_request(params)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content}

    def runner(self, arg):
        # Return minion status
        params = {'client': 'runner', 'fun': arg}
        content = self.post_request(params)
        if isinstance(content, dict):
            jid = content['return'][0]
            return jid
        else:
            return {"status": False, "message": "Salt API Error : " + content}

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

    def jobs_jid_status(self, jid):
        '''查看jid运行状态'''
        # token = 'X-Auth-Token:%s' % self.__token_id
        params = {"client": "runner", "fun": "jobs.lookup_jid", "jid": jid}
        content = self.post_request(params)
        print(content)
        return content

    def network(self, tgt=""):
        params = {'client': 'local', 'tgt': tgt, 'fun': 'network.netstat'}
        content = self.post_request(params)
        if isinstance(content, dict):
            return content['return'][0]
        else:
            return {"status": False, "message": "Salt API Error : " + content}


# if __name__ == '__main__':
#     a = SaltAPI("https://106.15.50.194:8011", "saltapi", "123456.coM")

    # b = a.grains("www.yukinoneko.com")
    # print(b.get("data").get("www.yukinoneko.com").get("fqdn_ip4"))
    # data = a.network("*")
    # print(data)
    # data = a.network("*").get("master-local")
    # end_data = []
    # for i in data:
    #     dt = {
    #         "port": i.get("local-address").split(":")[1],
    #         "address": i.get("local-address").split(":")[0],
    #         "proto": i.get("proto"),
    #         "pid": i.get("program").split("/")[0],
    #         "program": i.get("program").split("/")[1]
    #     }
    #     end_data.append(dt)
    # c = a.shell_remote_execution_sync("*", "ls")
    # print(c)
    # b = a.jobs_jid_status("20200305054843787628")
    # print(b)
    # c = a.grains("www.womaiyun.com")
    # b = c.get("data").keys()
    # for i in b:
    #     print(i)
    # c = a.shell_remote_execution_sync("*", "systemctl restart salt-minion")
    # print(c)
    # 已同意
    # {'local': ['master.pem', 'master.pub'], 'minions_rejected': [], 'minions_denied': [], 'minions_pre': [], 'minions'
    # : ['dev.womaiyun.com']}
    # a.reject_key("dev.womaiyun.com")
    # b = a.get_token_id()
    # print(b, type(b))
