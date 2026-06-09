"""remove talk sections and items

Revision ID: 5f2b9e7a1d3c
Revises: ae2243c21ac1
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5f2b9e7a1d3c'
down_revision: Union[str, Sequence[str], None] = 'ae2243c21ac1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('talk_items')
    op.drop_table('talk_sections')


def downgrade() -> None:
    op.create_table(
        'talk_sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('talk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('orden', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['talk_id'], ['tactical_talks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'talk_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('orden', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['talk_sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
