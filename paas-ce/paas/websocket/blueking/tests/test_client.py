# -*- coding: utf-8 -*-
import json

from django.test import TestCase

from blueking.component import collections
from blueking.component.client import BaseComponentClient, ComponentClientWithSignature
from blueking.tests.utils.utils import tests_settings as TS  # noqa


class TestBaseComponentClient(TestCase):

    @classmethod
    def setUpTestData(cls):  # noqa
        cls.ComponentClient = BaseComponentClient
        cls.ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

    def test_api_get(self):
        client = self.ComponentClient(
            TS['valid_app']['bk_app_code'],
            TS['valid_app']['bk_app_secret'],
            common_args={
                'bk_username': TS['bk_user']['bk_username'],
            }
        )
        result = client.bk_login.get_user()
        self.assertTrue(result['result'], json.dumps(result))
        self.assertTrue(result['data']['bk_username'], TS['bk_user']['bk_username'])

    def test_api_post(self):
        client = self.ComponentClient(
            TS['valid_app']['bk_app_code'],
            TS['valid_app']['bk_app_secret'],
            common_args={
                'bk_username': TS['bk_user']['bk_username'],
            }
        )
        result = client.bk_login.get_batch_users({'bk_username_list': [TS['bk_user']['bk_username']]})
        self.assertTrue(result['result'], json.dumps(result))
        self.assertTrue(result['data'][TS['bk_user']['bk_username']]['bk_username'], TS['bk_user']['bk_username'])

    def test_set_bk_api_ver(self):
        client = self.ComponentClient(
            TS['valid_app']['bk_app_code'],
            TS['valid_app']['bk_app_secret'],
            common_args={
                'bk_username': TS['bk_user']['bk_username'],
            }
        )
        client.set_bk_api_ver('')
        result = client.bk_login.get_user({'username': TS['bk_user']['bk_username']})
        self.assertTrue(result['result'], json.dumps(result))
        self.assertTrue(result['data']['username'], TS['bk_user']['bk_username'])


class TestComponentClientWithSignature(TestCase):

    @classmethod
    def setUpTestData(cls):  # noqa
        cls.ComponentClient = ComponentClientWithSignature
        cls.ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

    def test_api(self):
        client = self.ComponentClient(
            TS['valid_app']['bk_app_code'],
            TS['valid_app']['bk_app_secret'],
            common_args={
                'bk_username': TS['bk_user']['bk_username'],
            }
        )
        result = client.bk_login.get_user()
        self.assertTrue(result['result'], json.dumps(result))
        self.assertTrue(result['data']['bk_username'], TS['bk_user']['bk_username'])

    def test_api_post(self):
        client = self.ComponentClient(
            TS['valid_app']['bk_app_code'],
            TS['valid_app']['bk_app_secret'],
            common_args={
                'bk_username': TS['bk_user']['bk_username'],
            }
        )
        result = client.bk_login.get_batch_users({'bk_username_list': [TS['bk_user']['bk_username']]})
        self.assertTrue(result['result'], json.dumps(result))
        self.assertTrue(result['data'][TS['bk_user']['bk_username']]['bk_username'], TS['bk_user']['bk_username'])
