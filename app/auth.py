from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings
from app.database import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.auth_settings.secret_key, algorithm=settings.auth_settings.algorithm)
    return encoded_jwt

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def add_to_whitelist(token: str, user_id: str, expires_in: int):
    await redis_client.setex(f"whitelist:{user_id}", expires_in, token)

async def is_token_whitelisted(user_id: str, token: str) -> bool:
    stored_token = await redis_client.get(f"whitelist:{user_id}")
    return stored_token == token

async def remove_from_whitelist(user_id: str):
    await redis_client.delete(f"whitelist:{user_id}")

async def add_to_blacklist(token: str):
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get('exp')

        if exp:
            expires_at = datetime.fromtimestamp(exp)
            now = datetime.now()

            if expires_at > now:
                ttl = int((expires_at - now).total_seconds())
                await redis_client.setex(f"blacklist:{token}", ttl, "true")
                return True

    except Exception as e:
        print(f"Error adding to blacklist: {e}")

    return False

async def authenticate_user(username: str, password: str) -> str | None:
    user = await redis_client.get(username)

    if not user:
        return None

    if not pwd_context.verify(password, user.hashed_password):
        return None

    return user

