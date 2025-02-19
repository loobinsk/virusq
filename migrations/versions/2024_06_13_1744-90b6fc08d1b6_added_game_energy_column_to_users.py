"""Added game_energy column to users

Revision ID: 90b6fc08d1b6
Revises: a130b240c77b
Create Date: 2024-06-13 17:44:36.152838

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '90b6fc08d1b6'
down_revision: Union[str, None] = 'a130b240c77b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('game_energy', sa.SmallInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'game_energy')
    # ### end Alembic commands ###
