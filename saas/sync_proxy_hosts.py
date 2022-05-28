#!/usr/local/bin/python
# coding:utf8

import argparse

import MySQLdb


class MysqlSync:
    def __init__(self, mysql_ip, mysql_port, control_username, control_password, control_db_name, proxy_username,
                 proxy_password, proxy_db_name):
        self.mysql_ip = mysql_ip
        self.mysql_port = mysql_port
        self.control_username = control_username
        self.control_password = control_password
        self.control_db_name = control_db_name
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_db_name = proxy_db_name

    def get_control_host(self):
        db = MySQLdb.connect(host=self.mysql_ip, port=self.mysql_port, db=self.control_db_name,
                             user=self.control_username, password=self.control_password, charset='utf8')
        cursor = db.cursor()
        sql = "SELECT name, ip, username, system_type, ssh_port, control_type, password, ssh_type FROM agent_admin where controller_id IS NOT NULL;"
        cursor.execute(sql)
        results = cursor.fetchall()
        end_data = [(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7]) for res in results]
        # end_data.append({
        #     "host_name": res[0],
        #     "ip": res[1],
        #     "username": res[2],
        #     "system_type": res[3],
        #     "ssh_port": res[4],
        #     "control_type": res[5],
        #     "password": res[6],
        #     "ssh_type": res[7],
        # })
        cursor.close()
        db.close()
        print("Find Control Host Count: {}".format(len(end_data)))
        return end_data

    def update_proxy_host(self, host_list):
        db = MySQLdb.connect(host=self.mysql_ip, port=self.mysql_port, db=self.proxy_db_name,
                             user=self.proxy_username, password=self.proxy_password, charset='utf8')
        cursor = db.cursor()
        sync_count = 0
        for host in host_list:
            host_name = host[0]
            select_sql = "SELECT id, host_name FROM agent_admin where host_name=\'{}\';".format(host_name)
            cursor.execute(select_sql)
            results = cursor.fetchone()
            if not results:
                insert_sql = "insert into agent_admin(`create_time`, `update_time`, `host_name`, `ip`, `username`, `system_type`, `ssh_port`, `control_type`, `password`, `ssh_type`) values(NOW(), NOW(), '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(*host)
                cursor.execute(insert_sql)
                sync_count += 1
        db.commit()
        cursor.close()
        db.close()
        print("Sync Proxy Host Count: {}".format(sync_count))
        return 1

    def update_proxy_host_many(self, host_list):
        db = MySQLdb.connect(host=self.mysql_ip, port=self.mysql_port, db=self.proxy_db_name,
                             user=self.proxy_username, password=self.proxy_password, charset='utf8')
        cursor = db.cursor()
        sql = "insert into agent_admin(`create_time`, `update_time`, `host_name`, `ip`, `username`, `system_type`, `ssh_port`, `control_type`, `password`, `ssh_type`) values(NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.executemany(sql, host_list)
        db.commit()
        cursor.close()
        db.close()


def run(mysql_ip, mysql_port, control_username, control_password, control_db_name, proxy_username, proxy_password,
        proxy_db_name):
    try:
        mysql_port = int(mysql_port)
    except:
        mysql_port = 3306
    mysql_sync = MysqlSync(mysql_ip, mysql_port, control_username, control_password, control_db_name, proxy_username,
                           proxy_password, proxy_db_name)
    host_list = mysql_sync.get_control_host()
    # 检测是否存在，保证数据唯一
    mysql_sync.update_proxy_host(host_list)


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--mysql_ip", help="Required parameters.", required=True)
    parameter.add_argument("--mysql_port", help="Required parameters.", required=True)
    parameter.add_argument("--control_username", help="Control Mysql Username.", required=True)
    parameter.add_argument("--control_password", help="Control Mysql Password.", required=True)
    parameter.add_argument("--control_db_name", help="Control Mysql DB Name.", required=True)
    parameter.add_argument("--proxy_username", help="Proxy Mysql Username.", required=True)
    parameter.add_argument("--proxy_password", help="Proxy Mysql Password.", required=True)
    parameter.add_argument("--proxy_db_name", help="Proxy Mysql DB Name.", required=True)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    run(
        options.mysql_ip,
        options.mysql_port,
        options.control_username,
        options.control_password,
        options.control_db_name,
        options.proxy_username,
        options.proxy_password,
        options.proxy_db_name,
    )

command = "python3 sync_proxy_hosts.py --mysql_ip mysql_host " \
          "--mysql_port 3306 " \
          "--control_username control " \
          "--control_password control_password " \
          "--control_db_name control" \
          " --proxy_username proxy_username " \
          "--proxy_password proxy_password " \
          "--proxy_db_name opsany_proxy"
