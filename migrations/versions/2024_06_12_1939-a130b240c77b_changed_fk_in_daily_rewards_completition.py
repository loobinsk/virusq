"""Changed fk in daily_rewards_completition

Revision ID: a130b240c77b
Revises: 86e1772893bb
Create Date: 2024-06-12 19:39:43.188435

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a130b240c77b'
down_revision: Union[str, None] = '86e1772893bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('daily_rewards_completition', sa.Column('daily_reward_id', sa.BigInteger(), nullable=True))
    op.add_column('daily_rewards_completition', sa.Column('collected_at', sa.DateTime(), nullable=True))
    op.drop_index('ix_daily_rewards_completition_bonus_task_id', table_name='daily_rewards_completition')
    op.create_index(op.f('ix_daily_rewards_completition_daily_reward_id'), 'daily_rewards_completition', ['daily_reward_id'], unique=False)
    op.drop_constraint('fk_daily_rewards_completition_bonus_task_id_bonus_tasks', 'daily_rewards_completition', type_='foreignkey')
    op.create_foreign_key(op.f('fk_daily_rewards_completition_daily_reward_id_daily_rewards'), 'daily_rewards_completition', 'daily_rewards', ['daily_reward_id'], ['id'], ondelete='CASCADE')
    op.drop_column('daily_rewards_completition', 'bonus_task_id')
    op.drop_column('users', 'last_daily_reward_collected_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_daily_reward_collected_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('daily_rewards_completition', sa.Column('bonus_task_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_daily_rewards_completition_daily_reward_id_daily_rewards'), 'daily_rewards_completition', type_='foreignkey')
    op.create_foreign_key('fk_daily_rewards_completition_bonus_task_id_bonus_tasks', 'daily_rewards_completition', 'bonus_tasks', ['bonus_task_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_daily_rewards_completition_daily_reward_id'), table_name='daily_rewards_completition')
    op.create_index('ix_daily_rewards_completition_bonus_task_id', 'daily_rewards_completition', ['bonus_task_id'], unique=False)
    op.drop_column('daily_rewards_completition', 'collected_at')
    op.drop_column('daily_rewards_completition', 'daily_reward_id')
    # ### end Alembic commands ###
