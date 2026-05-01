"""Add trip preferences to trips

Revision ID: a1b2c3d4e5f6
Revises: c059da7a7ad5
Create Date: 2025-12-30 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "c059da7a7ad5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add trip_preferences JSON column to trips table
    op.add_column(
        "trips",
        sa.Column("trip_preferences", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("trips", "trip_preferences")
