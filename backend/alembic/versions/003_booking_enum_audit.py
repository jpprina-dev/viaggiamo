"""Add BookingStatus enum, migrate status column, and create booking_audit_logs table.

Revision ID: 003_booking_enum_audit
Revises: 002_trip_request_reimpl
Create Date: 2026-04-02
"""

import sqlalchemy as sa

from alembic import op

revision = "003_booking_enum_audit"
down_revision = "002_trip_request_reimpl"
branch_labels = None
depends_on = None

# PostgreSQL enum type names
BOOKING_STATUS_ENUM = "bookingstatus"
ACTOR_ROLE_ENUM = "actorrole"

BOOKING_STATUS_VALUES = ("pending", "accepted", "rejected", "cancelled", "revoked")
ACTOR_ROLE_VALUES = ("passenger", "driver")


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create PostgreSQL enum types (idempotent)
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            f"  CREATE TYPE {BOOKING_STATUS_ENUM} AS ENUM "
            f"    ('pending', 'accepted', 'rejected', 'cancelled', 'revoked'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; "
            "END $$;"
        )
    )
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            f"  CREATE TYPE {ACTOR_ROLE_ENUM} AS ENUM ('passenger', 'driver'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; "
            "END $$;"
        )
    )

    # 2. Add new enum column alongside the old String column (skip if already done)
    has_status_new = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name='bookings' AND column_name='status_new'"
        )
    ).scalar()

    status_is_varchar = conn.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name='bookings' AND column_name='status'"
        )
    ).scalar()

    if status_is_varchar == "character varying":
        # status is still varchar — we need to do the full migration
        if not has_status_new:
            op.add_column(
                "bookings",
                sa.Column(
                    "status_new",
                    sa.Enum(
                        *BOOKING_STATUS_VALUES,
                        name=BOOKING_STATUS_ENUM,
                        create_type=False,
                    ),
                    nullable=True,
                ),
            )

        # 3. Backfill
        #    "canceled" (American) → "cancelled" (British)
        #    "revalidated" (legacy) → "pending"
        #    "confirmed" (legacy) → "accepted"
        conn.execute(
            sa.text(
                f"""
            UPDATE bookings
            SET status_new = CASE
                WHEN status = 'canceled'     THEN 'cancelled'::{BOOKING_STATUS_ENUM}
                WHEN status = 'revalidated'  THEN 'pending'::{BOOKING_STATUS_ENUM}
                WHEN status = 'confirmed'    THEN 'accepted'::{BOOKING_STATUS_ENUM}
                ELSE status::{BOOKING_STATUS_ENUM}
            END
            """
            )
        )

        # 4. Make the new column NOT NULL now that it's populated
        op.alter_column("bookings", "status_new", nullable=False)

        # 5. Drop the old partial unique index
        op.drop_index("idx_unique_active_booking", table_name="bookings")

        # 6. Drop old String status column and rename new one
        op.drop_column("bookings", "status")
        op.alter_column("bookings", "status_new", new_column_name="status")

        # 7. Recreate partial unique index excluding 'cancelled'
        op.create_index(
            "idx_unique_active_booking",
            "bookings",
            ["trip_id", "passenger_id"],
            unique=True,
            postgresql_where=sa.text("status != 'cancelled'"),
        )
    # else: status column is already the enum type — nothing to do

    # 8. Create booking_audit_logs table (idempotent)
    has_audit_table = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name='booking_audit_logs'"
        )
    ).scalar()

    if not has_audit_table:
        op.create_table(
            "booking_audit_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column(
                "booking_id",
                sa.Integer,
                sa.ForeignKey("bookings.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("from_status", sa.String(20), nullable=False),
            sa.Column("to_status", sa.String(20), nullable=False),
            sa.Column(
                "actor_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False
            ),
            sa.Column(
                "actor_role",
                sa.Enum(*ACTOR_ROLE_VALUES, name=ACTOR_ROLE_ENUM, create_type=False),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()

    # 1. Drop audit log table
    op.drop_table("booking_audit_logs")

    # 2. Drop new partial unique index
    op.drop_index("idx_unique_active_booking", table_name="bookings")

    # 3. Add back the old String column
    op.add_column(
        "bookings",
        sa.Column("status_old", sa.String(20), nullable=True),
    )

    # 4. Backfill: "cancelled" → "canceled" (American, as in migration 002)
    conn.execute(
        sa.text(
            """
        UPDATE bookings
        SET status_old = CASE
            WHEN status::text = 'cancelled' THEN 'canceled'
            ELSE status::text
        END
        """
        )
    )

    op.alter_column("bookings", "status_old", nullable=False)

    # 5. Drop enum column and rename old one back
    op.drop_column("bookings", "status")
    op.alter_column("bookings", "status_old", new_column_name="status")

    # 6. Recreate old partial unique index
    op.create_index(
        "idx_unique_active_booking",
        "bookings",
        ["trip_id", "passenger_id"],
        unique=True,
        postgresql_where=sa.text("status != 'canceled'"),
    )

    # 7. Drop PostgreSQL enum types
    conn.execute(sa.text(f"DROP TYPE IF EXISTS {BOOKING_STATUS_ENUM};"))
    conn.execute(sa.text(f"DROP TYPE IF EXISTS {ACTOR_ROLE_ENUM};"))
