from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = '6379'
    redis_password: str = ''


class Settings(BaseSettings):
    redis_settings = RedisSettings()


settings = Settings()
