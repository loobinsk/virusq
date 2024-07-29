from typing import List

from pydantic import BaseModel

from app.schemas.admin.stats import UsersDynamicStats, UsersAmountStats
from app.schemas.base import AdminReferralLinkEntity


class GetActiveReferralLinksResponse(BaseModel):
    referral_links: List[AdminReferralLinkEntity]


class GetInactiveReferralLinksResponse(BaseModel):
    referral_links: List[AdminReferralLinkEntity]


class ReferralLinkStats(BaseModel):
    users_amount_stats: UsersAmountStats
    dynamic_stats: UsersDynamicStats


class GetReferralLinkByIdResponse(BaseModel):
    referral_link: AdminReferralLinkEntity
    stats: ReferralLinkStats


class DeactivateReferralLinkResponse(BaseModel):
    referral_link: AdminReferralLinkEntity


class ActivateReferralLinkResponse(BaseModel):
    referral_link: AdminReferralLinkEntity


class CreateReferralLinkInputData(BaseModel):
    id: str
    name: str


class CreateReferralLinkResponse(BaseModel):
    referral_link: AdminReferralLinkEntity


class DeleteReferralLinkResponse(BaseModel):
    referral_link: AdminReferralLinkEntity
