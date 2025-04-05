from fastapi import APIRouter, Depends, Request

from app.dependencies import Dependencies
from app.enums.roles import Role
from app.exceptions.api_exceptions import ForbiddenException
from app.schemas.schemas import ResponseDto
from app.models.models import UserInDbModel

router = APIRouter(prefix="/protected", tags=["protected"])


# RBAC model
@router.get(
    "/admin-only",
    response_model=ResponseDto,
    summary="Доступ к ресурсам администраторов",
)
async def admin_only_protected_source(
    request: Request,
    current_user: UserInDbModel = Depends(Dependencies.get_current_user),
):
    if current_user.role != Role.ADMIN.value:
        raise ForbiddenException(detail="Not enough rights to access admin source")

    return ResponseDto(success=True, msg="Got access to admin source")


# all users (and admin)
@router.get(
    "/users", response_model=ResponseDto, summary="Доступ к ресурсам пользователей"
)
async def admin_only_protected_source(
    request: Request,
    current_user: UserInDbModel = Depends(Dependencies.get_current_user),
):
    if current_user.role not in Role.list():
        raise ForbiddenException(detail="Not enough rights to access users source")

    return ResponseDto(success=True, msg="Got access to user source")


@router.get(
    "/role-based", response_model=ResponseDto, summary="Проверка роли на уровне API"
)
async def role_based_endpoint(
    request: Request,
    current_user: UserInDbModel = Depends(Dependencies.get_current_user),
):
    if current_user.role in Role.list():
        return ResponseDto(success=True, msg=f"Your role is: {current_user.role}")
    else:
        return ResponseDto(success=True, msg="Your role is: undefined")
