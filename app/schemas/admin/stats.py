from typing import List

from pydantic import BaseModel


class DetailedStatsEntity(BaseModel):
    amount: int
    percentage_reference_value: int


class UsersAmountStats(BaseModel):
    total_users: int
    active_users: DetailedStatsEntity
    inactive_users: DetailedStatsEntity


class UsersDynamicStats(BaseModel):
    daily_dynamic: DetailedStatsEntity
    weekly_dynamic: DetailedStatsEntity
    monthly_dynamic: DetailedStatsEntity


class GamePlayersAmountStats(BaseModel):
    total_players: int
    active_players: DetailedStatsEntity
    inactive_players: DetailedStatsEntity
    players_online: int


class GamePlayersEngagementStats(BaseModel):
    total_games_played: int
    daily_unique_players: int
    daily_games_played: int
    weekly_games_played: int


class GameStats(BaseModel):
    players: GamePlayersAmountStats
    games_in_progress: int
    engagement: GamePlayersEngagementStats


class AdminStatsResponse(BaseModel):
    users_amount_stats: UsersAmountStats
    dynamic_stats: UsersDynamicStats
    game_stats: GameStats


class AdminPlotStatsResponse(BaseModel):
    new_users: List[int]
    blocked_users: List[int]
    users_without_source: List[int]
