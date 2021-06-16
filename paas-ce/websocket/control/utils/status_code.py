# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from enum import Enum


class ErrorStatusCode(Enum):
    # code = 400
    INVALID_REQUEST = (400, 40000, '不合法的请求')

    # code = 401
    INVALID_TOKEN = (401, 40100, '无效的token')
    USER_NOT_EXISTED_OR_WRONG_PASSWORD = (401, 40101, '用户名/密码错误')
    NOT_HAVE_USER_IFNO = (401, 40102, '没有相应用户信息')

    # code = 404
    DATA_NOT_EXISTED = (404, 40400, '数据不存在')
    INVALID_LAYER_ID = (404, 40401, 'layer_id不存在')
    NOT_ADD_ACCESSKEY = (404, 40402, "当前用户没有添加accessKey")
    ACCESSKEY_ERROR = (404, 40403, "access错误")
    NOT_IMPORT_ACCESS = (404, 40404, "请输入access信息")
    GROUP_NOT_FOUND = (404, 40405, "分组不存在")

    # code = 422
    RECORD_HAS_EXISTED = (422, 42200, '记录已经存在')
    NO_PARAMS = (422, 42201, '参数不能为空')
    PARENT_DATA_NOT_EXISTED = (422, 42202, '父节点不存在')
    AGGREGATION_NOT_EXISTED = (422, 42203, '模型组不存在')
    PARENT_INSTANCE_NO_FOUND = (422, 42204, '父模型不存在')
    PARENT_ID_IS_REQUIRED = (422, 42205, 'parent_id参数是必须')
    USER_RO_ROLE_ALREADY_EXIST = (422, 42206, "用户或者角色已存在，创建失败")
    DATA_NOT_ALLOW = (404, 40404, "账号、密码包含特殊字符：(=,&), 请重新输入！")

    # 模型部分  07 - 09
    MESSAGE_EXISTENCE = (422, 42207, "信息已存在，创建失败")
    MESSAGE_NOT_NULL = (422, 42208, '分类下有内容，禁止删除')
    MESSAGE_NOT_FIND = (422, 42209, '没有找到相关信息')

    NOT_FIND_MODEL_GROUP = (422, 42210, '没有找到相关模型组信息')
    NOT_RECEIVE_FILE = (422, 42211, '没有接收到csv文件')
    IS_NOT_CSV = (422, 42212, '不是csv文件')

    MUST_INPUT_MESSAGE = (422, 42213, '必须输入相关信息')
    MODEL_HAS_NO_PK_NAME = (422, 42214, '模型中不含有主键字段')

    NOT_HAVE_RELATIONSHIP = (422, 42215, '没有相应的关系')

    MODEL_HAS_PARENT = (422, 42216, '该模型已有父模型，请勿重复创建')
    MODEL_HAS_NOT_PARENT = (422, 42216, '当前模型没有关系可删除')

    NOT_COVER_DISTRIBUTION = (422, 42217, '当前主机没有被分配')
    INST_HAS_SON = (422, 42218, '当前实例对象有子实例与其关联，禁止删除')

    NAME_IS_UNIQUE = (422, 42219, '唯一标识字段和IP地址字段为联合唯一字段')
    SALT_SSH_ERROR = (422, 42220, 'Salt-ssh 链接目标服务器失败')
    CONTROLLER_LINK_ERROR = (422, 42221, '控制器链接失败')

    AGENT_NOT_HAVE_CONTROLLER = (422, 42222, '当前节点没有选择控制器')
    CONTROLLER_STATE_ERROR = (422, 42223, '控制器异常')
    AGENT_STATE_ERROR = (422, 42224, '节点异常')
    PING_AGENT_STATE_ERROR = (422, 42225, 'Agent异常')
    
    NOT_PASSKEY = (422, 42226, '该节点没有被纳管, 无法采集信息')
    ACQUIRE_GRAINS_ERROR = (422, 42227, '信息采集失败，请稍后再试')
    AGENT_NAME_IS_UNIQUE = (422, 42228, '唯一标识字段不可重复')
    GROUP_NAME_NOT_USE = (422, 42228, '分组名已被占用')
    MESSAGE_GROUP_MESSAGE = (422, 42229, '分组信息没有找到')
    PING_AGENT_STATE_INSTALLED = (422, 42230, 'Agent已安装')

