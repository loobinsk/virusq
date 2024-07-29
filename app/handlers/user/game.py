import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security
from structlog import get_logger

from app.database.models import Game
from app.database.repositories.game import GameRepository
from app.database.repositories.user import UserRepository
from app.database.uow.base import BaseUoW
from app.exceptions.game import GameStartImpossibleError
from app.handlers.user.account import jwt_auth
from app.schemas.base import ErrorResponse, UserEntity
from app.schemas.general.auth import JWTValidationData, GameFinishChecksumData
from app.schemas.user.game import StartGameResponse, FinishGameResponse
from app.typings.consts import (
    GAME_LEVELS_POINTS_MAPPER,
    GAME_SECONDS_MINUMUM_FOR_ONE_LAP,
    GAME_LEVELS_SUSPICION_AFTER,
)
from app.utils.auth import ChecksumAuth

logger = get_logger()

game_router = APIRouter(prefix="/game", route_class=DishkaRoute)
game_finish_checksum_scheme = ChecksumAuth(
    auth_data_model=GameFinishChecksumData,
    name="Checksum Cookie",
    description="Checksum for game finishing. Format: b'score=999&game_id=8590e1f6-254e-4f26-99eb-60f2e3df0dc4'. Encode similar string using Fernet",
)


@game_router.post(
    "/start",
    responses={
        200: {"model": StartGameResponse},
        401: {"model": ErrorResponse},
    },
    summary="Start new game",
    tags=["Game actions"],
)
async def start_game_handler(
    user_repo: FromDishka[UserRepository],
    game_repo: FromDishka[GameRepository],
    uow: FromDishka[BaseUoW],
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = jwt_data.extra_data.user

    if user.game_energy <= 0:
        raise GameStartImpossibleError("Not enough energy")

    user = await user_repo.decrement_game_energy(user.id)
    game = await game_repo.create(game=Game(user_id=user.id))

    await uow.commit()
    return StartGameResponse(game_id=game.id)


@game_router.post(
    "/finish",
    responses={
        200: {"model": FinishGameResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Finish active game",
    tags=["Game actions"],
)
async def finish_game_handler(
    user_repo: FromDishka[UserRepository],
    game_repo: FromDishka[GameRepository],
    uow: FromDishka[BaseUoW],
    checksum_data: GameFinishChecksumData = Security(game_finish_checksum_scheme),
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    user = jwt_data.extra_data.user
    game = await game_repo.get_active_game(model_id=checksum_data.game_id, user_id=user.id)
    update_daily_highscore = False
    update_alltime_highscore = False

    marked_as_suspicious = _check_game_for_suspicion(game=game, score=checksum_data.score)

    await game_repo.finish_game(
        game_id=game.id,
        score=checksum_data.score,
        marked_as_suspicious=marked_as_suspicious,
    )

    if game.score > user.game_daily_highscore:
        update_daily_highscore = True
    if game.score > user.game_alltime_highscore:
        update_alltime_highscore = True

    user = await user_repo.update_highscores(
        update_daily_highscore=update_daily_highscore,
        update_alltime_highscore=update_alltime_highscore,
        user_id=user.id,
        score=game.score,
    )

    await user_repo.reward_user_referrers(
        user_id=user.id,
        initial_profit=checksum_data.score,
    )
    await uow.commit()

    return FinishGameResponse(user=UserEntity.from_user_model(user=user))


def _check_game_for_suspicion(game: Game, score: int) -> bool:
    played_seconds = (datetime.datetime.utcnow() - game.created_at).seconds
    completed_levels_amount = 0
    cumulative_score = 0

    for level, level_points in GAME_LEVELS_POINTS_MAPPER.items():
        cumulative_score += level_points
        if score >= cumulative_score:
            completed_levels_amount += 1
        else:
            break

    minimum_played_seconds = GAME_SECONDS_MINUMUM_FOR_ONE_LAP * completed_levels_amount
    marked_as_suspicious = (
        completed_levels_amount >= GAME_LEVELS_SUSPICION_AFTER
        or minimum_played_seconds >= played_seconds
    )

    if marked_as_suspicious:
        logger.info(f"Game with id {game.id} was marked as suspicious")

    return marked_as_suspicious
