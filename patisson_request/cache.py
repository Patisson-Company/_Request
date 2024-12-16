"""
This module provides an abstract base class and a concrete subclass for asynchronous caching systems

Classes:
    - BaseAsyncTTLCache: An abstract base class for cache systems that support TTL. It defines the 
      required `set` and `get` methods for storing and retrieving cache entries with expiration logic.
    - RedisAsyncCache: A subclass of `BaseAsyncTTLCache` that implements caching using Redis. It includes 
      methods for asynchronously interacting with a Redis server for storing and retrieving cached data.

Constants:
    - REDIS_DB_BY_SERVICE: A mapping of services to specific Redis database numbers, 
      used to organize data storage across multiple Redis databases.
"""

import abc
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Optional

import redis.asyncio as aioredis

from patisson_request.services import Service
from patisson_request.types import Encodable, Seconds

REDIS_DB_BY_SERVICE = {
    Service._TEST: 0,
    Service.AUTHENTICATION: 1,
    Service.BOOKS: 2,
    Service.USERS: 3,
    Service.FORUM: 4,
    Service.INTERNAL_MEDIA: 5,
    Service.API_GATEWAY: 6
}

@dataclass(kw_only=True)
class BaseAsyncTTLCache(abc.ABC):
    """
    Abstract base class for asynchronous cache systems with time-to-live (TTL) support.
    
    This class enforces the implementation of the `set` and `get` methods for subclasses 
    that implement caching mechanisms. The cache entries have an expiration time, 
    which can be customized by providing a TTL value.

    Attributes:
        service (Service): The service associated with the cache. 
        logger (logging.Logger): A logger instance for logging cache events and exceptions.
        default_cache_lifetime (Seconds | timedelta, default 60): The default lifetime for cache entries.
    """
    service: Service
    logger: logging.Logger
    default_cache_lifetime: Seconds | timedelta = 60
    
    @abc.abstractmethod
    async def set(self, key: str, value: Encodable, 
                  time: Optional[Seconds | timedelta] = None) -> None:
        """
        Asynchronously sets a cache entry.

        Args:
            key (str): The unique key for the cache entry.
            value (Encodable): The value to store in the cache.
            time (Optional[Seconds | timedelta], optional): The TTL (Time-To-Live) for the cache entry. 
                If not provided, the default cache lifetime is used.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

    @abc.abstractmethod
    async def get(self, key: str) -> bytes | None: 
         """
        Asynchronously retrieves a cache entry by its key.

        Args:
            key (str): The unique key for the cache entry.

        Returns:
            bytes | None: The cached value or None if the key does not exist or an error occurs.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """  
    

@dataclass(kw_only=True)
class RedisAsyncCache(BaseAsyncTTLCache):
    """
    A subclass of `BaseAsyncTTLCache` that implements caching using Redis.

    This class provides the actual logic for setting and retrieving cache entries 
    asynchronously using a Redis server.

    Attributes:
        redis_host (str, default 'localhost'): The Redis server hostname.
        redis_port (int, default 6379): The Redis server port.
        redis_db (Optional[str | int], optional): The Redis database number or name to use. 
            Defaults to None, which determines the DB based on the service.
    """
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: Optional[str | int] = None
    
    def __post_init__(self):
        """
        Initializes the Redis connection instance using the specified host, port, and database.

        The database is selected based on the provided service or defaults to a preconfigured one.
        """
        self.redis = aioredis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            db=REDIS_DB_BY_SERVICE[self.service] if not self.redis_db else self.redis_db
            )
        
    async def set(self, key: str, value: Encodable, 
            time: Optional[Seconds | timedelta] = None) -> None:
        """
        Asynchronously sets a cache entry in Redis.

        Args:
            key (str): The unique key for the cache entry.
            value (Encodable): The value to store in the cache.
            time (Optional[Seconds | timedelta], optional): The TTL for the cache entry. 
                Defaults to the `default_cache_lifetime` if not provided.
        """
        try:
            await self.redis.set(name=key, value=value, 
                                ex=time if time else self.default_cache_lifetime)
        except Exception as e:
            self.logger.warning(e)

    async def get(self, key: str) -> bytes | None:
        """
        Asynchronously retrieves a cache entry from Redis by its key.

        Args:
            key (str): The unique key for the cache entry.

        Returns:
            bytes | None: The cached value or None if the key does not exist or an error occurs.

        Logs a warning if an exception occurs while getting the cache.
        """

        try:
            return await self.redis.get(name=key)
        except Exception as e:
            self.logger.warning(e)