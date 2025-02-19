"""Changed sponsor_type field to task_type at bonus_tasks

Revision ID: e11cc1f1bcc4
Revises: 5e3e8b837dde
Create Date: 2024-06-19 21:57:38.072076

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e11cc1f1bcc4'
down_revision: Union[str, None] = '5e3e8b837dde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='bonustasktype').create(op.get_bind())
    op.add_column('bonus_tasks', sa.Column('task_type', postgresql.ENUM('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='bonustasktype', create_type=False), nullable=False))
    op.drop_column('bonus_tasks', 'sponsor_type')
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype').drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype').create(op.get_bind())
    op.add_column('bonus_tasks', sa.Column('sponsor_type', postgresql.ENUM('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype', create_type=False), autoincrement=False, nullable=False))
    op.drop_column('bonus_tasks', 'task_type')
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='bonustasktype').drop(op.get_bind())
    # ### end Alembic commands ###
