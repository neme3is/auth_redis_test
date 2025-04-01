from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"

    @classmethod
    def list(cls):
        return [role.value for role in cls]
