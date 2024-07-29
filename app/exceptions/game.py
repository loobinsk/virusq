from app.exceptions.base import BaseAPIError


class GameStartImpossibleError(BaseAPIError):
    def __init__(self, reason: str):
        super().__init__(message=f"Game start impossible: {reason}")
