# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""  # noqa


import datetime
import json
import uuid

import yaml
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View

from app.constants import AppStateEnum
from app.forms import AppQueryForm
from common.log import logger
from common.mixins.base import SaaSAdminMixin, SuperuserRequiredMixin
from common.mymako import render_mako_context, render_mako_tostring_context
from common.responses import FailJsonResponse, OKJsonResponse
from common.views.mako import MakoTemplateView
from common.utils import first_error_message, md5_for_file
from app.models import App, SecureInfo, DesktopSettings
from engine.models import BkApp, BkAppToken
from release.models import Record
from release.utils import sync_app_state
from saas.models import SaaSApp, SaaSUploadFile, SaaSAppVersion
from saas.utils import (delete_saas_app, extract_logo_file, saas_online_task,
                        save_saas_app_info, upload_response_tpl,
                        validate_and_extract_tar_file)


class SaaSListPageView(SuperuserRequiredMixin, MakoTemplateView):
    """SaaS 列表
    """
    template_name = 'saas/list.html'


class SaaSListView(SuperuserRequiredMixin, View):
    """查询获得上传部署应用的列表
    """

    def get(self, request):

        form = AppQueryForm(request.GET)
        if not form.is_valid():
            message = first_error_message(form)
            logger.exception("应用列表页面参数异常:%s", message)
            return JsonResponse({
                'data': "请求参数异常",
                'total_num': 0,
                'extend_fun': ''
            })

        keyword = form.cleaned_data["keyword"]
        hide_offline = form.cleaned_data["hide_offline"]
        page = form.cleaned_data["page"]
        page_size = form.cleaned_data["page_size"]

        start = (page - 1) * page_size
        end = page * page_size

        total, app_list = SaaSApp.objects.query_saas_list(keyword, hide_offline, start, end)

        # 判断应用状态是否需要刷新
        refresh_app_list = []
        app_refresh_states = [AppStateEnum.IN_TEST.value, AppStateEnum.IN_ONLINE.value, AppStateEnum.IN_OFFLINE.value]
        for _app in app_list:
            if _app.state in app_refresh_states:
                _app_code = _app.code
                try:
                    sync_app_state(_app_code)
                    # 获取更新后的应用信息
                    _app = SaaSApp.objects.get(code=_app_code)
                except Exception:
                    logger.exception("更新应用[%s]状态失败", _app_code)
            refresh_app_list.append(_app)

        result = {
            'total': total,
            'app_list': app_list,
        }
        template_name = 'saas/list_table.part'
        html_data = render_mako_tostring_context(request, template_name, result)
        return JsonResponse({
            'data': html_data,
            'total_num': total,
            'extend_fun': ''
        })


class InfoView(SaaSAdminMixin, MakoTemplateView):
    """SaaS 应用基本信息
    """
    template_name = 'saas/info.html'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)

        app_code = self.kwargs["app_code"]

        saas_app = SaaSApp.objects.get(code=app_code)
        app = saas_app.app
        app_state = saas_app.state

        app_info = {
            'code': saas_app.code or '--',
            'name': saas_app.name or '--',
            'introduction': app.introduction if app else '',
            'current_version': saas_app.current_version,
            'create_time': saas_app.created_date_display,
            'state': app_state,
        }
        # 获取版本信息
        ok, version_info = saas_app.get_current_version_info()
        if ok:
            app_info.update(version_info)

        context.update({
            'app_info': app_info,
            'app_code': app_code,
            'app_state': app_state,
        })
        return context


class ReleasePageView(SaaSAdminMixin, MakoTemplateView):
    """部署页面
    """
    template_name = 'saas/release.html'

    def get_context_data(self, **kwargs):
        context = super(ReleasePageView, self).get_context_data(**kwargs)

        app_code = self.kwargs["app_code"]

        # 部署已有应用，查询应用是否已有部署文件
        app_state = ''
        version_info = {}
        if app_code not in (0, '0'):
            saas_app = SaaSApp.objects.get(code=app_code)
            app_state = saas_app.state
            # 获取应用的版本信息
            _, version_info = saas_app.get_current_version_info()

        context.update({
            'app_code': app_code,
            'app_state': app_state,
            'version_info': version_info,
        })
        return context


