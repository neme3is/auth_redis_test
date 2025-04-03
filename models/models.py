from typing import Optional
from pydantic import BaseModel, EmailStr
from app.enums.roles import Role


class UserInDbModel(BaseModel):
    username: str
    role: Role = Role.USER
    email: Optional[EmailStr] = None
    hashed_password: str
    disabled: bool = False
    client_ip: str
