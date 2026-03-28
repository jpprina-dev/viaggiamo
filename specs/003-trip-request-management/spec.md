# Feature Specification: Trip Request Management

**Feature Branch**: `001-trip-request-management`
**Created**: 2026-03-02
**Status**: Draft
**Input**: User description: "Update Trip Creation and Passenger Management. As a driver, I want to publish my trip and manage join requests so that I can choose who I travel with and ensure my car reaches full capacity before the departure time. I need the ability to accept or reject passengers, with the option to reconsider a previously rejected user if I change my mind."

## Clarifications

### Session 2026-03-21

- Q: Does driver revocation of an accepted request (accepted → rejected) trigger a notification to the passenger? → A: Yes — notify the passenger immediately, same as other status changes.
- Q: What passenger details are shown in the accepted passengers list (FR-017)? → A: Name, profile photo, and average rating.
- Q: After revocation, can the passenger submit a new join request for the same trip? → A: No — a revoked passenger cannot submit a new join request for the same trip.
- Q: Is passenger-initiated cancellation (accepted/revalidated → canceled) in scope for this feature? → A: Out of scope. The `canceled` status is defined in the state machine for data model completeness; the trigger and UI are handled by a separate passenger-cancellation feature.
- Q: What are the canonical Join Request statuses and their transitions? → A: pending → accepted (driver accepts) | pending → rejected (driver rejects; passenger cannot rejoin unless driver revalidates) | pending → canceled (passenger withdraws) | rejected → revalidated (driver re-enables) | accepted → canceled (passenger exits) | accepted → revoked (driver removes) | revalidated → canceled (passenger exits) | revalidated → revoked (driver removes).

### Session 2026-03-02

- Q: When only one seat remains and multiple requests are being approved around the same time, what is the canonical rule? → A: First successful acceptance action wins; later accepts are rejected as full.
- Q: When all seats are filled, how should new incoming join requests be handled before departure? → A: Block new requests entirely once full.
- Q: Who is allowed to accept/reject/reconsider join requests for a trip? → A: Only the trip owner (driver).
- Q: If a seat reopens (for example, an accepted passenger cancels), what should happen to previously rejected requests? → A: Stay rejected; driver must manually reconsider.
- Q: When should passengers stop being allowed to submit join requests for a trip? → A: At the scheduled departure time.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish Trip and Receive Requests (Priority: P1)

As a driver, I create and publish a trip so passengers can discover it and submit join requests before departure.

**Why this priority**: Trip publication and request intake are the core entry point for passenger management; without this flow, no approval decisions can happen.

**Independent Test**: Can be fully tested by publishing a new trip, viewing it as available, submitting join requests from passenger accounts, and verifying that requests appear in the driver's pending queue.

**Acceptance Scenarios**:

1. **Given** a driver has entered all required trip details and available seats are greater than zero, **When** the driver publishes the trip, **Then** the trip becomes visible for passenger join requests.
2. **Given** a trip is published and still open for requests, **When** a passenger submits a join request, **Then** the request is recorded and shown to the driver as pending.

---

### User Story 2 - Accept or Reject Passengers (Priority: P2)

As a driver, I review pending join requests and choose to accept or reject each passenger so I can control who travels with me and fill seats intentionally.

**Why this priority**: Decision management creates the user value requested by the driver and directly controls trip occupancy and travel group composition.

**Independent Test**: Can be fully tested by creating multiple pending requests, accepting some, rejecting others, and validating that each passenger receives the correct status.

**Acceptance Scenarios**:

1. **Given** a driver has pending join requests, **When** the driver accepts a request and seats remain, **Then** that passenger status changes to accepted and available seat count decreases by one.
2. **Given** a driver has pending join requests, **When** the driver rejects a request, **Then** that passenger status changes to rejected and available seat count remains unchanged.
3. **Given** no seats are available on a trip, **When** the driver attempts to accept an additional request, **Then** the system prevents acceptance and informs the driver that capacity is full.

---

### User Story 3 - Monitor Confirmed Passengers and Revoke (Priority: P2)

