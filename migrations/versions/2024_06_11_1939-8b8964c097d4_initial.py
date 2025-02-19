"""Initial

Revision ID: 8b8964c097d4
Revises: 
Create Date: 2024-06-11 19:39:06.893855

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8b8964c097d4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype').create(op.get_bind())
    op.create_table('bonus_tasks',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('reward', sa.Integer(), nullable=False),
    sa.Column('sponsor_type', postgresql.ENUM('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype', create_type=False), nullable=False),
    sa.Column('check_access_data', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bonus_tasks'))
    )
    op.create_table('daily_rewards',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('day', sa.SmallInteger(), nullable=False),
    sa.Column('reward_amount', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_daily_rewards')),
    sa.UniqueConstraint('day', name=op.f('uq_daily_rewards_day'))
    )
    op.create_table('referral_links',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_referral_links'))
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('source', sa.String(), nullable=True),
    sa.Column('balance', sa.BigInteger(), nullable=False),
    sa.Column('farming_started_at', sa.DateTime(), nullable=True),
    sa.Column('farming_duration_hours', sa.SmallInteger(), nullable=False),
    sa.Column('farming_hour_mining_rate', sa.Integer(), nullable=False),
    sa.Column('last_daily_reward_collected_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('referral_links')
    op.drop_table('daily_rewards')
    op.drop_table('bonus_tasks')
    sa.Enum('TG_CHANNEL', 'TG_BOT', 'UNSPECIFIED', name='sponsortype').drop(op.get_bind())
    # ### end Alembic commands ###
