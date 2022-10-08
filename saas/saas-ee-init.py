# coding=utf-8
"""
执行前请执行
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany/uploads/workbench/icon/
/bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany-paas/paas-ce/paas/paas/media/applogo/
"""

import os
import shutil

import requests
import json

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


class InitData:
    # 公司/企业
    # DEPARTMENT
    DEPARTMENT = {
        "dep_name": "测试企业",
        "dep_level": 1
    }

    # 初始化用户，关联DEPARTMENT
    ADMIN = {
        "username": "admin",
        "chname": "管理员",
        "position": "管理员",
        "phone": "12345678910",
        "email": "123456@qq.com",
        "bk_role": "1",
    }

    # 事件中心-概览页
    event_home = [
        {
            "button_name": "查看页面",
            "button_code": "8.1",
            "is_required": 1
        }
    ]

    # 事件中心-事件查询-事件历史
    event_RouteView1_eventHistory = [
        {
            "button_name": "查看页面",
            "button_code": "8.2.1"
        }
    ]

    # 事件中心-事件查询-告警事件
    event_RouteView1_alarmEvent = [
        # {
        #     "button_name": "查看页面",
        #     "button_code": "8.2.2"
        # }
    ]

    # 事件中心-事件运营-事件接入
    event_RouteView2_eventTriggers = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.1"
        }

    ]

    # 事件中心-事件运营-触发规则
    event_RouteView2_eventRules = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.2"
        },
        {
            "button_name": "新建规则",
            "button_code": "event_rule_create"
        },
        {
            "button_name": "修改规则",
            "button_code": "event_rule_update"
        },
        {
            "button_name": "规则开关",
            "button_code": "event_rule_on_off"
        },
        {
            "button_name": "删除规则",
            "button_code": "event_rule_delete"
        }
    ]

    # 事件中心-事件运营-执行动作
    event_RouteView2_eventActions = [
        {
            "button_name": "查看页面",
            "button_code": "8.3.3"
        },
        {
            "button_name": "执行动作",
            "button_code": "event_action_create"
        }
    ]

    # 事件中心-智能告警-告警事件
    event_RouteView4_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.1"
        },
        {
            "button_name": "认领",
            "button_code": "event_claim_event"
        },
        {
            "button_name": "转派",
            "button_code": "event_delivery_event"
        },
        {
            "button_name": "关闭",
            "button_code": "event_close_event"
        }
    ]

    # 事件中心-智能告警-分派策略
    event_RouteView4_dispatchStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.2"
        },
        {
            "button_name": "新建分派策略",
            "button_code": "event_assign_create"
        },
        {
            "button_name": "修改分派策略",
            "button_code": "event_assign_update"
        },
        {
            "button_name": "删除分派策略",
            "button_code": "event_assign_delete"
        },
        {
            "button_name": "分派策略开关",
            "button_code": "event_assign_on_off"
        }
    ]

    # 事件中心-智能告警-通知策略
    event_RouteView4_notificationStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "8.4.3"
        },
        {
            "button_name": "新建通知策略",
            "button_code": "event_inform_create"
        },
        {
            "button_name": "修改通知策略",
            "button_code": "event_inform_update"
        },
        {
            "button_name": "删除通知策略",
            "button_code": "event_inform_delete"
        },
        {
            "button_name": "新建通知组",
            "button_code": "event_inform_group_create"
        },
        {
            "button_name": "修改通知组",
            "button_code": "event_inform_group_update"
        },
        {
            "button_name": "删除通知组",
            "button_code": "event_inform_group_delete"
        }
    ]

    # 事件中心-平台设置-事件模板
    event_RouteView3_packs = [
        {
            "button_name": "查看页面",
            "button_code": "8.5.1"
        },
        {
            "button_name": "卸载",
            "button_code": "event_pack_uninstall"
        },
        {
            "button_name": "安装",
            "button_code": "event_pack_install"
        }
    ]

    # 事件中心-平台设置-系统设置
    event_RouteView3_systemSetting = [
        {
            "button_name": "查看页面",
            "button_code": "8.5.2"
        },
        {
            "button_name": "修改配置",
            "button_code": "event_settings"
        }
    ]

    # 智能巡检-概览页
    auto_home = [
        {
            "button_name": "查看页面",
            "button_code": "9.1",
            "is_required": 1
        }
    ]
    # 智能巡检-智能巡检-快速巡检
    auto_RouteView_fastPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.1"
        }
    ]
    # 智能巡检-智能巡检-定时巡检
    auto_RouteView_timingPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.2"
        },
        {
            "button_name": "启用定时巡检",
            "button_code": "auto_timing_patrol_start"
        },
        {
            "button_name": "暂停定时巡检",
            "button_code": "auto_timing_patrol_stop"
        },
        {
            "button_name": "新建定时巡检",
            "button_code": "auto_timing_patrol_create"
        },
        {
            "button_name": "修改定时巡检",
            "button_code": "auto_timing_patrol_update"
        },
        {
            "button_name": "删除定时巡检",
            "button_code": "auto_timing_patrol_delete"
        }
    ]
    # 智能巡检-智能巡检-巡检历史
    auto_RouteView_patrolLog = [
        {
            "button_name": "查看页面",
            "button_code": "9.2.3"
        },
        {
            "button_name": "删除巡检历史",
            "button_code": "auto_patrol_delete"
        }
    ]
    # 智能巡检-巡检管理-巡检模板
    auto_RouteView1_patrolTemplate = [
        {
            "button_name": "查看页面",
            "button_code": "9.3.1"
        },
        {
            "button_name": "新建巡检模板",
            "button_code": "auto_patrol_template_create"
        },
        {
            "button_name": "修改巡检模板",
            "button_code": "auto_patrol_template_update"
        },
        {
            "button_name": "删除巡检模板",
            "button_code": "auto_patrol_template_delete"
        },
        {
            "button_name": "导入巡检模板",
            "button_code": "auto_patrol_template_import"
        },
        {
            "button_name": "导出巡检模板",
            "button_code": "auto_patrol_template_export"
        },
        {
            "button_name": "执行巡检模板",
            "button_code": "auto_patrol_template_execute"
        },
        {
            "button_name": "查看模板内容",
            "button_code": "auto_patrol_template_details"
        },
        {
            "button_name": "修改模板内容",
            "button_code": "auto_patrol_template_details_update"
        }
    ]

    # 应用监控-概览
    prom_home = [
        {
            "button_name": "查看页面",
            "button_code": "14.1",
            "is_required": 1
        }
    ]

    # 应用监控-监控大屏-Dashboard列表
    prom_RouteView_dashboard = [
        {
            "button_name": "查看页面",
            "button_code": "14.2.1",
        }
    ]

    # 应用监控-监控大屏-Dashboard列表
    prom_RouteView_dashboardList = [
        {
            "button_name": "查看页面",
            "button_code": "14.2.2",
        },
        {
            "button_name": "导入Dashboard模板",
            "button_code": "prom_Dashboard_folder_import"
        },
        {
            "button_name": "新建文件夹",
            "button_code": "prom_Dashboard_folder_create"
        },
        {
            "button_name": "修改文件夹",
            "button_code": "prom_Dashboard_folder_update"
        },
        {
            "button_name": "删除文件夹",
            "button_code": "prom_Dashboard_folder_delete"
        },
        {
            "button_name": "新建Dashboard",
            "button_code": "prom_Dashboard_read_create"
        },
        {
            "button_name": "修改Dashboard",
            "button_code": "prom_Dashboard_read_update"
        },
        {
            "button_name": "删除Dashboard",
            "button_code": "prom_Dashboard_delete"
        },
        {
            "button_name": "移动Dashboard",
            "button_code": "prom_Dashboard_move"
        }
    ]

    # 应用监控-监控对象-告警事件
    prom_RouteView_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "14.3.1"
        }
    ]

    # 应用监控-监控对象-主机监控
    prom_RouteView_hostMonitoring = [
        {
            "button_name": "查看页面",
            "button_code": "14.3.2"
        }
    ]

    # 应用监控-监控对象-组件监控
    prom_RouteView_componentMonitoring = [
        {
            "button_name": "查看页面",
            "button_code": "14.3.3"
        }
    ]

    # 应用监控-监控对象-服务拨测
    prom_RouteView_serviceDialTest = [
        {
            "button_name": "查看页面",
            "button_code": "14.3.4"
        },
        {
            "button_name": "新建目录",
            "button_code": "prom_server_test_folder_create"
        },
        {
            "button_name": "修改目录",
            "button_code": "prom_server_test_folder_update"
        },
        {
            "button_name": "删除目录",
            "button_code": "prom_server_test_folder_delete"
        },
        {
            "button_name": "新建服务拨测",
            "button_code": "prom_server_test_create"
        },
        {
            "button_name": "修改服务拨测",
            "button_code": "prom_server_test_update"
        },
        {
            "button_name": "删除服务拨测",
            "button_code": "prom_server_test_delete"
        },
        {
            "button_name": "启用服务拨测",
            "button_code": "prom_server_test_enable"
        },
        {
            "button_name": "禁用服务拨测",
            "button_code": "prom_server_test_disable"
        },
        {
            "button_name": "导入服务拨测",
            "button_code": "prom_server_test_import"
        },
        {
            "button_name": "导出服务拨测",
            "button_code": "prom_server_test_export"
        }
    ]

    # 应用监控-告警管理-告警规则
    prom_RouteView1_dispatchStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "14.4.1"
        },
        {
            "button_name": "新建告警规则",
            "button_code": "prom_alert_create"
        },
        {
            "button_name": "修改告警规则",
            "button_code": "prom_alert_update"
        },
        {
            "button_name": "删除告警规则",
            "button_code": "prom_alert_delete"
        },
    ]

    # 应用监控-平台设置-数据接入
    prom_RouteView2_dataAccess = [
        {
            "button_name": "查看页面",
            "button_code": "14.5.1"
        },
        {
            "button_name": "数据接入",
            "button_code": "prom_data_access"
        },
    ]

    # 容器平台-概览
    k8s_home__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.1",
            "is_required": 1
        }
    ]
    # 容器平台-集群概览
    k8s_home__container = [
        {
            "button_name": "查看页面",
            "button_code": "15.2",
            "is_required": 1
        }
    ]
    # 容器平台-项目概览
    k8s_home__project = [
        {
            "button_name": "查看页面",
            "button_code": "15.3",
            "is_required": 1
        }
    ]

    # 容器平台-集群管理-集群列表
    k8s_home__RouteView1__list_clusterList__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.4.1",
        },
        {
            "button_name": "导入集群",
            "button_code": "k8s_cluster_list_import",
        },
        {
            "button_name": "编辑集群",
            "button_code": "k8s_cluster_list_update",
        },
        {
            "button_name": "删除集群",
            "button_code": "k8s_cluster_list_delete",
        },
        {
            "button_name": "进入集群",
            "button_code": "k8s_cluster_list_enter",
        },
    ]

    # 容器平台-集群管理-集群设置
    k8s_home__RouteView1__list_clusterSetting__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.4.2",
        },
        {
            "button_name": "查看集群授权",
            "button_code": "k8s_cluster_setting_review",
        },
        {
            "button_name": "集群授权",
            "button_code": "k8s_cluster_setting_auth",
        },
        {
            "button_name": "查看用户授权(集群)",
            "button_code": "k8s_cluster_setting_user_review",
        },
        {
            "button_name": "用户授权(集群)",
            "button_code": "k8s_cluster_setting_user_auth",
        }
    ]

    # 容器平台-项目管理-项目列表
    k8s_home__RouteView2__list_projectList__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.5.1",
        },
        {
            "button_name": "进入项目",
            "button_code": "k8s_project_list_enter",
        }
    ]

    # 容器平台-项目管理-项目设置
    k8s_home__RouteView2__list_projectSetting__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.5.2",
        },
        {
            "button_name": "查看项目授权",
            "button_code": "k8s_project_setting_review",
        },
        {
            "button_name": "项目授权",
            "button_code": "k8s_project_setting_auth",
        },
        {
            "button_name": "查看用户授权(项目)",
            "button_code": "k8s_project_setting_user_review",
        },
        {
            "button_name": "用户授权(项目)",
            "button_code": "k8s_project_setting_user_auth",
        }
    ]

    # 容器平台-平台设置-操作审计
    k8s_RouteView3__list_operAudit__list = [
        {
            "button_name": "查看页面",
            "button_code": "15.6.1",
        }
    ]
    # 容器平台-集群管理-节点管理
    k8s_RouteView1__container_nodeManage__container = [
        {
            "button_name": "查看页面",
            "button_code": "15.7.1",
        }
    ]
    # 容器平台-集群管理-命名空间
    k8s_RouteView1__container_namespace__container = [
        {
            "button_name": "查看页面",
            "button_code": "15.7.2",
        },
        {
            "button_name": "创建项目",
            "button_code": "k8s_namespace_project_create",
        },
        {
            "button_name": "编辑项目",
            "button_code": "k8s_namespace_project_update",
        },
        {
            "button_name": "删除项目",
            "button_code": "k8s_namespace_project_delete",
        },
        {
            "button_name": "创建命名空间",
            "button_code": "k8s_namespace_create",
        },
        {
            "button_name": "修改命名空间",
            "button_code": "k8s_namespace_update",
        },
        {
            "button_name": "删除命名空间",
            "button_code": "k8s_namespace_delete",
        },
        {
            "button_name": "移动命名空间",
            "button_code": "k8s_namespace_remove",
        }
    ]
    # 容器平台-集群管理-事件查询
    k8s_RouteView1__container_eventquery__container = [
        {
            "button_name": "查看页面",
            "button_code": "15.7.3",
        }
    ]
    # 容器平台-应用负载-工作负载
    k8s_RouteView1__public_workLoad__public = [
        {
            "button_name": "查看页面",
            "button_code": "15.8.1",
        },
        {
            "button_name": "查看Deployment",
            "button_code": "k8s_workLoad_deployment_review",
        },
        {
            "button_name": "新建Deployment",
            "button_code": "k8s_workLoad_deployment_create",
        },
        {
            "button_name": "查看CronJob",
            "button_code": "k8s_workLoad_cron_job_review",
        },
        {
            "button_name": "查看DaemonSet",
            "button_code": "k8s_workLoad_daemon_set_review",
        },
        {
            "button_name": "查看Job",
            "button_code": "k8s_workLoad_job_review",
        },
        {
            "button_name": "查看StatefulSet",
            "button_code": "k8s_workLoad_stateful_set_review",
        },
        {
            "button_name": "查看Pod",
            "button_code": "k8s_workLoad_pod_review",
        },
    ]
    # 容器平台-应用负载-服务路由
    k8s_RouteView1__public_serviceRoute__public = [
        {
            "button_name": "查看页面",
            "button_code": "15.8.2",
        },
        {
            "button_name": "查看Service",
            "button_code": "k8s_service_route_service_review",
        },
        {
            "button_name": "查看Ingress",
            "button_code": "k8s_service_route_Ingress_review",
        },
    ]
    # 容器平台-应用负载-配置管理
    k8s_RouteView1__public_settingManage__public = [
        {
            "button_name": "查看页面",
            "button_code": "15.8.3",
        },
        {
            "button_name": "查看ConfigMap",
            "button_code": "k8s_setting_manage_config_map_review",
        },
        {
            "button_name": "查看Secret",
            "button_code": "k8s_setting_manage_secret_review",
        },
    ]
    # 容器平台-应用负载-存储管理
    k8s_RouteView1__public_storageManage__public = [
        {
            "button_name": "查看页面",
            "button_code": "15.8.4",
        },
        {
            "button_name": "查看PersistentVolume",
            "button_code": "k8s_storage_manage_persistent_volume_review",
        },
        {
            "button_name": "查看PersistentVolumeClaim",
            "button_code": "k8s_storage_manage_persistent_volume_claim_review",
        },
        {
            "button_name": "查看StorageClass",
            "button_code": "k8s_storage_manage_storage_class_review",
        },

    ]
    # 容器平台-应用负载-应用市场
    k8s_RouteView1__public_appMarket__container = [
        {
            "button_name": "查看页面",
            "button_code": "15.8.5",
        }
    ]
    # 容器平台-项目管理-项目设置
    k8s_RouteView1__public_projectSetting__project = [
        {
            "button_name": "查看页面",
            "button_code": "15.9.1",
        },
        {
            "button_name": "查看基本设置",
            "button_code": "k8s_project_setting_project_review",
        },
        {
            "button_name": "编辑基本设置",
            "button_code": "k8s_project_setting_project_update",
        },
        {
            "button_name": "查看成员管理",
            "button_code": "k8s_project_setting_member_review",
        },
        {
            "button_name": "添加成员",
            "button_code": "k8s_storage_manage_storage_member_add",
        },
        {
            "button_name": "移除成员",
            "button_code": "k8s_storage_manage_storage_member_remove",
        },
    ]

    event = event_home + event_RouteView1_eventHistory + event_RouteView1_alarmEvent + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView3_packs + event_RouteView4_alarmEvent + event_RouteView4_dispatchStrategy + event_RouteView4_notificationStrategy + event_RouteView3_systemSetting

    auto = auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate

    # prom
    prom = prom_home + prom_RouteView_dashboard + prom_RouteView_dashboardList + prom_RouteView_alarmEvent + prom_RouteView_hostMonitoring + prom_RouteView_componentMonitoring + prom_RouteView_serviceDialTest + prom_RouteView1_dispatchStrategy + prom_RouteView2_dataAccess

    k8s = k8s_home__list + k8s_home__container + k8s_home__project + k8s_home__RouteView1__list_clusterList__list + k8s_home__RouteView1__list_clusterSetting__list + k8s_home__RouteView2__list_projectList__list + k8s_home__RouteView2__list_projectSetting__list + k8s_RouteView3__list_operAudit__list + k8s_RouteView1__container_nodeManage__container + k8s_RouteView1__container_namespace__container + k8s_RouteView1__container_eventquery__container + k8s_RouteView1__public_workLoad__public + k8s_RouteView1__public_serviceRoute__public + k8s_RouteView1__public_settingManage__public + k8s_RouteView1__public_storageManage__public + k8s_RouteView1__public_projectSetting__project

    general = event_home + event_RouteView1_eventHistory + event_RouteView1_alarmEvent + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView4_alarmEvent + auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate + prom_home + prom_RouteView_dashboard + prom_RouteView_dashboardList + prom_RouteView_alarmEvent + prom_RouteView_hostMonitoring + prom_RouteView_componentMonitoring + prom_RouteView_serviceDialTest + k8s_home__list + k8s_home__container + k8s_home__project + k8s_home__RouteView1__list_clusterList__list + k8s_home__RouteView2__list_projectList__list + k8s_RouteView3__list_operAudit__list + k8s_RouteView1__container_nodeManage__container + k8s_RouteView1__container_namespace__container + k8s_RouteView1__container_eventquery__container + k8s_RouteView1__public_workLoad__public + k8s_RouteView1__public_serviceRoute__public + k8s_RouteView1__public_settingManage__public + k8s_RouteView1__public_storageManage__public

    #  菜单
    MENU_LIST = [
        {
            "menu_name": "事件中心",
            "menu_code": "event",
            "menu_type": "platform",
            "menu_address": "/o/event",
            "priority": "8",
            "platform_cname": "event",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "8.1",
                    "platform_cname": "event",
                    "children": [],
                    "buttons": event_home
                },
                {
                    "menu_name": "事件查询",
                    "menu_code": "RouteView1",
                    "menu_type": "directory",
                    "menu_address": "/eventQuery",
                    "priority": "8.2",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件历史",
                            "menu_code": "eventHistory",
                            "menu_type": "menu",
                            "menu_address": "/eventQuery/eventHistory",
                            "priority": "8.2.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView1_eventHistory
                        }
                    ]
                },
                {
                    "menu_name": "事件运营",
                    "menu_code": "RouteView2",
                    "menu_type": "directory",
                    "menu_address": "/eventOperation",
                    "priority": "8.3",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件接入",
                            "menu_code": "eventTriggers",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventTriggers",
                            "priority": "8.3.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventTriggers
                        },
                        {
                            "menu_name": "触发规则",
                            "menu_code": "eventRules",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventRules",
                            "priority": "8.3.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventRules
                        },
                        {
                            "menu_name": "执行动作",
                            "menu_code": "eventActions",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventActions",
                            "priority": "8.3.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventActions
                        }
                    ]
                },
                {
                    "menu_name": "智能告警",
                    "menu_code": "RouteView4",
                    "menu_type": "directory",
                    "menu_address": "/intelligentAlarm",
                    "priority": "8.4",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/alarmEvent",
                            "priority": "8.4.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_alarmEvent
                        },
                        {
                            "menu_name": "分派策略",
                            "menu_code": "dispatchStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/dispatchStrategy",
                            "priority": "8.4.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_dispatchStrategy
                        },
                        {
                            "menu_name": "通知策略",
                            "menu_code": "notificationStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/notificationStrategy",
                            "priority": "8.4.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_notificationStrategy
                        }
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView3",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "8.5",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件模板",
                            "menu_code": "packs",
                            "menu_type": "menu",
                            "menu_address": "/setting/packs",
                            "priority": "8.5.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView3_packs
                        },
                        {
                            "menu_name": "系统设置",
                            "menu_code": "systemSetting",
                            "menu_type": "menu",
                            "menu_address": "/setting/systemSetting",
                            "priority": "8.5.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView3_systemSetting
                        }
                    ]
                }
            ]
        },
        {
            "menu_name": "智能巡检",
            "menu_code": "auto",
            "menu_type": "platform",
            "menu_address": "/o/auto",
            "priority": "9",
            "platform_cname": "auto",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "9.1",
                    "platform_cname": "auto",
                    "children": [],
                    "buttons": auto_home
                },
                {
                    "menu_name": "智能巡检",
                    "menu_code": "RouteView",
                    "menu_type": "directory",
                    "menu_address": "smartPatrol",
                    "priority": "9.2",
                    "platform_cname": "auto",
                    "children": [
                        {
                            "menu_name": "快速巡检",
                            "menu_code": "fastPatrol",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/fastPatrol",
                            "priority": "9.2.1",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_fastPatrol
                        },
                        {
                            "menu_name": "定时巡检",
                            "menu_code": "timingPatrol",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/timingPatrol",
                            "priority": "9.2.2",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_timingPatrol
                        },
                        {
                            "menu_name": "巡检历史",
                            "menu_code": "patrolLog",
                            "menu_type": "menu",
                            "menu_address": "/smartPatrol/patrolLog",
                            "priority": "9.2.3",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView_patrolLog
                        }
                    ]
                },
                {
                    "menu_name": "巡检管理",
                    "menu_code": "RouteView1",
                    "menu_type": "directory",
                    "menu_address": "patrolManage",
                    "priority": "9.3",
                    "platform_cname": "auto",
                    "children": [
                        {
                            "menu_name": "巡检模板",
                            "menu_code": "patrolTemplate",
                            "menu_type": "menu",
                            "menu_address": "/patrolManage/patrolTemplate",
                            "priority": "9.3.1",
                            "platform_cname": "auto",
                            "children": [],
                            "buttons": auto_RouteView1_patrolTemplate
                        }
                    ]
                }
            ]
        },
        {
            "menu_name": "应用监控",
            "menu_code": "prom",
            "menu_type": "platform",
            "menu_address": "/o/prom/",
            "priority": "14",
            "platform_cname": "prom",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "14.1",
                    "platform_cname": "prom",
                    "children": [],
                    "buttons": prom_home
                },
                {
                    "menu_name": "监控大屏",
                    "menu_code": "RouteView3",
                    "menu_type": "directory",
                    "menu_address": "/monitorScreen",
                    "priority": "14.2",
                    "platform_cname": "prom",
                    "children": [
                        {
                            "menu_name": "Dashboard",
                            "menu_code": "dashboard",
                            "menu_type": "menu",
                            "menu_address": "/monitorScreen/dashboard",
                            "priority": "14.2.1",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_dashboard
                        },
                        {
                            "menu_name": "Dashboard列表",
                            "menu_code": "dashboardList",
                            "menu_type": "menu",
                            "menu_address": "/monitorScreen/dashboardList",
                            "priority": "14.2.2",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_dashboardList
                        }
                    ]
                },
                {
                    "menu_name": "监控对象",
                    "menu_code": "RouteView",
                    "menu_type": "directory",
                    "menu_address": "/monitoringObject",
                    "priority": "14.3",
                    "platform_cname": "prom",
                    "children": [
                        {
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/alarmEvent",
                            "priority": "14.3.1",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_alarmEvent
                        },
                        {
                            "menu_name": "主机监控",
                            "menu_code": "hostMonitoring",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/hostMonitoring",
                            "priority": "14.3.2",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_hostMonitoring
                        },
                        {
                            "menu_name": "组件监控",
                            "menu_code": "componentMonitoring",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/componentMonitoring",
                            "priority": "14.3.3",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_componentMonitoring
                        },
                        {
                            "menu_name": "服务拨测",
                            "menu_code": "serviceDialTest",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/serviceDialTest",
                            "priority": "14.3.4",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_serviceDialTest
                        },
                    ]
                },
                {
                    "menu_name": "告警管理",
                    "menu_code": "RouteView1",
                    "menu_type": "directory",
                    "menu_address": "/alarmManagement",
                    "priority": "14.4",
                    "platform_cname": "prom",
                    "children": [
                        {
                            "menu_name": "告警规则",
                            "menu_code": "dispatchStrategy",
                            "menu_type": "menu",
                            "menu_address": "/alarmManagement/dispatchStrategy",
                            "priority": "14.4.1",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView1_dispatchStrategy
                        }
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView2",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "14.5",
                    "platform_cname": "prom",
                    "children": [
                        {
                            "menu_name": "数据接入",
                            "menu_code": "dataAccess",
                            "menu_type": "menu",
                            "menu_address": "/setting/dataAccess",
                            "priority": "14.5.1",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView2_dataAccess
                        }
                    ]
                }
            ]
        },
        {
            "menu_name": "容器平台",
            "menu_code": "k8s",
            "menu_type": "platform",
            "menu_address": "/o/k8s/",
            "priority": "15",
            "platform_cname": "k8s",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home__list",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "15.1",
                    "platform_cname": "k8s",
                    "children": [],
                    "buttons": k8s_home__list
                },
                {
                    "menu_name": "集群概览",
                    "menu_code": "home__container",
                    "menu_type": "directory",
                    "menu_address": "/home__container",
                    "priority": "15.2",
                    "platform_cname": "k8s",
                    "children": [],
                    "buttons": k8s_home__container
                },
                {
                    "menu_name": "项目概览",
                    "menu_code": "home__project",
                    "menu_type": "directory",
                    "menu_address": "/home__project",
                    "priority": "15.3",
                    "platform_cname": "k8s",
                    "children": [],
                    "buttons": k8s_home__project
                },
                {
                    "menu_name": "集群管理",
                    "menu_code": "RouteView1__list",
                    "menu_type": "directory",
                    "menu_address": "/clusterManage",
                    "priority": "15.4",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "集群列表",
                            "menu_code": "clusterList__list",
                            "menu_type": "menu",
                            "menu_address": "/clusterManage/clusterList",
                            "priority": "15.4.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_home__RouteView1__list_clusterList__list
                        },
                        {
                            "menu_name": "集群设置",
                            "menu_code": "clusterSetting__list",
                            "menu_type": "menu",
                            "menu_address": "/clusterManage/clusterSetting",
                            "priority": "15.4.2",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_home__RouteView1__list_clusterSetting__list
                        },
                    ]
                },
                {
                    "menu_name": "项目管理",
                    "menu_code": "RouteView2__list",
                    "menu_type": "directory",
                    "menu_address": "/projectManage",
                    "priority": "15.5",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "项目列表",
                            "menu_code": "projectList__list",
                            "menu_type": "menu",
                            "menu_address": "/projectManage/projectList",
                            "priority": "15.5.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_home__RouteView2__list_projectList__list
                        },
                        {
                            "menu_name": "项目设置",
                            "menu_code": "projectSetting__list",
                            "menu_type": "menu",
                            "menu_address": "/projectManage/projectSetting",
                            "priority": "15.5.2",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_home__RouteView2__list_projectSetting__list
                        },
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView3__list",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "15.6",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "操作审计",
                            "menu_code": "operAudit__list",
                            "menu_type": "menu",
                            "menu_address": "/setting/operAudit",
                            "priority": "15.6.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView3__list_operAudit__list
                        }
                    ]
                },
                {
                    "menu_name": "集群管理",
                    "menu_code": "RouteView1__container",
                    "menu_type": "directory",
                    "menu_address": "/clusterManage_container",
                    "priority": "15.7",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "节点管理",
                            "menu_code": "nodeManage__container",
                            "menu_type": "menu",
                            "menu_address": "/clusterManage_container/nodeManage",
                            "priority": "15.7.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__container_nodeManage__container
                        },
                        {
                            "menu_name": "命名空间",
                            "menu_code": "namespace__container",
                            "menu_type": "menu",
                            "menu_address": "/clusterManage_container/namespace",
                            "priority": "15.7.2",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__container_namespace__container
                        },
                        {
                            "menu_name": "事件查询",
                            "menu_code": "eventquery__container",
                            "menu_type": "menu",
                            "menu_address": "/clusterManage_container/eventquery",
                            "priority": "15.7.3",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__container_eventquery__container
                        },
                    ]
                },
                {
                    "menu_name": "应用负载",
                    "menu_code": "RouteView1__public",
                    "menu_type": "directory",
                    "menu_address": "/appLoad",
                    "priority": "15.8",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "工作负载",
                            "menu_code": "workLoad__public",
                            "menu_type": "menu",
                            "menu_address": "/appLoad/workLoad_public",
                            "priority": "15.8.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__public_workLoad__public
                        },
                        {
                            "menu_name": "服务路由",
                            "menu_code": "serviceRoute__public",
                            "menu_type": "menu",
                            "menu_address": "/appLoad/serviceRoute_public",
                            "priority": "15.8.2",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__public_serviceRoute__public
                        },
                        {
                            "menu_name": "配置管理",
                            "menu_code": "settingManage__public",
                            "menu_type": "menu",
                            "menu_address": "/appLoad/settingManage_public",
                            "priority": "15.8.3",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__public_settingManage__public
                        },
                        {
                            "menu_name": "存储管理",
                            "menu_code": "storageManage__public",
                            "menu_type": "menu",
                            "menu_address": "/appLoad/storageManage_public",
                            "priority": "15.8.4",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__public_storageManage__public
                        },
                        {
                            "menu_name": "应用市场",
                            "menu_code": "appMarket__container",
                            "menu_type": "menu",
                            "menu_address": "/appLoad/appMarket_container",
                            "priority": "15.8.5",
                            "platform_cname": "k8s",
                            "display": 0,
                            "children": [],
                            "buttons": k8s_RouteView1__public_appMarket__container
                        },
                    ]
                },
                {
                    "menu_name": "项目管理",
                    "menu_code": "RouteView1__project",
                    "menu_type": "directory",
                    "menu_address": "/projectManage__project",
                    "priority": "15.9",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "项目设置",
                            "menu_code": "projectSetting__project",
                            "menu_type": "menu",
                            "menu_address": "/projectManage_project/projectSetting_project",
                            "priority": "15.9.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_RouteView1__public_projectSetting__project
                        }
                    ]
                }
            ]
        },
    ]

    # 内置权限
    BUILD_IN_STRATEGY_LIST = [
        {
            "strategy_name": "超级管理员",
            "strategy_type": "built-in",
            "description": "拥有所有平台的所有权限，并登陆【统一权限】",
            "platform_name_list": ["event", "auto", "prom", "k8s"],
            "buttons": event + auto + prom + k8s
        },
        {
            "strategy_name": "事件中心管理员",
            "strategy_type": "built-in",
            "description": "拥有【事件中心】所有菜单权限",
            "platform_name_list": ["event"],
            "buttons": event
        },
        {
            "strategy_name": "智能巡检管理员",
            "strategy_type": "built-in",
            "description": "拥有【智能巡检】所有菜单权限",
            "platform_name_list": ["auto"],
            "buttons": auto
        },
        {
            "strategy_name": "应用监控管理员",
            "strategy_type": "built-in",
            "description": "拥有【应用监控】所有菜单权限",
            "platform_name_list": ["prom"],
            "buttons": prom
        },
        {
            "strategy_name": "容器平台管理员",
            "strategy_type": "built-in",
            "description": "拥有【容器平台】所有菜单权限",
            "platform_name_list": ["k8s"],
            "buttons": k8s
        },
        {
            "strategy_name": "普通用户",
            "strategy_type": "built-in",
            "description": "普通用户，仅可以访问工作台和授权的平台菜单",
            "platform_name_list": ["event", "auto", "prom", "k8s"],
            "buttons": general
        },
    ]

    # 导航分组
    NAV_GROUP = [
        {
            "group_name": "智能运维",
            "nav_list": [
                {
                    "nav_name": "事件中心",
                    "nav_url": "/o/event/",
                    "describe": "事件中心和故障自愈",
                    "icon_name": "event.png"
                },
                {
                    "nav_name": "智能巡检",
                    "nav_url": "/o/auto/",
                    "describe": "运维自动化巡检",
                    "icon_name": "auto.png"
                }
            ]
        },
        {
            "group_name": "云原生",
            "nav_list": [
                {
                    "nav_name": "应用监控",
                    "nav_url": "/o/prom/",
                    "describe": "应用可观测平台",
                    "icon_name": "prom.png"
                },
                {
                    "nav_name": "容器平台",
                    "nav_url": "/o/k8s/",
                    "describe": "Kubernetes多集群管理",
                    "icon_name": "k8s.png"
                }
            ]
        }
    ]

    # 通知模板
    PLATFORM_TEMPLATE = [
        {
            "platform_name": "应用监控",
            "platform_code": "prom",
            "template_list": [
                {
                    "id": 10,
                    "type": "服务拨测告警通知",
                    "title_one": "服务拨测告警",
                    "title_two": "告警内容",
                    "info": "您的服务拨测：{} 发现了新的告警！<br /> 告警信息：{}",
                    "parameter_describe": "title, prom_info",
                    "platform": "应用监控"
                }
            ]
        },
        {
            "platform_name": "智能巡检",
            "platform_code": "auto",
            "template_list": [
                {
                    "id": 11,
                    "type": "巡检任务通知",
                    "title_one": "巡检任务",
                    "title_two": "巡检任务结果",
                    "info": "您的巡检任务：{} 已经完成！详情请前往智能巡检进行查看。",
                    "parameter_describe": "task_name",
                    "platform": "智能巡检"
                },
                {
                    "id": 12,
                    "type": "定时巡检通知",
                    "title_one": "定时巡检任务",
                    "title_two": "定时巡检任务结果",
                    "info": "您的定时巡检任务：{} 已经完成！详情请前往智能巡检进行查看。",
                    "parameter_describe": "task_name",
                    "platform": "智能巡检"
                },
            ]
        },
        {
            "platform_name": "事件中心",
            "platform_code": "event",
            "template_list": [
                {
                    "id": 8001,
                    "type": "事件中心告警通知",
                    "title_one": "事件中心告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8002,
                    "type": "事件中心认领告警通知",
                    "title_one": "事件中心认领告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_claim_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8003,
                    "type": "事件中心关闭告警通知",
                    "title_one": "事件中心关闭告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br /> 告警信息：{}",
                    "parameter_describe": "title, event_close_alert_info",
                    "platform": "事件中心"
                },
            ]
        }
    ]


