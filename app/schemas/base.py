import datetime
from typing import Any
from urllib.parse import parse_qsl

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.database.models import User, DailyReward, BonusTask, ReferralLink
from app.typings.enums import UserFarmingStatus, UserLanguage, BonusTaskType


class ErrorResponse(BaseModel):
    status_code: int
    message: Any

    @property
    def json_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"message": self.message},
        )


class FarmingEntity(BaseModel):
    started_at: datetime.datetime | None = None
    duration_hours: int
    hour_mining_rate: int
    second_mining_rate: float
    total_profit: int
    status: UserFarmingStatus

    @classmethod
    def from_user_model(cls, user: User) -> "FarmingEntity":
        return cls(
            started_at=user.farming_started_at,
            status=user.farming_status,
            duration_hours=user.farming_duration_hours,
            hour_mining_rate=user.farming_hour_mining_rate,
            second_mining_rate=user.farming_second_mining_rate,
            total_profit=user.farming_total_profit,
        )


class UserEntity(BaseModel):
    id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    language: UserLanguage

    is_banned: bool

    referral_balance: int
    balance: int
    daily_overall_profit: int

    farming: FarmingEntity

    game_energy: int
    game_daily_highscore: int
    game_alltime_highscore: int

    @classmethod
    def from_user_model(cls, user: User) -> "UserEntity":
        return cls(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language=user.language,
            is_banned=user.is_banned,
            referral_balance=user.referral_balance,
            balance=user.balance,
            daily_overall_profit=user.daily_overall_profit,
            farming=FarmingEntity.from_user_model(user),
            game_energy=user.game_energy,
            game_daily_highscore=user.game_daily_highscore,
            game_alltime_highscore=user.game_alltime_highscore,
        )


class UserRankingEntity(BaseModel):
    id: int

    first_name: str
    last_name: str | None = None

    score: int

    @classmethod
    def from_user_model(cls, user: User, ranking_field: str) -> "UserRankingEntity":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            score=getattr(user, ranking_field),
        )


class DailyRewardEntity(BaseModel):
    day: int
    reward: int

    @classmethod
    def from_daily_reward_model(cls, daily_reward: DailyReward) -> "DailyRewardEntity":
        return cls(
            day=daily_reward.day,
            reward=daily_reward.reward_amount,
        )


class BonusTaskEntity(BaseModel):
    id: int
    name: str
    description: str
    photo: bytes
    link: str
    reward_amount: int
    task_type: BonusTaskType

    @classmethod
    def from_bonus_task_model(cls, bonus_task: BonusTask) -> "BonusTaskEntity":
        return cls(
            id=bonus_task.id,
            name=bonus_task.name,
            description=bonus_task.description,
            photo=bonus_task.photo,
            link=bonus_task.link,
            reward_amount=bonus_task.reward_amount,
            task_type=bonus_task.task_type,
        )


class AdminBonusTaskEntity(BaseModel):
    id: int
    name: str
    task_type: BonusTaskType
    description: str
    photo: bytes
    link: str
    reward_amount: int
    access_id: int | None
    access_data: str | None
    created_at: datetime.datetime

    @classmethod
    def from_bonus_task_model(cls, bonus_task: BonusTask) -> "AdminBonusTaskEntity":
        return cls(
            id=bonus_task.id,
            name=bonus_task.name,
            task_type=bonus_task.task_type,
            description=bonus_task.description,
            photo=bonus_task.photo,
            link=bonus_task.link,
            reward_amount=bonus_task.reward_amount,
            access_id=bonus_task.access_id,
            access_data=bonus_task.access_data,
            created_at=bonus_task.created_at,
        )


class AdminReferralLinkEntity(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime.datetime

    @classmethod
    def from_referral_link_model(cls, referral_link: ReferralLink) -> "AdminReferralLinkEntity":
        return cls(
            id=referral_link.id,
            name=referral_link.name,
            is_active=referral_link.is_active,
            created_at=referral_link.created_at,
        )


class BaseChecksumEntity(BaseModel):
    @classmethod
    def from_decoded_checksum(cls, decoded_checksum: str):
        checksum_dict = dict(parse_qsl(decoded_checksum))

        return cls(**checksum_dict)
