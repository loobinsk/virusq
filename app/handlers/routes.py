from fastapi import APIRouter

from app.handlers.admin.bonus_tasks import admin_bonus_tasks_router
from app.handlers.admin.dump import dump_router
from app.handlers.admin.referral_links import referral_links_router
from app.handlers.admin.stats import admin_stats_router
from app.handlers.user.account import account_router
from app.handlers.user.bonus_tasks import bonus_tasks_router
from app.handlers.user.daily_rewards import daily_rewards_router
from app.handlers.user.farming import farming_router
from app.handlers.user.game import game_router
from app.handlers.user.ranking import ranking_router
from app.handlers.user.referrals import referrals_router

user_router = APIRouter(prefix="/user")
admin_router = APIRouter(prefix="/admin")


for router in (
    account_router,
    farming_router,
    daily_rewards_router,
    referrals_router,
    bonus_tasks_router,
    ranking_router,
    game_router,
):
    user_router.include_router(router)


for router in (
    admin_bonus_tasks_router,
    admin_stats_router,
    referral_links_router,
    dump_router,
):
    admin_router.include_router(router)
