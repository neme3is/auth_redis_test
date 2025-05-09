from datetime import datetime, timedelta
from typing import Tuple

from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.database.redis_client import RedisClient
from app.enums.token_type import TokenType
from app.helpers.token_helper import TokenHelper
from app.logger import Logger
from app.models.models import UserInDbModel, TokenModel


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    async def create_token(cls, data: TokenModel, token_type: TokenType) -> Tuple[str, int]:
        to_encode = data.model_copy()

        if token_type == TokenType.ACCESS:
            token_ttl = settings.auth_settings.access_token_expire_minutes
        if token_type == TokenType.REFRESH:
            token_ttl = settings.auth_settings.refresh_token_expire_minutes

        expire = datetime.now() + timedelta(minutes=token_ttl)
        to_encode.exp = expire

        if token_type == TokenType.ACCESS:
            secret_key = settings.auth_settings.access_token_secret_key
        if token_type == TokenType.REFRESH:
            secret_key = settings.auth_settings.refresh_token_secret_key

        encoded_jwt = jwt.encode(
            to_encode.model_dump(),
            secret_key,
            algorithm=settings.auth_settings.algorithm,
        )
        return encoded_jwt, token_ttl

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def add_token_to_whitelist(
        cls, token_type: TokenType, token: str, user_id: str, expires_in_minutes: int
    ) -> None:
        await RedisClient.setex(
            f"whitelist:{token_type}:{user_id}",
            int(timedelta(minutes=expires_in_minutes).total_seconds()),
            token,
        )

    @classmethod
    async def is_token_whitelisted(
        cls, username: str, token_type: TokenType, token: str
    ) -> bool:
        stored_token = await RedisClient.get(f"whitelist:{token_type}:{username}")
        return stored_token == token

    @classmethod
    async def is_token_blacklisted(
        cls, username: str, token_type: TokenType, token: str
    ) -> bool:
        stored_token = await RedisClient.get(f"blacklist:{token_type}:{username}")
        return stored_token == token

    @classmethod
    async def remove_from_whitelist(cls, username: str, token_type: TokenType) -> None:
        await RedisClient.delete(f"whitelist:{token_type}:{username}")

    @classmethod
    async def add_to_blacklist(cls, token_type: TokenType, token: str, username: str) -> None:
        try:
            exp = TokenHelper.get_token_expiration(token)
            if exp:
                expires_at = datetime.fromtimestamp(exp)
                now = datetime.now()
                if expires_at > now:
                    ttl = int((expires_at - now).total_seconds())
                    await RedisClient.setex(
                        f"blacklist:{token_type}:{username}", ttl, token
                    )
        except Exception as e:
            Logger.logger.debug(f"Error adding to blacklist", exc_info=e)

    @classmethod
    async def invalidate_old_tokens(cls, username: str) -> None:
        for token_type in TokenType.list():
            token = await RedisClient.get(f"whitelist:{token_type}:{username}")
            if token:
                await AuthService.add_to_blacklist(token_type, token, username)
                await AuthService.remove_from_whitelist(username, token_type)

    @classmethod
    async def authenticate_user(
        cls, username: str, password: str, client_ip: str
    ) -> UserInDbModel | None:
        user = await RedisClient.hgetall(f"user:{username}")

        if not user:
            return None

        user_model = UserInDbModel(
            username=user["username"],
            hashed_password=user["hashed_password"],
            email=user["email"] if user.get("email") else None,
            role=user["role"],
            client_ip=client_ip,
        )

        if not await cls.verify_password(password, user_model.hashed_password):
            return None

        return user_model
