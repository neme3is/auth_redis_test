from fastapi import APIRouter

from app.database.redis_client import RedisClient
from app.schemas import UserCreate

router = APIRouter(tags=["create-user"])

# удобное добавление пользователя в redis
@router.post("/create-user")
async def create_user(user: UserCreate):

    user_key = f"user:{user.username}"

    user_data = {
        "username": user.username,
        "email": user.email or "",
        "password": user.password
    }

    await RedisClient.hset(user_key, mapping=user_data)

    return {"status": "success", "username": user.username}
