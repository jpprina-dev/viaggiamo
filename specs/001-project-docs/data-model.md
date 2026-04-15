# Data Model: Viaggiamo Carpooling Platform

**Feature**: 001-project-docs | **Date**: 2026-02-28

This document defines the authoritative data model for the Viaggiamo carpooling MVP. It contains:
1. The **PostgreSQL database schema** (current + PostGIS evolution)
2. The **Strawberry GraphQL type definitions** in Python
3. Entity relationships and validation rules

---

## Entity-Relationship Overview

```text
┌──────────┐       ┌──────────┐       ┌──────────┐
│  User    │1────N│  Vehicle  │       │  Rating  │
│          │       │           │       │          │
│          │1──┐   └──────────┘       └──────────┘
│          │   │         │1                 │
│          │   │         │                  │
│          │   │   ┌─────┴────┐             │
│          │   └──N│   Trip   │1───────────N│
│          │       │          │             │
│          │1──────│──────────│─────────────┘
│          │       │          │
│          │       └──────────┘
│          │1            │1
│          │             │
│          │       ┌─────┴────┐
│          │1────N│  Booking  │
│          │       │           │
└──────────┘       └───────────┘
```

**Relationships**:
- A **User** can own many **Vehicles** (1:N)
- A **User** (as driver) can create many **Trips** (1:N)
- A **Trip** is associated with exactly one **Vehicle** (N:1)
- A **User** (as passenger) can have many **Bookings** (1:N)
- A **Trip** can have many **Bookings** (1:N)
- A **Trip** can have many **Ratings** (1:N)
- A **Rating** links a rater (User) to a rated user (User) within a Trip

---

## 1. PostgreSQL Database Schema (Current)

### Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Base Fields (inherited by all tables)

Every table includes these columns from the SQLAlchemy `Base` model:

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | `INTEGER` | `PRIMARY KEY`, indexed | Auto-increment |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `now()` |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `now()` (updated on change) |

---

