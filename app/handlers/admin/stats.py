from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from app.database.repositories.game import GameRepository
from app.database.repositories.user import UserRepository
from app.handlers.user.account import bot_jwt_auth
from app.schemas.admin.stats import (
    AdminStatsResponse,
    UsersAmountStats,
    UsersDynamicStats,
    DetailedStatsEntity,
    GameStats,
    GamePlayersAmountStats,
    GamePlayersEngagementStats,
    AdminPlotStatsResponse,
)
from app.schemas.base import ErrorResponse

admin_stats_router = APIRouter(
    prefix="/stats",
    route_class=DishkaRoute,
)


@admin_stats_router.get(
    "/",
    summary="Get Stats",
    responses={
        200: {"model": AdminStatsResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Admin Stats Actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def get_stats(
    user_repo: FromDishka[UserRepository],
    game_repo: FromDishka[GameRepository],
):
    total_users, active_users, inactive_users = await user_repo.get_users_amount_stats()

    daily_dynamic, weekly_dynamic, monthly_dynamic = await user_repo.get_users_dynamic_stats()
    (
        total_players,
        active_players,
        inactive_players,
        players_online,
    ) = await user_repo.get_game_players_stats()
    (
        total_games_played,
        daily_unique_players,
        daily_games_played,
        weekly_games_played,
    ) = await game_repo.get_game_engagement_stats()
    games_in_progress_amount = await game_repo.get_games_in_progress_amount()

    return AdminStatsResponse(
        users_amount_stats=UsersAmountStats(
            total_users=total_users,
            active_users=DetailedStatsEntity(
                amount=active_users, percentage_reference_value=total_users
            ),
            inactive_users=DetailedStatsEntity(
                amount=inactive_users, percentage_reference_value=total_users
            ),
        ),
        dynamic_stats=UsersDynamicStats(
            daily_dynamic=DetailedStatsEntity(
                amount=daily_dynamic, percentage_reference_value=total_users
            ),
            weekly_dynamic=DetailedStatsEntity(
                amount=weekly_dynamic, percentage_reference_value=total_users
            ),
            monthly_dynamic=DetailedStatsEntity(
                amount=monthly_dynamic, percentage_reference_value=total_users
            ),
        ),
        game_stats=GameStats(
            players=GamePlayersAmountStats(
                total_players=total_players,
                active_players=DetailedStatsEntity(
                    amount=active_players, percentage_reference_value=total_players
                ),
                inactive_players=DetailedStatsEntity(
                    amount=inactive_players, percentage_reference_value=total_players
                ),
                players_online=players_online,
            ),
            games_in_progress=games_in_progress_amount,
            engagement=GamePlayersEngagementStats(
                total_games_played=total_games_played,
                daily_unique_players=daily_unique_players,
                daily_games_played=daily_games_played,
                weekly_games_played=weekly_games_played,
            ),
        ),
    )


@admin_stats_router.get(
    "/plot",
    summary="Get Plot Stats",
    responses={
        200: {"model": AdminPlotStatsResponse},
        401: {"model": ErrorResponse},
    },
    tags=["Admin Stats Actions"],
    dependencies=[Security(bot_jwt_auth)],
    include_in_schema=False,
)
async def get_plot_stats(
    user_repo: FromDishka[UserRepository],
):
    new_users, blocked_users, users_without_source = await user_repo.get_data_for_stats_plot()

    return AdminPlotStatsResponse(
        new_users=new_users,
        blocked_users=blocked_users,
        users_without_source=users_without_source,
    )