def error(error_info=ErrorStatusCode.INVALID_REQUEST, errors=None):
    http_code, error_code, error_msg = error_info.value
    params = {
        'code': http_code,
        'message': error_msg,
        'errcode': error_code,
    }
    if errors:
        params['errors'] = errors
    return params


class SuccessStatusCode(Enum):
    # code = 200
    # 测试使用
    TEST_SUCCESS = (200, 20000, '服务器连接成功')
    # 公有云部分
    COULD_REGION_LIST_GET_SUCCESS = (200, 20001, '公有云地区列表获取成功')
    GET_COULD_INSTANCES_INFO_SUCCESS = (200, 20002, '公有云实例详细信息查询成功')
    COULD_INSTANCES_IMPORT_SUCCESS = (200, 20003, '共有云主机导入成功')
    # 模型组部分 04 - 07
    MESSAGE_CREATE_SUCCESS = (200, 20004, '相关信息创建成功')
    MESSAGE_GET_SUCCESS = (200, 20005, '相关信息信息获取成功')
    MESSAGE_DELETE_SUCCESS = (200, 20006, '相关信息删除成功')
    MESSAGE_UPDATE_SUCCESS = (200, 20007, '相关信息更新成功')
    # 关系部分
    MODEL_OR_INST_RELATIONSHIP_SUCCESS = (200, 20008, '模型/实例关系添加成功')

    RELATIONSHIP_LINK_SUCCESS = (200, 20009, '连接关系添加成功')
    MODEL_RELATIONSHIP_SUCCESS = (200, 20009, '从属关系添加成功')

    FIELD_INDEX_PUT_SUCCESS = (200, 20010, '字段组排序成功')
    GET_COULD_INSTANCES_IMPORT_SUCCESS = (200, 20011, '已导入的公有云实例信息获取成功')
    DELETE_COULD_INSTANCES_SUCCESS = (200, 20012, '成功删除云主机实例')

    ACCESS_AUTH_PASS = (200, 20013, 'Access正确，请进行下一步操作')
    CONTROL_SUCCESS = (200, 20014, '节点正在接受纳管')

    HOST_RESTART_SUCCESS = (200, 20015, '开始执行Agent重启操作')
    HOST_STOP_SUCCESS = (200, 20016, '开始执行Agent关闭操作')
    AGENT_UNINSTALL_SUCCESS = (200, 20017, '开始执行Agent卸载操作')
    AGENT_INSTALL_SUCCESS = (200, 20018, '开始执行Agent安装操作')
    AGENT_DELETE_SUCCESS = (200, 20019, '开始执行Agent删除操作')

    GET_RUN_STATE_SUCCESS = (200, 20020, '获取执行状态成功')
    CONTROLLER_STATE_UPDATE_SUCCESS = (200, 20021, '控制器状态已更新')
    MENU_GET_SUCCESS = (200, 20022, '获得菜单列表成功')
    # operation
    OPERATION_SUCCESS = (200, 20023, '操作成功')
    MESSAGE_SEND_SUCCESS = (200, 20024, '信息发送成功')
    AGENT_PING_CHECK_SUCCESS = (200, 20025, "Agent运行中")
    AGENT_PING_CHECK_INSTALLED = (200, 20026, "Agent已安装")
    AGENT_PING_CHECK_ERROR = (200, 20027, "Agent异常")


def success(success_info=SuccessStatusCode.TEST_SUCCESS, data=None):
    http_code, success_code, success_msg = success_info.value
    params = {
        'code': http_code,
        'successcode': success_code,
        'message': success_msg,
        'data': data
    }
    return params
