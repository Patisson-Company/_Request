import abc
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import redis.asyncio as aioredis

from patisson_request.services import Service
from patisson_request.types import Encodable, Seconds

REDIS_DB_BY_SERVICE = {
    Service.AUTHENTICATION: 0,
    Service.BOOKS: 1,
    Service.USERS: 2
}

@dataclass(kw_only=True)
class BaseAsyncTTLCache(abc.ABC):
    service: Service
    default_cache_lifetime: Seconds | timedelta = 60
    
    @abc.abstractmethod
    async def set(self, key: str, value: Encodable, 
                  time: Optional[Seconds | timedelta] = None) -> None: ...

    @abc.abstractmethod
    async def get(self, key) -> bytes | None: ...    
    

@dataclass(kw_only=True)
class RedisAsyncCache(BaseAsyncTTLCache):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: Optional[str | int] = None
    
    def __post_init__(self):
        self.redis = aioredis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            db=REDIS_DB_BY_SERVICE[self.service] if not self.redis_db else self.redis_db
            )
        
    async def set(self, key: str, value: Encodable, 
            time: Optional[Seconds | timedelta] = None) -> None:
        try:
            await self.redis.set(name=key, value=value, 
                                ex=time if time else self.default_cache_lifetime)
        except:
            ...

    async def get(self, key: str) -> bytes | None:
        try:
            return await self.redis.get(name=key)
        except:
            ...