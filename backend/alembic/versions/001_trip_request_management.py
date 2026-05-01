"""Add request decision events audit table

Revision ID: 001_trip_request_mgmt
Revises: a1b2c3d4e5f6
Create Date: 2026-03-02 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_trip_request_mgmt"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "request_decision_events",
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", sa.String(length=20), nullable=False),
        sa.Column("new_status", sa.String(length=20), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("seat_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_request_decision_events_actor_user_id",
        "request_decision_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_request_decision_events_id",
        "request_decision_events",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_request_decision_events_id",
        table_name="request_decision_events",
    )
    op.drop_index(
        "ix_request_decision_events_actor_user_id",
        table_name="request_decision_events",
    )
    op.drop_table("request_decision_events")