As a driver, I can view the list of accepted and revalidated passengers for my trip and revoke any of them so I can remove a passenger if circumstances change before departure.

**Why this priority**: Once requests are accepted or revalidated, the driver still needs visibility over confirmed passengers and must be able to act if a passenger becomes unreachable or circumstances change. Without revocation, the driver has no recourse after acceptance.

**Independent Test**: Can be fully tested by accepting multiple requests, viewing the confirmed passengers list, revoking one, and verifying the passenger status changes to revoked and the seat count increases.

**Acceptance Scenarios**:

1. **Given** a trip has accepted or revalidated passengers, **When** the driver navigates to the trip request management view, **Then** the driver can see a dedicated list of all confirmed passengers (accepted and revalidated) with their name, profile photo, average rating, and a revoke option.
2. **Given** a driver views a confirmed passenger, **When** the driver revokes them and the trip is still open, **Then** the passenger status changes to revoked and the available seat count increases by one.
3. **Given** a driver views a confirmed passenger, **When** the driver attempts to revoke after the trip departure time has passed, **Then** the system prevents the revocation and informs the driver.

---

### User Story 4 - Revalidate Rejected Requests (Priority: P3)

As a driver, I can revisit a previously rejected passenger request and revalidate it so I can adapt to cancellations, open seats, or changed preferences before departure.

**Why this priority**: Revalidation is a requested flexibility feature that improves seat utilization and reduces manual work when trip circumstances change.

**Independent Test**: Can be fully tested by rejecting a passenger, revalidating that rejected request, and verifying capacity and statuses remain consistent.

**Acceptance Scenarios**:

1. **Given** a passenger request is in rejected status and the trip is still open, **When** the driver revalidates the request and seats are available, **Then** the request status updates to revalidated and seat count decreases by one.
2. **Given** a passenger request is in rejected status and no seats are available, **When** the driver attempts to revalidate the request, **Then** the system blocks the change and keeps the request rejected.

---

## Documentation Context & Lifecycle Impact *(mandatory)*

- **Docs Reviewed**: `docs/overview.md`, `docs/architecture/overview.md`, `docs/architecture/data-model.md`, `docs/api/queries.md`, `docs/api/mutations.md`
- **Lifecycle Stage**: Driver creates trip, opens booking window, manages incoming passenger requests until departure readiness.
- **Cross-Feature Impact**: Trip creation workflow, passenger booking flow, trip seat availability display, and booking status notifications.
- **Docs to Update After Implementation**: `docs/api/mutations.md`, `docs/api/queries.md`, `docs/architecture/data-model.md`, and any booking/trip management user-flow documentation in `docs/` affected by acceptance/reconsideration behavior.

### Edge Cases

