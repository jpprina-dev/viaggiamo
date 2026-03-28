# Feature Specification: Passenger Seat Booking & Status Tracking

**Feature Branch**: `004-passenger-booking`
**Created**: 2026-03-14
**Status**: Draft
**Input**: User description: "As a passenger, I want to request a seat and track my booking status in my bookings tab. I need to know if I have been accepted or rejected so I can plan my commute, and I expect the trip to stay visible until it is completed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request a Seat on a Trip (Priority: P1)

A passenger browses available trips and requests a seat on one that fits their commute. After submitting the request, the booking appears immediately in their "Bookings" tab with a pending status so they know their request was received.

**Why this priority**: Without the ability to request a seat, the entire feature has no value. This is the entry point for the whole booking workflow.

**Independent Test**: Can be fully tested by submitting a seat request from the trip listing and verifying the booking appears in the Bookings tab as "Pending". Delivers value as a standalone MVP that proves the request flow works end to end.

**Acceptance Scenarios**:

1. **Given** a passenger is viewing an available trip with open seats, **When** they submit a seat request, **Then** a booking record is created with status "Pending" and the trip appears in their Bookings tab immediately.
2. **Given** a passenger has already submitted a request for a trip, **When** they view that same trip again, **Then** the request button is replaced with a status indicator showing "Pending".
3. **Given** a trip has no available seats remaining, **When** a passenger views that trip, **Then** the request option is not shown or is unavailable, making it impossible to submit a request.

---

### User Story 2 - Track Booking Status (Priority: P2)

A passenger visits their Bookings tab to check whether their seat request has been accepted or rejected by the driver. The status is clearly displayed for each booking so the passenger can plan their commute accordingly.

**Why this priority**: Knowing the outcome of a request is critical for commute planning. Without status visibility, passengers cannot act on driver decisions.

**Independent Test**: Can be fully tested by simulating a driver accepting or rejecting a booking and verifying the status change is reflected in the passenger's Bookings tab.

**Acceptance Scenarios**:

1. **Given** a driver has accepted a passenger's seat request, **When** the passenger opens their Bookings tab, **Then** the booking is shown with status "Accepted" and the trip details are visible.
2. **Given** a driver has rejected a passenger's seat request, **When** the passenger opens their Bookings tab, **Then** the booking is shown with status "Rejected" with a clear visual indicator distinguishing it from accepted or pending bookings.
3. **Given** a passenger has multiple bookings in different states, **When** they view the Bookings tab, **Then** all bookings are listed and each displays its individual status clearly.

---

### User Story 3 - Trip Remains Visible Until Completed (Priority: P3)

An accepted booking remains visible in the passenger's Bookings tab throughout the entire lifecycle of the trip — from acceptance through departure and until the trip is marked as completed — so the passenger always has access to trip details when needed.

**Why this priority**: Passengers need trip details during the journey itself (departure city, time, driver info). Premature disappearance of an accepted booking would break trust and usability.

**Independent Test**: Can be fully tested by accepting a booking, simulating the trip progressing through its lifecycle states, and verifying the booking remains visible at each stage until the trip is marked completed.

**Acceptance Scenarios**:

1. **Given** a passenger has an accepted booking, **When** the trip's departure time has passed but the trip has not been marked completed, **Then** the booking remains visible in the Bookings tab.
2. **Given** a trip has been marked as completed by the driver, **When** the passenger views their Bookings tab, **Then** the booking may be moved to a completed/history section but is not deleted or hidden from the passenger.
3. **Given** a passenger has a rejected booking, **When** they view their Bookings tab, **Then** the rejected booking remains visible in the Solicitudes tab (not filtered out even if the trip becomes inactive) so the passenger is always aware of the outcome.

---

### Edge Cases