class OfflinePageView(SaaSAdminMixin, MakoTemplateView):
    """下架页面
    """
    template_name = 'saas/offline.html'

    def get_context_data(self, **kwargs):
        context = super(OfflinePageView, self).get_context_data(**kwargs)
        request = self.request

        app_code = self.kwargs["app_code"]

        saas_app = SaaSApp.objects.get(code=app_code)
        app_state = saas_app.state
        ok, version_info = saas_app.get_current_version_info()
        # TODO: will return or not?
        if not ok:
            return render_mako_context(request, 'error/app_error3.html', {'app_code': app_code})
        version_info['app_code'] = app_code
        version_info['app_state'] = app_state

        context.update(version_info)
        return context


class DeleteSaaSView(SaaSAdminMixin, View):
    """删除某个 saas 及其所有版本
    """

    def post(self, request, *args, **kwargs):
        app_code = self.kwargs["app_code"]
        username = request.user.username
        ok, message = delete_saas_app(app_code, username)
        if ok:
            return OKJsonResponse(message)
        return FailJsonResponse(message)


# FIXME: can be merge with app's record?
class RecordView(SaaSAdminMixin, MakoTemplateView):
    """应用发布记录
    """
    template_name = 'saas/record.html'

    def get_context_data(self, **kwargs):
        context = super(RecordView, self).get_context_data(**kwargs)

        app_code = self.kwargs["app_code"]
        saas_app = SaaSApp.objects.get(code=app_code)
        app_state = saas_app.state

        context.update({'app_code': app_code, 'app_state': app_state})
        return context


