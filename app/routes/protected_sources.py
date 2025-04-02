from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.schemas import UserInDB
from app.enums.roles import Role

router = APIRouter(prefix="/protected", tags=["protected"])


@router.post("/admin-only")
async def admin_only_protected_source(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(
        status_code=403,
        detail="Not enough rights to access admin source"
    )

    return {"success": True, "msg": "Got access to admin source"}

@router.post("/users")
async def admin_only_protected_source(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role not in Role.list():
        raise HTTPException(
        status_code=403,
        detail="Not enough rights to access user source"
    )

    return {"success": True, "msg": "Got access to user source"}
