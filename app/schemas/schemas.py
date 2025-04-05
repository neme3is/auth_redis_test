from pydantic import BaseModel

from app.enums.roles import Role


class TokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class ResponseDto(BaseModel):
    success: bool
    msg: str


class CreateUserResponseDto(BaseModel):
    success: bool
    username: str


class ErrorResponseDto(BaseModel):
    detail: str


class CreateUserRequestDto(BaseModel):
    username: str
    password: str
    role: Role
    email: str = None
