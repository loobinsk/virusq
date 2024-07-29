from typing import Final, Dict

DAILY_GAME_ENERGY_AMOUNT: Final[int] = 5
INITIAL_BALANCE: Final[int] = 0
INITIAL_REFERRAL_BALANCE: Final[int] = 0

FARMING_HOUR_MINING_RATE: Final[int | float] = 36
FARMING_DURATION_HOURS: Final[int] = 10

DEFAULT_REFERRAL_BONUS: Final[int] = 100
DEFAULT_PREMIUM_REFERRAL_BONUS: Final[int] = 500

RANKING_PLACE_LIMIT: Final[int] = 10000
RANKING_CHUNK_SIZE: Final[int] = 100
RANKING_MAX_TOP_PLACE: Final[int] = 1000

REFERRAL_SYSTEM_PROFIT_PERCENT: Final[Dict[int, int | float]] = {
    1: 5,
    2: 2.5,
    3: 1.25,
}

REFERRAL_SYSTEM_MAX_LEVEL: Final[int] = list(REFERRAL_SYSTEM_PROFIT_PERCENT.keys())[-1]

GAME_SECONDS_MINUMUM_FOR_ONE_LAP: Final[int] = 6
GAME_LEVELS_SUSPICION_AFTER: Final[int] = 9
GAME_LEVELS_POINTS_MAPPER: Final[Dict[int, int]] = {
    1: 87,
    2: 145,
    3: 203,
    4: 261,
    5: 319,
    6: 377,
    7: 435,
    8: 493,
    9: 551,
}


ADMIN_STATS_PLOT_DAYS_AMOUNT: Final[int] = 14
