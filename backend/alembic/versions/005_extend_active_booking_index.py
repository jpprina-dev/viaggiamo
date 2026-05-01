"""Extend active booking unique index to also exclude rejected and revoked statuses.

Passengers can now re-book after being rejected or revoked. The index previously only
excluded 'cancelled'; now all three terminal driver-action statuses are excluded.

Revision ID: 005_extend_active_booking_index
Revises: 004_rating_model
Create Date: 2026-04-11
"""

from alembic import op

revision = "005_extend_active_booking_index"
down_revision = "004_rating_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "idx_unique_active_booking",
        table_name="bookings",
        postgresql_where="status != 'cancelled'",
    )
    op.create_index(
        "idx_unique_active_booking",
        "bookings",
        ["trip_id", "passenger_id"],
        unique=True,
        postgresql_where="status NOT IN ('cancelled', 'rejected', 'revoked')",
    )


def downgrade() -> None:
    op.drop_index(
        "idx_unique_active_booking",
        table_name="bookings",
        postgresql_where="status NOT IN ('cancelled', 'rejected', 'revoked')",
    )
    op.create_index(
        "idx_unique_active_booking",
        "bookings",
        ["trip_id", "passenger_id"],
        unique=True,
        postgresql_where="status != 'cancelled'",
    )
