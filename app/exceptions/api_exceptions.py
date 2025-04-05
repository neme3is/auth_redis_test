from fastapi import HTTPException
from starlette import status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials.", **kwargs):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, **kwargs)


class IpSecurityException(HTTPException):
    def __init__(self, detail: str = "IP validation failed.", **kwargs):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, **kwargs)


class TokenProcessingException(HTTPException):
    def __init__(
        self,
        detail: str = "Token processing failed.",
        exception: Exception = None,
        **kwargs,
    ):
        if exception:
            detail = f"{detail}: {str(exception)}"
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, **kwargs)


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request.", **kwargs):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, **kwargs)


class InternalServerErrorException(HTTPException):
    def __init__(
        self,
        detail: str = "An internal server error occurred.",
        exception: Exception = None,
        **kwargs,
    ):
        if exception:
            detail = f"{detail}: {str(exception)}"
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, **kwargs
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden!", exception: Exception = None, **kwargs):
        if exception:
            detail = f"{detail}: {str(exception)}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, **kwargs)
