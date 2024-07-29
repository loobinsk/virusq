from typing import List

from pydantic import field_validator

from app.schemas.base import (
    BaseModel,
    UserEntity,
)
from app.typings.consts import REFERRAL_SYSTEM_MAX_LEVEL


class ReferralsStatsLevel(BaseModel):
    level: int
    referrals_amount: int
    referrals_profit: int


class ReferralsClaimProfitResponse(BaseModel):
    user: UserEntity


class ReferralsStatsResponse(BaseModel):
    levels: List[ReferralsStatsLevel]

    @field_validator("levels", mode="after")
    @classmethod
    def add_missing_levels(cls, levels: List[ReferralsStatsLevel]) -> List[ReferralsStatsLevel]:
        if len(levels) != REFERRAL_SYSTEM_MAX_LEVEL:
            if len(levels) == 0:
                last_existing_level = 0
            else:
                last_existing_level = levels[-1].level

            for level in range(last_existing_level + 1, REFERRAL_SYSTEM_MAX_LEVEL + 1):
                levels.append(
                    ReferralsStatsLevel(level=level, referrals_amount=0, referrals_profit=0)
                )
        return levels
