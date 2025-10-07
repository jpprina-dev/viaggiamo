"""Add OAuth fields to User model

Revision ID: add_oauth_fields
Revises:
Create Date: 2025-10-07

This migration adds OAuth/SSO support to the User model by:
- Adding auth_provider field (default: 'local')
- Adding provider_user_id field for OAuth provider's user ID
- Making hashed_password nullable (OAuth users don't have passwords)
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_oauth_fields"
down_revision = None  # Update this to your previous migration if you have one
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add OAuth fields to users table."""
    # Add auth_provider column
    op.add_column(
        "users", sa.Column("auth_provider", sa.String(length=50), nullable=True)
    )

    # Add provider_user_id column with index
    op.add_column(
        "users", sa.Column("provider_user_id", sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f("ix_users_provider_user_id"), "users", ["provider_user_id"], unique=False
    )

    # Update existing users to have 'local' as auth_provider
    op.execute("UPDATE users SET auth_provider = 'local' WHERE auth_provider IS NULL")

    # Make hashed_password nullable (it was NOT NULL before)
    op.alter_column(
        "users", "hashed_password", existing_type=sa.String(length=255), nullable=True
    )


def downgrade() -> None:
    """Remove OAuth fields from users table."""
    # Remove the index first
    op.drop_index(op.f("ix_users_provider_user_id"), table_name="users")

    # Remove columns
    op.drop_column("users", "provider_user_id")
    op.drop_column("users", "auth_provider")

    # Make hashed_password NOT NULL again
    # Note: This will fail if there are OAuth users without passwords
    op.alter_column(
        "users", "hashed_password", existing_type=sa.String(length=255), nullable=False
    )