- **Passenger cancels a pending request**: The booking record is deleted entirely. The passenger returns to the pre-request state and can re-request the same trip if seats are still available.
- **Driver cancels an accepted trip**: The booking is deleted entirely. An in-app notification (e.g., banner or toast in the Bookings tab) informs the passenger that the trip was cancelled by the driver.
- **Driver never responds (trip completes)**: When a trip is marked as completed, any remaining Pending bookings are automatically moved to "Rejected" status and the passenger receives an in-app notification.
- What happens if a passenger requests a seat and the driver accepts them, but the trip is already full due to a concurrent acceptance?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a passenger to submit a seat request for any available trip that has open seats.
- **FR-002**: System MUST create a booking record with status "Pending" immediately upon a passenger submitting a seat request.
- **FR-003**: System MUST display all of a passenger's bookings (Pending, Accepted, Rejected) in a dedicated "Bookings" tab accessible from the main navigation.
- **FR-004**: System MUST reflect status changes (Accepted / Rejected) in the passenger's Bookings tab requiring the passenger to manually refresh. The passenger triggers an update by pulling to refresh or tapping a refresh control.
- **FR-005**: System MUST keep an accepted booking visible in the Bookings tab until the associated trip is marked as completed.
- **FR-006**: System MUST prevent a passenger from submitting duplicate seat requests for the same trip.
- **FR-009**: System MUST allow a passenger to cancel a pending booking request; cancellation deletes the booking record entirely, returning the passenger to the pre-request state with the ability to re-request if seats remain available.
- **FR-010**: When a driver cancels a trip, the system MUST delete all associated accepted bookings and display an in-app notification to each affected passenger.
- **FR-011**: When a trip is marked as completed, the system MUST automatically move any remaining Pending bookings for that trip to "Rejected" status and notify the affected passengers in-app.
- **FR-007**: System MUST hide or disable the seat request option for trips that have no available seats remaining, making the action unavailable before the passenger can attempt it.
- **FR-008**: System MUST display the booking status with a clear visual distinction between Pending, Accepted, and Rejected states.
- **FR-012**: The active bookings view (Solicitudes tab) MUST only show bookings whose associated trip is active (`trip.is_active == true`), except rejected bookings which MUST remain visible regardless of trip state so passengers are always aware of the outcome (satisfies US3 scenario 3).
- **FR-013**: Rejected bookings MUST be displayed as read-only for passengers. If a driver resets a rejected booking back to Pending, the passenger MUST be notified in-app and presented with a "Keep" (stay Pending) or "Cancel" action. The `wasResetFromRejected` flag on `BookingType` indicates this state.
- **FR-014**: A `myBookingHistory` GraphQL query MUST return the passenger's accepted bookings for trips that are no longer active (`status == 'accepted' AND trip.is_active == false`), powering the History tab passenger view.
- **FR-015**: A `myDriverTripHistory` GraphQL query MUST return the driver's inactive trips together with the list of passengers who had accepted bookings, powering the History tab driver view.

### Key Entities

- **Booking**: Represents a passenger's seat request for a specific trip. Key attributes: status (Pending / Accepted / Rejected / Cancelled), associated trip, associated passenger, request timestamp, `cancelled_by` (passenger/driver/system), `wasResetFromRejected` (computed: true when current status is Pending and the most recent `RequestDecisionEvent` transitioned from Rejected → Pending).
- **Trip**: The journey offered by a driver. Relevant attributes for this feature: available seats, departure time, completion status.
- **Passenger**: The user requesting a seat. Has a collection of bookings visible in their Bookings tab.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Passengers can submit a seat request in under 30 seconds from the trip listing screen.
- **SC-002**: Booking status changes (Accept / Reject by driver) are reflected in the passenger's Bookings tab upon manual refresh by the passenger.
- **SC-003**: 100% of accepted bookings remain visible in the Bookings tab until the trip is marked as completed.
- **SC-004**: Passengers can distinguish between Pending, Accepted, and Rejected bookings at a glance without reading additional detail screens.
- **SC-005**: Zero cases where a passenger is accepted on a fully-booked trip.

## Clarifications

### Session 2026-03-15

- Q: Can a passenger cancel a pending booking request before the driver responds? → A: Yes — booking is deleted entirely; passenger can re-request if seats remain available.
- Q: What happens to a passenger's accepted booking when the driver cancels the trip? → A: Booking is deleted; an in-app notification informs the passenger the trip was cancelled.
- Q: What mechanism should FR-004 use to reflect status changes? → A: Manual refresh — the passenger pulls to refresh or taps a refresh control to get the latest status.
- Q: What happens to a Pending booking if the driver never responds and the trip completes? → A: Automatically moved to Rejected when the trip is marked completed; passenger notified in-app.

## Assumptions

- The "Bookings" tab already exists or will be introduced as part of this feature as a dedicated section in the passenger's main navigation.
- Drivers have a separate mechanism to view and respond to seat requests (Accept / Reject); that driver-side flow is out of scope for this feature.
- A "completed" trip state is managed by the driver and already exists or will be addressed in the trip lifecycle feature.
- Push/email notifications for status changes are out of scope; only in-app Bookings tab visibility is required.
- A passenger can only hold one active booking per trip at a time.
