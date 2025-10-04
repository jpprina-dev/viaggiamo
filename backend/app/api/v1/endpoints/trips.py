"""Trip endpoints."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import Trip as TripSchema
from app.schemas.trip import TripCreate, TripUpdate, TripWithDriver

router = APIRouter()


@router.post("/", response_model=TripSchema)
async def create_trip(
    trip_in: TripCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Trip:
    """Create a new trip."""
    db_trip = Trip(driver_id=current_user.id, **trip_in.model_dump())

    db.add(db_trip)
    await db.commit()
    await db.refresh(db_trip)

    return db_trip


@router.get("/", response_model=list[TripSchema])
async def read_trips(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    origin: str | None = Query(None),
    destination: str | None = Query(None),
    departure_date: datetime | None = Query(None),
) -> list[Trip]:
    """Get trips with optional filtering."""
    query = select(Trip).where(Trip.is_active.is_(True))

    if origin:
        query = query.where(Trip.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.where(Trip.destination.ilike(f"%{destination}%"))
    if departure_date:
        query = query.where(Trip.departure_time >= departure_date)

    query = query.offset(skip).limit(limit).order_by(Trip.departure_time)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{trip_id}", response_model=TripWithDriver)
async def read_trip(trip_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> Trip:
    """Get trip by ID with driver information."""
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    # Get driver information
    driver = await db.get(User, trip.driver_id)

    trip_dict = {
        **trip.__dict__,
        "driver": {
            "id": driver.id,
            "username": driver.username,
            "full_name": driver.full_name,
            "profile_picture": driver.profile_picture,
        },
    }

    return trip_dict


@router.put("/{trip_id}", response_model=TripSchema)
async def update_trip(
    trip_id: int,
    trip_in: TripUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Trip:
    """Update a trip."""
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    if trip.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    update_data = trip_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)

    await db.commit()
    await db.refresh(trip)

    return trip


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Delete a trip."""
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    if trip.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    await db.delete(trip)
    await db.commit()

    return {"message": "Trip deleted successfully"}


@router.get("/my/trips", response_model=list[TripSchema])
async def read_my_trips(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Trip]:
    """Get current user's trips."""
    query = (
        select(Trip)
        .where(Trip.driver_id == current_user.id)
        .order_by(Trip.departure_time)
    )
    result = await db.execute(query)
    return result.scalars().all()
