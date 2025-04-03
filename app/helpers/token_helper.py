from fastapi import HTTPException
from jose import JWTError, jwt
from starlette import status

from app.config import settings
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token missing expiration claim",
                )
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
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Token missing expiration claim",
                    )
                return payload.get("exp")

            except JWTError as e:
                Logger.logger.debug(f"Error decoding refresh token: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Token processing failed: {str(e)}",
                )

        except Exception as e:
            Logger.logger.debug("Exception while verifying token", exc_info=e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token processing failed: {str(e)}",
            )
