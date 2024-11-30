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

    saas_queue = [
        ("统一权限", "rbac", "celery", "1"),
        ("工作台", "workbench", "celery", "2"),
        ("资源平台", "cmdb", "celery", "3"),
        ("管控平台", "control", "celery", "4"),
        ("作业平台", "job", "celery", "5"),
        ("基础监控", "monitor", "celery", "6"),
        ("云管平台", "cmp", "celery", "7"),
        ("堡垒机", "bastion", "celery", "8"),
        ("应用平台", "devops", "celery", "9"),
        ("制品仓库", "repo", "celery", "17"),
        ("流水线", "pipeline", "celery", "17"),
        ("持续部署", "deploy", "celery", "18"),
        ("事件中心", "event", "celery", "11"),
        ("智能巡检", "auto", "celery", "12"),
        ("容器平台", "k8s", "celery", "14"),
        ("应用监控", "prom", "celery", "15"),
        ("APM平台", "apm", "celery", "21"),
        # ("代码仓库", "code", "celery", "0"),
        # ("知识库", "kbase", "celery", "0"),
        # ("日志平台", "log", "celery", "0"),
    ]

    # 事件中心-概览页
    event_home = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_home",  # 8.1
            "is_required": 1
        }
    ]

    # 事件中心-事件查询-告警事件
    event_RouteView4_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_alarm_event"  # 8.2.1
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

    # 事件中心-事件查询-事件历史
    event_RouteView1_eventHistory = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_event_history"  # 8.2.2
        }
    ]


    # 事件中心-智能告警-分派策略
    event_RouteView4_dispatchStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_dispatch_strategy"  # 8.3.2
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
            "button_code": "event_review_notification_strategy"  # 8.3.3
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

    # 事件中心-智能告警-告警接入
    event_RouteView4_alarmAccess = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_alarm_access"  # 8.3.4
        },
    ]


    # 事件中心-事件运营-事件接入
    event_RouteView2_eventTriggers = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_event_triggers"  # 8.4.1
        }
    ]

    # 事件中心-事件运营-触发规则
    event_RouteView2_eventRules = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_event_rules"  # 8.4.2
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
            "button_code": "event_review_event_actions"  # 8.4.3
        },
        {
            "button_name": "执行动作",
            "button_code": "event_action_create"
        }
    ]


    # 事件中心-平台设置-事件模板
    event_RouteView3_packs = [
        {
            "button_name": "查看页面",
            "button_code": "event_review_packs"  # 8.5.1
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

    # 智能巡检-概览页
    auto_home = [
        {
            "button_name": "查看页面",
            "button_code": "auto_review_home",  # 9.1
            "is_required": 1
        }
    ]
    # 智能巡检-智能巡检-快速巡检
    auto_RouteView_fastPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "auto_review_fast_patrol"  # 9.2.1
        }
    ]
    # 智能巡检-智能巡检-定时巡检
    auto_RouteView_timingPatrol = [
        {
            "button_name": "查看页面",
            "button_code": "auto_review_timing_patrol"  # 9.2.2
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
            "button_code": "auto_review_patrol_log"  # 9.2.3
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
            "button_code": "auto_review_patrol_template"  # 9.3.1
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
            "button_code": "prom_review_home",  # 14.1
            "is_required": 1
        }
    ]

    # 应用监控-监控大屏-Dashboard列表
    prom_RouteView_dashboard = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_dashboard",  # 14.2.1
        }
    ]

    # 应用监控-监控大屏-Dashboard列表
    prom_RouteView_dashboardList = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_dashboard_list",  # 14.2.2
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


    # 应用监控-监控大屏-应用分析
    prom_RouteView_analyzeList = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_analyze_list",  # 14.2.3
        },
        {
            "button_name": "置顶和取消置顶",
            "button_code": "prom_analyze_is_top",
        },
    ]

    # 应用监控-监控对象-告警通知
    prom_RouteView_alarmNotify = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_alarm_notify"  # 14.3.1
        }
    ]

    # 应用监控-监控对象-告警事件
    prom_RouteView_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_alarm_event"  # 14.3.2
        }
    ]

    # 应用监控-监控对象-主机监控
    prom_RouteView_hostMonitoring = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_host_monitoring"  # 14.3.3
        }
    ]

    # 应用监控-监控对象-组件监控
    prom_RouteView_componentMonitoring = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_component_monitoring"  # 14.3.4
        }
    ]

    # 应用监控-告警管理-告警规则
    prom_RouteView1_dispatchStrategy = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_dispatch_strategy"  # 14.4.1
        },
        {
            "button_name": "新建告警规则分组",
            "button_code": "prom_alert_group_create"
        },
        {
            "button_name": "修改告警规则分组",
            "button_code": "prom_alert_group_update"
        },
        {
            "button_name": "删除告警规则分组",
            "button_code": "prom_alert_group_delete"
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
        {
            "button_name": "是否启用",
            "button_code": "prom_alert_enable"
        },
        {
            "button_name": "导入",
            "button_code": "prom_alert_import"
        },
        {
            "button_name": "导出",
            "button_code": "prom_alert_export"
        },
        {
            "button_name": "克隆分组",
            "button_code": "prom_alert_clone_group"
        },
        {
            "button_name": "克隆告警规则",
            "button_code": "prom_alert_clone_rule"
        }
    ]
    
    # 应用监控-告警管理-通知规则
    prom_RouteView1_alarmManage = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_alarm_manage"  # 14.4.2
        },
        {
            "button_name": "新建通知规则",
            "button_code": "prom_alert_notify_create"
        },
        {
            "button_name": "修改通知规则",
            "button_code": "prom_alert_notify_update"
        },
        {
            "button_name": "删除通知规则",
            "button_code": "prom_alert_notify_delete"
        },
    ]

    # 应用监控-平台设置-数据接入
    prom_RouteView2_dataAccess = [
        {
            "button_name": "查看页面",
            "button_code": "prom_review_data_access"  # 14.5.1
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
            "button_code": "k8s_review_list",  # 15.1
            "is_required": 1
        }
    ]
    # 容器平台-集群概览
    k8s_home__container = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_container",  # 15.2
            "is_required": 1
        }
    ]
    # 容器平台-应用概览
    k8s_home__project = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_project",  # 15.3
            "is_required": 1
        }
    ]

    # 容器平台-集群管理-集群列表
    k8s_home__RouteView1__list_clusterList__list = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_list_cluster_list",  # 15.4.1
        },
        {
            "button_name": "导入集群",
            "button_code": "k8s_cluster_list_import",
        },
        {
            "button_name": "修改集群",
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
            "button_code": "k8s_review_list_cluster_setting",  # 15.4.2
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

    # 容器平台-应用管理-应用列表
    k8s_home__RouteView2__list_projectList__list = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_list_project_list",  # 15.5.1
        },
        {
            "button_name": "进入应用",
            "button_code": "k8s_project_list_enter",
        }
    ]

    # 容器平台-应用管理-应用设置
    k8s_home__RouteView2__list_projectSetting__list = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_list_project_setting",  # 15.5.2
        },
        {
            "button_name": "查看应用授权",
            "button_code": "k8s_project_setting_review",
        },
        {
            "button_name": "应用授权",
            "button_code": "k8s_project_setting_auth",
        },
        {
            "button_name": "查看用户授权(应用)",
            "button_code": "k8s_project_setting_user_review",
        },
        {
            "button_name": "用户授权(应用)",
            "button_code": "k8s_project_setting_user_auth",
        }
    ]

    # 容器平台-平台设置-操作审计
    k8s_RouteView3__list_operAudit__list = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_list_oper_audit",  # 15.6.1
        }
    ]
    # 容器平台-集群管理-节点管理
    k8s_RouteView1__container_nodeManage__container = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_container_node_manage",  # 15.7.1
        }
    ]
    # 容器平台-集群管理-命名空间
    k8s_RouteView1__container_namespace__container = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_container_namespace",  # 15.7.2
        },
        {
            "button_name": "创建应用",
            "button_code": "k8s_namespace_project_create",
        },
        {
            "button_name": "修改应用",
            "button_code": "k8s_namespace_project_update",
        },
        {
            "button_name": "删除应用",
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
            "button_code": "k8s_review_container_eventquery",  # 15.7.3
        }
    ]
    # 容器平台-应用负载-工作负载
    k8s_RouteView1__public_workLoad__public = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_workLoad",  # 15.8.1
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
            "button_name": "修改Deployment",
            "button_code": "k8s_workLoad_deployment_update",
        },
        {
            "button_name": "删除Deployment",
            "button_code": "k8s_workLoad_deployment_delete",
        },
        {
            "button_name": "Deployment扩缩容",
            "button_code": "k8s_workLoad_deployment_expansion_and_contraction_volume",
        },
        {
            "button_name": "Deployment预览/编辑YAML",
            "button_code": "k8s_workLoad_deployment_preview_update_yaml",
        },
        {
            "button_name": "Deployment调整镜像版本",
            "button_code": "k8s_workLoad_deployment_adjust_image_version",
        },
        {
            "button_name": "查看StatefulSet",
            "button_code": "k8s_workLoad_stateful_set_review",
        },
        {
            "button_name": "新建StatefulSet",
            "button_code": "k8s_workLoad_stateful_set_create",
        },
        {
            "button_name": "修改StatefulSet",
            "button_code": "k8s_workLoad_stateful_set_update",
        },
        {
            "button_name": "删除StatefulSet",
            "button_code": "k8s_workLoad_stateful_set_delete",
        },
        {
            "button_name": "StatefulSet扩缩容",
            "button_code": "k8s_workLoad_stateful_set_expansion_and_contraction_volume",
        },
        {
            "button_name": "StatefulSet预览/编辑YAML",
            "button_code": "k8s_workLoad_stateful_set_preview_update_yaml",
        },
        {
            "button_name": "StatefulSet调整镜像版本",
            "button_code": "k8s_workLoad_stateful_set_adjust_image_version",
        },
        {
            "button_name": "查看DaemonSet",
            "button_code": "k8s_workLoad_daemon_set_review",
        },
        {
            "button_name": "新建DaemonSet",
            "button_code": "k8s_workLoad_daemon_set_create",
        },
        {
            "button_name": "修改DaemonSet",
            "button_code": "k8s_workLoad_daemon_set_update",
        },
        {
            "button_name": "删除DaemonSet",
            "button_code": "k8s_workLoad_daemon_set_delete",
        },
        {
            "button_name": "DaemonSet预览/编辑YAML",
            "button_code": "k8s_workLoad_daemon_set_preview_update_yaml",
        },
        {
            "button_name": "DaemonSet调整镜像版本",
            "button_code": "k8s_workLoad_daemon_set_adjust_image_version",
        },
        {
            "button_name": "查看CronJob",
            "button_code": "k8s_workLoad_cron_job_review",
        },
        {
            "button_name": "新建CronJob",
            "button_code": "k8s_workLoad_cron_job_create",
        },
        {
            "button_name": "修改CronJob",
            "button_code": "k8s_workLoad_cron_job_update",
        },
        {
            "button_name": "删除CronJob",
            "button_code": "k8s_workLoad_cron_job_delete",
        },
        {
            "button_name": "CronJob预览/编辑YAML",
            "button_code": "k8s_workLoad_cron_job_preview_update_yaml",
        },
        {
            "button_name": "查看Job",
            "button_code": "k8s_workLoad_job_review",
        },
        {
            "button_name": "新建Job",
            "button_code": "k8s_workLoad_job_create",
        },
        {
            "button_name": "修改Job",
            "button_code": "k8s_workLoad_job_update",
        },
        {
            "button_name": "删除Job",
            "button_code": "k8s_workLoad_job_delete",
        },
        {
            "button_name": "Job预览/编辑YAML",
            "button_code": "k8s_workLoad_job_preview_update_yaml",
        },
        {
            "button_name": "查看ReplicaSet",
            "button_code": "k8s_workLoad_replica_set_review",
        },
        {
            "button_name": "查看Pod",
            "button_code": "k8s_workLoad_pod_review",
        },
        {
            "button_name": "Pod登录",
            "button_code": "k8s_workLoad_pod_login",
        },
        {
            "button_name": "Pod删除",
            "button_code": "k8s_workLoad_pod_delete",
        },
        {
            "button_name": "Pod预览/编辑YAML",
            "button_code": "k8s_workLoad_pod_preview_update_yaml"
        },
    ]
    # 容器平台-应用负载-服务路由
    k8s_RouteView1__public_serviceRoute__public = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_service_route",  # 15.8.2
        },
        {
            "button_name": "查看Service",
            "button_code": "k8s_service_route_service_review",
        },
        {
            "button_name": "新建Service",
            "button_code": "k8s_service_route_service_create",
        },
        {
            "button_name": "修改Service",
            "button_code": "k8s_service_route_service_update",
        },
        {
            "button_name": "删除Service",
            "button_code": "k8s_service_route_service_delete",
        },
        {
            "button_name": "Service预览/编辑YAML",
            "button_code": "k8s_service_route_service_preview_update_yaml",
        },
        {
            "button_name": "查看Ingress",
            "button_code": "k8s_service_route_Ingress_review",
        },
        {
            "button_name": "新建Ingress",
            "button_code": "k8s_service_route_Ingress_create",
        },
        {
            "button_name": "修改Ingress",
            "button_code": "k8s_service_route_Ingress_update",
        },
        {
            "button_name": "删除Ingress",
            "button_code": "k8s_service_route_Ingress_delete",
        },
        {
            "button_name": "Ingress预览/编辑YAML",
            "button_code": "k8s_service_route_Ingress_preview_update_yaml",
        },
        {
            "button_name": "查看Endpoint",
            "button_code": "k8s_service_route_endpoint_review",
        },
        {
            "button_name": "查看EndpointSlice",
            "button_code": "k8s_service_route_endpoint_slice_review",
        },
    ]
    # 容器平台-应用负载-配置管理
    k8s_RouteView1__public_settingManage__public = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_setting_manage",  # 15.8.3
        },
        {
            "button_name": "查看ConfigMap",
            "button_code": "k8s_setting_manage_config_map_review",
        },
        {
            "button_name": "新建ConfigMap",
            "button_code": "k8s_setting_manage_config_map_create",
        },
        {
            "button_name": "修改ConfigMap",
            "button_code": "k8s_setting_manage_config_map_update",
        },
        {
            "button_name": "删除ConfigMap",
            "button_code": "k8s_setting_manage_config_map_delete",
        },
        {
            "button_name": "ConfigMap预览/编辑YAML",
            "button_code": "k8s_setting_manage_config_map_preview_update_yaml"
        },
        {
            "button_name": "查看Secret",
            "button_code": "k8s_setting_manage_secret_review",
        },
        {
            "button_name": "新建Secret",
            "button_code": "k8s_setting_manage_secret_create",
        },
        {
            "button_name": "删除Secret",
            "button_code": "k8s_setting_manage_secret_delete",
        },
    ]
    # 容器平台-应用负载-存储管理
    k8s_RouteView1__public_storageManage__public = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_storage_manage",  # 15.8.4
        },
        {
            "button_name": "查看PersistentVolume",
            "button_code": "k8s_storage_manage_persistent_volume_review",
        },
        {
            "button_name": "新建PersistentVolume",
            "button_code": "k8s_storage_manage_persistent_volume_create",
        },
        {
            "button_name": "删除PersistentVolume",
            "button_code": "k8s_storage_manage_persistent_volume_delete",
        },
        {
            "button_name": "PersistentVolume预览/编辑YAML",
            "button_code": "k8s_storage_manage_persistent_volume_preview_update_yaml",
        },
        {
            "button_name": "查看PersistentVolumeClaim",
            "button_code": "k8s_storage_manage_persistent_volume_claim_review",
        },
        {
            "button_name": "新建PersistentVolumeClaim",
            "button_code": "k8s_storage_manage_persistent_volume_claim_create",
        },
        {
            "button_name": "修改PersistentVolumeClaim",
            "button_code": "k8s_storage_manage_persistent_volume_claim_update",
        },
        {
            "button_name": "删除PersistentVolumeClaim",
            "button_code": "k8s_storage_manage_persistent_volume_claim_delete",
        },
        {
            "button_name": "查看StorageClass",
            "button_code": "k8s_storage_manage_storage_class_review",
        },
        {
            "button_name": "新建StorageClass",
            "button_code": "k8s_storage_manage_storage_class_create",
        },
        {
            "button_name": "修改StorageClass",
            "button_code": "k8s_storage_manage_storage_class_update",
        },
        {
            "button_name": "删除StorageClass",
            "button_code": "k8s_storage_manage_storage_class_delete",
        },
        {
            "button_name": "StorageClass预览/编辑YAML",
            "button_code": "k8s_storage_manage_storage_class_preview_update_yaml",
        },
    ]
    # 容器平台-应用负载-应用市场
    k8s_RouteView1__public_appMarket__container = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_app_market",  # 15.8.5
        }
    ]
    # 容器平台-应用管理-应用设置
    k8s_RouteView1__public_projectSetting__project = [
        {
            "button_name": "查看页面",
            "button_code": "k8s_review_public_project_setting",  # 15.9.1
        },
        {
            "button_name": "查看基本设置",
            "button_code": "k8s_project_setting_project_review",
        },
        {
            "button_name": "修改基本设置",
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

    kbase_home_outer = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_home_outer",  # 16.1
        },
    ]

    kbase_RouteView1_outer_knowledgeBaseList_outer = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_outer_knowledge_base_list",  # 16.2.1
        },
        {
            "button_name": "创建知识库",
            "button_code": "kbase_kbase_create",
        },
    ]

    kbase_RouteView1_outer_Memo = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_outer_memo",  # 16.2.2
        },
    ]

    kbase_RouteView1_favorite_outer = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_favorite_outer",  # 16.2.3
        },
    ]

    kbase_RouteView2_outer_recycleBin_outer = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_recycle_bin_outer",  # 16.3.1
        },
    ]

    kbase_RouteView2_outer_templateManagement_outer = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_outer_template_management",  # 16.3.2
        },
    ]

    kbase_home_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_home_inner",  # 16.4
        },
    ]

    kbase_RouteView3_inner_allArticles_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_all_articles",  # 16.5.1
        },
    ]

    kbase_RouteView3_inner_myArticles_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_my_articles",  # 16.5.2
        },
    ]

    kbase_RouteView3_inner_myCollect_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_my_collect",  # 16.5.3
        },
    ]

    kbase_RouteView4_inner_basicInformation_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_basic_information",  # 16.6.1
        },
    ]

    kbase_RouteView4_inner_memberManagement_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_member_management",  # 16.6.2
        },
    ]

    kbase_RouteView4_inner_recentlyDeleted_inner = [
        {
            "button_name": "查看页面",
            "button_code": "kbase_review_inner_recently_deleted",  # 16.6.3
        },
    ]
    
    log_home = [
        {
            "button_name": "查看页面",
            "button_code": "log_review_home",  # 17.1
        },
    ]
    
    log_RouteView_logRetrieval = [
        {
            "button_name": "查看页面",
            "button_code": "log_review_log_retrieval",  # 17.2.1
        },
    ]

    log_RouteView5_indexManagement = [
        {
            "button_name": "查看页面",
            "button_code": "log_review_index_management",  # 17.6.1
        },
        {
            "button_name": "新建数据视图",
            "button_code": "log_index_view_create",
        },
        {
            "button_name": "设置默认数据视图",
            "button_code": "log_index_view_default",
        },
        {
            "button_name": "修改数据视图",
            "button_code": "log_index_view_update",
        },
        {
            "button_name": "删除数据视图",
            "button_code": "log_index_view_delete",
        },
        {
            "button_name": "授权用户数据视图",
            "button_code": "log_index_view_auth",
        },
        {
            "button_name": "显示索引设置",
            "button_code": "log_index_setting",
        },
        {
            "button_name": "显示索引映射",
            "button_code": "log_index_mapping",
        },
        {
            "button_name": "显示索引统计信息",
            "button_code": "log_index_state",
        },
        {
            "button_name": "关闭索引",
            "button_code": "log_index_close",
        },
        {
            "button_name": "开启索引",
            "button_code": "log_index_view_open",
        },
        {
            "button_name": "合并索引",
            "button_code": "log_index_merge",
        },
        {
            "button_name": "刷新索引",
            "button_code": "log_index_refresh",
        },
        {
            "button_name": "清除索引缓存",
            "button_code": "log_index_clear_cache",
        },
        {
            "button_name": "删除索引",
            "button_code": "log_index_delete",
        },
        {
            "button_name": "清空索引",
            "button_code": "log_index_clear",
        },
    ]

    log_RouteView5_clusterSettings = [
        {
            "button_name": "查看页面",
            "button_code": "log_review_cluster_settings",  # 17.6.2
        },
        {
            "button_name": "切换集群",
            "button_code": "log_cluster_update",
        }
    ]
    
    apm_home = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_home",  # 18.1
        },
    ]
    
    # APM平台-性能监控-服务
    apm_RouteView_service = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_service",  # 18.2.1
        },
        {
            "button_name": "新建服务组",
            "button_code": "apm_service_group_create",
        },
        {
            "button_name": "修改服务组",
            "button_code": "apm_service_group_update",
        },
        {
            "button_name": "删除服务组",
            "button_code": "apm_service_group_delete",
        },
    ]
    
    # APM平台-性能监控-调用链
    apm_RouteView_callChain = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_call_chain",  # 18.2.2
        },
    ]
    
    # APM平台-性能监控-依赖项
    apm_RouteView_dependencies = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_dependencies",  # 18.2.3
        },
    ]
    
    # APM平台-可用性监控-服务拨测
    apm_RouteView3_serviceDialTest = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_service_dial_test"  # 18.3.1
        },
        {
            "button_name": "新建目录",
            "button_code": "apm_server_test_folder_create"
        },
        {
            "button_name": "修改目录",
            "button_code": "apm_server_test_folder_update"
        },
        {
            "button_name": "删除目录",
            "button_code": "apm_server_test_folder_delete"
        },
        {
            "button_name": "新建服务拨测",
            "button_code": "apm_server_test_create"
        },
        {
            "button_name": "修改服务拨测",
            "button_code": "apm_server_test_update"
        },
        {
            "button_name": "删除服务拨测",
            "button_code": "apm_server_test_delete"
        },
        {
            "button_name": "启用服务拨测",
            "button_code": "apm_server_test_enable"
        },
        {
            "button_name": "禁用服务拨测",
            "button_code": "apm_server_test_disable"
        },
        {
            "button_name": "导入服务拨测",
            "button_code": "apm_server_test_import"
        },
        {
            "button_name": "导出服务拨测",
            "button_code": "apm_server_test_export"
        }
    ]
    # APM平台-可用性监控-TLS证书
    apm_RouteView3_TLSManage = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_tls_manage"  # 18.3.2
        }
    ]
    # APM平台-性能监控-告警事件
    apm_RouteView5_alarmEvent = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_alarm_event",  # 18.4.1
        },
    ]
    # APM平台-性能监控-告警规则
    apm_RouteView5_alarmRules = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_alarm_rules",  # 18.4.2
        },
        {
            "button_name": "新建规则",
            "button_code": "apm_alert_rule_create",
        },
        {
            "button_name": "修改规则",
            "button_code": "apm_alert_rule_update",
        },
        {
            "button_name": "删除规则",
            "button_code": "apm_alert_rule_delete",
        },
    ]
    # APM平台-平台设置-数据接入
    apm_setting_dataAccess = [
        {
            "button_name": "查看页面",
            "button_code": "apm_review_data_access",  # 18.5.1
        },
    ]
    
    event = event_home + event_RouteView1_eventHistory + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView3_packs + event_RouteView4_alarmEvent + event_RouteView4_dispatchStrategy + event_RouteView4_notificationStrategy

    auto = auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate

    # prom
    prom = prom_home + prom_RouteView_dashboard + prom_RouteView_dashboardList + prom_RouteView_analyzeList + prom_RouteView_alarmNotify + prom_RouteView_alarmEvent + prom_RouteView_hostMonitoring + prom_RouteView_componentMonitoring + prom_RouteView1_dispatchStrategy + prom_RouteView1_alarmManage + prom_RouteView2_dataAccess

    k8s = k8s_home__list + k8s_home__container + k8s_home__project + k8s_home__RouteView1__list_clusterList__list + k8s_home__RouteView1__list_clusterSetting__list + k8s_home__RouteView2__list_projectList__list + k8s_home__RouteView2__list_projectSetting__list + k8s_RouteView3__list_operAudit__list + k8s_RouteView1__container_nodeManage__container + k8s_RouteView1__container_namespace__container + k8s_RouteView1__container_eventquery__container + k8s_RouteView1__public_workLoad__public + k8s_RouteView1__public_serviceRoute__public + k8s_RouteView1__public_settingManage__public + k8s_RouteView1__public_storageManage__public + k8s_RouteView1__public_projectSetting__project

    kbase = kbase_home_outer + kbase_RouteView1_outer_knowledgeBaseList_outer + kbase_RouteView1_outer_Memo + kbase_RouteView1_favorite_outer + kbase_RouteView2_outer_recycleBin_outer + kbase_RouteView2_outer_templateManagement_outer + kbase_home_inner + kbase_RouteView3_inner_allArticles_inner + kbase_RouteView3_inner_myArticles_inner + kbase_RouteView3_inner_myCollect_inner + kbase_RouteView4_inner_basicInformation_inner + kbase_RouteView4_inner_memberManagement_inner + kbase_RouteView4_inner_recentlyDeleted_inner

    log = log_home + log_RouteView_logRetrieval + log_RouteView5_indexManagement + log_RouteView5_clusterSettings

    apm = apm_home + apm_RouteView_service + apm_RouteView_callChain + apm_RouteView_dependencies + apm_RouteView3_serviceDialTest + apm_RouteView3_TLSManage + apm_RouteView5_alarmEvent + apm_RouteView5_alarmRules + apm_setting_dataAccess
    
    general = event_home + event_RouteView1_eventHistory + event_RouteView2_eventTriggers + event_RouteView2_eventRules + event_RouteView2_eventActions + event_RouteView4_alarmEvent + auto_home + auto_RouteView_fastPatrol + auto_RouteView_timingPatrol + auto_RouteView_patrolLog + auto_RouteView1_patrolTemplate + prom_home + prom_RouteView_dashboard + prom_RouteView_dashboardList + prom_RouteView_analyzeList + prom_RouteView_alarmNotify + prom_RouteView_alarmEvent + prom_RouteView_hostMonitoring + prom_RouteView_componentMonitoring + k8s_home__list + k8s_home__container + k8s_home__project + k8s_home__RouteView1__list_clusterList__list + k8s_home__RouteView2__list_projectList__list + k8s_RouteView3__list_operAudit__list + k8s_RouteView1__container_nodeManage__container + k8s_RouteView1__container_namespace__container + k8s_RouteView1__container_eventquery__container + k8s_RouteView1__public_workLoad__public + k8s_RouteView1__public_serviceRoute__public + k8s_RouteView1__public_settingManage__public + k8s_RouteView1__public_storageManage__public + kbase_home_outer + kbase_RouteView1_outer_knowledgeBaseList_outer + kbase_RouteView1_outer_Memo + kbase_RouteView1_favorite_outer + kbase_home_inner + kbase_RouteView3_inner_allArticles_inner + kbase_RouteView3_inner_myArticles_inner + kbase_RouteView3_inner_myCollect_inner + log_RouteView_logRetrieval + apm_home + apm_RouteView_service + apm_RouteView_callChain + apm_RouteView_dependencies + apm_RouteView3_serviceDialTest + apm_RouteView3_TLSManage + apm_RouteView5_alarmEvent
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
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/alarmEvent",
                            "priority": "8.2.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_alarmEvent
                        },
                        {
                            "menu_name": "事件历史",
                            "menu_code": "eventHistory",
                            "menu_type": "menu",
                            "menu_address": "/eventQuery/eventHistory",
                            "priority": "8.2.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView1_eventHistory
                        },

                    ]
                },
                {
                    "menu_name": "智能告警",
                    "menu_code": "RouteView4",
                    "menu_type": "directory",
                    "menu_address": "/intelligentAlarm",
                    "priority": "8.3",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "分派策略",
                            "menu_code": "dispatchStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/dispatchStrategy",
                            "priority": "8.3.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_dispatchStrategy
                        },
                        {
                            "menu_name": "通知策略",
                            "menu_code": "notificationStrategy",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/notificationStrategy",
                            "priority": "8.3.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_notificationStrategy
                        },
                        {
                            "menu_name": "告警接入",
                            "menu_code": "alarmAccess",
                            "menu_type": "menu",
                            "menu_address": "/intelligentAlarm/alarmAccess",
                            "priority": "8.3.4",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView4_alarmAccess
                        },
                    ]
                },
                {
                    "menu_name": "事件运营",
                    "menu_code": "RouteView2",
                    "menu_type": "directory",
                    "menu_address": "/eventOperation",
                    "priority": "8.4",
                    "platform_cname": "event",
                    "children": [
                        {
                            "menu_name": "事件接入",
                            "menu_code": "eventTriggers",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventTriggers",
                            "priority": "8.4.1",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventTriggers
                        },
                        {
                            "menu_name": "触发规则",
                            "menu_code": "eventRules",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventRules",
                            "priority": "8.4.2",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventRules
                        },
                        {
                            "menu_name": "执行动作",
                            "menu_code": "eventActions",
                            "menu_type": "menu",
                            "menu_address": "/eventOperation/eventActions",
                            "priority": "8.4.3",
                            "platform_cname": "event",
                            "children": [],
                            "buttons": event_RouteView2_eventActions
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
                        },
                        {
                            "menu_name": "应用分析",
                            "menu_code": "analyze",
                            "menu_type": "menu",
                            "menu_address": "/monitorScreen/analyze",
                            "priority": "14.2.3",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_analyzeList
                        },
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
                            "menu_name": "告警通知",
                            "menu_code": "alarmNotify",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/alarmNotify",
                            "priority": "14.3.1",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_alarmNotify
                        },
                        {
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/alarmEvent",
                            "priority": "14.3.2",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_alarmEvent
                        },
                        {
                            "menu_name": "主机监控",
                            "menu_code": "hostMonitoring",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/hostMonitoring",
                            "priority": "14.3.3",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_hostMonitoring
                        },
                        {
                            "menu_name": "组件监控",
                            "menu_code": "componentMonitoring",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/componentMonitoring",
                            "priority": "14.3.4",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView_componentMonitoring
                        }
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
                        },
                        {
                            "menu_name": "通知规则",
                            "menu_code": "alarmManage",
                            "menu_type": "menu",
                            "menu_address": "/alarmManagement/alarmManage",
                            "priority": "14.4.2",
                            "platform_cname": "prom",
                            "children": [],
                            "buttons": prom_RouteView1_alarmManage
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
                    "menu_name": "应用概览",
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
                    "menu_name": "应用管理",
                    "menu_code": "RouteView2__list",
                    "menu_type": "directory",
                    "menu_address": "/projectManage",
                    "priority": "15.5",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "应用列表",
                            "menu_code": "projectList__list",
                            "menu_type": "menu",
                            "menu_address": "/projectManage/projectList",
                            "priority": "15.5.1",
                            "platform_cname": "k8s",
                            "children": [],
                            "buttons": k8s_home__RouteView2__list_projectList__list
                        },
                        {
                            "menu_name": "应用设置",
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
                    "menu_name": "应用管理",
                    "menu_code": "RouteView1__project",
                    "menu_type": "directory",
                    "menu_address": "/projectManage__project",
                    "priority": "15.9",
                    "platform_cname": "k8s",
                    "children": [
                        {
                            "menu_name": "应用设置",
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
        {
            "menu_name": "知识库",
            "menu_code": "kbase",
            "menu_type": "platform",
            "menu_address": "/o/kbase/",
            "priority": "16",
            "platform_cname": "kbase",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home_outer",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "16.1",
                    "platform_cname": "kbase",
                    "children": [],
                    "buttons": kbase_home_outer
                },
                {
                    "menu_name": "知识库管理",
                    "menu_code": "RouteView1_outer",
                    "menu_type": "directory",
                    "menu_address": "/knowledgeManagement",
                    "priority": "16.2",
                    "platform_cname": "kbase",
                    "children": [
                        {
                            "menu_name": "知识库",
                            "menu_code": "knowledgeBaseList_outer",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/knowledgeBaseList",
                            "priority": "16.2.1",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView1_outer_knowledgeBaseList_outer
                        },
                        {
                            "menu_name": "备忘录",
                            "menu_code": "memo_outer",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/memo",
                            "priority": "16.2.2",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView1_outer_Memo
                        }, {
                            "menu_name": "收藏夹",
                            "menu_code": "favorite_outer",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/favorite",
                            "priority": "16.2.3",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView1_favorite_outer
                        }
                    ]
                },
                {
                    "menu_name": "设置",
                    "menu_code": "RouteView2_outer",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "16.3",
                    "platform_cname": "kbase",
                    "children": [
                        {
                            "menu_name": "回收站",
                            "menu_code": "recycleBin_outer",
                            "menu_type": "menu",
                            "menu_address": "/setting/recycleBin",
                            "priority": "16.3.1",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView2_outer_recycleBin_outer
                        },
                        # {
                        #     "menu_name": "模板管理",
                        #     "menu_code": "templateManagement_outer",
                        #     "menu_type": "menu",
                        #     "menu_address": "/setting/templateManagement",
                        #     "priority": "16.3.2",
                        #     "platform_cname": "kbase",
                        #     "children": [],
                        #     "buttons": kbase_RouteView2_outer_templateManagement_outer
                        # }
                    ]
                },
                {
                    "menu_name": "知识库概览",
                    "menu_code": "home_inner",
                    "menu_type": "directory",
                    "menu_address": "/home_inner",
                    "priority": "16.4",
                    "platform_cname": "kbase",
                    "children": [],
                    "buttons": kbase_home_inner
                },
                {
                    "menu_name": "知识库",
                    "menu_code": "RouteView3_inner",
                    "menu_type": "directory",
                    "menu_address": "/knowledgeBase",
                    "priority": "16.5",
                    "platform_cname": "kbase",
                    "children": [
                        {
                            "menu_name": "所有文章",
                            "menu_code": "allArticles_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/allArticles",
                            "priority": "16.5.1",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView3_inner_allArticles_inner
                        },
                        {
                            "menu_name": "我的文章",
                            "menu_code": "myArticles_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/myArticles",
                            "priority": "16.5.2",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView3_inner_myArticles_inner
                        },
                        {
                            "menu_name": "我的收藏",
                            "menu_code": "myCollect_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBase/myCollect",
                            "priority": "16.5.3",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView3_inner_myCollect_inner
                        }
                    ]
                },
                {
                    "menu_name": "知识库设置",
                    "menu_code": "RouteView4_inner",
                    "menu_type": "directory",
                    "menu_address": "/knowledgeBaseSettings",
                    "priority": "16.6",
                    "platform_cname": "kbase",
                    "children": [
                        {
                            "menu_name": "基本信息",
                            "menu_code": "basicInformation_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBaseSettings/basicInformation",
                            "priority": "16.6.1",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView4_inner_basicInformation_inner
                        },
                        {
                            "menu_name": "成员管理",
                            "menu_code": "memberManagement_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBaseSettings/memberManagement",
                            "priority": "16.6.2",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView4_inner_memberManagement_inner
                        },
                        {
                            "menu_name": "最近删除",
                            "menu_code": "recentlyDeleted_inner",
                            "menu_type": "menu",
                            "menu_address": "/knowledgeBaseSettings/recentlyDeleted",
                            "priority": "16.6.3",
                            "platform_cname": "kbase",
                            "children": [],
                            "buttons": kbase_RouteView4_inner_recentlyDeleted_inner
                        }
                    ]
                },
            ]
        },
        {
            "menu_name": "日志平台",
            "menu_code": "log",
            "menu_type": "platform",
            "menu_address": "/o/log/",
            "priority": "17",
            "platform_cname": "log",
            "children": [
                {
                    "menu_name": "搜索",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "17.1",
                    "platform_cname": "log",
                    "children": [],
                    "buttons": log_home
                },
                {
                    "menu_name": "数据查询",
                    "menu_code": "RouteView",
                    "menu_type": "directory",
                    "menu_address": "/dataQuery",
                    "priority": "17.2",
                    "platform_cname": "log",
                    "children": [
                        {
                            "menu_name": "开发者",
                            "menu_code": "logRetrieval",
                            "menu_type": "menu",
                            "menu_address": "/dataQuery/logRetrieval",
                            "priority": "17.2.1",
                            "platform_cname": "log",
                            "children": [],
                            "buttons": log_RouteView_logRetrieval
                        }
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView5",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "17.6",
                    "platform_cname": "log",
                    "children": [
                        {
                            "menu_name": "索引管理",
                            "menu_code": "indexManagement",
                            "menu_type": "menu",
                            "menu_address": "/setting/indexManagement",
                            "priority": "17.6.1",
                            "platform_cname": "log",
                            "children": [],
                            "buttons": log_RouteView5_indexManagement
                        },
                        {
                            "menu_name": "集群设置",
                            "menu_code": "clusterSettings",
                            "menu_type": "menu",
                            "menu_address": "/setting/clusterSettings",
                            "priority": "17.6.2",
                            "platform_cname": "log",
                            "children": [],
                            "buttons": log_RouteView5_clusterSettings
                        }
                    ]
                },
            ]
        },
        {
            "menu_name": "APM平台",
            "menu_code": "apm",
            "menu_type": "platform",
            "menu_address": "/o/apm/",
            "priority": "18",
            "platform_cname": "apm",
            "children": [
                {
                    "menu_name": "概览",
                    "menu_code": "home",
                    "menu_type": "directory",
                    "menu_address": "/",
                    "priority": "18.1",
                    "platform_cname": "apm",
                    "children": [],
                    "buttons": apm_home
                },
                {
                    "menu_name": "性能监控",
                    "menu_code": "RouteView",
                    "menu_type": "directory",
                    "menu_address": "/performanceMonitoring",
                    "priority": "18.2",
                    "platform_cname": "apm",
                    "children": [
                        {
                            "menu_name": "服务",
                            "menu_code": "service",
                            "menu_type": "menu",
                            "menu_address": "/performanceMonitoring/service",
                            "priority": "18.2.1",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView_service
                        },
                        {
                            "menu_name": "调用链",
                            "menu_code": "callChain",
                            "menu_type": "menu",
                            "menu_address": "/performanceMonitoring/callChain",
                            "priority": "18.2.2",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView_callChain
                        },
                        {
                            "menu_name": "依赖项",
                            "menu_code": "dependencies",
                            "menu_type": "menu",
                            "menu_address": "/performanceMonitoring/dependencies",
                            "priority": "18.2.3",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView_dependencies
                        }
                    ]
                },
                {
                    "menu_name": "可用性监控",
                    "menu_code": "RouteView3",
                    "menu_type": "directory",
                    "menu_address": "/availabilityMonitoring",
                    "priority": "18.3",
                    "platform_cname": "apm",
                    "children": [
                        {
                            "menu_name": "服务拨测",
                            "menu_code": "serviceDialTest",
                            "menu_type": "menu",
                            "menu_address": "/monitoringObject/serviceDialTest",
                            "priority": "18.3.1",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView3_serviceDialTest
                        },
                        {
                            "menu_name": "TLS证书",
                            "menu_code": "TLSManage",
                            "menu_type": "menu",
                            "menu_address": "/availabilityMonitoring/TLSManage",
                            "priority": "18.3.2",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView3_TLSManage
                        },
                    ]
                },
                {
                    "menu_name": "告警管理",
                    "menu_code": "RouteView5",
                    "menu_type": "directory",
                    "menu_address": "/alarmManagement",
                    "priority": "18.4",
                    "platform_cname": "apm",
                    "children": [
                        {
                            "menu_name": "告警事件",
                            "menu_code": "alarmEvent",
                            "menu_type": "menu",
                            "menu_address": "/alarmManagement/alarmEvent",
                            "priority": "18.4.1",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView5_alarmEvent
                        },
                        {
                            "menu_name": "告警规则",
                            "menu_code": "alarmRules",
                            "menu_type": "menu",
                            "menu_address": "/alarmManagement/alarmRules",
                            "priority": "18.4.2",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_RouteView5_alarmRules
                        },
                    ]
                },
                {
                    "menu_name": "平台设置",
                    "menu_code": "RouteView2",
                    "menu_type": "directory",
                    "menu_address": "/setting",
                    "priority": "18.5",
                    "platform_cname": "apm",
                    "children": [
                        {
                            "menu_name": "数据接入",
                            "menu_code": "dataAccess",
                            "menu_type": "menu",
                            "menu_address": "/setting/dataAccess",
                            "priority": "18.5.1",
                            "platform_cname": "apm",
                            "children": [],
                            "buttons": apm_setting_dataAccess
                        }
                    ]
                },
            ]
        },
    ]

    # 内置权限
    BUILD_IN_STRATEGY_LIST = [
        {
            "strategy_name": "超级管理员",
            "strategy_type": "built-in",
            "description": "拥有所有平台的所有权限，并登陆【统一权限】",
            "platform_name_list": ["event", "auto", "prom", "k8s", "pipeline", "deploy", "kbase", "log", "apm"],
            "buttons": event + auto + prom + k8s + kbase + log + apm
        },
        {
            "strategy_name": "稳定性平台管理员",
            "strategy_type": "built-in",
            "description": "拥有【稳定性平台】所有菜单权限",
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
            "strategy_name": "知识库管理员",
            "strategy_type": "built-in",
            "description": "拥有【知识库】所有菜单权限",
            "platform_name_list": ["kbase"],
            "buttons": kbase
        },
        {
            "strategy_name": "日志管理员",
            "strategy_type": "built-in",
            "description": "拥有【日志平台】所有菜单权限",
            "platform_name_list": ["log"],
            "buttons": log
        },
        {
            "strategy_name": "APM平台管理员",
            "strategy_type": "built-in",
            "description": "拥有【APM平台】所有菜单权限",
            "platform_name_list": ["apm"],
            "buttons": apm
        },
        {
            "strategy_name": "普通用户",
            "strategy_type": "built-in",
            "description": "普通用户，仅可以访问工作台和授权的平台菜单",
            "platform_name_list": ["event", "auto", "prom", "k8s", "kbase", "log", "apm"],
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
                    "describe": "稳定性和故障自愈",
                    "icon_name": "event.png",
                    "update_nav_name": "事件中心",
                },
                {
                    "nav_name": "智能巡检",
                    "nav_url": "/o/auto/",
                    "describe": "运维自动化巡检",
                    "icon_name": "auto.png"
                },
                {
                    "nav_name": "知识库",
                    "nav_url": "/o/kbase/",
                    "describe": "知识库管理",
                    "icon_name": "kbase.png"
                }
            ]
        },
        {
            "group_name": "云原生",
            "nav_list": [
                {
                    "nav_name": "容器平台",
                    "nav_url": "/o/k8s/",
                    "describe": "Kubernetes多集群管理",
                    "icon_name": "k8s.png"
                }
            ]
        },
        {
            "group_name": "可观测",
            "nav_list": [
                {
                    "nav_name": "应用监控",
                    "nav_url": "/o/prom/",
                    "describe": "应用可观测平台",
                    "icon_name": "prom.png"
                },
                {
                    "nav_name": "日志平台",
                    "nav_url": "/o/log/",
                    "describe": "统一日志平台",
                    "icon_name": "log.png"
                },
                {
                    "nav_name": "APM平台",
                    "nav_url": "/o/apm/",
                    "describe": "应用性能监控平台",
                    "icon_name": "apm.png"
                }
            ]
        }
    ]

    # 通知模板
    PLATFORM_TEMPLATE = [
        {
            "platform_name": "APM平台",
            "platform_code": "apm",
            "template_list": [
                {
                    # "id": 10,
                    "id": 19001,
                    "type": "服务拨测告警通知",
                    "title_one": "服务拨测告警",
                    "title_two": "告警内容",
                    "info": "您的服务拨测：{} 发现了新的告警！<br /> 告警信息：{}",
                    "parameter_describe": "service_check_name, info",
                    "platform": "APM平台"
                },
                {
                    # "id": 13,
                    "id": 19002,
                    "type": "服务拨测恢复告警通知",
                    "title_one": "服务拨测恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的服务拨测：{} 告警已恢复！<br /> 告警信息：{}",
                    "parameter_describe": "service_check_name, info",
                    "platform": "APM平台"
                },
                {
                    # "id": 14,
                    "id": 19003,
                    "type": "TLS证书告警通知",
                    "title_one": "TLS证书告警",
                    "title_two": "告警内容",
                    "info": "您的TLS证书 {} 发现告警(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 相关拨测：{}",
                    "parameter_describe": "tls_subject, rule_name, context_status_message, service_message",
                    "platform": "APM平台"
                },
                {
                    # "id": 15,
                    "id": 19004,
                    "type": "TLS证书恢复告警通知",
                    "title_one": "TLS证书恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的TLS证书：{} 证书告警已恢复(由告警规则 {} 触发！<br /> 告警信息：{}<br /> 相关拨测：{}",
                    "parameter_describe": "tls_subject, rule_name, context_status_message, service_message",
                    "platform": "APM平台"
                },
                {
                    "id": 19005,  # apm_error_rate  服务错误率阈值
                    "type": "APM服务错误超阈值告警通知",
                    "title_one": "APM服务错误超阈值告警",
                    "title_two": "告警内容",
                    "info": "您的服务 {} 发现告警(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19006,  # apm_error_rate  服务错误率阈值
                    "type": "APM服务错误超阈值恢复告警通知",
                    "title_one": "APM服务错误超阈值恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的服务 {} 发现告警已恢复(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19007,  # apm_transaction_error_rate  服务事务错误率阈值
                    "type": "APM服务事务错误超阈值告警通知",
                    "title_one": "APM服务事务错误超阈值告警",
                    "title_two": "告警内容",
                    "info": "您的服务 {} 发现告警(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19008,  # apm_transaction_error_rate  服务事务错误率阈值
                    "type": "APM服务事务错误超阈值恢复告警通知",
                    "title_one": "APM服务事务错误超阈值恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的服务 {} 发现告警已恢复(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19009,  # apm_transaction_duration  服务事务延迟阈值
                    "type": "APM服务事务延迟超阈值告警通知",
                    "title_one": "APM服务事务延迟超阈值告警",
                    "title_two": "告警内容",
                    "info": "您的服务 {} 发现告警(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19010,  # apm_transaction_duration  服务事务延迟阈值
                    "type": "APM服务事务延迟超阈值恢复告警通知",
                    "title_one": "APM服务事务延迟超阈值恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的服务 {} 发现告警已恢复(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19011,  # apm_anomaly  服务健康度阈值
                    "type": "APM服务健康度超阈值告警通知",
                    "title_one": "APM服务健康度超阈值告警",
                    "title_two": "告警内容",
                    "info": "您的服务 {} 发现告警(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
                {
                    "id": 19012,  # apm_anomaly  服务健康度阈值
                    "type": "APM服务健康度超阈值恢复告警通知",
                    "title_one": "APM服务健康度超阈值恢复告警",
                    "title_two": "恢复告警内容",
                    "info": "您的服务 {} 发现告警已恢复(由告警规则 {} 触发)！<br /> 告警信息：{}<br /> 告警时间：{}",
                    "parameter_describe": "context_service_name, rule_name, context_status_message alert_date",
                    "platform": "APM平台"
                },
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
                    "info": "您的主机：{} 发现了新的告警通知！<br />{}",
                    "parameter_describe": "title, event_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8002,
                    "type": "事件中心认领告警通知",
                    "title_one": "事件中心认领告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br />告警信息：{}",
                    "parameter_describe": "title, event_claim_alert_info",
                    "platform": "事件中心"
                },
                {
                    "id": 8003,
                    "type": "事件中心关闭告警通知",
                    "title_one": "事件中心关闭告警",
                    "title_two": "告警内容",
                    "info": "您的主机：{} 发现了新的告警通知！<br />告警信息：{}",
                    "parameter_describe": "title, event_close_alert_info",
                    "platform": "事件中心"
                },
            ]
        },
        {
            "platform_name": "应用监控",
            "platform_code": "prom",
            "template_list": [
                {
                    "id": 15001,
                    "type": "应用监控告警通知",
                    "title_one": "应用监控告警",
                    "title_two": "告警内容",
                    "info": "应用监控发现新的告警 {} ！<br />{}",
                    "parameter_describe": "info",
                    "platform": "应用监控"
                },
                {
                    "id": 15002,
                    "type": "应用监控恢复告警通知",
                    "title_one": "应用监控恢复告警",
                    "title_two": "告警内容",
                    "info": "应用监控发现新的恢复告警 {} ！<br />{}",
                    "parameter_describe": "info",
                    "platform": "应用监控"
                },
                {
                    "id": 15003,
                    "type": "应用监控升级告警通知",
                    "title_one": "应用监控升级告警",
                    "title_two": "告警内容",
                    "info": "应用监控发现新的升级告警 {} ！<br />{}",
                    "parameter_describe": "info",
                    "platform": "应用监控"
                },
            ]
        },
    ]

    HOME_PAGE_TEMPLATE = [
        {
            "unique": "prom_one",
            "platform": "prom",
            "platform_name": "应用监控",
            "name": "应用监控概览",
            "attribute": {
                "x": 0,
                "y": 25,
                "w": 9,
                "h": 9,
                "i": "11",
                "minW": 8,
                "minH": 9,
                "maxW": 24,
                "maxH": 16,
                "static": False,
                "platform_key": ''
            },
            "group_name": "默认分组",
            "show_type": "1",
            "api": "api/workbench/v0_1/home-page-prom/"
        },
        {
            "unique": "prom_two",
            "platform": "prom",
            "platform_name": "应用监控",
            "name": "应用监控告警事件",
            "attribute": {
                "x": 0,
                "y": 8,
                "w": 18,
                "h": 13,
                "i": "13",
                "minW": 16,
                "minH": 13,
                "maxW": 24,
                "maxH": 16,
                "static": False,
                "platform_key": "prom"
            },
            "group_name": "默认分组",
            "show_type": "1",
            "api": "api/workbench/v0_1/home-page-prom/"
        },
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
            if resp.status_code in [200, 400]:
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
            return self.session.cookies.get("bk_token")
        except:
            return False

    def init_event_auto_menu_strategy(self):
        """rbac 初始化菜单，权限策略"""
        try:
            # API = "/t/rbac//api/rbac/v0_1/init_ee_data/"
            # API = "/api/rbac/v0_1/init_ee_data/"
            API = "/o/rbac/api/rbac/v0_1/init_ee_data/"
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
            # NAV_API = "/t/workbench/api/workbench/v0_1/update-nav-v2/"
            # NAV_API = "/api/workbench/v0_1/update-nav-v2/"
            NAV_API = "/o/workbench/api/workbench/v0_1/update-nav-v2/"
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
            NAV_API = "/o/workbench/api/workbench/v0_1/update-message-template/"
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

    def workbench_add_home_page_template(self):
        """工作台初始化站内信模板"""
        try:
            NAV_API = "/o/workbench/api/workbench/v0_1/update-home-page-template/"
            TEMPLATE_API = self.paas_domain + NAV_API

            data = InitData()
            platform_data = {"home_page_template_list": data.HOME_PAGE_TEMPLATE}

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
            API = "/o/event/api/event/v0_1/init-st2/"
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

    def init_celery_queue(self, queue):
        API = "/o/control/api/control/v0_1/celery-queue-init/"
        url = self.paas_domain + API
        res = self.session.post(url, json={"init_data_list": queue}, verify=False)
        try:
            res_data = res.json()
        except Exception:
            return False, "后台任务初始化中 API连接不成功，请检查API地址{}".format(res.content.decode())
        if res.status_code == 200:
            if str(res_data.get("code", "")) == "200":
                return True, "后台任务初始化成功！"
            else:
                return False, res_data.get("message")
        else:
            return False, "后台任务初始化中 API连接不成功，请检查API地址{}".format(url)


def start(paas_domain, username, password, st2_url="", st2_username="", st2_password="", init_type=None):
    run_obj = OpsAnyApi(paas_domain=paas_domain, username=username, password=password)
    default_list = ["menu", "nav", "temp", "home_page", "st2", "queue"]
    if (not init_type) or (init_type=="all"):
        init_type_list = default_list
    else:
        init_type_list = init_type.split(",")

    # if init_type not in ["menu", "nav", "temp", "st2", "all"]:
    #     print("Nothing was executed, init_type choose: all | menu | nav | temp | st2")

    if "queue" in init_type_list:
        # 初始化管控平台后台任务
        queue_status, queue_data = run_obj.init_celery_queue(InitData.saas_queue)
        print("[SUCCESS] Init control celery queue success") if queue_status else print(
            "[ERROR] Init control celery queue error, error info: {}".format(queue_data))

    if "menu" in init_type_list:
        # 初始化事件中心，智能巡检菜单，权限策略
        rbac_status, rbac_data = run_obj.init_event_auto_menu_strategy()
        print("[SUCCESS] Init menu strategy success") if rbac_status else print(
            "[ERROR] Init menu strategy error, error info: {}".format(rbac_data))

    if "nav" in init_type_list:
        # 初始化工作台导航目录
        add_nav_status, add_nav_data = run_obj.workbench_add_nav()
        print("[SUCCESS] Add nav success") if add_nav_status else print(
            "[ERROR] Add nav error, error info: {}".format(add_nav_data))

    if "temp" in init_type_list:
        # 初始化工作台站内信模板
        add_nav_status, add_nav_data = run_obj.workbench_add_message_template()
        print("[SUCCESS] Add message_template success") if add_nav_status else print(
            "[ERROR] Add message_template error, error info: {}".format(add_nav_data))

    if "home_page" in init_type_list:
        # 初始化工作台站内信模板
        add_nav_status, add_home_page_data = run_obj.workbench_add_home_page_template()
        print("[SUCCESS] Add home_page_template success") if add_nav_status else print(
            "[ERROR] Add home_page_template error, error info: {}".format(add_home_page_data))

    if "st2" in init_type_list:
        # 初始化StackStorm
        if st2_url:
            st2_status, st2_data = run_obj.init_event_st2(st2_url, st2_username, st2_password)
            print("[SUCCESS] init st2 success:") if st2_status else print(
                "[ERROR] init st2 error info, error info: {}".format(str(st2_data)))
        else:
            print("[ERROR] init st2 error info, st2_url can not be empty")


def add_parameter():
    parameter = argparse.ArgumentParser()
    parameter.add_argument("--domain", help="domain parameters.", required=True)
    parameter.add_argument("--username", help="opsany admin username.", required=True)
    parameter.add_argument("--password", help="opsany admin password.", required=True)
    parameter.add_argument("--st2_url", help="StackStorm service url.", required=False)
    parameter.add_argument("--st2_username", help="StackStorm service username.", required=False)
    parameter.add_argument("--st2_password", help="StackStorm service password.", required=False)
    parameter.add_argument("--init_type", help="init type [all | menu | nav | temp | home_page | st2 | menu,nav,temp ]", required=False)
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
"""  # 需要将RBAC更新到2.2.3
# 第一次初始化，需要将企业版平台菜单权限，导航，站内信模板，事件中心st2服务全部初始化
python3 saas-ee-init.py --domain https://domain.com --username username --password password --st2_url st2_url --st2_username st2_username --st2_password st2_password
# 只初始化或更新企业版平台菜单权限，导航，站内信模板
python3 saas-ee-init.py --domain https://domain.com --username username --password password --init_type menu,nav,temp,home_page
# 增加新saas,更新脚本
python saas-ee-init.py --domain http://192.168.0.13:8066 --username huxingqi --password Huxingqi --init_type menu,nav
"""
