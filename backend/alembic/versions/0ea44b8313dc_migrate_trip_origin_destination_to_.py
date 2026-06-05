"""migrate_trip_origin_destination_to_locality_fk_snapshot

Revision ID: 0ea44b8313dc
Revises: 008_georef_localities
Create Date: 2026-05-17 13:48:58.155612

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0ea44b8313dc"
down_revision = "008_georef_localities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Truncate existing trips (project is in beta, all trips are seed data)
    # Proyecto en beta: todos los trips existentes son datos de seed.
    # CASCADE trunca también bookings, request_decision_events y demás dependientes.
    op.execute("TRUNCATE TABLE trips RESTART IDENTITY CASCADE")

    # 2. Drop old free-text columns
    op.drop_column("trips", "origin")
    op.drop_column("trips", "destination")

    # 3. Add FK columns referencing localities
    op.add_column(
        "trips", sa.Column("origin_locality_id", sa.String(24), nullable=False)
    )
    op.add_column(
        "trips", sa.Column("destination_locality_id", sa.String(24), nullable=False)
    )
    op.create_foreign_key(
        "fk_trips_origin_locality",
        "trips",
        "localities",
        ["origin_locality_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_trips_destination_locality",
        "trips",
        "localities",
        ["destination_locality_id"],
        ["id"],
    )

    # 4. Add snapshot columns (human-readable name at trip-creation time)
    # Snapshots del nombre de localidad al momento de creación (inmutables).
    # String(200) > localities.name(150) para dar margen a formatos de display.
    op.add_column("trips", sa.Column("origin_name", sa.String(200), nullable=False))
    op.add_column(
        "trips", sa.Column("destination_name", sa.String(200), nullable=False)
    )


def downgrade() -> None:
    # Remove snapshot columns
    op.drop_column("trips", "destination_name")
    op.drop_column("trips", "origin_name")

    # Remove FK constraints and columns
    op.drop_constraint("fk_trips_destination_locality", "trips", type_="foreignkey")
    op.drop_constraint("fk_trips_origin_locality", "trips", type_="foreignkey")
    op.drop_column("trips", "destination_locality_id")
    op.drop_column("trips", "origin_locality_id")

    # Restore original free-text columns (with server_default to satisfy NOT NULL, then remove it)
    op.add_column(
        "trips", sa.Column("origin", sa.String(200), nullable=False, server_default="")
    )
    op.add_column(
        "trips",
        sa.Column("destination", sa.String(200), nullable=False, server_default=""),
    )
    op.alter_column("trips", "origin", server_default=None)
    op.alter_column("trips", "destination", server_default=None)
