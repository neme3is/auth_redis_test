from pydantic import SecretStr
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = '6379'
    redis_password: str = ''


class AuthSettings(BaseSettings):
    secret_key: SecretStr = '123'
    algorithm: str = 'HS256'


class Settings(BaseSettings):
    redis_settings = RedisSettings()
    auth_settings = AuthSettings()

settings = Settings()
