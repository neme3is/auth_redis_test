from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime

from fastapi import Request

from app.database.redis_client import RedisClient
from app.dependencies import Dependencies
from app.config import settings
from app.enums.token_type import TokenType
from app.schemas.schemas import Token, UserInDB, Message
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host
    user = await AuthService.authenticate_user(
        form_data.username, form_data.password, client_ip
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, access_token_expires = await AuthService.create_token(
        data={"sub": user.username, "role": user.role.value, "ip": client_ip},
        token_type=TokenType.access_token,
    )

    refresh_token, refresh_token_expires = await AuthService.create_token(
        data={"sub": user.username, "role": user.role.value, "ip": client_ip},
        token_type=TokenType.refresh_token,
    )

    await AuthService.add_to_whitelist(
        token=access_token,
        user_id=user.username,
        expires_in=int(timedelta(minutes=access_token_expires).total_seconds(),
    )
)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=Message)
async def logout(
    request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)
):
    token = await RedisClient.get(f"whitelist:{current_user.username}")

    if token is not None:
        await AuthService.add_to_blacklist(token)
    return Message(success=True, msg=f"Successfully logged out")


router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Header(..., alias="Authorization")):
    user_data = await AuthService.validate_refresh_token(refresh_token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    new_access_token = await AuthService.create_access_token(
        data={"sub": user_data["sub"], "role": user_data.get("role")},
        expires_delta=timedelta(minutes=settings.auth_settings.access_token_expire_minutes),
    )

    await AuthService.add_to_whitelist(
        old_refresh_token=refresh_token,
        new_access_token=new_access_token,
        user_id=user_data["sub"],
    )

    return Token(
        access_token=new_access_token,
        refresh_token=refresh_token
    )
