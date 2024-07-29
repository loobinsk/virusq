import json
from copy import deepcopy
from typing import Literal, Dict, Any
from urllib.parse import unquote, parse_qsl

from app.database.models import User
from app.schemas.base import BaseModel, BaseChecksumEntity


class TelegramWebappChatData(BaseModel):
    id: int
    type: Literal["group", "supergroup", "channel"]
    title: str
    username: str | None = None
    photo_url: str | None = None


class TelegramWebappUserData(BaseModel):
    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = None


class TelegramWebappAuthData(BaseModel):
    query_id: str | None = None

    user: TelegramWebappUserData
    reciever: TelegramWebappUserData | None = None

    chat: TelegramWebappChatData | None = None
    chat_type: Literal["sender", "private", "group", "supergroup", "channel"] | None = None
    chat_instance: str | None = None

    start_param: str | None = None
    can_send_after: int | None = None
    auth_date: str
    hash: str

    raw_data: Dict[str, Any]

    @classmethod
    def from_webapp_init_data(cls, webapp_init_data: str) -> "TelegramWebappAuthData":
        try:
            webapp_init_data = unquote(webapp_init_data)
            init_data = dict(parse_qsl(webapp_init_data))

            parsed_data = {
                key: json.loads(value) if value.startswith("{") else value
                for key, value in init_data.items()
            }

            parsed_data["raw_data"] = deepcopy(init_data)
            return cls.model_validate(parsed_data)

        except ValueError:
            raise ValueError("Invalid data")


class RenewJWTInputData(BaseModel):
    init_data: str


class JWTParsedData(BaseModel):
    user_id: int


class JWTExtraData(BaseModel):
    user: User

    class Config:
        arbitrary_types_allowed = True


class JWTValidationData(BaseModel):
    parsed_data: JWTParsedData
    extra_data: JWTExtraData


class RenewJWTResponse(BaseModel):
    webapp_auth_data: TelegramWebappAuthData
    jwt_token: str


class GameFinishChecksumData(BaseChecksumEntity):
    game_id: str
    score: int
