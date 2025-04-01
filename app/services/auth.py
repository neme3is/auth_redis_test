from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings
from app.database.redis_client import RedisClient
from app.logger import Logger


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.auth_settings.secret_key, algorithm=settings.auth_settings.algorithm)
        return encoded_jwt

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def add_to_whitelist(cls, token: str, user_id: str, expires_in: int):
        await RedisClient.setex(f"whitelist:{user_id}", expires_in, token)

    @classmethod
    async def is_token_whitelisted(cls, user_id: str, token: str) -> bool:
        stored_token = await RedisClient.get(f"whitelist:{user_id}")
        return stored_token == token

    @classmethod
    async def remove_from_whitelist(cls, user_id: str):
        await RedisClient.delete(f"whitelist:{user_id}")

    @classmethod
    async def add_to_blacklist(cls, token: str):
        try:
            payload = jwt.get_unverified_claims(token)
            exp = payload.get('exp')
            if exp:
                expires_at = datetime.fromtimestamp(exp)
                now = datetime.now()

                if expires_at > now:
                    ttl = int((expires_at - now).total_seconds())
                    await RedisClient.setex(f"blacklist:{token}", ttl, "true")
                    return True
        except Exception as e:
            Logger.logger(f"Error adding to blacklist: {e}")

        return False

    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> dict | None:
        user = await RedisClient.get(username)

        if not user:
            return None

        if not cls.pwd_context.verify(password, user.hashed_password):
            return None

        return user

