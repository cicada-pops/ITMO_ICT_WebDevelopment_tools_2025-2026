"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "participant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("bio", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "hackathon",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("planned", "ongoing", "finished", name="hackathonstatus"),
            nullable=False,
        ),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "team",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("hackathon_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["hackathon_id"], ["hackathon.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("requirements", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "evaluation_criteria", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("hackathon_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["hackathon_id"], ["hackathon.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "teamparticipantlink",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(["participant_id"], ["participant.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"]),
        sa.PrimaryKeyConstraint("team_id", "participant_id"),
    )

    op.create_table(
        "submission",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("repo_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"]),
        sa.PrimaryKeyConstraint("team_id", "task_id"),
    )


def downgrade() -> None:
    op.drop_table("submission")
    op.drop_table("teamparticipantlink")
    op.drop_table("task")
    op.drop_table("team")
    op.drop_table("hackathon")
    op.drop_table("participant")
    op.drop_table("location")
    sa.Enum(name="hackathonstatus").drop(op.get_bind(), checkfirst=False)
