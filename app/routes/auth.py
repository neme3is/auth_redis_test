from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from fastapi import Request

from app.database.redis_client import RedisClient
from app.dependencies import Dependencies
from app.schemas import Token, UserInDB
from app.config import settings
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host
    user = await AuthService.authenticate_user(form_data.username, form_data.password, client_ip)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.auth_settings.access_toke_expire_minutes)
    access_token = await AuthService.create_access_token(
        data={"sub": user.username, "role": user.role.value, "ip": client_ip},
        expires_delta=access_token_expires
    )

    await AuthService.add_to_whitelist(
        token=access_token,
        user_id=user.username,
        expires_in=int(access_token_expires.total_seconds())
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)):
    token = await RedisClient.get(f"whitelist:{current_user.username}")

    if token is not None:
        await AuthService.add_to_blacklist(token)

    return {"message": "Successfully logged out"}
