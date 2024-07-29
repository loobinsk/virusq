from app.schemas.base import (
    UserEntity,
    BaseModel,
)


class FarmingStartResponse(BaseModel):
    user: UserEntity


class FarmingClaimResponse(BaseModel):
    user: UserEntity
