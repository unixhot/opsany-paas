#!/usr/local/bin/python3
# coding:utf8
import hashlib
import json
import os
import sys
import random

import MySQLdb
from base64 import urlsafe_b64decode

import argparse
from Crypto.Cipher import AES

DB_HOST = "LOCALHOST"
DB_PORT = MYSQL_SERVER_PORT
DB_NAME = "opsany_proxy"
DB_PASSWORD = "PROXY_PASSWORD"
DB_USERNAME = "opsany"
SECRET_KEY = "CONTROL_SECRET_KEY"


class PasswordEncryption(object):
    def get_random_string(self, length=8):
        """生成长度为length 的随机字符串"""
        aplhabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(map(lambda _: random.choice(aplhabet), range(length)))

    def decrypt(self, ciphertext, key=SECRET_KEY, base64=True):
        try:
            if base64:
                ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))

            data = ciphertext

            key = hashlib.md5(key.encode('utf-8')).digest()
            cipher = AES.new(key, AES.MODE_ECB)
            text = cipher.decrypt(data).decode("utf-8")
            pad = ord(text[-1])
            return text[:-pad]
        except:
            return ""


class ReadMySQLData:
    def run(self, data_type="list", host_name=""):
        db = MySQLdb.connect(host=DB_HOST, port=DB_PORT, db=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD,
                             charset='utf8')
        cursor = db.cursor()
        field = "host_name, ip, ssh_port, username, password, ssh_type, private_key_file, privilege, privilege_password"
        table = "agent_admin"
        if data_type == "list":
            where = "control_type in ('1', '3','4')"
        elif data_type == "all_list":
            where = "control_type in ('1', '2', '3','4')"
        else:
            where = "host_name='{}'".format(host_name)
        sql = "SELECT {} FROM {} WHERE {};".format(field, table, where)
        cursor.execute(sql)
        if not host_name:
            results = cursor.fetchall()
            end_data = [self.get_sql_data(res) for res in results]
        else:
            res = cursor.fetchone()
            end_data = self.get_sql_data(res)
        cursor.close()
        db.close()
        return end_data

    def get_sql_data(self, res):
        dt = {
            "name": res[0],
            "ip": res[1],
            "ssh_port": res[2],
            "username": res[3],
            "password": res[4],
            "ssh_type": res[5],
            "private_key_file": res[6],
            "privilege": res[7],
            "privilege_password": res[8],
        }
        return dt


class GetAgent:
    def __init__(self):
        self.password = PasswordEncryption()

    def to_json(self, in_dict):
        return json.dumps(in_dict, sort_keys=True, indent=2)

    def get_single_agent(self, host_query):
        host_info_dict = {
            "ansible_host": host_query.get("ip"),
            "ansible_ssh_port": host_query.get("ssh_port"),
            "ansible_ssh_user": host_query.get("username"),
        }
        if host_query.get("ssh_type") == "key":
            host_info_dict["ansible_ssh_private_key_file"] = host_query.get("private_key_file", "")
        else:
            new_password = self.password.decrypt(host_query.get("password"))
            host_info_dict["ansible_ssh_pass"] = new_password
        privilege_password = host_query.get("privilege_password")
        if host_query.get("privilege") and privilege_password:
            host_info_dict["ansible_become_password"] = self.password.decrypt(privilege_password)
        return host_info_dict

    def get_agent_list_json(self, data_type="list"):
        host_unique = []
        hostvars = {}
        host_queryset = ReadMySQLData().run(data_type)
        for host_query in host_queryset:
            host_unique.append(host_query.get("name"))
            hostvars[host_query.get("name")] = self.get_single_agent(host_query)
        data = {
            "all": {
                "hosts": host_unique,
                "vars": {},
                "children": []
            },
            "_meta": {
                "hostvars": hostvars
            }
        }
        return self.to_json(data)

    def get_agent_host_json(self, host):
        host_query = ReadMySQLData().run("agent", host)
        if host_query:
            return self.to_json(self.get_single_agent(host_query))
        return {}


def parse_args():
    parser = argparse.ArgumentParser(description='Ansible Dynamic Inventory')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='List active servers control_type in 1 3 4')
    group.add_argument('--all_list', action='store_true', help='List active servers control_type in 1 2 3 4')
    group.add_argument('--host', help='List details about the specific host')
    return parser.parse_args()


def main():
    env = os.getenv("INVSCRIPT_PROXY_ENV") or "list"
    args = parse_args()
    output = {}
    agent = GetAgent()
    if args.list:
        if env == "list":
            output = agent.get_agent_list_json(data_type="list")  # 取出全部ansible纳管主机
        else:
            output = agent.get_agent_list_json(data_type="all_list")  # 取出全部主机
    elif args.all_list:
        output = agent.get_agent_list_json(data_type="all_list")  # 取出全部主机
    elif args.host:
        output = agent.get_agent_host_json(args.host)
    print(output)
    sys.exit(0)


if __name__ == '__main__':
    # python invscript_proxy.py --list
    # python invscript_proxy.py --all_list
    # python invscript_proxy.py --host "node1"
    # ansible all -i invscript_proxy.py -m ping
    main()
