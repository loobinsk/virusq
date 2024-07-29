import datetime

from app.database.models import User
from app.schemas.base import UserEntity, BaseModel
from app.typings.enums import UserLanguage


class UserRegistrationInputData(BaseModel):
    id: int
    language: UserLanguage
    source: str | None = None
    username: str | None = None
    first_name: str
    last_name: str | None = None
    is_premium: bool


class GetUserResponse(BaseModel):
    user: UserEntity


class UserBotEntity(BaseModel):
    id: int
    language: UserLanguage
    is_banned: bool
    bot_blocked_at: datetime.datetime | None

    @classmethod
    def from_user_model(cls, user: User) -> "UserBotEntity":
        return cls(
            id=user.id,
            language=user.language,
            is_banned=user.is_banned,
            bot_blocked_at=user.bot_blocked_at,
        )


class UserRegistrationResponse(BaseModel):
    user: UserBotEntity


class GetUserByIdResponse(BaseModel):
    user: UserBotEntity


class SetUserInactiveResponse(BaseModel):
    user: UserBotEntity


class SetUserActiveResponse(BaseModel):
    user: UserBotEntity
