# -*- coding: utf-8 -*-


def init_password():
    user = BkUser.objects.filter(username="admin").first()
    if user:
        user.set_password("123456.coM")
        user.save()
        print "success"
    else:
        print "error"


if __name__ == '__main__':
    import os
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ["BK_ENV"] = "production"
    sys.path.append(parent_path)
    import django
    django.setup()
    from bkaccount.models import BkUser
    init_password()


