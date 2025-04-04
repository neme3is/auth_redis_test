from pydantic import BaseModel
from app.enums.roles import Role


class UserInDbModel(BaseModel):
    username: str
    role: Role = Role.USER
    email: str | None = None
    hashed_password: str
    disabled: bool = False
    client_ip: str