### Table: `users`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `email` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL`, indexed | — | Login email |
| `username` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, indexed | — | Display name |
| `name` | `VARCHAR(100)` | `NOT NULL` | — | First name |
| `last_name` | `VARCHAR(100)` | `NOT NULL` | — | Last name |
| `hashed_password` | `VARCHAR(255)` | nullable | — | Argon2 hash; NULL for OAuth users |
| `identification` | `VARCHAR(100)` | nullable | — | Government ID number |
| `identification_type` | `VARCHAR(50)` | nullable | — | `passport`, `national_id`, `drivers_license` |
| `phone` | `VARCHAR(20)` | nullable | — | Phone number |
| `phone_verified` | `BOOLEAN` | `NOT NULL` | `false` | Phone verification status |
| `email_verified` | `BOOLEAN` | `NOT NULL` | `false` | Email verification status |
| `profile_picture` | `VARCHAR(500)` | nullable | — | URL to profile image |
| `profile_short_bio` | `TEXT` | nullable | — | Short bio text |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'active'` | `active`, `suspended`, `under_review` |
| `trip_preferences` | `JSON` | nullable | — | e.g. `{"preferences": ["no_smoking"]}` |
| `auth_provider` | `VARCHAR(50)` | nullable | `'local'` | `local`, `google`, `facebook`, `github` |
| `provider_user_id` | `VARCHAR(255)` | nullable, indexed | — | OAuth provider's user ID |

**Indexes**:
- `ix_users_email` — unique B-tree on `email`
- `ix_users_username` — unique B-tree on `username`
- `ix_users_provider_user_id` — B-tree on `provider_user_id`

---

### Table: `vehicles`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `user_id` | `INTEGER` | `NOT NULL`, FK → `users.id` | — | Owner |
| `make` | `VARCHAR(50)` | `NOT NULL` | — | e.g. "Toyota" |
| `model` | `VARCHAR(50)` | `NOT NULL` | — | e.g. "Corolla" |
| `year` | `INTEGER` | `NOT NULL` | — | Manufacture year |
| `color` | `VARCHAR(30)` | nullable | — | Vehicle color |
| `license_plate` | `VARCHAR(20)` | `UNIQUE`, `NOT NULL`, indexed | — | Unique plate number |
| `seats` | `INTEGER` | `NOT NULL` | — | Total passenger seats |
| `is_active` | `BOOLEAN` | `NOT NULL` | `true` | Available for trips |
| `vehicle_legal_compliance_ack` | `BOOLEAN` | `NOT NULL` | `false` | Legal compliance acknowledged |

**Indexes**:
- `ix_vehicles_license_plate` — unique B-tree on `license_plate`

**Deletion behavior**: Soft-delete (set `is_active = false`) when vehicle has associated trips; hard-delete when no trips exist.

---

### Table: `trips`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `driver_id` | `INTEGER` | `NOT NULL`, FK → `users.id` | — | Trip creator (driver) |
| `vehicle_id` | `INTEGER` | `NOT NULL`, FK → `vehicles.id` | — | Vehicle used |
| `origin` | `VARCHAR(200)` | `NOT NULL` | — | Origin city/location name |
| `destination` | `VARCHAR(200)` | `NOT NULL` | — | Destination city/location name |
| `departure_time` | `TIMESTAMPTZ` | `NOT NULL` | — | Scheduled departure |
| `available_seats` | `INTEGER` | `NOT NULL` | `1` | Remaining seats |
| `total_seats` | `INTEGER` | `NOT NULL` | `1` | Total offered seats |
| `price_per_seat` | `NUMERIC(10,2)` | `NOT NULL` | — | Price per seat |
| `description` | `TEXT` | nullable | — | Trip notes |
| `is_active` | `BOOLEAN` | `NOT NULL` | `true` | Whether trip is listed |
| `is_completed` | `BOOLEAN` | `NOT NULL` | `false` | Whether trip has finished |
| `trip_legal_compliance_ack` | `BOOLEAN` | `NOT NULL` | `false` | Legal compliance acknowledged |
| `trip_preferences` | `JSON` | nullable | — | e.g. `{"preferences": ["no_smoking"]}` |

**Indexes**:
- `idx_trips_origin_trgm` — GIN (`gin_trgm_ops`) on `origin` for fuzzy search
- `idx_trips_destination_trgm` — GIN (`gin_trgm_ops`) on `destination` for fuzzy search
- `idx_trips_departure_time` — B-tree on `departure_time`
- `idx_trips_active_departure` — partial B-tree on `(is_active, departure_time) WHERE is_active = true`

**Deletion behavior**: Soft-delete only (set `is_active = false`).

---

### Table: `bookings`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `trip_id` | `INTEGER` | `NOT NULL`, FK → `trips.id` | — | Booked trip |
| `passenger_id` | `INTEGER` | `NOT NULL`, FK → `users.id` | — | Passenger |
| `seats_requested` | `INTEGER` | `NOT NULL` | `1` | Number of seats booked |
| `total_price` | `NUMERIC(10,2)` | `NOT NULL` | — | `price_per_seat * seats_requested` |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'pending'` | `pending`, `confirmed`, `cancelled` |
| `notes` | `VARCHAR(500)` | nullable | — | Passenger notes |
| `booking_time` | `TIMESTAMPTZ` | `NOT NULL` | — | When booking was made |
| `cancelled_by` | `VARCHAR(20)` | nullable | — | `passenger`, `driver`, `system` |
| `cancellation_reason` | `VARCHAR(500)` | nullable | — | Reason text |
| `cancellation_time` | `TIMESTAMPTZ` | nullable | — | When cancellation occurred |

**Indexes**:
- `idx_unique_active_booking` — unique partial index on `(trip_id, passenger_id) WHERE status != 'cancelled'`

**State transitions**:
```text
pending ──→ confirmed ──→ cancelled
   │                         ↑
   └─────────────────────────┘
```

**Business rules**:
- A passenger cannot have more than one active (non-cancelled) booking per trip
- If a driver cancels a passenger's booking, that passenger cannot re-book the same trip
- Cancellation restores `available_seats` on the trip

---

