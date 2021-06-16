# -*- coding: utf-8 -*-
"""
Copyright © 2012-2020 OpsAny. All Rights Reserved.
""" # noqa

from django.urls import path
from django.conf.urls import url
from control.views import *

urlpatterns = [
    path("controller/", CreateControllerAdmin.as_view()),
    path("update-controller-status/", UpdateControllerStatusView.as_view()),
    path("all-host/", GetAllHost.as_view()),
    path("host-group/", CreateGroup.as_view()),
    path("select-agent-status/", SelectAgentStatusView.as_view()),              # agent查询当前状态
    path("group-list/", GroupNameListView.as_view()),                           # 分组列表-高级搜索
    path("agent-admin/", AgentAdminView.as_view()),                             # agent增删改查
    path("update-host-sign-variable-template/", AgentAdminUpdateZabbixView.as_view()),       # 修改主机标记，变量，监控模板
    path('check-ping/', CheckPingView.as_view()),                               # 测试agent是否可以ping通
    path("classify-admin/", PassKeyView.as_view()),                             # 纳管
    path("acquire-grains/", AcquireGrainsView.as_view()),                       # 信息采集接口
    path("restart-admin/", RestartView.as_view()),                              # 重启
    path("uninstall-admin/", UninstallAgentView.as_view()),                     # 卸载
    path("stop-admin/", StopAgentView.as_view()),                               # 停止
    path("install-admin/", InstallAgentView.as_view()),                         # 安装
    path("home-page/", HomePageView.as_view()),                                 # 首页
    path("get-agent/", GetAgent.as_view()),                                     # 从资源平台来的数据
    # path("inst-by-business/", GetHostInstanceByEsb.as_view()),                # ESB根据业务code获取主机列表
    path("get-run-state/", GetTaskRunState.as_view()),
    path("net-equipment-admin/", NetWorkEquipmentView.as_view()),
    # path("share-agent/", UserCanSeeAgentView.as_view()),
    # ESB API
    path("get-agent-network/", GetAgentNetWork.as_view()),
    path("get-host-info/", GetHostInfo.as_view()),
    path("get-host-file-info/", GetHostFileInfo.as_view()),
    path("get-agent-group/", GetAgentAndGroup.as_view()),
    path("get-agent-ps-info/", GetAgentPsInfo.as_view()),
    path("get-all-zabbix-agent/", GetAllZabbixAgentView.as_view()),
    path("get-controller-for-panel/", GetControllerByHostInfo.as_view()),
    path("get-info-for-workbench/", GetInfoForWorkbenchView.as_view()),
    path("get-nav-and-collection/", GetNavCollectionView.as_view()),
    path("collection/", CollectionNavView.as_view()),
    path("get-user-message/", GetUserMessageView.as_view()),
    path("get-menu/", ControlMenuStrategyCtrl.as_view()),
    path("get-zabbix-template/", GetZabbixTemplateView.as_view()),
    path("read-all-message/", ReadAllMessageView.as_view()),
    path("get-all-host-group/", GetAllHostGroupView.as_view()),
    path("get-host-info-for-monitor/", GetHostInfoForMonitorView.as_view()),
    path("stop-or-start-zabbix/", StopZabbixView.as_view()),
    # 获取用户SSH-KEY
    path("ssh-key/", GetUserSshKeyView.as_view()),
    # 监控平台首页所需数据
    path("monitor-host-count/", MonitorHostCountView.as_view()),        # 主机监控情况API     首页使用    ##
    path("host-monitor-type-count/", HostMonitorTypeView.as_view()),    # 主机监控类型统计API       首页使用
    path("event-type-count/", EventTypeCountView.as_view()),            # 主机告警统计API      首页使用
    path("host-problem-info/", HostProblemInfoView.as_view()),          # 主机问题信息API        首页使用     ##
    # 监控平台问题中心
    path("problem-info/", ProblemInfoView.as_view()),
    path("search-host-group/", SearchHostGroupView.as_view()),          # 搜索主机组的
    path("search-host/", SearchHostView.as_view()),                     # 搜索主机的
    path("search-application/", SearchApplicationView.as_view()),       # 搜索应用集的
    path("search-trigger/", SearchTriggerView.as_view()),               # 搜索触发器的
    path("send-message-from-monitor/", SendMessageView.as_view()),      # 向工作台发送主机告警情况
    path("alarm-rank/", AlarmRankView.as_view()),                       # 监控平台告警排名
    path("receive-action-info/", ReceiveActionInfoView.as_view()),      # 接收动作日志
    # 获取所有用户
    path("get-all-user/", GetAllUserView.as_view()),
    path("get-all-agent/", GetAllAgentView.as_view()),
    path("get-user-by-agent/", GetUserByAgentView.as_view()),
    # 分配主机到用户
    path("bind-agent-for-user/", AddAgentToUserView.as_view()),
    path("data-for-screen/", DataForScreenView.as_view()),                      # 为大屏提供数据

    path("host-group-to-job/", HostGroupView.as_view()),                # 获取分组信息
    path("host-admin-from-group-to-job/", HostView.as_view()),          # 按照分组查询主机-过滤主机授权

    # 获取当前用户信息
    url(r'^user_info', GetUserInfoCtrl.as_view())
]
