from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, Query
from fastapi_cache.decorator import cache

from app.database.repositories.user import UserRepository
from app.handlers.user.account import jwt_auth
from app.schemas.base import ErrorResponse
from app.schemas.general.auth import JWTValidationData
from app.schemas.user.ranking import GetUserRankingInfoResponse, GetRankingChunkResponse
from app.typings.consts import RANKING_MAX_TOP_PLACE, RANKING_CHUNK_SIZE
from app.typings.literals import RankingsPeriodLiteral, RankingsTypeLiteral
from app.utils.ranking import get_ranking_field

ranking_router = APIRouter(prefix="/ranking", route_class=DishkaRoute)


@ranking_router.get(
    "/getUserRankingInfo",
    responses={
        200: {"model": GetUserRankingInfoResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    summary="Get User Ranking Info",
    tags=["Ranking actions"],
)
async def get_user_ranking_info_handler(
    user_repo: FromDishka[UserRepository],
    ranking_period: RankingsPeriodLiteral,
    ranking_type: RankingsTypeLiteral,
    jwt_data: JWTValidationData = Security(jwt_auth),
):
    ranking_field = get_ranking_field(ranking_type, ranking_period)

    user_place, user_score = await user_repo.get_user_ranking_info(
        model_id=jwt_data.parsed_data.user_id,
        ranking_field=ranking_field,
    )

    return GetUserRankingInfoResponse(place=user_place, score=user_score)  # type: ignore[arg-type]


@ranking_router.get(
    "/getRankingChunk",
    responses={
        200: {"model": GetRankingChunkResponse},
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    dependencies=[Security(jwt_auth)],
    summary="Get Ranking Chunk",
    tags=["Ranking actions"],
)
@cache(expire=5)
async def get_ranking_chunk_handler(
    user_repo: FromDishka[UserRepository],
    ranking_period: RankingsPeriodLiteral,
    ranking_type: RankingsTypeLiteral,
    offset: int = Query(default=0, ge=0, le=RANKING_MAX_TOP_PLACE - RANKING_CHUNK_SIZE),
):
    ranking_field = get_ranking_field(ranking_type, ranking_period)

    ranking_chunk = await user_repo.get_ranking_chunk(
        ranking_field=ranking_field,
        offset=offset,
    )

    return GetRankingChunkResponse.from_ranking_chunk(
        ranking_chunk=ranking_chunk,
        ranking_offset=offset,
        ranking_field=ranking_field,
    )
