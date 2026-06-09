"""add public_token to training_weeks

Revision ID: e6f8c52a1f91
Revises: 8341fdaf851b
Create Date: 2026-05-31 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6f8c52a1f91'
down_revision: Union[str, Sequence[str], None] = '8341fdaf851b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('training_weeks', sa.Column('public_token', sa.String(), nullable=True))
    op.create_unique_constraint('uq_training_weeks_public_token', 'training_weeks', ['public_token'])


def downgrade() -> None:
    op.drop_constraint('uq_training_weeks_public_token', 'training_weeks', type_='unique')
    op.drop_column('training_weeks', 'public_token')
