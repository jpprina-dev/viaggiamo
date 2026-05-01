"""Vehicle-related GraphQL types."""

from datetime import datetime
from typing import TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


@strawberry.type
class VehicleType:
    """GraphQL Vehicle type."""

    id: int
    user_id: int
    make: str
    model: str
    year: int
    color: str | None = None
    license_plate: str
    seats: int
    is_active: bool
    vehicle_legal_compliance_ack: bool
    created_at: datetime
    updated_at: datetime


def to_vehicle_type(vehicle: "Vehicle") -> VehicleType:
    """Map a SQLAlchemy Vehicle to the GraphQL VehicleType."""
    return VehicleType(
        id=vehicle.id,
        user_id=vehicle.user_id,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        color=vehicle.color,
        license_plate=vehicle.license_plate,
        seats=vehicle.seats,
        is_active=vehicle.is_active,
        vehicle_legal_compliance_ack=vehicle.vehicle_legal_compliance_ack,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
    )


@strawberry.input
class VehicleCreateInput:
    """Input type for vehicle creation."""

    make: str
    model: str
    year: int
    license_plate: str
    seats: int
    color: str | None = None
    is_active: bool = True
    vehicle_legal_compliance_ack: bool


@strawberry.input
class VehicleUpdateInput:
    """Input type for vehicle updates."""

    make: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    license_plate: str | None = None
    seats: int | None = None
    is_active: bool | None = None
    vehicle_legal_compliance_ack: bool | None = None
