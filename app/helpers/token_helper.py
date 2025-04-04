from jose import JWTError, jwt

from app.config import settings
from app.exceptions.api_exceptions import TokenProcessingException, BadRequestException, InternalServerErrorException
from app.logger import Logger


class TokenHelper:

    @classmethod
    def get_token_expiration(cls, token: str) -> float | None:
        try:
            payload = jwt.decode(
                token,
                settings.auth_settings.access_token_secret_key,
                algorithms=[settings.auth_settings.algorithm],
            )

            if "exp" not in payload:
                Logger.logger.debug("Token missing expiration claim")
                raise BadRequestException(detail="Token missing expiration claim")
            return payload.get("exp")

        except JWTError as e:
            Logger.logger.debug(f"Error decoding access token: {str(e)}")
            try:
                payload = jwt.decode(
                    token,
                    settings.auth_settings.refresh_token_secret_key,
                    algorithms=[settings.auth_settings.algorithm],
                )

                if "exp" not in payload:
                    Logger.logger.debug("Token missing expiration claim")
                    raise BadRequestException(detail="Token missing expiration claim")
                return payload.get("exp")

            except JWTError as e:
                Logger.logger.debug(f"Error decoding refresh token: {str(e)}")
                raise InternalServerErrorException(detail=f"Token processing failed", exception=e)

        except Exception as e:
            Logger.logger.debug("Exception while verifying token", exc_info=e)
            raise TokenProcessingException(exception=e)
