"""add joined_at field to teamparticipantlink

Revision ID: 0002_add_joined_at
Revises: 0001_initial
Create Date: 2026-04-09 00:00:01.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_add_joined_at"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "teamparticipantlink",
        sa.Column("joined_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("teamparticipantlink", "joined_at")
