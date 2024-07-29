from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class ReferralLink(Base):
    __tablename__ = "referral_links"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default="1")
