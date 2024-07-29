from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ReferralLink
from app.database.repositories.base import BaseRepository


class ReferralLinkRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session
        self._repository = BaseRepository(ReferralLink, session)

    async def get_by_id(self, model_id: str) -> ReferralLink:
        result = await self._repository.get_one(whereclause=ReferralLink.id == model_id)

        return result

    async def get_active(self) -> Sequence[ReferralLink]:
        result = await self._repository.get_many(whereclause=ReferralLink.is_active == True)

        return result

    async def get_inactive(self) -> Sequence[ReferralLink]:
        result = await self._repository.get_many(whereclause=ReferralLink.is_active == False)

        return result

    async def create(self, referral_link: ReferralLink) -> ReferralLink:
        result = await self._repository.create_one(referral_link)

        return result

    async def update_one_by_id(
        self,
        model_id: str,
        **kwargs,
    ) -> ReferralLink:
        result = await self._repository.update_one(
            whereclause=ReferralLink.id == model_id, **kwargs
        )

        return result

    async def delete_one_by_id(self, model_id: str) -> ReferralLink:
        result = await self._repository.delete_one(whereclause=ReferralLink.id == model_id)

        return result

    async def deactivate_by_id(self, model_id: str) -> ReferralLink:
        result = await self._repository.update_one(
            whereclause=ReferralLink.id == model_id, is_active=False
        )

        return result

    async def activate_by_id(self, model_id: str) -> ReferralLink:
        result = await self._repository.update_one(
            whereclause=ReferralLink.id == model_id,
            is_active=True,
        )

        return result
