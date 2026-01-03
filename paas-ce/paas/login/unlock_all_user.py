# -*- coding: utf-8 -*-
import random
import string


def unlock_all_user():
    UserAuthToken.objects.filter(app_code="login").delete()
    print(f"Unlock all User success")


if __name__ == '__main__':
    import os
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ["BK_ENV"] = "production"
    sys.path.append(parent_path)
    import django
    django.setup()
    from bkaccount.models import UserAuthToken
    unlock_all_user()


