from fastapi import APIRouter

from app.database.redis_client import RedisClient
from app.schemas import UserCreate
from app.services.auth import AuthService

router = APIRouter(tags=["create-user"])

# удобное добавление пользователя в redis
@router.post("/create-user")
async def create_user(user: UserCreate):

    user_key = f"user:{user.username}"

    user_data = {
        "username": user.username,
        "email": user.email or "",
        "hashed_password": AuthService.get_password_hash(user.password),
        "role": user.role
    }

    await RedisClient.hset(user_key, mapping=user_data)

    return {"status": "success", "username": user.username}
