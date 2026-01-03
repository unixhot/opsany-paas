# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from enum import Enum

from login.return_message import *

DEFAULT_LANGUAGE = "chinese_simplified"


class ErrorStatusCode(Enum):
    # code = 400
    INVALID_REQUEST = (400, 40000, INVALID_REQUEST_MESSAGE)

    # code = 401
    INVALID_TOKEN = (401, 40100, INVALID_TOKEN_MESSAGE)
    USER_NOT_EXISTED_OR_WRONG_PASSWORD = (401, 40101, USER_NOT_EXISTED_OR_WRONG_PASSWORD_MESSAGE)
    USER_NOT_AUTH = (401, 40102, USER_NOT_AUTH_MESSAGE)

    # code 403
    INVALID_ACCESS_TOKEN = (403, 40301, AUTH_FAILED_MESSAGE)
    # permission denied
    PERMISSION_DENIED = (403, 40302, PERMISSION_DENIED_MESSAGE)

    # code = 404
    DATA_NOT_EXISTED = (404, 40400, DATA_NOT_EXISTED_MESSAGE)
    METHOD_ERROR = (404, 40405, METHOD_ERROR_MESSAGE)

    # code = 422
    RECORD_HAS_EXISTED = (422, 42200, RECORD_HAS_EXISTED_MESSAGE)
    NO_PARAMS = (422, 42201, NO_PARAMS_MESSAGE)

    MUST_INPUT_MESSAGE = (422, 42213, MUST_INPUT_MESSAGE_MESSAGE)

    PARAMS_ERROR = (422, 42232, PARAMETER_ERROR_MESSAGE)
    OPERATION_ERROR = (422, 42232, OPERATION_ERROR_MESSAGE)
    CUSTOM_ERROR = (422, 42234, CUSTOM_ERROR_MESSAGE)
    CUSTOM_ERROR2 = (423, 42301, CUSTOM_ERROR_MESSAGE)


def error(error_info=ErrorStatusCode.INVALID_REQUEST, errors=None, custom_message=None, language=DEFAULT_LANGUAGE, add_params=None):
    http_code, error_code, error_msg = error_info.value
    params = {
        'code': http_code,
        'message': get_language_message(error_msg, language),
        'errcode': error_code,
    }
    if add_params and isinstance(params, dict):
        params.update(add_params)
        
    if errors:
        params['errors'] = errors
    if custom_message:
        params['message'] = get_language_message(custom_message, language)
    return params


class SuccessStatusCode(Enum):
    # code = 200
    # 测试使用
    TEST_SUCCESS = (200, 20000, '服务器连接成功')

    MESSAGE_CREATE_SUCCESS = (200, 20004, MESSAGE_CREATE_SUCCESS_MESSAGE)
    MESSAGE_GET_SUCCESS = (200, 20005, MESSAGE_GET_SUCCESS_MESSAGE)
    MESSAGE_DELETE_SUCCESS = (200, 20006, MESSAGE_DELETE_SUCCESS_MESSAGE)
    MESSAGE_UPDATE_SUCCESS = (200, 20007, MESSAGE_UPDATE_SUCCESS_MESSAGE)

    OPERATION_SUCCESS = (200, 20023, OPERATION_SUCCESS_MESSAGE)


def success(success_info=SuccessStatusCode.TEST_SUCCESS, data=None, language=DEFAULT_LANGUAGE, add_params=None):
    http_code, success_code, success_msg = success_info.value
    params = {
        'code': http_code,
        'successcode': success_code,
        'message': get_language_message(success_msg, language),
        'data': data
    }
    if add_params:
        params.update(add_params)
    return params


def get_language_message(message, language):
    try:
        message = eval(message)
    except Exception:
        pass
    if isinstance(message, dict):
        if "chinese_simplified" not in message.keys():
            msg = str(message)
        else:
            format_str = message.pop("format_str", "")
            msg = message.get(language) or message.get(DEFAULT_LANGUAGE, "!")
            if format_str:
                msg = msg.format(format_str)
    else:
        msg = str(message)
    return msg
