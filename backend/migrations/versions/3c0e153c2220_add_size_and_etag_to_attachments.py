"""add size and etag to attachments

Revision ID: 3c0e153c2220
Revises: f2aff7651ee0
Create Date: 2025-08-16 21:51:37.276996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c0e153c2220'
down_revision: Union[str, None] = 'f2aff7651ee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