class OpsAnyApi:
    def __init__(self, paas_domain, username, password):
        self.paas_domain = paas_domain
        self.session = requests.Session()
        self.session.headers.update({'referer': paas_domain})
        self.session.verify = False
        self.login_url = self.paas_domain + "/login/"
        self.csrfmiddlewaretoken = self.get_csrftoken()
        self.username = username
        self.password = password
        self.token = self.login()

    def get_csrftoken(self):
        try:
            resp = self.session.get(self.login_url, verify=False)
            if resp.status_code == 200:
                return resp.cookies["bklogin_csrftoken"]
            else:
                return ""
        except:
            return ""

    def login(self):
        try:
            login_form = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken,
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(self.login_url, data=login_form, verify=False)
            if resp.status_code == 200:
                return self.session.cookies.get("bk_token")
            return ""
        except:
            return False

    def init_event_auto_menu_strategy(self):
        """rbac 初始化菜单，权限策略"""
        try:
            # API = "/t/rbac//api/rbac/v0_1/init_ee_data/"
            API = "/o/rbac//api/rbac/v0_1/init_ee_data/"
            URL = self.paas_domain + API
            data = InitData()

            data = {
                "ADMIN": data.ADMIN,
                "DEPARTMENT": data.DEPARTMENT,
                "MENU_LIST": data.MENU_LIST,
                "BUILD_IN_STRATEGY_LIST": data.BUILD_IN_STRATEGY_LIST
            }
            response = self.session.post(url=URL, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def workbench_add_nav(self):
        """工作台初始化导航菜单"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-nav-v2/"
            NAV_GROUP_URL = self.paas_domain + NAV_API

            data = InitData()
            nav_data = data.NAV_GROUP
            for nav in nav_data:
                nav.update({"username": self.username})
            response = self.session.post(url=NAV_GROUP_URL, data=json.dumps({"group_list": nav_data}), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def workbench_add_message_template(self):
        """工作台初始化站内信模板"""
        try:
            NAV_API = "/o/workbench//api/workbench/v0_1/update-message-template/"
            TEMPLATE_API = self.paas_domain + NAV_API

            data = InitData()
            platform_data = {"platform_list": data.PLATFORM_TEMPLATE}

            response = self.session.post(url=TEMPLATE_API, data=json.dumps(platform_data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)

    def init_event_st2(self, st2_url, st2_username, st2_password):
        """初始化事件中心st2"""
        try:
            API = "/o/event//api/event/v0_1/init-st2/"
            URL = self.paas_domain + API
            if not all([st2_url, st2_username, st2_password]):
                return 0, "初始化失败，缺失参数"
            data = {
                "STACK_STORM_URL": st2_url,
                "STACK_STORM_USERNAME": st2_username,
                "STACK_STORM_PASSWORD": st2_password
            }
            response = self.session.post(url=URL, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                res = response.json()
            else:
                res = {"code": 500, "message": "error", "data": response.status_code}
            if res.get("code") == 200:
                return 1, res.get("data") or res.get("message")
            else:
                return 0, res.get("data") or res.get("errors") or res.get("message")
        except Exception as e:
            return 0, str(e)


def start(paas_domain, username, password, st2_url="", st2_username="", st2_password="", init_type=None):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)
    if not init_type:
        init_type = "all"

    if init_type not in ["menu", "nav", "temp", "st2", "all"]:
        print("Nothing was executed, init_type choose: all | menu | nav | temp | st2")

    if init_type in ["all", "menu"]:
        # 初始化事件中心，智能巡检菜单，权限策略
        rbac_status, rbac_data = run_obj.init_event_auto_menu_strategy()
        print("[SUCCESS] init menu strategy success") if rbac_status else print(
            "[ERROR] init menu strategy error, error info: {}".format(rbac_data))

    if init_type in ["all", "nav"]:
        # 初始化工作台导航目录
        add_nav_status, add_nav_data = run_obj.workbench_add_nav()
        print("[SUCCESS] add nav success") if add_nav_status else print(
            "[ERROR] add nav error, error info: {}".format(add_nav_data))

    if init_type in ["all", "temp"]:
        # 初始化工作台站内信模板
        add_nav_status, add_nav_data = run_obj.workbench_add_message_template()
        print("[SUCCESS] add message_template success") if add_nav_status else print(
            "[ERROR] add message_template error, error info: {}".format(add_nav_data))

    if init_type in ["all", "st2"]:
        # 初始化StackStorm
        if st2_url:
            st2_status, st2_data = run_obj.init_event_st2(st2_url, st2_username, st2_password)
            print("[SUCCESS] init st2 success:") if st2_status else print(
                "[ERROR] init st2 error info, error info: {}".format(str(st2_data)))


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--st2_url", help="StackStorm service url.", required=False)
    parameter.add_argument("--st2_username", help="StackStorm service username.", required=False)
    parameter.add_argument("--st2_password", help="StackStorm service password.", required=False)
    parameter.add_argument("--init_type", help="init type [all | menu | nav | temp | st2]", required=False)
    parameter.parse_args()
    return parameter


if __name__ == '__main__':
    parameter = add_parameter()
    options = parameter.parse_args()
    domain = options.domain
    username = options.username
    password = options.password
    st2_url = options.st2_url
    st2_username = options.st2_username
    st2_password = options.st2_password
    init_type = options.init_type  # 只 初始化部分数据
    start(domain, username, password, st2_url=st2_url, st2_username=st2_username, st2_password=st2_password, init_type=init_type)

# TODO 初始化导航需要将平台logo放置在 uploads/workbench/icon 下，且名称为 导航指定icon_name名称，否则将使用默认图标
"""
# 第一次初始化，需要将企业版平台菜单权限，导航，站内信模板，事件中心st2服务全部初始化
python3 saas-ee-init.py --domain https://domain.com --username username --password password --st2_url st2_url --st2_username st2_username --st2_password st2_password
# 只初始化或更新企业版平台菜单权限，导航，站内信模板
python saas-ee-init.py --domain https://www.opsany.com --username huxingqi --password Huxingqi --init_type menu
"""