class UploadAndRegisterView(SuperuserRequiredMixin, View):
    # @transaction.atomic
    def get(self, request):
        data = request.GET.dict()
        is_update = True if data.get("is_update") in [1, "1", "true", "True"] else False
        saas_file_name = data.get("saas_file_name")
        app_code = data.get("saas_app_code")
        app_name = data.get("saas_app_name")
        version = data.get("saas_app_version")
        secret_key = data.get("saas_app_secret_key")
        result = True
        message = "Success"
        if not is_update:
            try:
                uuid.UUID(secret_key.replace('-', ''))
            except Exception:
                result = False
                message = "saas_app_secret_key必须是UUID生成的数值！"
        app = App.objects.filter(code=app_code).first()
        app_by_name = App.objects.filter(name=app_name).first()
        if app != app_by_name:
            result = False
            message = "该应用 <{}> 应用名称 <{}> 已被 <{}> 使用".format(app_code, app_name, app_by_name.name)
        if not all([saas_file_name, app_code, app_name, version, secret_key]):
            result = False
            message = "缺失参数"
        if not is_update:
            if request.user.username != "admin":
                result = False
                message = "无权操作"
        if not is_update:
            if app:
                result = False
                message = "该应用已存在: {}".format(app_code)
        else:
            if not app:
                result = False
                message = "该应用不存在无法更新: {}".format(app_code)
        if result:
            saas_upload_file = self._save_saas_upload_file(saas_file_name)  # 创建上传记录
            app, this_secret_key = self._save_app(app_code, app_name, secret_key)  # app基本信息表 包含开发中心列表页信息
            saas_app = self._save_saas_app(app)  # saas基础表
            bk_app = self._save_bk_app(saas_app)  # appengine表 app信息
            self._save_bk_app_token(bk_app, this_secret_key)  # appengine表 app token 信息
            self._save_saas_app_version(saas_app, version, saas_upload_file, this_secret_key)  # saas版本表
            self._save_secure_info(app_code)  # 数据库信息
            self._save_desktop_setting(app_code)  # 桌面配置
            self._save_record(app_code, app_name, version, secret_key)  # 日志
        result = {"result": result, "message": message}
        result.update(data)
        return JsonResponse(result)

    def _save_saas_upload_file(self, saas_file_name):
        saas_upload_file = SaaSUploadFile.objects.create(
            name=saas_file_name,
            size=20971520,
            md5=str(uuid.uuid4())[:18],
            file=saas_file_name,
        )
        return saas_upload_file

    def _save_saas_app(self, app):
        app_code = app.code
        saas_app = SaaSApp.objects.filter(code=app_code).first()
        if not saas_app:
            saas_app = SaaSApp()
        saas_app.code = app_code
        saas_app.name = app.name
        saas_app.app = app
        saas_app.save()
        return saas_app

    def _save_saas_app_version(self, saas_app, version, upload_file, secret_key):
        version_settings = {
            'app_code': saas_app.code,
            'app_name': saas_app.name,
            'app_version': version,
            'secret_key': secret_key,
            'language': "Python",
            'author': "OpsAny",
            'introduction': "OpsAny{}".format(saas_app.name),
            'category': "OpsAny",
            'language_support': "Python3.6",
            'date': str(datetime.datetime.now()).split('.')[0],
            'desktop': {"width": 1300, "is_max": True, "height": 720},
            'env': None
        }
        saas_app_version = SaaSAppVersion.objects.filter(version=version, saas_app=saas_app).first()
        if not saas_app_version:
            saas_app_version = SaaSAppVersion()
        saas_app_version.version = version
        saas_app_version.saas_app = saas_app
        saas_app_version.upload_file = upload_file
        saas_app_version.settings = json.dumps(version_settings)
        saas_app_version.save()
        saas_app.current_version = saas_app_version
        saas_app.online_version = saas_app_version
        saas_app.save()
        return saas_app_version

    def _save_bk_app(self, saas_app):
        bk_app = BkApp.objects.filter(app_code=saas_app.code).first()
        if not bk_app:
            bk_app = BkApp()
        bk_app.name = saas_app.name
        bk_app.app_code = saas_app.code
        bk_app.app_lang = "Python"
        bk_app.save()
        return bk_app

    def _save_bk_app_token(self, bk_app, secret_key):
        bk_app_token = BkAppToken.objects.filter(bk_app=bk_app).first()
        if not bk_app_token:
            bk_app_token = BkAppToken()
            bk_app_token.key = secret_key
        bk_app_token.bk_app = bk_app
        bk_app_token.save()

    def _save_app(self, app_code, app_name, secret_key):
        app = App.objects.filter(code=app_code).first()
        if not app:
            app = App()
            app.auth_token = secret_key
        app.name = app_name
        app.code = app_code
        app.introduction = "OpsAny{}".format(app_name)
        app.creater = "admin"
        app.name = app_name
        app.state = 4
        app.is_already_test = 0
        app.is_already_online = 1
        app.first_test_time = None
        app.first_online_time = datetime.datetime.now()
        app.language = "Python"
        app.is_use_celery = False
        app.is_use_celery_beat = False
        app.is_saas = True
        app.save()
        return app, app.auth_token

    def _save_secure_info(self, app_code):
        secure_info = SecureInfo.objects.filter(app_code=app_code).first()
        if not secure_info:
            secure_info = SecureInfo()
        secure_info.app_code = app_code
        secure_info.vcs_type = 0
        secure_info.db_type = "mysql"
        secure_info.db_name = "app_code"
        secure_info.save()
        return secure_info

    def _save_desktop_setting(self, app_code):
        desktop_setting = DesktopSettings.objects.filter(app_code=app_code).first()
        if not desktop_setting:
            desktop_setting = DesktopSettings()
        desktop_setting.app_code = app_code
        desktop_setting.is_display = 1
        desktop_setting.save()
        # AppEnvVar.objects.add_env_vars(code, env)

        return desktop_setting

    def _save_record(self, app_code, app_name, version, secret_key):
        record = Record()
        message = "手动部署成功\n"
        message += "  \n应用ID：{}\n".format(app_code)
        message += "  \n应用名称：{}\n".format(app_name)
        message += "  \n应用版本：{}\n".format(version)
        message += "  \n应用秘钥：{}\n".format(secret_key)
        record.app_code = app_code
        record.operate_id = 1
        record.operate_user = "admin"
        record.app_old_state = 0
        record.operate_time = datetime.datetime.now()
        record.is_success = True
        record.is_tips = True
        record.is_version = False
        record.version = version
        record.message = message
        record.extra_data = message
        record.event_id = str(uuid.uuid4())
        record.save()
        return record


