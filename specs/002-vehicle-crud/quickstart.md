# Quickstart: Vehicle CRUD with Smart Delete

**Feature**: `001-vehicle-crud`
**Date**: 2026-02-21

This guide walks you through verifying the vehicle CRUD behaviour end-to-end after the fix is implemented.

---

## Prerequisites

1. Docker and Docker Compose installed
2. `uv` installed for Python tooling
3. `pnpm` installed for frontend tooling
4. Repository cloned and on branch `001-vehicle-crud`

---

## 1. Start the Full Stack

From the repository root:

```bash
docker compose up -d
```

Wait for all services to be healthy:

```bash
docker compose ps
# All three services (postgres, redis, backend) should show "healthy"
```

The backend GraphQL playground is available at: http://localhost:8000/graphql
The frontend is available at: http://localhost:3000

---

## 2. Run Backend Tests First (Constitution Principle II)

Tests must pass before and after the implementation change.

```bash
cd backend
uv run pytest tests/test_graphql/test_vehicle_resolvers.py -v
uv run pytest tests/test_graphql/test_vehicle_integration.py -v
```

**Expected before the fix**: All existing tests pass. The two new tests (`test_my_vehicles_returns_only_active_vehicles` and `test_delete_vehicle_hard_deletes_vehicle_without_trips`) should **fail** at this point — this is the Red phase.

---

## 3. Verify the Bug (Before Fix)

### 3a. Register a user and get a token

```graphql
# 1. Register
mutation {
  register(userInput: {
    email: "test@example.com"
    username: "testuser"
    name: "Test"
    lastName: "User"
    password: "password123"
  }) { id email }
}

# 2. Login
mutation {
  login(loginInput: {
    email: "test@example.com"
    password: "password123"
  }) { accessToken }
}
```

Set the Authorization header in the playground:
```json
{ "Authorization": "Bearer <your_access_token>" }
```

### 3b. Create a vehicle with no trips

```graphql
mutation {
  createVehicle(vehicleInput: {
    make: "Toyota"
    model: "Corolla"
    year: 2020
    licensePlate: "ABC-001"
    seats: 5
    vehicleLegalComplianceAck: true
  }) { id make model isActive }
}
```

### 3c. Delete the vehicle

```graphql
mutation {
  deleteVehicle(vehicleId: 1)
}
```

### 3d. Confirm the bug — vehicle still visible

```graphql
query {
  myVehicles { id make model isActive }
}
```

**Before the fix**: The query returns the vehicle with `isActive: false`.
**After the fix**: The query returns an empty list `[]`.

---

## 4. Apply the Fix

### Backend — add `is_active` filter

In `backend/app/graphql/resolvers/vehicle.py`, update the `my_vehicles` resolver:

```python
# Before
result = await context.db.execute(
    select(Vehicle).where(Vehicle.user_id == context.user.id)
)

# After
result = await context.db.execute(
    select(Vehicle).where(
        Vehicle.user_id == context.user.id,
        Vehicle.is_active == True,  # noqa: E712
    )
)
```

### Frontend — update comment

In `frontend/src/features/vehicles/hooks/useMyVehiclesAll.ts`, update the file header comment from:

```typescript
/**
 * Hook for fetching all current user's vehicles (including inactive) for CRUD list
 */
```

to:

```typescript
/**
 * Hook for fetching the current user's active vehicles for CRUD management
 */
```

---

## 5. Verify the Fix

### 5a. Re-run backend tests — all should pass

```bash
cd backend
uv run pytest tests/test_graphql/test_vehicle_resolvers.py -v
uv run pytest tests/test_graphql/test_vehicle_integration.py -v
```

All tests including the new ones should be **green**.

### 5b. Lint and type check

```bash
cd backend
uv run ruff check .
uv run mypy .
```

```bash
cd frontend
pnpm build
```

All must pass with zero errors.

### 5c. Manual end-to-end test — hard delete path

1. Create a vehicle (no trips attached)
2. Navigate to `/add-vehicle` in the browser
3. Click the delete (trash) icon → confirm in the modal
4. **Expected**: Vehicle disappears immediately from the list

### 5d. Manual end-to-end test — soft delete path

1. Create a vehicle
2. Create a trip that references that vehicle
3. Navigate to `/add-vehicle`
4. Delete the vehicle
5. **Expected**: Vehicle disappears from the list

6. Query the trip to confirm trip data is intact:

```graphql
query {
  trip(tripId: 1) {
    id
    origin
    destination
    vehicleId
  }
}
```

**Expected**: Trip still exists with `vehicleId` pointing to the deleted vehicle.

### 5e. Confirm soft-deleted vehicle is excluded from trip creation

1. Navigate to the trip creation flow
2. In the vehicle selection step, confirm the soft-deleted vehicle does **not** appear.

---

## 6. Test Scenarios Summary

| Scenario | Expected Result | How to Verify |
|---|---|---|
| Hard delete (no trips) | Vehicle permanently removed; not in `myVehicles` | Steps 5c above |
| Soft delete (has trips) | `is_active = false`; not in `myVehicles`; trip data intact | Steps 5d above |
| Create vehicle without legal ack | Error: "Legal compliance acknowledgment is required" | Submit form with checkbox unchecked |
| Delete vehicle not owned | Error: "Not authorized to delete this vehicle" | Call mutation with wrong user's token |
| Update partial fields | Only changed fields update; others unchanged | Edit only color; verify make/model unchanged |
| Unauthenticated access | Error: "Authentication required" | Call `myVehicles` without Authorization header |

---

## 7. Quick Reference Commands

```bash
# Start everything
docker compose up -d

# Backend tests
cd backend && uv run pytest -v

# Backend lint + type check
cd backend && uv run ruff check . && uv run mypy .

# Frontend build check
cd frontend && pnpm build

# Stop everything
docker compose down
```
