from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security
from starlette.responses import Response

from app.database.repositories.user import UserRepository
from app.handlers.user.account import bot_jwt_auth

dump_router = APIRouter(
    prefix="/dump",
    route_class=DishkaRoute,
)


@dump_router.get(
    "/users",
    include_in_schema=False,
    dependencies=[Security(bot_jwt_auth)],
    summary="Get Users Dump",
    tags=["Dump actions"],
)
async def get_users_dump(
    user_repo: FromDishka[UserRepository],
):
    users_ids = [str(user_id) for user_id in await user_repo.get_all_ids()]
    users_data = bytes(" ".join(users_ids), encoding="utf-8")

    return Response(
        users_data,
        media_type="text/plain",
    )
