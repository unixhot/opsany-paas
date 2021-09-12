#!/opt/opsany/paas-agent/apps/Envs/control/bin/python
#coding:utf8

import argparse
import json
import sys

import MySQLdb
import hashlib
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES


DB_HOST = "localhost"
DB_NAME = "control"
DB_PASSWORD = "control"
DB_USERNAME = "control"
SECRET_KEY = "099f6e6f-9ad8-43d7-b487-7f655519598d"


class PasswordEncryption(object):
    def get_random_string(self, length=8):
        """
        生成长度为length 的随机字符串
        """
        aplhabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(map(lambda _: random.choice(aplhabet), range(length)))

    def pad(self, text, blocksize=16):
        """
        PKCS#5 Padding
        """
        pad = blocksize - (len(text) % blocksize)
        return (text + pad * chr(pad)).encode('utf-8')

    def encrypt(self, plaintext, key='', base64=True):
        """
        AES Encrypt
        """
        key = hashlib.md5(key.encode('utf-8')).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(self.pad(plaintext))
        # 将密文base64加密
        if base64:
            ciphertext = urlsafe_b64encode(ciphertext).decode("utf-8").rstrip('=')

        return ciphertext

    def decrypt(self, ciphertext, key='', base64=True):
        """
        AES Decrypt
        """
        if base64:
            ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))

        data = ciphertext

        key = hashlib.md5(key.encode('utf-8')).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        return self.unpad(cipher.decrypt(data).decode("utf-8"))

    def unpad(self, text):
        """
        PKCS#5 Padding
        """
        pad = ord(text[-1])
        return text[:-pad]


def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description='Ansible Dynamic Inventory')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                       help='List active servers')
    group.add_argument('--host', help='List details about the specific host')

    return parser.parse_args()


def get_host_groups():
    dt = get_agent()
    return to_json(dt)


def commmysql(host=""):
    db = MySQLdb.connect(host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8')
    cursor = db.cursor()
    if not host:
        sql = "SELECT name, ip, ssh_port, username, password, ssh_type FROM agent_admin;"
    else:
        sql = "SELECT name, ip, ssh_port, username, password, ssh_type FROM agent_admin WHERE name='{}';".format(host)
    cursor.execute(sql)
    if not host:
        results = cursor.fetchall()
        end_data = []
        for res in results:
            end_data.append({
                "name": res[0],
                "ip": res[1],
                "ssh_port": res[2],
                "username": res[3],
                "password": res[4],
                "ssh_type": res[5],
            })
    else:
        res = cursor.fetchone()
        end_data = {
            "name": res[0],
            "ip": res[1],
            "ssh_port": res[2],
            "username": res[3],
            "password": res[4],
            "ssh_type": res[5],
        }
    return end_data


def get_host_detail(host):
    dt = get_agent("host", host)
    return to_json(dt.get(host, {}))


def get_password(password):
    try:
        new_passwrod = PasswordEncryption().decrypt(password, key=SECRET_KEY)
    except:
        new_passwrod = ""
    return new_passwrod


def get_agent_group_json():
    """
    Agent query object to ansible group json type

    example: {
        "all": {
            "hosts": [
                "xxxx",
            ],
            "vars": {},
            "children": []
        },
        "_meta": {
            "hostvars": {
                "xxxx": {
                    "ansible_host": "xxxxx",
                    "ansible_ssh_port": xxx,
                    "ansible_ssh_user": "xxxx",
                    "ansible_ssh_pass": "xxxxxxx"
                },
            }
        }
    }
    """
    host_unique = []
    hostvars = {}
    host_queryset = commmysql()
    for host_query in host_queryset:
        host_unique.append(host_query.get("name"))
        host_info_dict = {
            "ansible_host": host_query.get("ip"),
            "ansible_ssh_port": host_query.get("ssh_port"),
            "ansible_ssh_user": host_query.get("username"),
        }
        if host_query.get("ssh_type") == "password":
            new_password = get_password(host_query.get("password"))
            host_info_dict["ansible_ssh_pass"] = new_password
        hostvars[host_query.get("name")] = host_info_dict
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
    return data


def get_agent_host_json(host):
    """
    Agent query object to ansible host json type

    example: {
        "xxxx": {
            "ansible_host": "xxxxx",
            "ansible_ssh_port": xxx,
            "ansible_ssh_user": "xxxx",
            "ansible_ssh_pass": "xxxxxxx"
        }
    }
    """
    host_query_object = commmysql(host)
    if host_query_object:
        data = {
            host_query_object.get("name"): {
                "ansible_host": host_query_object.get("ip"),
                "ansible_ssh_port": host_query_object.get("ssh_port"),
                "ansible_ssh_user": host_query_object.get("username"),
            }
        }
        if host_query_object.get("ssh_type") == "password":
            new_password = get_password(host_query_object.get("password"))
            data[host_query_object.get("name")]["ansible_ssh_pass"] = new_password
        return data
    return {}


def get_agent(json_type="group", host=""):
    if json_type == "group":
        return get_agent_group_json()
    else:
        return get_agent_host_json(host)


def main():
    args = parse_args()
    if args.list:
        output = get_host_groups()
    elif args.host:
        output = get_host_detail(args.host)
    print(output)
    sys.exit(0)


if __name__ == '__main__':
    main()
