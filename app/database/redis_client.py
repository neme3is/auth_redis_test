import redis.asyncio as redis
from app.config import settings


class RedisClient:
    _instance: redis.Redis | None = None

    @classmethod
    async def get_instance(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.redis_settings.redis_host,
                port=settings.redis_settings.redis_port,
                password=settings.redis_settings.redis_password,
                decode_responses=True,
            )
        return cls._instance

    @classmethod
    async def set(cls, key: str, value: str, ex: int = None):
        redis_client = await cls.get_instance()
        await redis_client.set(key, value, ex=ex)

    @classmethod
    async def get(cls, key: str):
        redis_client = await cls.get_instance()
        return await redis_client.get(key)

    @classmethod
    async def delete(cls, key: str):
        redis_client = await cls.get_instance()
        await redis_client.delete(key)

    @classmethod
    async def exists(cls, key: str):
        redis_client = await cls.get_instance()
        return await redis_client.exists(key)

    @classmethod
    async def setex(cls, key: str, expires_in: int, token: str):
        redis_client = await cls.get_instance()
        return await redis_client.setex(key, expires_in, token)

    @classmethod
    async def hset(cls, key: str, mapping: dict):
        redis_client = await cls.get_instance()
        return await redis_client.hset(key, mapping=mapping)

    @classmethod
    async def hget(cls, key: str, field: str):
        redis_client = await cls.get_instance()
        return await redis_client.hget(key, field)

    @classmethod
    async def hgetall(cls, key: str):
        redis_client = await cls.get_instance()
        return await redis_client.hgetall(key)

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
