from fastapi import APIRouter, Request

from app.database.redis_client import RedisClient
from app.schemas.schemas import UserInDB, CreateUserMessage
from app.services.auth_service import AuthService

router = APIRouter(tags=["create-user"])


# удобное добавление пользователя в redis
@router.post("/create-user", response_model=CreateUserMessage)
async def create_user(request: Request, user: UserInDB):
    client_ip = request.client.host
    user_key = f"user:{user.username}"

    user_data = {
        "username": user.username,
        "email": user.email or "",
        "hashed_password": AuthService.get_password_hash(user.hashed_password),
        "role": user.role,
        "ip": client_ip,
    }

    await RedisClient.hset(user_key, mapping=user_data)

    return CreateUserMessage(success=True, username=user.username)
