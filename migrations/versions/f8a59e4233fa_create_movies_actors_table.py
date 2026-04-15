"""create movies_actors table

Revision ID: f8a59e4233fa
Revises: 87857cbd3ef4
Create Date: 2026-04-14 21:48:30.889571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a59e4233fa'
down_revision: Union[str, Sequence[str], None] = '87857cbd3ef4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'movies_actors',
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id']),
        sa.PrimaryKeyConstraint('movie_id', 'actor_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('movies_actors')
