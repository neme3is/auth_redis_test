from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import Dependencies
from app.enums.roles import Role
from app.schemas.schemas import Message, UserInDB

router = APIRouter(prefix="/protected", tags=["protected"])


# RBAC model
@router.get("/admin-only", response_model=Message, summary="Доступ к ресурсам администраторов")
async def admin_only_protected_source(
    request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)
):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=403, detail="Not enough rights to access admin source"
        )

    return Message(success=True, msg="Got access to admin source")


# all users (and admin)
@router.get("/users", response_model=Message, summary="Доступ к ресурсам пользователей")
async def admin_only_protected_source(
    request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)
):
    if current_user.role not in Role.list():
        raise HTTPException(
            status_code=403, detail="Not enough rights to access user source"
        )

    return Message(success=True, msg="Got access to user source")


@router.get("/role-based", response_model=Message, summary="Проверка роли на уровне API")
async def admin_only_protected_source(
    request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)
):
    if current_user.role in Role.list():
        return Message(success=True, msg=f"Your role is: {current_user.role}")
    else:
        return Message(success=True, msg="Your role is: undefined")
