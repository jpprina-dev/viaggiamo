"""add_trip_search_indexes

Revision ID: 7d87745a8fcd
Revises: 7f733f43bdd0
Create Date: 2025-10-25 00:29:41.502284

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7d87745a8fcd"
down_revision = "7f733f43bdd0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pg_trgm extension for fuzzy text matching
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Create indexes for trip search optimization
    # GIN indexes for fuzzy text search on origin and destination
    op.create_index(
        "idx_trips_origin_trgm",
        "trips",
        ["origin"],
        postgresql_using="gin",
        postgresql_ops={"origin": "gin_trgm_ops"},
    )
    op.create_index(
        "idx_trips_destination_trgm",
        "trips",
        ["destination"],
        postgresql_using="gin",
        postgresql_ops={"destination": "gin_trgm_ops"},
    )

    # Regular B-tree index for departure_time (date range queries)
    op.create_index("idx_trips_departure_time", "trips", ["departure_time"])

    # Composite index for common query pattern: active trips by date
    op.execute(
        "CREATE INDEX idx_trips_active_departure "
        "ON trips (is_active, departure_time) "
        "WHERE is_active = true"
    )


def downgrade() -> None:
    # Remove indexes in reverse order
    op.drop_index("idx_trips_active_departure", "trips")
    op.drop_index("idx_trips_departure_time", "trips")
    op.drop_index("idx_trips_destination_trgm", "trips")
    op.drop_index("idx_trips_origin_trgm", "trips")

    # Note: Not dropping pg_trgm extension as it might be used elsewhere
