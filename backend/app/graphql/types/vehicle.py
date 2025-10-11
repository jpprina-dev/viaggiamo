"""Vehicle-related GraphQL types."""

from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class VehicleType:
    """GraphQL Vehicle type."""

    id: int
    user_id: int
    make: str
    model: str
    year: int
    color: Optional[str] = None
    license_plate: str
    seats: int
    is_active: bool
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
    color: Optional[str] = None
    is_active: bool = True


@strawberry.input
class VehicleUpdateInput:
    """Input type for vehicle updates."""

    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    seats: Optional[int] = None
    is_active: Optional[bool] = None
