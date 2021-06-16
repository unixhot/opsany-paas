# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from django.urls import path
from django.conf.urls import url, include
from control.views import *
from .views import LinuxFile, TreeView, SessionView, SshSessionKill, ReplayFileView, SshReplay, BlockListView, BlockHistoryView, TerminalHostView
from guacamole.views import WinFile, GuacamoleReplayFileView
urlpatterns = [
    # terminal
    path("tree/", TreeView.as_view()),
    path("session/", SessionView.as_view()),
    # [get] status: [finished, unfinished]
    # [post] status: [getuuid]
    path("session/status/<str:status>/", SessionView.as_view()),
    path("session/<str:session_uuid>/", SessionView.as_view()),
    # [post]
    path("sshkill/", SshSessionKill.as_view()),
    path("blocklist/", BlockListView.as_view()),
    # [get]
    path("blockhistory/", BlockHistoryView.as_view()),
    path("replay/", SshReplay.as_view()),
    path("replay/<str:session_uuid>/", SshReplay.as_view()),
    path("file/<str:file_name>", ReplayFileView.as_view()),
    url(r'^linuxfile/(?P<server_id>\d+)/$', LinuxFile.as_view()),
    url(r'^linuxfile/(?P<server_id>\d+)/(?P<url>.+)$', LinuxFile.as_view()),
    # terminal create host in agent_admin
    # [get]
    path("terminalhost/<int:server_id>/", TerminalHostView.as_view()),
    # [post]
    path("terminalhost/", TerminalHostView.as_view()),
    # windows file/folder 
    # [get/post/delete]
    url(r'^winfile/(?P<server_id>\d+)/$', WinFile.as_view()),
    url(r'^winfile/(?P<server_id>\d+)/(?P<url>.+)$', WinFile.as_view()),
    path("guac_replay_log/<str:log_name>/", GuacamoleReplayFileView.as_view()),
    ]