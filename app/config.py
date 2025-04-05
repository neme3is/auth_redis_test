from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path="../.env")


class ApplicationSettings(BaseSettings):
    app_host: str = '0.0.0.0'
    app_port: int = 8000

class RedisSettings(BaseSettings):
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_password: str = ""


class PostgresSettings(BaseSettings):
    db_user: SecretStr = "postgres"
    db_password: SecretStr = ""
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "jwt_task"


class AuthSettings(BaseSettings):
    access_token_secret_key: str = "12345ABC"
    refresh_token_secret_key: str = "CAB54321"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 10080
    validate_ip: bool = True


class Settings(BaseSettings):
    redis_settings: RedisSettings = RedisSettings()
    auth_settings: AuthSettings = AuthSettings()
    postgres_settings: PostgresSettings = PostgresSettings()
    app_settings: ApplicationSettings = ApplicationSettings()
    log_level: str = 'DEBUG'


settings = Settings()
