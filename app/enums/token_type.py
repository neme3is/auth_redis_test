from enum import StrEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"

    @classmethod
    def list(cls):
        return [token.value for token in cls]
