"""index exceptions on due_at and status

Revision ID: f2aff7651ee0
Revises: 0c50cfd85f82
Create Date: 2025-08-16 20:16:23.083955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2aff7651ee0'
down_revision: Union[str, None] = '0c50cfd85f82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
