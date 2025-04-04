from fastapi import HTTPException


class Exceptions:
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials."
    )
    ip_security_exception = HTTPException(
        status_code=403, detail="Ip validation failed."
    )
