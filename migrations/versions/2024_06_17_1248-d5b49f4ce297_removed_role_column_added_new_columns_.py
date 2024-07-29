"""Removed role column & added new columns to users table

Revision ID: d5b49f4ce297
Revises: 90b6fc08d1b6
Create Date: 2024-06-17 12:48:24.420074

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5b49f4ce297'
down_revision: Union[str, None] = '90b6fc08d1b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('RU', 'EN', name='userlanguage').create(op.get_bind())
    op.add_column('users', sa.Column('language', postgresql.ENUM('RU', 'EN', name='userlanguage', create_type=False), nullable=False))
    op.add_column('users', sa.Column('earned_from_referrals', sa.BigInteger(), server_default='0', nullable=False))
    op.drop_column('users', 'role')
    sa.Enum('USER', 'ADMIN', name='userrole').drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('USER', 'ADMIN', name='userrole').create(op.get_bind())
    op.add_column('users', sa.Column('role', postgresql.ENUM('USER', 'ADMIN', name='userrole', create_type=False), server_default=sa.text("'USER'::userrole"), autoincrement=False, nullable=False))
    op.drop_column('users', 'earned_from_referrals')
    op.drop_column('users', 'language')
    sa.Enum('RU', 'EN', name='userlanguage').drop(op.get_bind())
    # ### end Alembic commands ###
