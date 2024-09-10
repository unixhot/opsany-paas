import json

from redis import Redis, StrictRedis
from django_redis import get_redis_connection


def get_redis_dict_data(conn, token):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    data_b = conn.get(token)
    try:
        data = data_b.decode("utf-8")
    except Exception as e:
        return data_b
    try:
        data = eval(data)
    except Exception as e:
        try:
            data = json.loads(data)
        except Exception as e:
            return data
    return data

def get_redis_str_data(conn, token):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    data_b = conn.get(token)
    try:
        data = data_b.decode("utf-8")
    except Exception as e:
        return data_b
    return data

def set_redis_data(conn, key, value, ex=None):
    if not isinstance(conn, (Redis, StrictRedis)):
        conn = get_redis_connection(str(conn))
    res = conn.set(key, value)
    if ex and isinstance(ex, int):
        conn.expire(key, ex)
    return res
