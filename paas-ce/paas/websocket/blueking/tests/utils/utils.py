# -*- coding: utf-8 -*-


def get_user_model():
    try:
        from account.models import BkUser as User
    except Exception:
        from django.contrib.auth.models import User
    return User


def load_tests_settings():
    return {
        'valid_app': {
            'bk_app_code': '',
            'bk_app_secret': '',
        },
        'bk_user': {
            'bk_username': 'admin',
            'bk_token': '',
        }
    }


tests_settings = load_tests_settings()
