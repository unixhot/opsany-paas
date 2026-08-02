import datetime
import inspect

from opsanymcp.api.base_api import BaseObj


class KbaseApi(BaseObj):
    def opsany_kbase_read_kbase_list(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        data = {
            "data_type": kwargs.get("data_type") or "all",
            "search_type": kwargs.get("search_type"),
            "search_data": kwargs.get("search_data"),
        }
        result_headers = {
            "unique_code": "知识库唯一标识(拉取知识库内文章使用)",
            "name": "知识库名称",
            "public": "是否为公共知识库",
            "description": "知识库描述",
            "created_at": "知识库创建时间",
            "cover": "知识库图标",
            "owner_user": "知识库拥有者(创建人)",
            "favorite": "是否点收藏",
        }
        return self._base_run(fun_name, "GET", data, {}, result_headers, kwargs)

    def opsany_kbase_read_kbase_article(self, **kwargs):
        fun_name = inspect.currentframe().f_code.co_name
        data = {}
        if not kwargs.get("data_type"):
            kwargs["data_type"] = "all"
        if kwargs.get("unique_code"):
            kwargs["data_type"] = "single"
        for i in ["data_type", "kbase", "current", "pageSize", "search_type", "search_data", "unique_code"]:
            if i in kwargs:
                data[i] = kwargs.get(i)
        result_headers = {
            "unique_code": "文章唯一标识(拉取文章内容使用)",
            "title": "文章标题",
            "contents": "文章内容",
            "contents_type": "contents_type文章类型(1: 富文本 2：markdown)",
            "review_count": "阅读数量",
            "comment_count": "评论数量",
            "like_count": "点赞数量",
            "favorite_count": "首次数量",
            "kbase": "知识库唯一标识",
            "folder": "知识库目录(第一个问知识库名称，后面我目录)",
            "create_user": "创建人",
            "last_update_user": "最后更新人",
            "created_at": "创建时间",
            "last_update_time": "最后更新时间",
            "favorite": "我是否收藏",
            "like": "我是否点赞",
        }
        return self._base_run(fun_name, "GET", data, {}, result_headers, kwargs)
