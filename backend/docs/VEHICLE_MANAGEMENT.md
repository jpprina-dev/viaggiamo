# Vehicle Management System

This document describes the vehicle management system implemented in the Viaggiamo backend, including GraphQL API, database models, and business logic.

## 📋 Overview

The vehicle management system allows users to:
- Register and manage their personal vehicles
- Associate vehicles with trips for carpooling
- Ensure legal compliance for both vehicles and trips
- Maintain vehicle ownership and access control

## 🏗️ Architecture

### Database Models

#### Vehicle Model (`app/models/vehicle.py`)
```python
class Vehicle(Base):
    __tablename__ = "vehicles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    vehicle_legal_compliance_ack: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="vehicles")
```

#### Trip Model Updates (`app/models/trip.py`)
```python
class Trip(Base):
    # ... existing fields ...
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    trip_legal_compliance_ack: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship("Vehicle")
```

### GraphQL Types

#### VehicleType
```graphql
type VehicleType {
  id: Int!
  userId: Int!
  make: String!
  model: String!
  year: Int!
  color: String
  licensePlate: String!
  seats: Int!
  isActive: Boolean!
  vehicleLegalComplianceAck: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime!
}
```

#### VehicleCreateInput
```graphql
input VehicleCreateInput {
  make: String!
  model: String!
  year: Int!
  licensePlate: String!
  seats: Int!
  color: String
  isActive: Boolean = true
  vehicleLegalComplianceAck: Boolean!
}
```

#### VehicleUpdateInput
```graphql
input VehicleUpdateInput {
  make: String
  model: String
  year: Int
  color: String
  licensePlate: String
  seats: Int
  isActive: Boolean
  vehicleLegalComplianceAck: Boolean
}
```

## 🔧 GraphQL API

### Queries

#### `myVehicles`
Get all vehicles owned by the authenticated user.

```graphql
query {
  myVehicles {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
    vehicleLegalComplianceAck
  }
}
```

**Response:**
```json
{
  "data": {
    "myVehicles": [
      {
        "id": 1,
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "licensePlate": "ABC-123",
        "seats": 5,
        "isActive": true,
        "vehicleLegalComplianceAck": true
      }
    ]
  }
}
```

#### `vehicle(vehicleId: Int!)`
Get a specific vehicle by ID (public access).

```graphql
query {
  vehicle(vehicleId: 1) {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
  }
}
```

#### `vehicle(tripId: Int!)`
Get vehicle information for a specific trip.

```graphql
query {
  vehicle(tripId: 1) {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
  }
}
```

### Mutations

#### `createVehicle(vehicleInput: VehicleCreateInput!)`
Create a new vehicle for the authenticated user.

```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Toyota"
    model: "Corolla"
    year: 2020
    licensePlate: "ABC-123"
    seats: 5
    color: "Blue"
    vehicleLegalComplianceAck: true
  }) {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
    vehicleLegalComplianceAck
  }
}
```

**Validation Rules:**
- User must be authenticated
- `vehicleLegalComplianceAck` must be `true`
- `licensePlate` must be unique across all vehicles
- `seats` must be greater than 0

#### `updateVehicle(vehicleId: Int!, vehicleInput: VehicleUpdateInput!)`
Update an existing vehicle (only by owner).

```graphql
mutation {
  updateVehicle(
    vehicleId: 1
    vehicleInput: {
      color: "Red"
      isActive: false
    }
  ) {
    id
    make
    model
    color
    isActive
  }
}
```

**Validation Rules:**
- User must be authenticated
- User must own the vehicle
- Cannot change `licensePlate` to an existing one

#### `deleteVehicle(vehicleId: Int!)`
Soft delete a vehicle (mark as inactive).

```graphql
mutation {
  deleteVehicle(vehicleId: 1)
}
```

**Response:**
```json
{
  "data": {
    "deleteVehicle": true
  }
}
```

**Validation Rules:**
- User must be authenticated
- User must own the vehicle

## 🚗 Trip Integration

### Updated Trip Creation

Trips now require a vehicle assignment and legal compliance acknowledgment:

```graphql
mutation {
  createTrip(tripInput: {
    origin: "Madrid"
    destination: "Barcelona"
    departureTime: "2024-01-15T10:00:00Z"
    vehicleId: 1
    totalSeats: 4
    pricePerSeat: 25.50
    tripLegalComplianceAck: true
  }) {
    id
    origin
    destination
    vehicleId
    tripLegalComplianceAck
  }
}
```

**Validation Rules:**
- User must be authenticated
- `vehicleId` must exist and belong to the authenticated user
- Vehicle must be active (`isActive: true`)
- `tripLegalComplianceAck` must be `true`

### Updated Trip Queries

Trip queries now include vehicle information:

```graphql
query {
  trips {
    id
    origin
    destination
    vehicleId
    tripLegalComplianceAck
    # Get vehicle details separately
  }

  # Get vehicle for a specific trip
  vehicle(tripId: 1) {
    make
    model
    year
    licensePlate
    seats
  }
}
```

## 🔒 Security & Validation

### Ownership Validation
- Users can only create, read, update, and delete their own vehicles
- Vehicle ownership is validated on all operations
- Trip creation validates that the vehicle belongs to the authenticated user

### Legal Compliance
- **Vehicle Level**: `vehicleLegalComplianceAck` must be `true` when creating a vehicle
- **Trip Level**: `tripLegalComplianceAck` must be `true` when creating a trip
- These are separate acknowledgments for different legal requirements

