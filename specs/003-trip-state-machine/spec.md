# Feature Specification: Trip State Machine

**Feature Branch**: `003-trip-state-machine`
**Created**: 2026-04-02
**Status**: Draft
**Input**: User description: "I want the system has a trip state machine that controls which status transitions are allowed and who can trigger them, ensuring every change is valid, role-gated and audited. A trip starts in pending once the passenger requests it. The driver can then accept or reject it. If accepted, the passenger can cancel it or the driver can revoke it. cancelled, rejected and revoked are terminal states — the trip flow ends there."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Driver Responds to a Trip Request (Priority: P1)

A passenger requests a trip and it enters the system as pending. The driver sees the request and either accepts or rejects it. The system enforces that only the driver assigned to that trip can perform this action, and that the transition is only valid from the pending state.

**Why this priority**: This is the core gating flow. Without accept/reject, no further state transitions are possible. It defines the entry point into all downstream scenarios.

**Independent Test**: Can be fully tested by creating a trip request and having the driver accept or reject it — delivering the minimum viable booking decision flow.

**Acceptance Scenarios**:

1. **Given** a trip is in `pending` state, **When** the driver accepts it, **Then** the trip transitions to `accepted` and the change is recorded with the driver's identity and timestamp.
2. **Given** a trip is in `pending` state, **When** the driver rejects it, **Then** the trip transitions to `rejected`, becomes terminal, and the change is recorded with the driver's identity and timestamp.
3. **Given** a trip is in `pending` state, **When** a passenger (non-driver) attempts to accept or reject it, **Then** the system rejects the action with a permission error and the trip remains `pending`.
4. **Given** a trip is already `accepted`, **When** the driver attempts to accept it again, **Then** the system rejects the action with an invalid transition error.

---

### User Story 2 - Passenger Cancels an Accepted Trip (Priority: P2)

After a driver accepts a trip, the passenger may need to cancel their request. The system must allow this only while the trip is in the `accepted` state and only when the requesting passenger triggers the action.

**Why this priority**: Passenger cancellation is a high-frequency real-world need. Without it, passengers are locked into trips they can no longer take, degrading trust in the platform.

**Independent Test**: Can be fully tested by accepting a trip and having the passenger cancel it — delivering a complete passenger-side cancellation flow.

**Acceptance Scenarios**:

1. **Given** a trip is in `accepted` state, **When** the passenger who requested it cancels it, **Then** the trip transitions to `cancelled`, becomes terminal, and the change is recorded with the passenger's identity and timestamp.
2. **Given** a trip is in `accepted` state, **When** a different user (not the requesting passenger) attempts to cancel it, **Then** the system rejects the action with a permission error and the trip remains `accepted`.
3. **Given** a trip is in `pending` state, **When** the passenger who requested it cancels it, **Then** the trip transitions to `cancelled`, becomes terminal, and the change is recorded with the passenger's identity and timestamp.

---

### User Story 3 - Driver Revokes an Accepted Trip (Priority: P3)

After accepting a trip, a driver may need to withdraw their acceptance due to unforeseen circumstances. The system must allow the driver to revoke only their own accepted trips.

**Why this priority**: Revocation protects drivers from being permanently locked into accepted commitments. It's lower priority than passenger cancellation because it is less frequent, but remains important for driver trust.

**Independent Test**: Can be fully tested by accepting a trip and having the driver revoke it — delivering a complete driver-side revocation flow.

**Acceptance Scenarios**:

1. **Given** a trip is in `accepted` state, **When** the driver revokes it, **Then** the trip transitions to `revoked`, becomes terminal, and the change is recorded with the driver's identity and timestamp.
2. **Given** a trip is in `accepted` state, **When** a passenger attempts to revoke it, **Then** the system rejects the action with a permission error and the trip remains `accepted`.
3. **Given** a trip is in `pending` state, **When** the driver attempts to revoke it, **Then** the system rejects the action with an invalid transition error.

---

### User Story 4 - Audit Trail of State Changes (Priority: P4)

Every trip state transition — regardless of who triggered it or which direction it moved — is permanently recorded. This record includes who performed the action, what changed, and when.

**Why this priority**: Audit trails are required for accountability and dispute resolution. They support the platform's integrity guarantees but don't block users from completing their primary flows.

**Independent Test**: Can be tested by performing any valid state transition and verifying a complete audit record is created — delivering observable accountability for trip lifecycle events.

**Acceptance Scenarios**:

1. **Given** any valid state transition occurs, **When** the change is persisted, **Then** a record exists capturing: the trip identifier, the previous state, the new state, the actor's identity, and the time of the change.
2. **Given** an invalid or unauthorized transition is attempted, **When** the system rejects it, **Then** no audit record is created for the rejected attempt.
3. **Given** a terminal state is reached, **When** any subsequent transition is attempted, **Then** the system rejects it and the existing audit trail remains intact.

