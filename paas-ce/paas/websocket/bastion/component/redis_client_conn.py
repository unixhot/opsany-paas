import ast
import json
import logging

from redis import Redis, StrictRedis
from django_redis import get_redis_connection

logger = logging.getLogger("app")


def get_redis_dict_data(conn, token):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    data_b = conn.get(token)
    if data_b is None:
        return None
    try:
        data = data_b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return data_b
    # 先尝试安全的 ast.literal_eval 解析（因为数据写入时可能是直接存的 Python 对象字面量）
    # ast.literal_eval 只解析 dict/list/str/int 等字面量，不会执行任意代码，比 eval() 安全
    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError, MemoryError):
        pass
    # 再尝试 json.loads（处理 JSON 格式数据）
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        logger.error("[get_redis_dict_data] Invalid JSON data for key: %s", str(token)[:8])
        return data


def get_redis_str_data(conn, token):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    data_b = conn.get(token)
    if data_b is None:
        return None
    try:
        data = data_b.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        return data_b
    return data


def set_redis_data(conn, key, value, ex=None):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    res = conn.set(key, value)
    if ex and isinstance(ex, int):
        conn.expire(key, ex)
    return res
