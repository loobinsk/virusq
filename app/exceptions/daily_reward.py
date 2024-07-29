from app.exceptions.base import BaseAPIError


class DailyRewardAlreadyClaimedError(BaseAPIError):
    def __init__(self):
        super().__init__(message="Daily reward already claimed")
