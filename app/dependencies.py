from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from app.config import settings
from app.database.redis_client import RedisClient
from app.enums.token_type import TokenType
from app.exceptions.api_exceptions import Exceptions
from app.logger import Logger
from app.services.auth_service import AuthService
from models.models import UserInDbModel


class Dependencies:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    @classmethod
    async def get_current_user(
        cls, request: Request, token: str = Depends(oauth2_scheme)
    ) -> UserInDbModel:

        try:
            payload = jwt.decode(
                token,
                settings.auth_settings.access_token_secret_key,
                algorithms=[settings.auth_settings.algorithm],
            )

            username: str = payload.get("sub")
            if username is None:
                Logger.logger.debug(f"Username is None.")
                raise Exceptions.credentials_exception

            if await AuthService.is_token_blacklisted(
                username, TokenType.access, token
            ):
                Logger.logger.debug(f"Token: {token} is blacklisted!")
                raise Exceptions.credentials_exception
            if not await AuthService.is_token_whitelisted(
                username, TokenType.access, token
            ):
                Logger.logger.debug(
                    f"User {username} with token {token} in whitelist not found!"
                )
                raise Exceptions.credentials_exception

        except JWTError as e:
            Logger.logger.debug(f"Error with access token: {str(e)}")

            try:
                payload = jwt.decode(
                    token,
                    settings.auth_settings.refresh_token_secret_key,
                    algorithms=[settings.auth_settings.algorithm],
                )

                username: str = payload.get("sub")
                if username is None:
                    Logger.logger.debug(f"Username is None.")
                    raise Exceptions.credentials_exception

                if await AuthService.is_token_blacklisted(
                    username, TokenType.refresh, token
                ):
                    Logger.logger.debug(f"Token: {token} is blacklisted!")
                    raise Exceptions.credentials_exception
                if not await AuthService.is_token_whitelisted(
                    username, TokenType.refresh, token
                ):
                    Logger.logger.debug(
                        f"User {username} with token {token} in whitelist not found!"
                    )
                    raise Exceptions.credentials_exception

            except JWTError as e:
                Logger.logger.debug(f"Error with refresh token: {str(e)}")
                raise Exceptions.credentials_exception

        user = await RedisClient.hgetall(f"user:{username}")

        if user is None:
            raise Exceptions.credentials_exception

        user_model = UserInDbModel(
            username=user["username"],
            hashed_password=user["hashed_password"],
            email=user["email"] if user.get("email") else None,
            role=user["role"],
            client_ip=user["ip"],
        )

        if settings.auth_settings.validate_ip and user_model.client_ip != request.client.host:
            await AuthService.invalidate_old_tokens(username)
            Logger.logger.debug(f"IP address changed for {username}. Please log in again.")
            raise Exceptions.ip_security_exception

        return user_model
