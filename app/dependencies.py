from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from app.config import settings
from app.database.redis_client import RedisClient
from app.enums.token_type import TokenType
from app.exceptions.api_exceptions import CredentialsException, IpSecurityException
from app.logger import Logger
from app.services.auth_service import AuthService
from app.models.models import UserInDbModel


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
                raise CredentialsException()

            if await AuthService.is_token_blacklisted(
                username, TokenType.ACCESS, token
            ):
                msg = f"Token: {token} is blacklisted!"
                Logger.logger.debug(msg)
                raise CredentialsException(detail=msg)
            if not await AuthService.is_token_whitelisted(
                username, TokenType.ACCESS, token
            ):
                msg = f"User {username} with token {token} in whitelist not found!"
                Logger.logger.debug(msg)
                raise CredentialsException(detail=msg)

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
                    raise CredentialsException()

                if await AuthService.is_token_blacklisted(
                    username, TokenType.REFRESH, token
                ):
                    msg = f"Token: {token} is blacklisted!"
                    Logger.logger.debug(msg)
                    raise CredentialsException(detail=msg)
                if not await AuthService.is_token_whitelisted(
                    username, TokenType.REFRESH, token
                ):
                    msg = f"User {username} with token {token} in whitelist not found!"
                    Logger.logger.debug(msg, exc_info=True)
                    raise CredentialsException(detail=msg)

            except JWTError:
                msg = f"Error with refresh token."
                Logger.logger.debug(msg, exc_info=True)
                raise CredentialsException(detail=msg)

        user = await RedisClient.hgetall(f"user:{username}")

        if user is None:
            raise CredentialsException()

        user_model = UserInDbModel(
            username=user["username"],
            hashed_password=user["hashed_password"],
            email=user["email"] if user.get("email") else None,
            role=user["role"],
            client_ip=user["ip"],
        )

        if (
            settings.auth_settings.validate_ip
            and user_model.client_ip != request.client.host
        ):
            await AuthService.invalidate_old_tokens(username)
            Logger.logger.debug(
                f"IP address changed for {username}."
            )
            raise IpSecurityException()

        return user_model
