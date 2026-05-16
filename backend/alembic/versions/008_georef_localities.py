"""Crear tablas de catálogo georef-ar: provinces, departments, localities.

Revision ID: 008_georef_localities
Revises: 007_add_deleted_at_to_vehicles
"""

import sqlalchemy as sa

from alembic import op

revision = "008_georef_localities"
down_revision = "007_add_deleted_at_to_vehicles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.create_table(
        "provinces",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "province_id",
            sa.String(24),
            sa.ForeignKey("provinces.id"),
            nullable=False,
        ),
    )

    op.create_table(
        "localities",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column(
            "province_id",
            sa.String(24),
            sa.ForeignKey("provinces.id"),
            nullable=False,
        ),
        sa.Column(
            "department_id",
            sa.String(24),
            sa.ForeignKey("departments.id"),
            nullable=False,
        ),
        sa.Column("province_name", sa.String(100), nullable=False),
        sa.Column("department_name", sa.String(100), nullable=False),
    )

    op.execute("""
        CREATE INDEX ix_localities_name_trgm
        ON localities USING gin (unaccent(name) gin_trgm_ops);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_localities_name_trgm;")
    op.drop_table("localities")
    op.drop_table("departments")
    op.drop_table("provinces")
