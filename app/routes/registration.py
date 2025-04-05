from fastapi import APIRouter, Request

from app.database.redis_client import RedisClient
from app.exceptions.api_exceptions import BadRequestException
from app.schemas.schemas import CreateUserDto, CreateUserMessageDto
from app.services.auth_service import AuthService

router = APIRouter(tags=["create-user"])


# удобное добавление пользователя в redis
@router.post("/create-user", response_model=CreateUserMessageDto)
async def create_user(request: Request, user: CreateUserDto):
    client_ip = request.client.host
    user_key = f"user:{user.username}"

    if await RedisClient.exists(user_key):
        raise BadRequestException(
            detail=f"Пользователь '{user.username}' уже существует."
        )

    user_data = {
        "username": user.username,
        "email": user.email or "",
        "hashed_password": AuthService.get_password_hash(user.password),
        "role": user.role,
        "ip": client_ip,
    }

    await RedisClient.hset(user_key, mapping=user_data)

    return CreateUserMessageDto(success=True, username=user.username)
