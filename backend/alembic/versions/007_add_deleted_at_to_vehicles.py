"""Add deleted_at column to vehicles for soft-delete support.

Revision ID: 007_add_deleted_at_to_vehicles
Revises: 006_available_seats_constraints
Create Date: 2026-05-09
"""

import sqlalchemy as sa

from alembic import op

revision = "007_add_deleted_at_to_vehicles"
down_revision = "006_available_seats_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vehicles",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("vehicles", "deleted_at")
