"""add matches and tactical talk tables

Revision ID: ae2243c21ac1
Revises: e6f8c52a1f91
Create Date: 2026-05-31 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ae2243c21ac1'
down_revision: Union[str, Sequence[str], None] = 'e6f8c52a1f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rival', sa.String(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('resultado', sa.String(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'tactical_talks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id'),
    )

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


def downgrade() -> None:
    op.drop_table('talk_items')
    op.drop_table('talk_sections')
    op.drop_table('tactical_talks')
    op.drop_table('matches')
