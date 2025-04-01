from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from app.enums.roles import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None
    exp: Optional[datetime] = None

class UserBase(BaseModel):
    username: str
    role: Role = Role.USER
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False

class UserOut(UserBase):
    role: Role
    disabled: bool

class WhitelistEntry(BaseModel):
    user_id: str
    token: str
    expires_at: datetime

class BlacklistEntry(BaseModel):
    token: str
    expires_at: datetime

class ContentItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None

class RoleSpecificContent(ContentItem):
    allowed_roles: List[Role]

class Message(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
