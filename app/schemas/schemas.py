from pydantic import BaseModel


class TokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class MessageDto(BaseModel):
    success: bool
    msg: str


class CreateUserMessageDto(BaseModel):
    success: bool
    username: str


class ErrorResponseDto(BaseModel):
    detail: str


class CreateUserDto(BaseModel):
    username: str
    password: str
    role: str
    email: str = None
