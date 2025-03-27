from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.config import settings
from app.database import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    if redis_client.exists(f"blacklist:{token}"):
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.auth_settings.secret_key, algorithms=[settings.auth_settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 3. Получение пользователя из БД
    user = get_user_from_db(username)  # Ваша функция для запроса к БД
    if user is None:
        raise credentials_exception

    return user