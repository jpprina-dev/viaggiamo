"""Create ratings table with booking_id, unique (booking_id, rater_id), CHECK score 1-5.

Revision ID: 004_rating_model
Revises: 003_booking_enum_audit
Create Date: 2026-04-05
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_rating_model"
down_revision = "003_booking_enum_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Guard: skip if table already exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ratings')"
        )
    )
    if result.scalar():
        # Table exists — ensure it has the new schema columns
        # Check if booking_id column exists (new schema) vs trip_id (old schema)
        col_result = conn.execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
                "WHERE table_name = 'ratings' AND column_name = 'booking_id')"
            )
        )
        if col_result.scalar():
            return  # Already migrated to new schema

        # Old schema exists with trip_id — drop and recreate
        op.drop_table("ratings")

    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("rater_id", sa.Integer(), nullable=False),
        sa.Column("ratee_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["rater_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ratee_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id", "rater_id", name="uq_rating_booking_rater"),
        sa.CheckConstraint("score BETWEEN 1 AND 5", name="ck_rating_score_range"),
    )


def downgrade() -> None:
    op.drop_table("ratings")
