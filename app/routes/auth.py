from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.dependencies import Dependencies
from app.enums.token_type import TokenType
from app.schemas.schemas import Message, Token, UserInDB
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
        token_type=TokenType.access,
    )

    refresh_token, refresh_token_expires = await AuthService.create_token(
        data={"sub": user.username, "role": user.role.value, "ip": client_ip},
        token_type=TokenType.refresh,
    )

    await AuthService.add_token_to_whitelist(
        token_type=TokenType.access,
        token=access_token,
        user_id=user.username,
        expires_in_minutes=access_token_expires
    )

    await AuthService.add_token_to_whitelist(
        token_type=TokenType.refresh,
        token=refresh_token,
        user_id=user.username,
        expires_in_minutes=refresh_token_expires
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=Message)
async def logout(
    request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)
):

    await AuthService.invalidate_old_tokens(current_user.username)

    return Message(success=True, msg=f"Successfully logged out")


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Header(..., alias="Authorization"),
                        current_user: UserInDB = Depends(Dependencies.get_current_user)
                        ):

    await AuthService.invalidate_old_tokens(current_user.username)

    new_access_token, new_access_token_expiration_time = await AuthService.create_token(
        data={"sub": current_user.username, "role": current_user.role}, token_type=TokenType.access
    )

    await AuthService.add_token_to_whitelist(
        TokenType.access,
        new_access_token,
        current_user.username,
        settings.auth_settings.access_token_expire_minutes
    )

    new_refresh_token, new_refresh_token_expiration_time = await AuthService.create_token(
        data={"sub": current_user.username, "role": current_user.role}, token_type=TokenType.refresh
    )

    await AuthService.add_token_to_whitelist(
        token_type=TokenType.access,
        token=new_access_token,
        user_id=current_user.username,
        expires_in_minutes=new_access_token_expiration_time
    )

    await AuthService.add_token_to_whitelist(
        token_type=TokenType.refresh,
        token=new_refresh_token,
        user_id=current_user.username,
        expires_in_minutes=new_refresh_token_expiration_time
    )

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)
