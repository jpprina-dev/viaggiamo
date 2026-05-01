# Feature Specification: Vehicle CRUD with Smart Delete

**Feature Branch**: `001-vehicle-crud`
**Created**: 2026-02-21
**Status**: Draft
**Input**: User description: "Validate the functionality of the CRUD operations for vehicles. The Soft delete from de database must be used when the vehicle is used in trips and Hard delete when no trips are associated with the vehicle. In the Frontend, after deletion, the vehicle must disappear."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hard Delete a Vehicle with No Trip History (Priority: P1)

A vehicle owner wants to delete a vehicle that has never been used in any trip. Since no historical data depends on this vehicle, it must be permanently and completely removed from the system. After confirming the deletion, the vehicle must no longer appear anywhere in the owner's vehicle list.

**Why this priority**: This is the most straightforward and complete form of deletion. It ensures the system does not accumulate orphaned vehicle records and that the deletion UI feedback works correctly end-to-end.

**Independent Test**: Can be fully tested by creating a vehicle (with no associated trips), deleting it via the UI, and verifying it no longer appears in the vehicle list — without requiring any other story to be complete.

**Acceptance Scenarios**:

1. **Given** a logged-in user has a vehicle with no trips associated, **When** the user confirms deletion via the delete modal, **Then** the vehicle record is permanently removed from the database and the vehicle disappears immediately from the vehicle list in the UI.
2. **Given** a logged-in user confirms deletion of a vehicle with no trips, **When** the deletion completes, **Then** no record of that vehicle remains — it cannot be retrieved by any subsequent query.
3. **Given** a user who does not own a vehicle attempts to delete it, **When** the delete mutation is called, **Then** the system rejects the request with an authorization error and the vehicle remains intact.
4. **Given** a vehicle ID that does not exist, **When** the delete mutation is called, **Then** the system returns a clear error and no changes are made.

---

### User Story 2 - Soft Delete a Vehicle with Trip History (Priority: P2)

A vehicle owner wants to delete a vehicle that has been used in one or more past trips. Since the trip records depend on this vehicle for historical and accounting purposes, the vehicle must not be permanently destroyed. Instead, the system marks it as deleted so it stops appearing in active vehicle lists while preserving the data integrity of associated trips. After confirming deletion, the vehicle must disappear from the owner's vehicle list in the UI.

**Why this priority**: This story protects data integrity for existing trip records while still delivering the user's intent of "removing" the vehicle from their active list. It directly depends on the same delete flow as P1.

**Independent Test**: Can be fully tested by using a vehicle in at least one trip, then deleting it via the UI, confirming the vehicle disappears from the list, and separately verifying that the associated trip records remain accessible and unaffected.

**Acceptance Scenarios**:

1. **Given** a logged-in user has a vehicle associated with one or more trips, **When** the user confirms deletion, **Then** the vehicle is marked as deleted in the system and disappears from the user's vehicle list.
2. **Given** a soft-deleted vehicle, **When** the user queries their vehicle list, **Then** the deleted vehicle does NOT appear — regardless of its internal status flag.
3. **Given** a soft-deleted vehicle, **When** a trip that was associated with that vehicle is viewed, **Then** the trip record still contains all vehicle information (make, model, year, license plate) and is not broken by the vehicle's deletion.
4. **Given** a soft-deleted vehicle, **When** the user attempts to use it in a new trip, **Then** the system prevents it from being selected as an available vehicle.

---

### User Story 3 - Create a New Vehicle (Priority: P3)

A logged-in user wants to register a new vehicle on their account so they can use it when publishing carpooling trips. The vehicle must include mandatory fields and the user must explicitly acknowledge legal compliance before the vehicle is saved.

**Why this priority**: Creation is a prerequisite for all vehicle management, but it is already implemented. This story validates its correctness.

**Independent Test**: Can be fully tested by filling out the add-vehicle form with valid data, submitting, and verifying the new vehicle appears in the vehicle list.

**Acceptance Scenarios**:

1. **Given** a logged-in user fills in all required vehicle fields and acknowledges legal compliance, **When** they submit the form, **Then** the vehicle is saved and immediately visible in their vehicle list.
2. **Given** a user submits the form without acknowledging legal compliance, **When** the submission is attempted, **Then** the system rejects the request with a clear error message and no vehicle is created.
3. **Given** a user tries to register a vehicle with a license plate already registered in the system, **When** the submission is attempted, **Then** the system rejects the request with a clear duplicate error.

