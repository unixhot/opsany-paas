# -*- coding: utf-8 -*-
import json

from django.test import TestCase, RequestFactory

from blueking.component.shortcuts import get_client_by_user, get_client_by_request
from blueking.tests.utils.utils import tests_settings as TS  # noqa
from blueking.tests.utils.utils import get_user_model


class TestShortcuts(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()

    def test_get_client_by_request(self):
        request = self.factory.get('/')
        request.user = self.user_model(username=TS['bk_user']['bk_username'])
        request.COOKIES = {'bk_token': TS['bk_user']['bk_token']}

        client = get_client_by_request(request)
        result = client.bk_login.get_user()
        self.assertTrue(result['result'], json.dumps(result))
        self.assertEqual(result['data']['bk_username'], TS['bk_user']['bk_username'])

    def test_get_client_by_user(self):
        user = self.user_model(username=TS['bk_user']['bk_username'])
        client = get_client_by_user(user)
        result = client.bk_login.get_user()
        self.assertTrue(result['result'], json.dumps(result))
        self.assertEqual(result['data']['bk_username'], TS['bk_user']['bk_username'])

        client = get_client_by_user(TS['bk_user']['bk_username'])
        result = client.bk_login.get_user()
        self.assertTrue(result['result'], json.dumps(result))
        self.assertEqual(result['data']['bk_username'], TS['bk_user']['bk_username'])
