# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
try:
    import simplejson as json
except ImportError:
    import json
from django.utils.translation import ugettext_lazy as _
from control.models import AgentAdmin
# Create your models here.


class SessionLog(models.Model):
    server = models.ForeignKey(AgentAdmin, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Server'))
    channel = models.CharField(max_length=100, verbose_name=_('Channel name'), blank=False, unique=True, editable=False)
    log_name = models.CharField(max_length=100, verbose_name=_('Log name'), blank=False, unique=False, editable=False)
    # log_name = models.UUIDField(max_length=100, default=uuid.uuid4, verbose_name=_('Log name'),
    # blank=False, unique=True, editable=False)
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Start time'))
    end_time = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('End time'))
    is_finished = models.BooleanField(default=False, verbose_name=_('Is finished'))
    user = models.CharField(max_length=100, verbose_name=_('username'), blank=False, unique=False)
    width = models.PositiveIntegerField(default=1024, verbose_name=_('Width'))
    height = models.PositiveIntegerField(default=768, verbose_name=_('Height'))
    guacamole_client_id = models.CharField(max_length=100, verbose_name=_('Gucamole channel name'), blank=True, editable=False)
    # TAG CHOICE: [init, connect]
    tag = models.CharField(max_length=100, verbose_name=_('Tag'), blank=True, null=True)

    def __unicode__(self):
        if self.server:
            return self.server.ip
        else:
            return self.user

    def __str__(self):
        if self.server:
            return self.server.ip
        else:
            return self.user

    def to_dict(self):
        dt = {}
        if self.server:
            dt["server"] = self.server.name
            dt["ip"] = self.server.ip
            dt["server_user"] = self.server.username
            dt["system_type"] = self.server.system_type
        else:
            dt["server"] = ''
            dt["ip"] = ''
            dt["server_user"] = ''
            dt["system_type"] = ''
        dt["channel"] = self.channel
        dt["log_name"] = self.log_name
        dt["start_time"] = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        dt["end_time"] = self.end_time.strftime("%Y-%m-%d %H:%M:%S")
        dt["is_finished"] = self.is_finished
        dt["user"] = self.user
        return dt

    class Meta:
        db_table = "control_terminal_log"
        # permissions = (
        #     ("can_delete_log", _("Can delete log info")),
        #     ("can_view_log", _("Can view log info")),
        #     ("can_play_log", _("Can play record")),
        # )
        ordering = [
            ('-start_time')
        ]


class CommandLog(models.Model):
    log = models.ForeignKey(SessionLog, on_delete=models.DO_NOTHING, null=True, verbose_name=_('Terminal Log'))
    datetime = models.DateTimeField(
        auto_now=True, verbose_name=_('date time'))
    command = models.CharField(max_length=255, verbose_name=_('command'))

    class Meta:
        db_table = "control_command_log"
        # permissions = (
        #     ("can_view_command_log", _("Can view command log info")),
        # )
        ordering = [
            ('-datetime')
        ]

    def __unicode__(self):
        return self.log.user.username

    def __str__(self):
        return self.log.user.username


class CommandBlockList(models.Model):
    command = models.CharField(max_length=255, verbose_name=_('指令名称'))
    datetime = models.DateTimeField(auto_now=True, verbose_name=_('date time'))
    type_choice = [('cancel', '取消'), ('confirm', '确认')]
    block_type = models.CharField(max_length=8, choices=type_choice, default='cancel', verbose_name=_('阻断类型'))
    block_info = models.CharField(max_length=255, verbose_name=_('阻断提示信息'))

    class Meta:
        db_table = "control_command_blocklist"
        ordering = [
            ('-datetime')
        ]

    def __unicode__(self):
        return self.command

    def __str__(self):
        return self.command

    def to_dict(self):
        return {
            "id": self.id,
            "command": self.command,
            "datetime": str(self.datetime).rsplit(".", 1)[0],
            "block_type": self.block_type,
            "block_info": self.block_info,
        }
    

class CommandBlockHistory(models.Model):
    command = models.CharField(max_length=255, verbose_name=_('指令'))
    block_type = models.CharField(max_length=8, null=True, verbose_name=_('阻断类型'))
    intercept_command = models.CharField(max_length=255, null=True)
    status_choice = [('y', '执行'), ('n', '未执行')]
    status = models.CharField(max_length=8, choices=status_choice, default='n', verbose_name=_('指令是否执行'))
    hostname = models.CharField(max_length=255, verbose_name=_('服务器IP'))
    user = models.CharField(max_length=32, null=True, verbose_name=_('用户名'))
    opt_user = models.CharField(max_length=32, null=True, verbose_name=_('操作用户'))
    datetime = models.DateTimeField(auto_now=True, verbose_name=_('date time'))

    class Meta:
        db_table = "control_command_blockhistroy"
        ordering = [
            ('-datetime')
        ]

    def __unicode__(self):
        return self.command

    def __str__(self):
        return self.command

    def to_dict(self):
        return {
            "id": self.id,
            "block_type": self.block_type,
            "intercept_command": self.intercept_command,
            "command": self.command,
            "status": self.status,
            "hostname": self.hostname,
            "user": self.user,
            "opt_user": self.opt_user,
            "datetime": str(self.datetime).rsplit(".", 1)[0],
        }