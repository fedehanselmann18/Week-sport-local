"""nombre --> username (unique=True)

Revision ID: ceee730de502
Revises: 285534027fec
Create Date: 2026-05-29 00:40:29.777082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceee730de502'
down_revision: Union[str, Sequence[str], None] = '285534027fec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'nombre', new_column_name='username')
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade() -> None:
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.alter_column('users', 'username', new_column_name='nombre')