- Driver publishes a trip with only one seat left and receives multiple requests in short succession; the first successful acceptance is confirmed and later acceptance attempts are rejected as full.
- Passenger submits a duplicate request for the same trip; system should prevent duplicates and preserve the original request status.
- Driver attempts to modify request decisions after trip departure time has passed; system should prevent changes.
- Accepted or revalidated passenger cancels (status: canceled), reopening a seat; previously rejected passengers remain rejected unless the driver explicitly revalidates them.
- Driver rejects all requests, leaving seats open; trip remains published and can continue receiving new requests until request window closes.
- Trip reaches full capacity; new join requests are blocked until a seat reopens via revocation or passenger cancellation.
- Driver revokes a confirmed passenger (status: revoked), freeing a seat; previously rejected passengers remain rejected unless the driver explicitly revalidates them.
- Driver attempts to revoke a confirmed passenger after departure time; system must block the action.
- A revoked passenger attempts to submit a new join request for the same trip; system must block it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow drivers to publish a trip with required trip details and a defined seat capacity.
- **FR-002**: System MUST allow passengers to submit a join request to a published trip while requests are open and at least one seat is available.
- **FR-003**: System MUST provide drivers with a request management view showing all requests for each trip, grouped by status: pending, accepted, revalidated, rejected, revoked, and canceled.
- **FR-004**: System MUST allow drivers to accept a pending request when at least one seat is available.
- **FR-005**: System MUST allow drivers to reject a pending request without changing seat availability.
- **FR-006**: System MUST prevent the combined count of accepted and revalidated passengers from exceeding trip seat capacity.
- **FR-007**: System MUST allow drivers to revalidate a previously rejected request (status: revalidated) when seats are available and the trip is still open.
- **FR-008**: System MUST preserve an auditable status history for each request decision change. Canonical statuses are: pending, accepted, rejected, revalidated, revoked, canceled.
- **FR-009**: System MUST prevent request decision changes once the trip is no longer open for passenger management (for example, after departure or closure).
- **FR-010**: System MUST notify the affected passenger whenever their request status changes, covering all transitions: accepted, rejected, revalidated, revoked, and canceled.
- **FR-011**: System MUST prevent the same passenger from holding more than one active request for the same trip at the same time. A passenger whose request has been revoked MUST NOT be allowed to submit a new join request for that trip.
- **FR-012**: System MUST resolve concurrent acceptance attempts by confirming the first successful acceptance action and rejecting subsequent acceptance attempts when no seats remain.
- **FR-013**: System MUST block new join requests when a trip has no available seats and provide a clear full-capacity message to the passenger.
- **FR-014**: System MUST allow only the trip owner (driver) to accept, reject, revalidate, or revoke passenger join requests for that trip.
- **FR-015**: System MUST keep previously rejected requests in rejected status when seats reopen, and only change them if the driver manually revalidates.
- **FR-016**: System MUST stop accepting new join requests at the scheduled trip departure time.
- **FR-017**: System MUST provide drivers with a dedicated frontend view listing all currently confirmed passengers (status: accepted or revalidated) for a trip, accessible from the request management screen. Each entry MUST display the passenger's name, profile photo, and average rating.
- **FR-018**: System MUST allow drivers to revoke a previously accepted or revalidated request (status: revoked) while the trip is still open, increasing available seat count by one.
- **FR-019**: System MUST prevent drivers from revoking a confirmed passenger after the trip departure time has passed.

### Key Entities *(include if feature involves data)*

- **Trip**: A driver-published ride offer with route, departure time, seat capacity, and current available seats.
- **Join Request**: A passenger request to join a specific trip, including requester identity, request timestamp, and current decision status. Canonical status state machine: `pending` → `accepted` (driver accepts) | `pending` → `rejected` (driver rejects) | `rejected` → `revalidated` (driver re-enables) | `accepted` → `canceled` (passenger exits) | `accepted` → `revoked` (driver removes) | `revalidated` → `canceled` (passenger exits) | `revalidated` → `revoked` (driver removes).
- **Request Decision Event**: A record of each driver action on a join request, including prior status, new status, actor, and decision timestamp.
- **Driver**: The trip owner responsible for publishing trips and deciding request outcomes.
- **Passenger**: The traveler requesting a seat and receiving decision updates.

### Assumptions & Dependencies

- Trip publication, driver identity, and passenger identity flows already exist and are out of scope for this feature.
- Passenger-initiated cancellation (accepted/revalidated → canceled) is out of scope. The `canceled` status exists in the data model for completeness and is reserved for a future passenger-cancellation feature.
- The feature depends on existing notification channels used for booking-related updates.
- Request management is only available before trip departure or explicit trip closure.
- The join-request submission window closes at the scheduled departure time.
- Capacity refers to confirmed passengers (status: accepted or revalidated) only; rejected, revoked, and canceled requests do not consume seats.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of drivers can publish a trip and process their first passenger request without support.
- **SC-002**: At least 90% of request decisions (accept/reject/revalidate/revoke) are completed by drivers in under 30 seconds per request.
- **SC-003**: 100% of confirmed passenger counts (accepted + revalidated) remain at or below trip seat capacity in production usage.
- **SC-004**: At least 95% of passengers receive a visible request status update within 1 minute of a driver decision.
- **SC-005**: During the first release cycle, at least 80% of trips with open seats reach full capacity before departure when enough requests exist.
