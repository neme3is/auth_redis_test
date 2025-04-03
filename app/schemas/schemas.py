from pydantic import BaseModel, EmailStr
from typing import Optional

from app.enums.roles import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class UserBase(BaseModel):
    username: str
    role: Role = Role.USER
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False
    client_ip: str


class Message(BaseModel):
    success: bool
    msg: str


class CreateUserMessage(BaseModel):
    success: bool
    username: str


class ErrorResponse(BaseModel):
    detail: str

class CreateUserDto(BaseModel):
    username: str
    password: str
    role: str
    email: str = None
