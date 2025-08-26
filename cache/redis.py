import datetime
import json
import logging

from functools import wraps
from types import NoneType
from typing import Any, get_args
from redis.asyncio import Redis

from configs import config


redis_db = Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    db=config.REDIS_DB,
)


async def redis_set(key: str, val: any, ttl: int = None):
    json_to_set = json.dumps({"result": val})
    await redis_db.set(key, json_to_set, ex=(ttl * 60) if ttl else None)


async def redis_get(key: str) -> Any | None:
    try:
        res = await redis_db.get(key)
        val = json.loads(res)["result"]
    except Exception as e:
        logging.error(e)
        return None

    return val


async def redis_mexists(*keys: list[str]):
    async with redis_db.pipeline() as pipe:
        for key in keys:
            pipe.exists(key)
        return await pipe.execute()


async def redis_del(key: str):
    await redis_db.delete(key)


SIMPLE_CLASSES = [bool, str, int, float, list, tuple, dict, set, datetime.datetime, datetime.date, NoneType]


def redis_cache(ttl: int = None, key: str = None, args_offset: int = 0) -> any:
    """Caching the result of a function execution in redis.

    :param ttl: time to live in minutes
    :param key: custom key (func.__name__ by default)
    :param args_offset: args offset count to skip (for example if Session class is in params)
    :return that wrapper function return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            model_class = func.__annotations__.get("return")
            cache_key = (key or f"{func.__name__}") + f"{args[args_offset:]}"
            try:
                val = await redis_get(cache_key)
            except Exception as e:
                logging.error(e)
            else:
                if val is not None:
                    if isinstance(val, list):
                        cls = get_args(model_class)[0]
                        return [parse_json_to_model(cls, row) for row in val]
                    if any(issubclass(model_class, cls) for cls in SIMPLE_CLASSES):
                        return val
                    return parse_json_to_model(model_class, val)

            result = redis_to_set = await func(*args, **kwargs)
            if result is None:
                return None
            elif isinstance(redis_to_set, list):
                redis_to_set = list(map(lambda el: el.model_dump(), redis_to_set))
            elif not any(isinstance(result, cls) for cls in SIMPLE_CLASSES):
                redis_to_set = result.model_dump()

            try:
                await redis_set(
                    cache_key, redis_to_set, ttl=ttl if ttl else None
                )
            except Exception as e:
                logging.error(e)

            return result

        return wrapper

    return decorator


def parse_json_to_model(model, json_dict):
    row = model()
    
    for k, v in json_dict.items():
        if isinstance(v, list):
            setattr(row, k, [parse_json_to_model(getattr(model, k).property.mapper.class_, x) for x in v])
        elif not any(isinstance(v, cls) for cls in SIMPLE_CLASSES):
            setattr(row, k, parse_json_to_model(getattr(model, k).property.mapper.class_), v)
        else:
            setattr(row, k, v)
    
    return row
