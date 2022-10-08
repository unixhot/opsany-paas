import MySQLdb
import argparse


def init_admin_mfa(host, port, username, password, name="rbac"):
    try:
        db = MySQLdb.connect(host=host, user=username, passwd=password, port=int(port), db=name, charset='utf8')
        cursor = db.cursor()
    except Exception as e:
        db = None
        print("Link mysql error: {}".format(str(e)))
    if db:
        sql = "UPDATE rbac_user SET google_auth_status=0, google_secret='' WHERE username='admin';"
        try:
            cursor.execute(sql)
            db.commit()
            print("Init admin user mfa success")
        except Exception as e:
            db.rollback()
            print("Init admin user mfa error, error info {}".format(str(e)))
        db.close()


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--mysql_password", help="Mysql password.", required=True)
    parameter.add_argument("--mysql_host", help="Mysql host.", required=True)
    parameter.add_argument("--mysql_username", help="Mysql username.", required=True)
    parameter.add_argument("--mysql_port", help="Mysql port.", required=True)
    return parameter

if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    mysql_password = options.mysql_password
    mysql_username = options.mysql_username
    mysql_host = options.mysql_host
    mysql_port = options.mysql_port
    init_admin_mfa(mysql_host, mysql_port, mysql_username, mysql_password)
