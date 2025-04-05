from datetime import datetime

from pydantic import BaseModel
from app.enums.roles import Role
from app.enums.token_type import TokenType


class UserInDbModel(BaseModel):
    username: str
    role: Role = Role.USER
    email: str | None = None
    hashed_password: str
    disabled: bool = False
    client_ip: str = None


class TokenModel(BaseModel):
    sub: str | None = None
    role: Role | None = None
    exp: datetime | None = None
    type: TokenType | None = None
