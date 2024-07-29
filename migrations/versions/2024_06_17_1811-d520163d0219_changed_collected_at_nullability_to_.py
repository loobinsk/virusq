"""Changed collected_at nullability to False at daily_rewards

Revision ID: d520163d0219
Revises: d5b49f4ce297
Create Date: 2024-06-17 18:11:46.374907

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd520163d0219'
down_revision: Union[str, None] = 'd5b49f4ce297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('daily_rewards_completition', 'collected_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('daily_rewards_completition', 'collected_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###
