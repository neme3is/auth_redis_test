from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import Dependencies
from app.schemas import UserInDB
from app.enums.roles import Role
from fastapi import Request


router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/admin-only")
async def admin_only_protected_source(request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(
        status_code=403,
        detail="Not enough rights to access admin source"
    )

    return {"success": True, "msg": "Got access to admin source"}

# all users (and admin)
@router.get("/users")
async def admin_only_protected_source(request: Request, current_user: UserInDB = Depends(Dependencies.get_current_user)):
    if current_user.role not in Role.list():
        raise HTTPException(
        status_code=403,
        detail="Not enough rights to access user source"
    )

    return {"success": True, "msg": "Got access to user source"}
