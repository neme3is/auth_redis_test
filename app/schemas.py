from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from app.enums.roles import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    username: str
    role: Role = Role.USER
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False
    client_ip: str


class Message(BaseModel):
    success: bool
    msg: str
