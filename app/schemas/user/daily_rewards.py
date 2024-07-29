from typing import Sequence

from pydantic import BaseModel

from app.schemas.base import UserEntity, DailyRewardEntity


class GetCurrentDailyRewardResponse(BaseModel):
    reward: DailyRewardEntity
    is_claimed: bool = False


class GetAllDailyRewardsResponse(BaseModel):
    rewards: Sequence[DailyRewardEntity]


class ClaimDailyRewardResponse(BaseModel):
    user: UserEntity
