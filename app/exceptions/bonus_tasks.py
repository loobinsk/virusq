from app.exceptions.base import BaseAPIError


class BonusTaskUncompletedError(BaseAPIError):
    def __init__(self):
        super().__init__(message="Bonus task is not completed yet")
