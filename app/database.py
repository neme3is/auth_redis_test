import redis

from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_settings.redis_host,
    port=settings.redis_settings.redis_port,
    password=settings.redis_settings.redis_password,
    decode_responses=True
)
