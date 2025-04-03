from enum import StrEnum


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"

    @classmethod
    def list(cls):
        return [role.value for role in cls]
