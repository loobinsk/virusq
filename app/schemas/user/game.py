from pydantic import BaseModel

from app.schemas.base import UserEntity


class StartGameResponse(BaseModel):
    game_id: str


class FinishGameResponse(BaseModel):
    user: UserEntity
