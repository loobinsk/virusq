from app.exceptions.base import BaseAPIError


class AuthError(BaseAPIError): ...


class InitDataAuthError(AuthError):
    def __init__(self, message: str):
        super().__init__(message=message)