class UploadView(SuperuserRequiredMixin, View):
    """
    执行上传, 一整个事务操作

    注意安全性处理

    Note:
    1. app_code = 0, 则上传的新应用
    2. app_code != 0, 则上传老的应用, 需要校验app_code同包里的 app_code 是否一致
    """

    def post(self, request, *args, **kwargs):
        app_code = self.kwargs["app_code"]

        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            message = first_error_message(form)
            return upload_response_tpl(False, message)

        saas_file = form.cleaned_data["saas_file"]

        md5 = md5_for_file(saas_file.chunks())

        # 2. save to SaaSUploadFile
        # 同名文件覆盖 => 覆盖, 但是这样saas upload file又会存在多个指向同一个文件
        # http://timonweb.com/posts/imagefield-overwrite-file-if-file-with-the-same-name-exists/
        saas_upload_file = SaaSUploadFile.objects.create(
            name=saas_file.name,
            size=saas_file.size,
            md5=md5,
            file=saas_file,
        )

        # 校验大小等参数
        is_valid, message, app_yml_content = validate_and_extract_tar_file(filename=saas_upload_file.name,
                                                                           path=saas_upload_file.file.path)
        if not is_valid:
            logger.info(message)
            return upload_response_tpl(False, message)

        app_config = {}
        try:
            app_config = yaml.load(app_yml_content)
        except Exception:
            message = "无法正确加载{}包中的yml文件".format(saas_upload_file.name)
            logger.exception(message)
            return upload_response_tpl(False, message)

        # basic settings check
        saas_app_code = app_config.get("app_code")

        # 校验app_code
        if app_code == "0":
            app_code = saas_app_code

            # NOTE: 从上传新应用入口进来的, 判定下是否上传的老的包
            if SaaSApp.objects.exists(app_code):
                message = "上传包应用 ID 为: {}. 应用已存在, 非新应用无法从此入口部署. 请从内置应用列表找到该应用, 进入部署页面部署".format(app_code)
                logger.info(message)
                return upload_response_tpl(False, message)
        else:
            if app_code != saas_app_code:
                message = ("当前应用 ID 为: {}, 上传包应用 ID 为: {}. 不是同一个应用, 无法部署. "
                           "请作为新应用上传部署或找到应用{}的部署页面上传部署 ").format(app_code, saas_app_code, saas_app_code)
                logger.info(message)
                return upload_response_tpl(False, message)

        app_name = app_config.get("app_name")
        version = app_config.get("version")
        if not (app_code and app_name and version):
            message = ("upload file: {}, app.yml settings error"
                       "[app_code={}, app_name={}, version={}]").format(saas_file.name,
                                                                        app_code,
                                                                        app_name,
                                                                        version)
            logger.info(message)
            return upload_response_tpl(False, message)

        try:
            saas_app_version_id = save_saas_app_info(app_config, saas_upload_file)
        except Exception:
            message = "保存SaaS包信息失败"
            logger.exception(message)
            return upload_response_tpl(False, message)

        # 解压包文件中的logo到 media/logo/ 目录下
        extract_logo_file(filename=saas_upload_file.name, path=saas_upload_file.file.path, saas_app_code=saas_app_code)

        # for: 部署时展示线上版本/当前版本信息给用户
        file_version_display = "{} (V{})".format(saas_file.name, version)

        data = {"saas_app_version_id": saas_app_version_id, 'file_version_display': file_version_display}
        return upload_response_tpl(True, "上传成功", data)


class OnlineView(SuperuserRequiredMixin, View):
    """执行部署
    """

    def post(self, request, *args, **kwargs):
        saas_app_version_id = self.kwargs["saas_app_version_id"]

        username = request.user.username
        ok, message, data = saas_online_task(saas_app_version_id, username)
        if not ok:
            result = {"result": False, "message": message}
        else:
            result = {"result": True, "message": message}
            result.update(data)

        return JsonResponse(result)


# FIXME: duplicate codes with app logo
class ModifyAppLogoView(SuperuserRequiredMixin, View):
    """修改应用图标
    """

    def post(self, request, *args, **kwargs):
        app_code = self.kwargs["app_code"]

        app = SaaSApp.objects.get(code=app_code)
        logo = request.FILES.get('logo_m', '')
        if not (logo and logo.content_type and logo.content_type.lower() == 'image/png'):
            error = "更换logo失败, logo必须为png格式"
            url = '{}saas/list/?error={}'.format(settings.SITE_URL, error)
            return HttpResponseRedirect(url)

        try:
            app.logo = logo
            app.save()
        except Exception:
            logger.exception("应用logo[%s]更换失败", app_code)

        url = '{}saas/list/'.format(settings.SITE_URL)
        return HttpResponseRedirect(url)
