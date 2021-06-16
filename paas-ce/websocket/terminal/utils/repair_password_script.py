import os
import sys


def repair_password():
    all_agent = AgentAdmin.fetch_all()
    for i in all_agent:
        password = i.password
        new_password = PasswordEncryption().decrypt(password)
        i.update(**{"password": new_password})


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import datetime
    print(" [Success] {} init_script Running".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
    os.environ["BK_ENV"] = os.getenv("BK_ENV", "development")
    # os.environ.setdefault("BK_ENV", "production")     # 生产环境解注改行
    # os.environ.setdefault("BK_ENV", "testing")        # 开发环境解注改行
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import django
    django.setup()
    from control.models import AgentAdmin
    from control.utils.encryption import PasswordEncryption
    print(" [Success] {} init_script Execution Complete".format(str(datetime.datetime.now()).rsplit(".", 1)[0]))
