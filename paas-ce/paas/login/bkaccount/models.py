# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.db import models
from django.utils import timezone
from urllib.parse import quote
from django.utils.translation import gettext_lazy as _

from bkaccount.manager import (BkUserManager, LoginLogManager)
from bkaccount.constants import (ROLECODE_CHOICES, RoleCodeEnum, LANGUAGE_CHOICES, TIME_ZONE_CHOICES)


class BkRole(models.Model):
    """
    角色表
    """
    code = models.IntegerField("角色编号", choices=ROLECODE_CHOICES, unique=True)

    def __unicode__(self):
        return '%s' % (self.code)

    class Meta:
        db_table = "login_bkrole"
        verbose_name = "用户角色"
        verbose_name_plural = "用户角色"


class BkUser(AbstractBaseUser, PermissionsMixin):
    """
    BK user

    username and password are required. Other fields are optional.
    """

    username = models.CharField("用户名", max_length=128, unique=True)
    chname = models.CharField("中文名", max_length=254, blank=True)
    qq = models.CharField("QQ号", max_length=32, blank=True)
    phone = models.CharField("手机号", max_length=64, blank=True)
    email = models.EmailField("邮箱", max_length=254, blank=True)
    role = models.ManyToManyField(BkRole, verbose_name="角色", through='BkUserRole')

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = BkUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def role_code(self):
        role_list = self.role.all().values_list('code', flat=True)
        # 多个角色，则已最高角色为主（superuser > developer > staff）
        if RoleCodeEnum.SUPERUSER in role_list:
            return RoleCodeEnum.SUPERUSER
        if RoleCodeEnum.DEVELOPER in role_list:
            return RoleCodeEnum.DEVELOPER
        if RoleCodeEnum.OPERATOR in role_list:
            return RoleCodeEnum.OPERATOR
        if RoleCodeEnum.AUDITOR in role_list:
            return RoleCodeEnum.AUDITOR
        return RoleCodeEnum.STAFF

    @property
    def is_superuser_role(self):
        return self.role.filter(code=RoleCodeEnum.SUPERUSER).exists()

    @property
    def wx_userid(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.wx_userid if self.userinfo.wx_userid else ''
        return ''

    @property
    def language(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.language if self.userinfo.language else ''
        return ''

    @property
    def time_zone(self):
        if hasattr(self, 'userinfo') and self.userinfo is not None:
            return self.userinfo.time_zone if self.userinfo.time_zone else ''
        return ''

    def get_absolute_url(self):
        return "/users/%s/" % quote(self.email)

    def get_full_name(self):
        """
        Return the username plus the chinese name, with a space in between
        """
        full_name = '%s %s' % (self.username, self.chname)
        return full_name.strip()

    def get_short_name(self):
        """
        Return the chinese name for the user
        """
        return self.chname


class BkUserRole(models.Model):
    """
    用户角色多对多表
    """
    user = models.ForeignKey(BkUser, on_delete=models.CASCADE)
    role = models.ForeignKey(BkRole, on_delete=models.CASCADE)
    create_time = models.DateTimeField(_('create_time'), default=timezone.now)

    def __unicode__(self):
        return '%s(%s)' % (self.user.username, self.role.code)

    class Meta:
        db_table = "login_bkuser_role"
        verbose_name = "用户角色关系表"
        verbose_name_plural = "用户角色关系表"


class Loignlog(models.Model):
    """
    User login log
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    login_time = models.DateTimeField("登录时间")
    login_browser = models.CharField("登录浏览器", max_length=200, blank=True, null=True)
    login_ip = models.CharField("用户登录ip", max_length=50, blank=True, null=True)
    login_host = models.CharField("登录HOST", max_length=100, blank=True, null=True)
    app_id = models.CharField('APP_ID', max_length=30, blank=True, null=True)

    objects = LoginLogManager()

    def __unicode__(self):
        return "%s(%s)" % (self.user.chname, self.user.username)

    class Meta:
        db_table = "login_bklog"
        verbose_name = "用户登录日志"
        verbose_name_plural = "用户登录日志"


class BkToken(models.Model):
    """
    登录票据
    """
    token = models.CharField("登录票据", max_length=255, unique=True, db_index=True)
    # 是否已经退出登录
    is_logout = models.BooleanField("票据是否已经执行过退出登录操作", default=False)
    # 无操作过期时间戳
    inactive_expire_time = models.IntegerField("无操作失效时间戳", default=0)

    def __uincode__(self):
        return self.token

    class Meta:
        db_table = "login_bktoken"
        verbose_name = "登录票据"
        verbose_name_plural = "登录票据"


class UserInfo(models.Model):
    """
    用户信息
    """
    user = models.OneToOneField(BkUser, on_delete=models.CASCADE)
    wx_userid = models.CharField("企业号用户USERID/公众号用户OPENID", max_length=64, blank=True, null=True)
    bind_time = models.DateTimeField("微信绑定时间", default=timezone.now, blank=True, null=True)
    language = models.CharField("语言", max_length=32, choices=LANGUAGE_CHOICES, blank=True, null=True)
    time_zone = models.CharField("时区", max_length=32, choices=TIME_ZONE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
        db_table = 'login_userinfo'


class UserAuthToken(models.Model):
    """AuthToken 内置表-用来记录登录失败次数
    """
    d = {
        "app_code": "login",  # login 时间
        "username": "huxingqi",  # 用户名
        "auth_token": "1",  # 失败次数
        "last_accessed_time": "2025-11-10 11:22:33",  # 最后失败时间
        "created_time": "2025-11-10 11:22:33",  # 首次时间
    }
    app_code = models.CharField(_('蓝鲸智云应用编码'), max_length=128)
    username = models.CharField(_('用户名'), max_length=64)
    auth_token = models.CharField(_('token内容'), max_length=255)
    expires = models.DateTimeField(_('token过期时间'))
    last_accessed_time = models.DateTimeField(_('最后访问时间'), auto_now_add=True)
    created_time = models.DateTimeField(_('创建时间'), auto_now_add=True)

    def __unicode__(self):
        return self.auth_token

    def __str__(self):
        return self.auth_token

    class Meta:
        db_table = 'esb_user_auth_token'
    
    def time_to_str(self, time_pro):
        if not time_pro:
            return "-"
        if isinstance(time_pro, datetime):
            return timezone.localtime(time_pro).strftime("%Y-%m-%d %H:%M:%S")
        return str(time_pro)
    
    def to_rbac_unlock_dict(self):
        dt = {
            "app_code": self.app_code,
            "username": self.username,
            "auth_token": self.auth_token,
            "created_time": self.time_to_str(self.created_time),
            "last_accessed_time": self.time_to_str(self.last_accessed_time)
        }
        return dt
        
        