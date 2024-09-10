# -*- coding: utf-8 -*-
from ..base import ComponentAPI


class CollectionsGSE(object):
    """Collections of GSE APIS"""

    def __init__(self, client):
        self.client = client

        self.get_agent_info = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_info/',
            description=u'Agent心跳信息查询'
        )
        self.get_agent_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_status/',
            description=u'Agent在线状态查询'
        )
        self.proc_create_session = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_create_session/',
            description=u'进程管理：新建 session'
        )
        self.proc_get_task_result_by_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/gse/proc_get_task_result_by_id/',
            description=u'进程管理：获取任务结果'
        )
        self.proc_run_command = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_run_command/',
            description=u'进程管理：执行命令'
        )
