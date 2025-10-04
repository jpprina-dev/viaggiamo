"""Booking endpoints."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.user import User
from app.schemas.booking import BookingCreate, Booking as BookingSchema, BookingUpdate, BookingWithDetails
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=BookingSchema)
async def create_booking(
    booking_in: BookingCreate,
    trip_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Booking:
    """Create a new booking."""
    # Get trip
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    if not trip.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip is not active"
        )
    
    if trip.driver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book your own trip"
        )
    
    if trip.available_seats < booking_in.seats_requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough seats available"
        )
    
    # Calculate total price
    total_price = trip.price_per_seat * booking_in.seats_requested
    
    # Create booking
    db_booking = Booking(
        trip_id=trip_id,
        passenger_id=current_user.id,
        seats_requested=booking_in.seats_requested,
        total_price=total_price,
        notes=booking_in.notes,
        booking_time=trip.departure_time
    )
    
    # Update available seats
    trip.available_seats -= booking_in.seats_requested
    
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    
    return db_booking


@router.get("/", response_model=list[BookingSchema])
async def read_bookings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[Booking]:
    """Get current user's bookings."""
    query = select(Booking).where(Booking.passenger_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{booking_id}", response_model=BookingWithDetails)
async def read_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Get booking by ID with details."""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user is passenger or trip driver
    trip = await db.get(Trip, booking.trip_id)
    if booking.passenger_id != current_user.id and trip.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get related data
    passenger = await db.get(User, booking.passenger_id)
    driver = await db.get(User, trip.driver_id)
    
    booking_dict = {
        **booking.__dict__,
        "trip": {
            "id": trip.id,
            "origin": trip.origin,
            "destination": trip.destination,
            "departure_time": trip.departure_time,
            "price_per_seat": trip.price_per_seat,
            "driver": {
                "id": driver.id,
                "username": driver.username,
                "full_name": driver.full_name,
            }
        },
        "passenger": {
            "id": passenger.id,
            "username": passenger.username,
            "full_name": passenger.full_name,
        }
    }
    
    return booking_dict


@router.put("/{booking_id}", response_model=BookingSchema)
async def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Booking:
    """Update a booking."""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    trip = await db.get(Trip, booking.trip_id)
    if booking.passenger_id != current_user.id and trip.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = booking_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    await db.commit()
    await db.refresh(booking)
    
    return booking


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, str]:
    """Cancel a booking."""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Return seats to trip
    trip = await db.get(Trip, booking.trip_id)
    trip.available_seats += booking.seats_requested
    
    await db.delete(booking)
    await db.commit()
    
    return {"message": "Booking cancelled successfully"}


@router.get("/trip/{trip_id}/bookings", response_model=list[BookingWithDetails])
async def read_trip_bookings(
    trip_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[dict]:
    """Get bookings for a trip (only for trip driver)."""
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    if trip.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = select(Booking).where(Booking.trip_id == trip_id)
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    # Get passenger details for each booking
    bookings_with_details = []
    for booking in bookings:
        passenger = await db.get(User, booking.passenger_id)
        booking_dict = {
            **booking.__dict__,
            "trip": {
                "id": trip.id,
                "origin": trip.origin,
                "destination": trip.destination,
                "departure_time": trip.departure_time,
            },
            "passenger": {
                "id": passenger.id,
                "username": passenger.username,
                "full_name": passenger.full_name,
                "phone": passenger.phone,
            }
        }
        bookings_with_details.append(booking_dict)
    
    return bookings_with_details
