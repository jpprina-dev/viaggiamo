"""Add check constraints to enforce available_seats invariants.

Revision ID: 006_available_seats_constraints
Revises: 005_extend_active_booking_index
Create Date: 2026-04-23
"""

from alembic import op

revision = "006_available_seats_constraints"
down_revision = "005_extend_active_booking_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_trip_available_seats_non_negative",
        "trips",
        "available_seats >= 0",
    )
    op.create_check_constraint(
        "ck_trip_available_seats_max",
        "trips",
        "available_seats <= total_seats",
    )


def downgrade() -> None:
    op.drop_constraint("ck_trip_available_seats_max", "trips", type_="check")
    op.drop_constraint("ck_trip_available_seats_non_negative", "trips", type_="check")
