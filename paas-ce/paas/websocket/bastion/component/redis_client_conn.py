import aioredis
import json
from django.conf import settings

async def get_async_redis_connection(alias="default"):
    redis_config = settings.CACHES[alias]
    conn = await aioredis.from_url(
        f"redis://{redis_config['LOCATION']}",
        decode_responses=True
    )
    return conn

async def get_redis_dict_data_async(conn, token):
    if not isinstance(conn, aioredis.Redis):
        conn = await get_async_redis_connection(str(conn))
    data = await conn.get(token)
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        try:
            return eval(data)
        except Exception:
            return data

async def get_redis_str_data_async(conn, token):
    if not isinstance(conn, aioredis.Redis):
        conn = await get_async_redis_connection(str(conn))
    return await conn.get(token)

async def set_redis_data_async(conn, key, value, ex=None):
    if not isinstance(conn, aioredis.Redis):
        conn = await get_async_redis_connection(str(conn))
    await conn.set(key, value, ex=ex)
    return True
