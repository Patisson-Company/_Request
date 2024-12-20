from datetime import timedelta

import pytest

from patisson_request.cache import RedisAsyncCache, MemcachedAsyncCache, BaseAsyncTTLCache
from patisson_request.services import Service
from tests.logger import logger


async def base_set_get_cache(cache: BaseAsyncTTLCache):
    key = "test_key"
    value = b"test_value"
    ttl = timedelta(seconds=30)
    
    await cache.set(key, value, ttl)
    assert (await cache.get(key)) == value
    assert (await cache.get('non_existent_key')) is None
    
    
@pytest.mark.asyncio
async def test_redis_set_get_cache():
    redis_cache = RedisAsyncCache(
        service=Service._TEST,
        logger=logger
    )
    await base_set_get_cache(redis_cache)


@pytest.mark.asyncio
async def test_memcached_set_get_cache():
    memcached_cache = MemcachedAsyncCache(
        service=Service._TEST,
        logger=logger
    )
    await base_set_get_cache(memcached_cache)