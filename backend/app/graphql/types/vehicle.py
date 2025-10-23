"""Vehicle-related GraphQL types."""

from datetime import datetime

import strawberry


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