### Table: `ratings`

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| `trip_id` | `INTEGER` | `NOT NULL`, FK → `trips.id` | — | Associated trip |
| `rater_id` | `INTEGER` | `NOT NULL`, FK → `users.id` | — | Who gave the rating |
| `rated_user_id` | `INTEGER` | `NOT NULL`, FK → `users.id` | — | Who received the rating |
| `role` | `VARCHAR(20)` | `NOT NULL` | — | `driver` or `passenger` |
| `rating` | `INTEGER` | `NOT NULL` | — | 1–5 stars (app-layer validated) |
| `comment` | `TEXT` | nullable | — | Optional review text |

**Validation rules** (enforced in application layer):
- `rating` must be between 1 and 5 inclusive
- `role` must be either `'driver'` or `'passenger'`
- A user can only rate another user once per trip per role

---

## 2. PostGIS Evolution (Planned)

The technical brief calls for geospatial capabilities. The following schema changes introduce PostGIS for proximity matching and route-based queries, **while preserving existing string columns for display and fuzzy text search**.

### New Extension

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Schema Changes: `trips` table

Add two geography columns alongside existing `origin`/`destination` strings:

```sql
ALTER TABLE trips
  ADD COLUMN origin_point      geography(Point, 4326),
  ADD COLUMN destination_point  geography(Point, 4326);

CREATE INDEX idx_trips_origin_point_gist
  ON trips USING GIST (origin_point);

CREATE INDEX idx_trips_destination_point_gist
  ON trips USING GIST (destination_point);
```

### Schema Changes: `users` table (optional)

For driver location tracking or home-city-based matching:

```sql
ALTER TABLE users
  ADD COLUMN home_location geography(Point, 4326);

CREATE INDEX idx_users_home_location_gist
  ON users USING GIST (home_location);
```

### Example Geospatial Queries

**Find trips departing within 25 km of a point**:

```sql
SELECT id, origin, destination,
       ST_Distance(origin_point, ST_SetSRID(ST_MakePoint(-58.3816, -34.6037), 4326)) AS distance_m
FROM trips
WHERE ST_DWithin(
    origin_point,
    ST_SetSRID(ST_MakePoint(-58.3816, -34.6037), 4326)::geography,
    25000  -- 25 km radius
)
AND is_active = true
ORDER BY distance_m;
```

**Calculate trip distance**:

```sql
SELECT id,
       ST_Distance(origin_point, destination_point) / 1000.0 AS distance_km
FROM trips
WHERE id = :trip_id;
```

### Alembic Migration Template

```python
"""Add PostGIS geography columns to trips

Revision ID: <auto>
Revises: a1b2c3d4e5f6
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.add_column("trips", sa.Column("origin_point", Geography("POINT", srid=4326), nullable=True))
    op.add_column("trips", sa.Column("destination_point", Geography("POINT", srid=4326), nullable=True))
    op.create_index("idx_trips_origin_point_gist", "trips", ["origin_point"], postgresql_using="gist")
    op.create_index("idx_trips_destination_point_gist", "trips", ["destination_point"], postgresql_using="gist")

def downgrade() -> None:
    op.drop_index("idx_trips_destination_point_gist", table_name="trips")
    op.drop_index("idx_trips_origin_point_gist", table_name="trips")
    op.drop_column("trips", "destination_point")
    op.drop_column("trips", "origin_point")
```

### SQLAlchemy Model Update (Planned)

```python
from geoalchemy2 import Geography

class Trip(Base):
    __tablename__ = "trips"

    # ... existing columns ...

    # PostGIS geography columns
    origin_point: Mapped[str | None] = mapped_column(
        Geography("POINT", srid=4326), nullable=True
    )
    destination_point: Mapped[str | None] = mapped_column(
        Geography("POINT", srid=4326), nullable=True
    )
```

**Dependencies to add**: `geoalchemy2>=0.14.0` via `uv add geoalchemy2`

---

## 3. Strawberry GraphQL Type Definitions (Python)

These are the current Strawberry types that map 1:1 with the database schema. They define the GraphQL API contract.

### UserType

