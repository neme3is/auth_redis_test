from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import (
    create_access_token,
    add_to_whitelist,
    add_to_blacklist,
    authenticate_user,
)
from app.dependencies import get_current_user
from app.models import User
from app.schemas import Token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.auth.access_toke_expire_minutes)
    access_token = await create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    await add_to_whitelist(
        token=access_token,
        user_id=user.username,
        expires_in=int(access_token_expires.total_seconds())
    )

    return {"access_token": access_token, "token_type": "bearer"}