### Data Validation
- License plates must be unique across all vehicles
- Vehicle seats must be greater than 0
- Vehicle must be active to be assigned to trips
- All required fields must be provided

## 📊 Database Schema

### Vehicles Table
```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    color VARCHAR(30),
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    seats INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    vehicle_legal_compliance_ack BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX ix_vehicles_id ON vehicles(id);
CREATE INDEX ix_vehicles_license_plate ON vehicles(license_plate);
```

### Trips Table Updates
```sql
ALTER TABLE trips ADD COLUMN vehicle_id INTEGER NOT NULL REFERENCES vehicles(id);
ALTER TABLE trips ADD COLUMN trip_legal_compliance_ack BOOLEAN NOT NULL DEFAULT false;
```

## 🚀 Usage Examples

### Complete Vehicle Management Flow

1. **Create a Vehicle**
```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Honda"
    model: "Civic"
    year: 2019
    licensePlate: "XYZ-789"
    seats: 5
    color: "Silver"
    vehicleLegalComplianceAck: true
  }) {
    id
    licensePlate
  }
}
```

2. **List User's Vehicles**
```graphql
query {
  myVehicles {
    id
    make
    model
    year
    licensePlate
    isActive
  }
}
```

3. **Create a Trip with Vehicle**
```graphql
mutation {
  createTrip(tripInput: {
    origin: "Madrid"
    destination: "Valencia"
    departureTime: "2024-01-20T14:30:00Z"
    vehicleId: 1
    totalSeats: 4
    pricePerSeat: 30.00
    tripLegalComplianceAck: true
  }) {
    id
    vehicleId
  }
}
```

4. **Get Trip with Vehicle Information**
```graphql
query {
  trip(tripId: 1) {
    id
    origin
    destination
    vehicleId
  }

  vehicle(tripId: 1) {
    make
    model
    year
    licensePlate
    seats
  }
}
```

5. **Update Vehicle**
```graphql
mutation {
  updateVehicle(
    vehicleId: 1
    vehicleInput: {
      color: "Black"
      isActive: false
    }
  ) {
    id
    color
    isActive
  }
}
```

## 🔧 Error Handling

### Common Error Responses

#### Authentication Required
```json
{
  "errors": [
    {
      "message": "Authentication required",
      "extensions": {
        "code": "AUTHENTICATION_REQUIRED"
      }
    }
  ]
}
```

#### Vehicle Not Found
```json
{
  "errors": [
    {
      "message": "Vehicle not found",
      "extensions": {
        "code": "VEHICLE_NOT_FOUND"
      }
    }
  ]
}
```

#### Not Authorized
```json
{
  "errors": [
    {
      "message": "Not authorized to update this vehicle",
      "extensions": {
        "code": "NOT_AUTHORIZED"
      }
    }
  ]
}
```

#### Legal Compliance Required
```json
{
  "errors": [
    {
      "message": "Legal compliance acknowledgment is required",
      "extensions": {
        "code": "LEGAL_COMPLIANCE_REQUIRED"
      }
    }
  ]
}
```

## 📝 Migration

The vehicle management system was added via Alembic migration:

```bash
# Create migration
uv run alembic revision --autogenerate -m "Add vehicle legal compliance and trip vehicle relationship"

# Apply migration
uv run alembic upgrade head
```

Migration file: `alembic/versions/c111d10c6526_add_vehicle_legal_compliance_and_trip_.py`

## 🧪 Testing

### Test Vehicle Creation
```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Test"
    model: "Car"
    year: 2020
    licensePlate: "TEST-001"
    seats: 4
    vehicleLegalComplianceAck: true
  }) {
    id
    make
    model
    licensePlate
  }
}
```

### Test Trip with Vehicle
```graphql
mutation {
  createTrip(tripInput: {
    origin: "Test Origin"
    destination: "Test Destination"
    departureTime: "2024-12-31T12:00:00Z"
    vehicleId: 1
    totalSeats: 3
    pricePerSeat: 20.00
    tripLegalComplianceAck: true
  }) {
    id
    vehicleId
    tripLegalComplianceAck
  }
}
```

## 🔄 Future Enhancements

### Potential Improvements
1. **Vehicle Images**: Add support for vehicle photos
2. **Vehicle Documents**: Store insurance, registration documents
3. **Vehicle Maintenance**: Track maintenance history
4. **Vehicle Categories**: Support for different vehicle types (car, van, motorcycle)
5. **Vehicle Availability**: Calendar-based availability management
6. **Vehicle Ratings**: Allow passengers to rate vehicles
7. **Bulk Operations**: Support for managing multiple vehicles
8. **Vehicle Sharing**: Allow vehicle sharing between trusted users

### API Extensions
1. **Vehicle Search**: Search vehicles by make, model, year
2. **Vehicle Filters**: Filter by seats, features, availability
3. **Vehicle Statistics**: Usage statistics and analytics
4. **Vehicle Recommendations**: Suggest vehicles based on trip requirements

## 📚 Related Documentation

- [GraphQL Architecture](GraphQL_Architecture.md) - Overall GraphQL structure
- [Quick Reference](QUICK_REFERENCE.md) - API quick reference
- [Structure Overview](STRUCTURE_OVERVIEW.md) - Project structure
- [Database Models](../app/models/) - Database model definitions
