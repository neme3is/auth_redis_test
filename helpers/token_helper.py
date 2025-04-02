from jose import jwt, ExpiredSignatureError
from passlib.exc import InvalidTokenError

from app.config import settings


class TokenHelper:
    @classmethod
    def get_token_expiration(cls, token: str) -> float | None:
        try:
            payload = jwt.decode(token, settings.auth_settings.secret_key,
                                 algorithms=[settings.auth_settings.algorithm])
            return payload.get("exp")
        except ExpiredSignatureError:
            return None
        # todo проверить
        except InvalidTokenError:
            return None