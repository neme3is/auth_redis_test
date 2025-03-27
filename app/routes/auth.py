from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import (
    create_access_token,
    add_to_whitelist,
    add_to_blacklist,
    authenticate_user,
)
from app.models import User
from app.schemas import Token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    # Добавляем токен в белый список
    add_to_whitelist(
        token=access_token,
        user_id=user.username,
        expires_in=int(access_token_expires.total_seconds())
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Добавляем токен в черный список
    token = get_current_active_token(current_user)
    expires_at = get_token_expiration(token)
    expires_in = expires_at - datetime.utcnow().timestamp()

    if expires_in > 0:
        add_to_blacklist(token=token, expires_in=int(expires_in))

    return {"message": "Successfully logged out"}