"""enable pgvector

Revision ID: 143e7c89cbd6
Revises: 0431574d2850
Create Date: 2026-09-11 14:51:39.957414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '143e7c89cbd6'
down_revision: Union[str, Sequence[str], None] = '0431574d2850'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")
