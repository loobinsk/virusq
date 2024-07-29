import datetime

from sqlalchemy import UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int | None]

    marked_as_suspicious: Mapped[bool | None] = mapped_column(index=True)
    on_fraud_check: Mapped[bool | None] = mapped_column(index=True)

    finished_at: Mapped[datetime.datetime | None]
