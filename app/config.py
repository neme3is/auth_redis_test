from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


load_dotenv(dotenv_path='../.env')


class RedisSettings(BaseSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_password: str = ''


class PostgresSettings(BaseSettings):
    db_user: SecretStr = 'postgres'
    db_password: SecretStr = ''
    db_host: str = '127.0.0.1'
    db_port: int = 5432
    db_name: str = 'jwt_task'


class AuthSettings(BaseSettings):
    secret_key: SecretStr = '123'
    algorithm: str = 'HS256'
    access_toke_expire_minutes: int = 15


class Settings(BaseSettings):
    redis_settings: RedisSettings = RedisSettings()
    auth_settings: AuthSettings = AuthSettings()
    postgres_settings: PostgresSettings = PostgresSettings()


settings = Settings()
