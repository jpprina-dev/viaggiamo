"""Create chat tables: threads, messages, thread_read_states.

Revision ID: 009_chat_threads_messages_read_states
Revises: 0ea44b8313dc
Create Date: 2026-06-07
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "009_chat_threads_messages_read_states"
down_revision = "0ea44b8313dc"
branch_labels = None
depends_on = None

MESSAGE_KIND_ENUM = "messagekind"
SYSTEM_EVENT_TYPE_ENUM = "systemeventtype"

MESSAGE_KIND_VALUES = ("user", "system")
SYSTEM_EVENT_TYPE_VALUES = (
    "seat_requested",
    "booking_accepted",
    "booking_rejected",
    "trip_cancelled",
    "contact_warning",
)


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create PostgreSQL enum types (idempotent)
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            f"  CREATE TYPE {MESSAGE_KIND_ENUM} AS ENUM ('user', 'system'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; "
            "END $$;"
        )
    )
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            f"  CREATE TYPE {SYSTEM_EVENT_TYPE_ENUM} AS ENUM "
            f"    ('seat_requested', 'booking_accepted', 'booking_rejected', "
            f"     'trip_cancelled', 'contact_warning'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; "
            "END $$;"
        )
    )

    # 2. threads
    has_threads = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'threads')"
        )
    ).scalar()
    if not has_threads:
        op.create_table(
            "threads",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("trip_id", sa.Integer(), nullable=False),
            sa.Column("passenger_user_id", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
            sa.ForeignKeyConstraint(["passenger_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "trip_id", "passenger_user_id", name="uq_thread_trip_passenger"
            ),
        )
        op.create_index("ix_threads_trip_id", "threads", ["trip_id"])
        op.create_index(
            "ix_threads_passenger_user_id", "threads", ["passenger_user_id"]
        )

    # 3. messages
    has_messages = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'messages')"
        )
    ).scalar()
    if not has_messages:
        op.create_table(
            "messages",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("thread_id", sa.Integer(), nullable=False),
            sa.Column(
                "kind",
                postgresql.ENUM(
                    *MESSAGE_KIND_VALUES, name=MESSAGE_KIND_ENUM, create_type=False
                ),
                nullable=False,
            ),
            sa.Column("sender_id", sa.Integer(), nullable=True),
            sa.Column(
                "event_type",
                postgresql.ENUM(
                    *SYSTEM_EVENT_TYPE_VALUES,
                    name=SYSTEM_EVENT_TYPE_ENUM,
                    create_type=False,
                ),
                nullable=True,
            ),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["thread_id"], ["threads.id"]),
            sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_messages_thread_id", "messages", ["thread_id"])

    # 4. thread_read_states
    has_read_states = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'thread_read_states')"
        )
    ).scalar()
    if not has_read_states:
        op.create_table(
            "thread_read_states",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("thread_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["thread_id"], ["threads.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "thread_id", "user_id", name="uq_read_state_thread_user"
            ),
        )
        op.create_index(
            "ix_thread_read_states_thread_id", "thread_read_states", ["thread_id"]
        )
        op.create_index(
            "ix_thread_read_states_user_id", "thread_read_states", ["user_id"]
        )


def downgrade() -> None:
    conn = op.get_bind()

    op.drop_table("thread_read_states")
    op.drop_table("messages")
    op.drop_table("threads")

    conn.execute(sa.text(f"DROP TYPE IF EXISTS {SYSTEM_EVENT_TYPE_ENUM};"))
    conn.execute(sa.text(f"DROP TYPE IF EXISTS {MESSAGE_KIND_ENUM};"))