```python
import strawberry
from datetime import datetime
from strawberry.scalars import JSON

@strawberry.type
class UserType:
    id: int
    email: str
    username: str
    name: str
    last_name: str
    status: str                             # "active" | "suspended" | "under_review"
    email_verified: bool
    phone: str | None = None
    phone_verified: bool = False
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None
    auth_provider: str | None = None        # "local" | "google" | "facebook" | "github"
    trip_preferences: JSON | None = None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def average_rating(self, info: strawberry.Info) -> float | None:
        """Average driver rating (1-5 scale). None if unrated."""
        ...
```

### UserCreateInput

```python
@strawberry.input
class UserCreateInput:
    email: str
    username: str
    name: str
    last_name: str
    password: str
    phone: str | None = None
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None
```

### UserUpdateInput

```python
@strawberry.input
class UserUpdateInput:
    username: str | None = None
    name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    profile_short_bio: str | None = None
    identification: str | None = None
    identification_type: str | None = None
    trip_preferences: JSON | None = None
```

### AuthToken

```python
@strawberry.type
class AuthToken:
    access_token: str
    token_type: str             # Always "bearer"
```

### LoginInput

```python
@strawberry.input
class LoginInput:
    email: str
    password: str
```

### OAuthLoginInput

```python
@strawberry.input
class OAuthLoginInput:
    provider: str               # "google" | "facebook" | "github"
    token: str                  # OAuth token from the provider
```

### VehicleType

```python
@strawberry.type
class VehicleType:
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
```

### VehicleCreateInput

```python
@strawberry.input
class VehicleCreateInput:
    make: str
    model: str
    year: int
    license_plate: str
    seats: int
    color: str | None = None
    is_active: bool = True
    vehicle_legal_compliance_ack: bool
```

### VehicleUpdateInput

```python
@strawberry.input
class VehicleUpdateInput:
    make: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    license_plate: str | None = None
    seats: int | None = None
    is_active: bool | None = None
    vehicle_legal_compliance_ack: bool | None = None
```

### TripType

```python
from decimal import Decimal
from typing import Annotated

@strawberry.type
class TripType:
    id: int
    driver_id: int
    vehicle_id: int
    origin: str
    destination: str
    departure_time: datetime
    available_seats: int
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None
    is_active: bool
    is_completed: bool
    trip_legal_compliance_ack: bool
    trip_preferences: JSON | None = None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def driver(self, info: strawberry.Info) -> "UserType":
        """Resolves the driver User for this trip."""
        ...

    # PostGIS evolution — planned fields:
    # origin_lat: float | None = None
    # origin_lng: float | None = None
    # destination_lat: float | None = None
    # destination_lng: float | None = None
```

### TripCreateInput

```python
@strawberry.input
class TripCreateInput:
    origin: str
    destination: str
    departure_time: datetime
    vehicle_id: int
    total_seats: int
    price_per_seat: Decimal
    description: str | None = None
    trip_preferences: JSON | None = None
    trip_legal_compliance_ack: bool

    # PostGIS evolution — planned fields:
    # origin_lat: float | None = None
    # origin_lng: float | None = None
    # destination_lat: float | None = None
    # destination_lng: float | None = None
```

### TripUpdateInput

```python
@strawberry.input
class TripUpdateInput:
    origin: str | None = None
    destination: str | None = None
    departure_time: datetime | None = None
    vehicle_id: int | None = None
    available_seats: int | None = None
    total_seats: int | None = None
    price_per_seat: Decimal | None = None
    description: str | None = None
    is_active: bool | None = None
    is_completed: bool | None = None
    trip_legal_compliance_ack: bool | None = None
    trip_preferences: JSON | None = None
```

### TripSearchInput

```python
from datetime import date

@strawberry.input
class TripSearchInput:
    origin: str
    destination: str
    departure_date: date | None = None
    min_seats: int = 1
    max_price: Decimal | None = None
    limit: int = 20
    offset: int = 0

    # PostGIS evolution — planned fields:
    # origin_lat: float | None = None
    # origin_lng: float | None = None
    # radius_km: float = 25.0
```

### TripSearchResultType

```python
@strawberry.type
class TripSearchResultType:
    trip: TripType
    driver: "UserType"
    vehicle: "VehicleType"
    relevance_score: float

    # PostGIS evolution — planned fields:
    # distance_km: float | None = None
```

