"""Expand booking statuses to 6-status state machine.

Revision ID: 002_trip_request_reimpl
Revises: 001_trip_request_mgmt
Create Date: 2026-03-28
"""

import sqlalchemy as sa

from alembic import op

revision = "002_trip_request_reimpl"
down_revision = "001_trip_request_mgmt"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Driver-cancelled bookings → revoked
    op.execute(
        "UPDATE bookings SET status = 'revoked', cancelled_by = NULL, "
        "cancellation_reason = NULL, cancellation_time = NULL "
        "WHERE status = 'cancelled' AND cancelled_by = 'driver'"
    )
    # 2. Passenger/system-cancelled → canceled (American spelling)
    op.execute("UPDATE bookings SET status = 'canceled' WHERE status = 'cancelled'")
    # 3. Backfill revalidated: pending bookings whose last decision event was rejected→pending
    op.execute(
        """
        UPDATE bookings b
        SET status = 'revalidated'
        WHERE b.status = 'pending'
          AND EXISTS (
              SELECT 1 FROM request_decision_events rde
              WHERE rde.booking_id = b.id
                AND rde.previous_status = 'rejected'
                AND rde.new_status = 'pending'
                AND rde.id = (
                    SELECT id FROM request_decision_events
                    WHERE booking_id = b.id
                    ORDER BY created_at DESC
                    LIMIT 1
                )
          )
        """
    )
    # 4. Drop and recreate unique index with new condition
    op.drop_index("idx_unique_active_booking", table_name="bookings")
    op.create_index(
        "idx_unique_active_booking",
        "bookings",
        ["trip_id", "passenger_id"],
        unique=True,
        postgresql_where=sa.text("status != 'canceled'"),
    )


def downgrade() -> None:
    # Recreate old index
    op.drop_index("idx_unique_active_booking", table_name="bookings")
    op.create_index(
        "idx_unique_active_booking",
        "bookings",
        ["trip_id", "passenger_id"],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'"),
    )
    # Revert revoked → cancelled+driver
    op.execute(
        "UPDATE bookings SET status = 'cancelled', cancelled_by = 'driver' "
        "WHERE status = 'revoked'"
    )
    # Revert revalidated → pending
    op.execute("UPDATE bookings SET status = 'pending' WHERE status = 'revalidated'")
    # Revert canceled → cancelled
    op.execute("UPDATE bookings SET status = 'cancelled' WHERE status = 'canceled'")
