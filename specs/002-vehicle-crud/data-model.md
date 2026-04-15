# Data Model: Vehicle CRUD with Smart Delete

**Feature**: `001-vehicle-crud`
**Date**: 2026-02-21

---

## Entities

### Vehicle

Represents a car registered by a user for use in carpooling trips.

| Field | Type | Nullable | Constraints | Notes |
|---|---|---|---|---|
| `id` | Integer | No | Primary key, auto-increment | |
| `user_id` | Integer | No | FK → `users.id` | Owner of the vehicle |
| `make` | String(50) | No | | e.g. "Toyota" |
| `model` | String(50) | No | | e.g. "Corolla" |
| `year` | Integer | No | | e.g. 2020 |
| `color` | String(30) | Yes | | Optional |
| `license_plate` | String(20) | No | Unique, indexed | Globally unique |
| `seats` | Integer | No | | Total seat count |
| `is_active` | Boolean | No | Default: `True` | **Soft-delete flag** — `False` = deleted |
| `vehicle_legal_compliance_ack` | Boolean | No | Default: `False` | User must explicitly set to `True` on creation |
| `created_at` | Timestamp | No | Auto-set on insert | |
| `updated_at` | Timestamp | No | Auto-set on update | |

**Soft-delete semantics**:
- `is_active = True` → Vehicle is active; visible in `myVehicles` list and selectable for trips.
- `is_active = False` → Vehicle is soft-deleted; hidden from `myVehicles` list and not selectable for new trips. The record persists to maintain trip history integrity.

**Hard-delete condition**: A vehicle is permanently removed (`DELETE FROM vehicles`) only when it has no associated trips. This is determined at deletion time, not stored as a field.

---

### Trip (read-only reference for this feature)

Only the vehicle relationship is relevant for this feature.

| Field | Type | Nullable | Constraints | Notes |
|---|---|---|---|---|
| `id` | Integer | No | Primary key | |
| `vehicle_id` | Integer | No | FK → `vehicles.id` | References the vehicle used in the trip |
| `driver_id` | Integer | No | FK → `users.id` | |
| *(other fields)* | — | — | — | Not modified by this feature |

**Constraint**: `vehicles.id` is referenced by `trips.vehicle_id` as a foreign key. Hard-deleting a vehicle that has trips would violate referential integrity — this is why soft delete is used when trips exist.

---

## State Transitions: Vehicle Lifecycle

```
                    create_vehicle()
                          │
                          ▼
                    ┌─────────────┐
                    │  is_active  │◄── update_vehicle(isActive: true)
                    │  = True     │
                    └─────────────┘
                          │
                    delete_vehicle()
                          │
              ┌───────────┴───────────┐
              │ has trips?            │ no trips?
              ▼                       ▼
     ┌─────────────────┐    ┌──────────────────────┐
     │   is_active     │    │  Record permanently   │
     │   = False       │    │  removed (hard delete)│
     │ (soft-deleted)  │    └──────────────────────┘
     └─────────────────┘
              │
       (record preserved for trip history)
```

**Note**: There is no "restore" transition. Once soft-deleted, a vehicle cannot be reactivated through the UI (out of scope for this feature).

---

## Query Filter Behavior

| Operation | Filter Applied | Result |
|---|---|---|
| `myVehicles` | `user_id = {me} AND is_active = True` | Only active vehicles owned by the current user |
| `vehicle(id)` | `id = {id}` | Single vehicle by ID (no active filter — used for trip history display) |
| Trip creation vehicle picker | Delegates to `myVehicles` | Only active vehicles available for selection |

---

## Validation Rules

| Rule | Trigger | Error |
|---|---|---|
| `vehicle_legal_compliance_ack` must be `True` | `createVehicle` | `"Legal compliance acknowledgment is required"` |
| `license_plate` must be unique | `createVehicle` | Database unique constraint violation |
| Caller must be vehicle owner | `updateVehicle`, `deleteVehicle` | `"Not authorized to update/delete this vehicle"` |
| Vehicle must exist | `updateVehicle`, `deleteVehicle` | `"Vehicle not found"` / returns `None` |
| Authentication required | All mutations, `myVehicles` | `"Authentication required"` |
