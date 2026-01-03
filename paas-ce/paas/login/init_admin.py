# -*- coding: utf-8 -*-
import random
import string


def init_password():
    characters = string.ascii_letters + string.digits
    password = "Ops" +"".join(random.choices(characters, k=9))
    user = BkUser.objects.filter(username="admin").first()
    UserAuthToken.objects.filter(username="admin", app_code="login").delete()
    if user:
        user.set_password(password)
        user.save()
        print(f"reset admin password success: \033[1;32m{password}\033[0m")
    else:
        print("reset admin password error: admin was not found.")


if __name__ == '__main__':
    import os
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ["BK_ENV"] = "production"
    sys.path.append(parent_path)
    import django
    django.setup()
    from bkaccount.models import BkUser, UserAuthToken

    init_password()