---

### User Story 4 - Edit an Existing Vehicle (Priority: P4)

A logged-in user wants to update one or more details of a vehicle they own (e.g., correct the color, update the number of seats). Only the owner of the vehicle is allowed to make changes.

**Why this priority**: Update functionality is already present; this story validates ownership enforcement and partial-update behavior.

**Independent Test**: Can be fully tested by editing a field on an existing vehicle, saving, and verifying the updated value appears in the vehicle list.

**Acceptance Scenarios**:

1. **Given** a logged-in user edits one or more fields of their own vehicle and saves, **When** the update completes, **Then** the vehicle list immediately reflects the new values.
2. **Given** a user attempts to edit a vehicle they do not own, **When** the update is attempted, **Then** the system rejects it with an authorization error.
3. **Given** a partial update (only some fields provided), **When** the update completes, **Then** only the provided fields are changed; all other fields retain their previous values.

---

### Edge Cases

- What happens when a user attempts to delete the same vehicle twice (double-click or race condition)?
- What happens if the network fails after the delete mutation is sent but before the UI is refreshed?
- What is displayed if the vehicle list fails to load after deletion (error state)?
- Can a soft-deleted vehicle be reactivated, or is its deletion final from the user's perspective?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST permanently remove a vehicle from the database when the delete action is triggered and the vehicle has no associated trips.
- **FR-002**: The system MUST mark a vehicle as deleted (without removing its database record) when the delete action is triggered and the vehicle has at least one associated trip.
- **FR-003**: A deleted vehicle (soft or hard) MUST NOT appear in the authenticated user's vehicle list after deletion.
- **FR-004**: The vehicle list query MUST exclude soft-deleted vehicles from its results so the frontend always displays only active, available vehicles.
- **FR-005**: The delete confirmation modal MUST inform the user that the vehicle will be permanently deleted or deactivated depending on trip association, so they can make an informed decision.
- **FR-006**: Only the owner of a vehicle MUST be permitted to delete, update, or manage that vehicle.
- **FR-007**: Creating a vehicle MUST require the user to acknowledge legal compliance; the system MUST reject creation if this acknowledgment is absent.
- **FR-008**: A vehicle's license plate MUST be unique across the system; duplicate registrations MUST be rejected with a clear error.
- **FR-009**: Updating a vehicle MUST support partial updates — only supplied fields are changed.
- **FR-010**: A soft-deleted vehicle MUST NOT be selectable for use in new trips.

### Key Entities

- **Vehicle**: A car registered by a user for use in carpooling trips. Key attributes: owner, make, model, year, color, license plate, seat count, active/deleted status, legal compliance acknowledgment.
- **Trip**: A carpooling journey that references a Vehicle. The trip record must remain intact when a vehicle is soft-deleted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After confirming deletion of any vehicle, the vehicle disappears from the user's vehicle list within the same interaction — no page reload required.
- **SC-002**: 100% of vehicles with associated trips survive deletion as historical records; 0% of trips lose their vehicle reference data as a result of vehicle deletion.
- **SC-003**: 100% of vehicles without associated trips are permanently and completely removed from the system upon deletion — no orphan records remain.
- **SC-004**: A user attempting to delete a vehicle they do not own receives an error message 100% of the time with no data modified.
- **SC-005**: The vehicle list displayed to a user contains only vehicles that are available for use (not deleted); soft-deleted vehicles are never shown.
- **SC-006**: All four CRUD operations (create, read, update, delete) complete without unhandled errors under normal operating conditions.

## Assumptions

- The existing delete confirmation modal (which already explains the soft/hard distinction) is sufficient UX — no additional user-facing explanation is required.
- "Disappear from the frontend" means the vehicle is removed from the in-memory list immediately after a successful delete response, without requiring a full page reload (refetch is acceptable).
- Soft-deleted vehicles are considered permanently unavailable from the user's perspective; there is no "restore" flow in scope for this feature.
- A vehicle is considered "associated with trips" if any trip record references it, regardless of the trip's status (active, completed, cancelled).
- The `myVehicles` query filter behavior (returning only active vehicles) applies only to the owner's vehicle management list, not to trip history views.
