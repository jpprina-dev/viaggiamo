"""Per-request DataLoaders for batched relationship loading.

Strawberry resolves fields one row at a time. When a list of ``BookingType``
is returned and the client asks for ``{ trip { id } }``, the lazy ``trip``
field on each booking would issue its own ``SELECT`` — the classic N+1
problem. A ``DataLoader`` collects all ``.load(id)`` calls in the same event
loop tick and resolves them with a single ``WHERE id IN (...)`` query.

Loaders are stateful (cache per instance) and must be scoped to a single
request, which is why they live on ``Context`` and are constructed in
``get_context``.
"""

from collections.abc import Iterable
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle

T = TypeVar("T")


def _index_by_id(rows: Iterable[T], ids: Iterable[int]) -> list[T | None]:
    by_id: dict[int, T] = {row.id: row for row in rows}  # type: ignore[attr-defined]
    return [by_id.get(i) for i in ids]


def make_user_loader(db: AsyncSession) -> DataLoader[int, User | None]:
    async def load(ids: list[int]) -> list[User | None]:
        result = await db.execute(select(User).where(User.id.in_(ids)))
        return _index_by_id(result.scalars().all(), ids)

    return DataLoader(load_fn=load)


def make_trip_loader(db: AsyncSession) -> DataLoader[int, Trip | None]:
    async def load(ids: list[int]) -> list[Trip | None]:
        result = await db.execute(select(Trip).where(Trip.id.in_(ids)))
        return _index_by_id(result.scalars().all(), ids)

    return DataLoader(load_fn=load)


def make_vehicle_loader(db: AsyncSession) -> DataLoader[int, Vehicle | None]:
    async def load(ids: list[int]) -> list[Vehicle | None]:
        result = await db.execute(select(Vehicle).where(Vehicle.id.in_(ids)))
        return _index_by_id(result.scalars().all(), ids)

    return DataLoader(load_fn=load)
