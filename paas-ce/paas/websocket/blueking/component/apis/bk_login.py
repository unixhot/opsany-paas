# -*- coding: utf-8 -*-
from ..base import ComponentAPI


class CollectionsBkLogin(object):
    """Collections of BK_LOGIN APIS"""

    def __init__(self, client):
        self.client = client

        self.get_all_users = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_all_users/',
            description=u'获取所有用户信息'
        )
        self.get_batch_users = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_batch_users/',
            description=u'批量获取用户信息'
        )
        self.get_batch_users_platform_role = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_batch_users_platform_role/',
            description=u'批量获取用户各平台角色信息'
        )
        self.get_user = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_user/',
            description=u'获取用户信息'
        )
        self.get_all_user = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_all_user/',
            description=u'获取所有用户信息'
        )
        self.get_batch_user = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_batch_user/',
            description=u'获取多个用户信息'
        )
        self.get_batch_user_platform_role = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_login/get_batch_user_platform_role/',
            description=u'获取多个用户在平台应用的角色'
        )