### BookingType

```python
@strawberry.type
class BookingType:
    id: int
    trip_id: int
    passenger_id: int
    seats_requested: int
    total_price: Decimal
    status: str                             # "pending" | "confirmed" | "cancelled"
    notes: str | None = None
    booking_time: datetime
    created_at: datetime
    updated_at: datetime

    # Cancellation tracking
    cancelled_by: str | None = None         # "passenger" | "driver" | "system"
    cancellation_reason: str | None = None
    cancellation_time: datetime | None = None

    @strawberry.field
    async def trip(self, info: strawberry.Info) -> "TripType":
        """Resolves the Trip for this booking."""
        ...

    @strawberry.field
    async def passenger(self, info: strawberry.Info) -> "UserType":
        """Resolves the passenger User for this booking."""
        ...
```

### BookingCreateInput

```python
@strawberry.input
class BookingCreateInput:
    trip_id: int
    seats_requested: int
    notes: str | None = None
```

### BookingUpdateInput

```python
@strawberry.input
class BookingUpdateInput:
    seats_requested: int | None = None
    status: str | None = None
    notes: str | None = None
```

### RatingType

```python
@strawberry.type
class RatingType:
    id: int
    trip_id: int
    rater_id: int
    rated_user_id: int
    role: str                               # "driver" | "passenger"
    rating: int                             # 1-5
    comment: str | None = None
    created_at: datetime
    updated_at: datetime
```

### RatingCreateInput

```python
@strawberry.input
class RatingCreateInput:
    trip_id: int
    rated_user_id: int
    role: str                               # "driver" | "passenger"
    rating: int                             # 1-5
    comment: str | None = None
```

---

## 4. PostGIS GraphQL Types (Planned Evolution)

When PostGIS is implemented, the following additional types will be introduced:

### GeoPointInput

```python
@strawberry.input
class GeoPointInput:
    latitude: float
    longitude: float
```

### GeoSearchInput (extends TripSearchInput)

```python
@strawberry.input
class GeoSearchInput:
    origin: GeoPointInput
    destination: GeoPointInput | None = None
    radius_km: float = 25.0
    departure_date: date | None = None
    min_seats: int = 1
    max_price: Decimal | None = None
    limit: int = 20
    offset: int = 0
```

### GeoTripSearchResultType

```python
@strawberry.type
class GeoTripSearchResultType:
    trip: TripType
    driver: "UserType"
    vehicle: "VehicleType"
    relevance_score: float
    origin_distance_km: float
    destination_distance_km: float | None = None
    trip_distance_km: float | None = None
```

---

## 5. Ride Lifecycle State Machine

The technical brief calls for a state-machine-driven ride lifecycle. The following documents the current implicit states and the proposed explicit state machine.

### Current State (Implicit)

Trips currently use two boolean flags:

| `is_active` | `is_completed` | Effective State |
|-------------|----------------|-----------------|
| `true` | `false` | Listed (accepting bookings) |
| `false` | `false` | Cancelled / Unlisted |
| `true` | `true` | Invalid (should not occur) |
| `false` | `true` | Completed |

### Proposed Explicit State Machine (Evolution)

```text
                    ┌─────────┐
          create    │ DRAFT   │  (driver fills details)
         ────────→  │         │
                    └────┬────┘
                         │ publish
                         ▼
                    ┌─────────┐
                    │ LISTED  │  (visible in search, accepting bookings)
                    │         │
                    └────┬────┘
                    │         │
           cancel   │         │  depart
              ┌─────┘         └──────┐
              ▼                      ▼
        ┌──────────┐          ┌──────────┐
        │CANCELLED │          │IN_TRANSIT│
        │          │          │          │
        └──────────┘          └────┬─────┘
                                   │ arrive
                                   ▼
                              ┌──────────┐
                              │COMPLETED │
                              │          │
                              └──────────┘
```

This evolution would replace the boolean flags with a `status VARCHAR(20)` column containing one of: `draft`, `listed`, `cancelled`, `in_transit`, `completed`.
