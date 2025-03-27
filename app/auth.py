from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings
from app.database import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.auth_settings.secret_key, algorithm=settings.auth_settings.algorithm)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def add_to_whitelist(token: str, user_id: str, expires_in: int):
    redis_client.setex(f"whitelist:{user_id}", expires_in, token)

def is_token_whitelisted(user_id: str, token: str) -> bool:
    stored_token = redis_client.get(f"whitelist:{user_id}")
    return stored_token == token

def remove_from_whitelist(user_id: str):
    redis_client.delete(f"whitelist:{user_id}")

def add_to_blacklist(token: str):
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get('exp')

        if exp:
            expires_at = datetime.fromtimestamp(exp)
            now = datetime.now()

            if expires_at > now:
                ttl = int((expires_at - now).total_seconds())
                redis_client.setex(f"blacklist:{token}", ttl, "true")
                return True

    except Exception as e:
        print(f"Error adding to blacklist: {e}")

    return False

def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)

    if not user:
        return None

    if not pwd_context.verify(password, user.hashed_password):
        return None

    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await get_user_from_db(username)  # Ваша функция для получения пользователя из БД
    if user is None:
        raise credentials_exception

    return user