---

### Edge Cases

- What happens when a trip in a terminal state (`cancelled`, `rejected`, `revoked`) receives any transition request? The system must reject all such requests with an "invalid transition" error, regardless of the requester's role.
- What happens if both the driver and the passenger attempt to modify the same trip simultaneously? The system must enforce first-request-wins sequential consistency — the first valid transition to arrive is applied; the second request sees the state has already changed and receives an invalid-transition error.
- What happens when a user who is neither the trip's passenger nor its driver attempts any transition? The system must reject with a permission error.
- What happens when a trip has no assigned driver yet and a driver attempts to accept/reject? The system must reject — only the driver associated with the trip may act on it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST enforce a fixed set of allowed state transitions: `pending → accepted`, `pending → rejected`, `pending → cancelled`, `accepted → cancelled`, `accepted → revoked`.
- **FR-002**: The system MUST reject any transition that is not in the allowed set, returning a clear error indicating the transition is invalid.
- **FR-003**: Only the driver associated with a trip MAY trigger the `pending → accepted` and `pending → rejected` transitions.
- **FR-004**: Only the passenger who requested a trip MAY trigger the `accepted → cancelled` transition.
- **FR-005**: Only the driver associated with a trip MAY trigger the `accepted → revoked` transition.
- **FR-006**: The system MUST reject any transition attempt made by a user who does not hold the required role for that transition, returning a permission error.
- **FR-007**: The states `cancelled`, `rejected`, and `revoked` MUST be terminal — no further transitions are allowed from these states.
- **FR-008**: Every successful state transition MUST produce an immutable audit record containing: trip identifier, previous state, new state, actor identity, and timestamp.
- **FR-009**: A trip MUST enter the `pending` state automatically when a passenger submits a trip request.
- **FR-010**: The system MUST NOT allow the same transition to be applied more than once to the same trip (idempotency protection for duplicate requests).
- **FR-011**: The audit trail for a trip MUST be readable only by the trip's passenger, the trip's driver, and platform administrators. Any other user attempting to access it MUST receive a permission error.

### Key Entities

- **Trip**: Represents a carpooling ride request. Key attributes: unique identifier, current status, associated passenger, associated driver. A trip transitions through statuses according to the state machine rules.
- **Trip Status**: The current lifecycle stage of a trip. Possible values: `pending`, `accepted`, `rejected`, `cancelled`, `revoked`. Determines which actions are available and to whom.
- **Status Transition**: A recorded change from one trip status to another. Captures: trip reference, previous status, new status, actor (user who triggered it), and timestamp. Immutable once created.
- **Actor**: The authenticated user performing a status change. Their role (passenger or driver) relative to the trip determines whether they are authorized to trigger a given transition.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of status transition attempts that violate the defined transition rules are rejected — no invalid transitions succeed under any circumstances.
- **SC-002**: 100% of unauthorized transition attempts (wrong role) are rejected with a permission error before any state change occurs.
- **SC-003**: Every successful state transition produces a complete audit record — zero transitions occur without a corresponding audit entry.
- **SC-004**: No trip in a terminal state can be transitioned further — all post-terminal transition attempts are rejected 100% of the time.
- **SC-005**: Users receive a clear, actionable error message within normal response times when a transition is rejected, whether due to an invalid transition or a permission violation.
- **SC-006**: The audit trail for any trip can be retrieved by its passenger, its driver, or a platform administrator, and shows the complete, ordered history of all state changes that occurred during its lifecycle.

## Assumptions

- A trip has exactly one passenger (the requester) and one driver (the assigned driver) for the purposes of this state machine. Multi-driver or multi-passenger scenarios are out of scope.
- The association between a trip and its driver is established at the time the trip is created or assigned — the state machine does not handle driver assignment, only role-gated transitions.
- "Audited" means a persistent, append-only record is created for each transition. Audit records are not editable or deletable.
- All transition requests are made by authenticated users — unauthenticated access to transition operations is already handled by the platform's existing auth layer.
- The state machine described here applies to the trip booking lifecycle, not to the trip ride itself (e.g., in-progress, completed states are out of scope for this feature).
- In-app or push notifications to passengers and drivers on state changes are **out of scope** for this feature. The state machine emits auditable transition records that a future notifications feature may consume to trigger alerts.

## Clarifications

### Session 2026-04-02

- Q: Who is authorized to read the audit trail for a trip? → A: The trip's passenger and driver can read their own trip's audit trail; platform administrators can read all.
- Q: How should concurrent conflicting transition attempts on the same trip be resolved? → A: First request wins — the first valid transition is applied; the second receives an invalid-transition error.
- Q: Are in-app notifications on state changes in scope? → A: Out of scope for this feature. The state machine produces auditable transition records; a future notifications feature may consume them to trigger alerts to passengers and drivers.
