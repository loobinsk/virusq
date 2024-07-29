from typing import List, Sequence

from pydantic import field_validator

from app.database.models import User
from app.schemas.base import (
    UserEntity,
    BaseModel,
    UserRankingEntity,
)
from app.typings.consts import RANKING_PLACE_LIMIT


class GetUserRankingInfoResponse(BaseModel):
    place: str
    score: int

    @field_validator("place", mode="before")
    @classmethod
    def convert_place_to_string(cls, place: int) -> str:
        if place >= RANKING_PLACE_LIMIT:
            return f"{RANKING_PLACE_LIMIT // 1000}K+"
        return str(place)


class UserRankingInfo(BaseModel):
    place: int
    user: UserRankingEntity


class GetRankingChunkResponse(BaseModel):
    users: List[UserRankingInfo]

    @classmethod
    def from_ranking_chunk(
        cls,
        ranking_chunk: Sequence[User],
        ranking_offset: int,
        ranking_field: str,
    ) -> "GetRankingChunkResponse":
        return cls(
            users=[
                UserRankingInfo(
                    user=UserRankingEntity.from_user_model(user=user, ranking_field=ranking_field),
                    place=ranking_offset + index + 1,
                )
                for index, user in enumerate(ranking_chunk)
            ]
        )


class FarmingClaimResponse(BaseModel):
    user: UserEntity
