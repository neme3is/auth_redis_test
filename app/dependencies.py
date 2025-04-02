from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError

from app.config import settings
from app.database.redis_client import RedisClient
from app.logger import Logger
from app.schemas import UserInDB
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    if await RedisClient.exists(f"blacklist:{token}") == 1:
        Logger.logger.debug(f"Token: {token} is blacklisted!")
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.auth_settings.secret_key, algorithms=[settings.auth_settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        if not await AuthService.is_token_whitelisted(username, token):
            Logger.logger.debug(f"User {username} with token {token} found!")
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await RedisClient.hgetall(f"user:{username}")

    if user is None:
        raise credentials_exception

    user_model = UserInDB(
        username=user['username'],
        hashed_password=user['hashed_password'],
        email=user['email'] if user.get('email') else None,
        role=user['role']
    )

    return user_model
