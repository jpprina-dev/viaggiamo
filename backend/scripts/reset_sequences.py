#!/usr/bin/env python3
"""Reset PostgreSQL sequences for all tables with auto-increment IDs."""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path if running from root
backend_dir = Path(__file__).parent.parent
if backend_dir not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402


async def reset_sequences():
    """Reset all ID sequences to the maximum ID in each table."""
    print("🔄 Resetting ID sequences...")

    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        tables = ["users", "vehicles", "trips", "bookings", "ratings"]

        for table in tables:
            try:
                # Get current max ID
                result = await session.execute(
                    text(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
                )
                max_id = result.scalar()

                # Reset sequence to max_id + 1 (so next INSERT will use max_id + 1)
                # Using setval with is_called=true means next value will be max_id + 1
                next_id = max_id + 1
                await session.execute(
                    text(
                        f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id}, true);"
                    )
                )
                print(f"   ✓ {table}: max_id={max_id}, next_id will be {next_id}")
            except Exception as e:
                print(f"   ✗ {table}: error - {e}")

        await session.commit()
        print("\n✅ All sequences reset successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_sequences())
