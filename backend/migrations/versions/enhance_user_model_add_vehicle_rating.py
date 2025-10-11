"""Enhance User model and add Vehicle and Rating models

Revision ID: enhance_user_model
Revises: add_oauth_fields
Create Date: 2025-10-10

This migration enhances the User model with detailed profile fields and adds:
- Split full_name into name and last_name
- Replace is_verified with email_verified
- Replace is_active with status (enum: active, suspended, under_review)
- Add identification, identification_type fields
- Add phone_verified, profile_short_bio fields
- Add trip_preferences JSON field
- Create Vehicle model for user cars
- Create Rating model for driver/passenger ratings
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "enhance_user_model"
down_revision = "add_oauth_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # 1. Create vehicles table
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("make", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=30), nullable=True),
        sa.Column("license_plate", sa.String(length=20), nullable=False),
        sa.Column("seats", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_plate"),
    )
    op.create_index(op.f("ix_vehicles_id"), "vehicles", ["id"], unique=False)
    op.create_index(
        op.f("ix_vehicles_license_plate"), "vehicles", ["license_plate"], unique=True
    )

    # 2. Create ratings table
    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("rater_id", sa.Integer(), nullable=False),
        sa.Column("rated_user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rater_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rated_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ratings_id"), "ratings", ["id"], unique=False)

    # 3. Modify users table - Add new columns first
    op.add_column("users", sa.Column("name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column(
        "users", sa.Column("identification", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "users", sa.Column("identification_type", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "phone_verified", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "email_verified", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column("users", sa.Column("profile_short_bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("status", sa.String(length=20), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "trip_preferences", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
    )

    # 4. Migrate existing data
    # Split full_name into name and last_name (simple split on first space)
    op.execute(
        """
        UPDATE users
        SET name = SPLIT_PART(full_name, ' ', 1),
            last_name = CASE
                WHEN LENGTH(TRIM(SUBSTRING(full_name FROM POSITION(' ' IN full_name)))) > 0
                THEN TRIM(SUBSTRING(full_name FROM POSITION(' ' IN full_name)))
                ELSE SPLIT_PART(full_name, ' ', 1)
            END
        WHERE full_name IS NOT NULL
    """
    )

    # Copy is_verified to email_verified
    op.execute(
        "UPDATE users SET email_verified = is_verified WHERE is_verified IS NOT NULL"
    )

    # Convert is_active to status
    op.execute(
        "UPDATE users SET status = CASE WHEN is_active THEN 'active' ELSE 'suspended' END"
    )

    # Set default status for any NULL values
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")

    # 5. Make new required columns NOT NULL after data migration
    op.alter_column(
        "users", "name", existing_type=sa.String(length=100), nullable=False
    )
    op.alter_column(
        "users", "last_name", existing_type=sa.String(length=100), nullable=False
    )
    op.alter_column(
        "users", "status", existing_type=sa.String(length=20), nullable=False
    )

    # 6. Drop old columns
    op.drop_column("users", "full_name")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_active")


def downgrade() -> None:
    """Downgrade database schema."""

    # 1. Add back old columns
    op.add_column("users", sa.Column("full_name", sa.String(length=100), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # 2. Migrate data back
    # Combine name and last_name into full_name
    op.execute("UPDATE users SET full_name = CONCAT(name, ' ', last_name)")

    # Copy email_verified to is_verified
    op.execute(
        "UPDATE users SET is_verified = email_verified WHERE email_verified IS NOT NULL"
    )

    # Convert status back to is_active
    op.execute("UPDATE users SET is_active = (status = 'active')")

    # 3. Make full_name NOT NULL
    op.alter_column(
        "users", "full_name", existing_type=sa.String(length=100), nullable=False
    )

    # 4. Drop new columns
    op.drop_column("users", "trip_preferences")
    op.drop_column("users", "status")
    op.drop_column("users", "profile_short_bio")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "phone_verified")
    op.drop_column("users", "identification_type")
    op.drop_column("users", "identification")
    op.drop_column("users", "last_name")
    op.drop_column("users", "name")

    # 5. Drop ratings table
    op.drop_index(op.f("ix_ratings_id"), table_name="ratings")
    op.drop_table("ratings")

    # 6. Drop vehicles table
    op.drop_index(op.f("ix_vehicles_license_plate"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_id"), table_name="vehicles")
    op.drop_table("vehicles")
