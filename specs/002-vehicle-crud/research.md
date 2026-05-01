# Research: Vehicle CRUD with Smart Delete

**Feature**: `001-vehicle-crud`
**Date**: 2026-02-21

---

## Finding 1: Root Cause of the Frontend Visibility Bug

**Question**: Why do soft-deleted vehicles remain visible in the frontend after deletion?

**Decision**: Fix the backend `my_vehicles` query to filter by `is_active == True`. Do not fix it in the frontend.

**Analysis**:
The `my_vehicles` resolver currently executes:
```python
select(Vehicle).where(Vehicle.user_id == context.user.id)
```
There is no `is_active` filter. After a soft delete (`is_active = False`), the next `refetch()` call still returns the vehicle.

The frontend `useMyVehiclesAll` hook comment even acknowledges this: `"// including inactive"`.

The trip-creation hook `useMyVehicles` works around this with a client-side filter (`filter(v => v.isActive)`) — but this is a leaky workaround. The canonical fix is backend-side, as the query contract should guarantee only active vehicles are returned.

**Fix**:
```python
# Before
select(Vehicle).where(Vehicle.user_id == context.user.id)

# After
select(Vehicle).where(
    Vehicle.user_id == context.user.id,
    Vehicle.is_active == True,
)
```

**Alternatives considered**:
- Client-side filter in `useMyVehiclesAll` — rejected because it sends unnecessary data over the wire and creates two sources of truth (one hook filters, one does not)
- New `myActiveVehicles` query — rejected because it adds schema surface area unnecessarily; the implicit contract of `myVehicles` is already "vehicles I can use"
- `deleted_at` timestamp column instead of `is_active` flag — rejected because it requires a migration and adds complexity for MVP; `is_active` is already the established soft-delete flag in this codebase

---

## Finding 2: Existing Unit Test Mocking Gap

**Question**: Are the existing delete vehicle tests testing the correct logic paths?

**Decision**: Fix the mock setup in `test_delete_vehicle_soft_deletes_vehicle` and add a new `test_delete_vehicle_hard_deletes_vehicle_without_trips`.

**Analysis**:
The current test mocks `db.execute = AsyncMock(return_value=mock_result)` with a single return value. The `delete_vehicle` resolver makes **two** `db.execute` calls:
1. `select(Vehicle).where(Vehicle.id == vehicle_id)` — to find the vehicle
2. `select(Trip).where(Trip.vehicle_id == vehicle_id).limit(1)` — to check trip association

Since the same `mock_result` is returned for both calls, `trip_result.scalar_one_or_none()` returns the mock `Vehicle` object (non-None), making `has_trips = True` — the test always exercises the soft-delete path accidentally.

The hard-delete path (`context.db.delete(vehicle)`) has **zero test coverage**.

**Fix**: Use `AsyncMock(side_effect=[vehicle_result, empty_trip_result])` to return different results for each call:
```python
# For hard-delete test: second call returns nothing
mock_vehicle_result = MagicMock()
mock_vehicle_result.scalar_one_or_none.return_value = mock_vehicle

mock_trip_result = MagicMock()
mock_trip_result.scalar_one_or_none.return_value = None  # No trips

mock_context.db.execute = AsyncMock(side_effect=[mock_vehicle_result, mock_trip_result])
mock_context.db.delete = MagicMock()
mock_context.db.commit = AsyncMock()
```

**Rationale**: Per constitution Principle II, both code paths of a conditional must be tested. The `side_effect` pattern is the idiomatic way to handle multiple sequential async calls in pytest with `unittest.mock`.

---

## Finding 3: Frontend Hook Comment Correction

**Question**: Should `useMyVehiclesAll` continue fetching all vehicles (including inactive) after the backend fix?

**Decision**: Once the backend filters, `useMyVehiclesAll` automatically reflects only active vehicles. The misleading `"including inactive"` comment should be removed and the hook description updated to `"active vehicles for CRUD management"`.

**Analysis**:
The hook name `useMyVehiclesAll` was designed to fetch all vehicles (including inactive) so the management page could show deactivated vehicles with visual indicators. With the new query contract (backend filters out inactive vehicles), the hook naturally becomes an "active vehicles" fetcher.

The toggle-active switch (`Switch` component in `VehicleList`) currently works by calling `updateVehicle` with `{ isActive: !vehicle.isActive }`. Once a vehicle is set to `is_active = False`, the next `refetch()` will remove it. This is the correct post-fix behavior.

**No code changes** to `useMyVehiclesAll` beyond comment correction — the logic (`refetch` after delete) already works correctly.

---

## Finding 4: Soft-Deleted Vehicle Exclusion from Trip Creation

**Question**: Does `useMyVehicles` (trip creation flow) need changes after the backend fix?

**Decision**: No code changes needed. The frontend filter `filter(v => v.isActive)` in `useMyVehicles` becomes redundant but harmless after the backend fix.

**Analysis**:
- Before fix: backend returns inactive vehicles → frontend filters them → only active shown
- After fix: backend returns only active vehicles → frontend filter is a no-op → only active shown

Both before and after the fix, trip creation correctly shows only active vehicles. The redundant client-side filter can be removed as a clean-up but is not required for correctness.

---

## Finding 5: `myVehicles` Query — No Schema Change Required

**Question**: Does adding the `is_active` filter to `myVehicles` require a GraphQL schema change?

**Decision**: No. The filter is purely an internal resolver implementation detail. The `myVehicles` query signature, input, and output types remain unchanged.

**Analysis**: GraphQL schemas describe _what_ is returned, not _how_ it is filtered. Adding `WHERE is_active = TRUE` is a resolver optimization/fix with no visible schema impact. No migration of the database schema is needed either — the `is_active` column and its default value (`True`) already exist.

---

## Summary Table

| # | Question | Decision | Files Affected |
|---|---|---|---|
| 1 | Why do soft-deleted vehicles show in frontend? | Fix backend `my_vehicles` query to filter `is_active == True` | `backend/app/graphql/resolvers/vehicle.py` |
| 2 | Test coverage gap in delete tests | Fix mock with `side_effect`; add hard-delete test | `backend/tests/test_graphql/test_vehicle_resolvers.py` |
| 3 | Frontend hook comment | Update misleading comment in `useMyVehiclesAll` | `frontend/src/features/vehicles/hooks/useMyVehiclesAll.ts` |
| 4 | Trip creation hook needs changes? | No — redundant frontend filter is harmless | None required |
| 5 | Schema change needed? | No — purely internal resolver fix | None |
