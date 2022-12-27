"""Модуль для работы с кэшем"""

from abc import ABC, abstractmethod

import redis

from src.core.config import settings


class CacheStorage(ABC):
    @abstractmethod
    def startup(self, *args, **kwargs):
        """Метод инициализации"""
        pass

    @abstractmethod
    def get(self, key: str, **kwargs):
        """Метод получения данных из кэша"""
        pass

    @abstractmethod
    def set(self, key: str, value: str, expire_at: int, **kwargs):
        """Метод сохранения данных в кэш"""
        pass


class RedisStorage(CacheStorage):
    def startup(self, *args, **kwargs):
        """Метод инициализации Redis"""
        pool = redis.ConnectionPool(*args, **kwargs)
        self._redis = redis.Redis(connection_pool=pool)

    def get(self, key: str) -> bytes | None:
        """Метод получения данных из Redis"""
        return self._redis.get(key)

    def set(self, key: str, value: str, expire_at: int):
        """Метод сохранения данных в Redis"""
        self._redis.set(key, value, exat=expire_at)

    def count_rate_limit(self, key: str, rate_limit: int) -> bool:
        """Метод увеличения счетчика в Redis"""
        pipeline = self._redis.pipeline()
        pipeline.incr(key, 1)
        pipeline.expire(key, 60)
        result = pipeline.execute()

        return result[0] <= rate_limit


cache: RedisStorage = RedisStorage()


def init_cache():
    cache.startup(host=settings.redis.host, port=settings.redis.port, db=0)
