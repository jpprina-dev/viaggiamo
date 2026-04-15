# Feature Specification: Booking Detail Screen with Role-Gated Actions

**Feature Branch**: `004-booking-detail-screen`
**Created**: 2026-04-02
**Status**: Draft
**Input**: User description: "Build a booking detail screen that shows the current booking status and renders only the actions available to the current user's role, keeping state in sync in real time."

---

## Clarifications

### Session 2026-04-02

- Q: How should real-time status sync be implemented — push (WebSocket/SSE), polling, or on-focus re-fetch? → A: Push-based (WebSocket or SSE) for in-app real-time sync. Push notifications (mobile/email) are out of scope.
- Q: How should server-side action rejections (conflict, forbidden) be surfaced to the user? → A: Inline error message displayed directly on the screen near the action buttons, alongside the updated status.
- Q: What form should the confirmation step before each action take? → A: Modal dialog with the action description and Confirm / Cancel buttons.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Passenger Views Booking and Takes Action (Priority: P1)

A passenger navigates to their booking detail page and sees the current status of their seat request. If the booking is still pending, they see a "Cancel request" button. If it has been accepted, they see a "Cancel booking" button. If the booking is in a terminal state (rejected, cancelled, or revoked), no action buttons are shown and the status is clearly communicated.

**Why this priority**: This is the core screen for the passenger — the primary actor who initiates bookings. Without it, passengers have no way to track or act on their own requests.

**Independent Test**: A passenger can open their booking detail, read the status, and — when applicable — cancel their request or booking without navigating away. A terminal-state booking can be viewed and shows a clear final status with no action buttons.

**Acceptance Scenarios**:

1. **Given** a passenger has a pending booking, **When** they open the booking detail, **Then** they see the status "Pending" and a single "Cancel request" button.
2. **Given** a passenger has an accepted booking, **When** they open the booking detail, **Then** they see the status "Accepted" and a "Cancel booking" button.
3. **Given** a passenger taps "Cancel request" or "Cancel booking" and confirms, **Then** the status updates immediately and the action button disappears.
4. **Given** a passenger has a rejected, cancelled, or revoked booking, **When** they open the booking detail, **Then** they see the terminal status with no action buttons.
5. **Given** a passenger cancels a pending booking, **When** they return to their active bookings list, **Then** that booking no longer appears in the list.

---

### User Story 2 — Driver Reviews a Pending Booking and Responds (Priority: P1)

A driver opens the booking detail for a passenger who has requested a seat on their trip. They see the request information and the current status. Because the booking is pending, they see two action buttons: "Accept" and "Reject". After acting, the status updates immediately and the buttons update to reflect the new state.

**Why this priority**: Drivers cannot manage seat allocation without this screen. Accepting and rejecting requests is their primary booking-related task.

**Independent Test**: A driver can view a pending booking, tap "Accept" or "Reject", see the status update, and confirm the action buttons are gone — all without any page reload.

**Acceptance Scenarios**:

1. **Given** a driver opens a pending booking on their trip, **When** the screen loads, **Then** they see the passenger name, the status "Pending", and "Accept" and "Reject" buttons.
2. **Given** a driver taps "Accept" and confirms, **Then** the status changes to "Accepted" and only the "Revoke" button remains.
3. **Given** a driver taps "Reject" and confirms, **Then** the status changes to "Rejected" and no action buttons are shown.
4. **Given** a driver views an accepted booking, **When** the screen loads, **Then** only the "Revoke" button is shown.
5. **Given** a driver taps "Revoke" and confirms, **Then** the status changes to "Revoked" and no action buttons are shown.

---

### User Story 3 — Real-Time Status Sync for Both Actors (Priority: P2)

If both the driver and the passenger have the booking detail screen open at the same time, a status change by one actor is reflected on the other actor's screen without requiring a manual page refresh.

**Why this priority**: Without real-time sync, actors may act on stale data (e.g., a passenger tries to cancel a booking the driver already rejected). Real-time updates prevent confusion and redundant actions.

**Independent Test**: Open the same booking in two browser sessions — one authenticated as the driver and one as the passenger. Perform a status change in one session; within a few seconds the other session's status and available buttons update automatically.

**Acceptance Scenarios**:

1. **Given** both actors have the booking detail open, **When** the driver accepts the booking, **Then** the passenger's screen updates from "Pending" to "Accepted" and their action button changes from "Cancel request" to "Cancel booking" within 5 seconds.
2. **Given** both actors have the booking detail open, **When** the passenger cancels the booking, **Then** the driver's screen reflects the terminal state and removes action buttons within 5 seconds.
3. **Given** the push connection is temporarily unavailable, **When** the user views the screen, **Then** a subtle indicator shows that the status may be stale, and refreshing the page shows the latest data.

---

### User Story 4 — Access Denied for Unrelated Users (Priority: P3)

A user who is neither the passenger nor the driver of a booking cannot open that booking's detail screen. Attempting to do so shows an appropriate error or redirects them away.

**Why this priority**: Privacy and access control are required before production use but do not block the core feature.

**Independent Test**: Log in as a user unrelated to a known booking and attempt to navigate to its detail URL. Verify the screen is not shown and no booking data is exposed.

**Acceptance Scenarios**:

1. **Given** a user is not the passenger or driver for a booking, **When** they navigate to the booking detail URL, **Then** they see an access-denied message and no booking information is displayed.
2. **Given** an unauthenticated user attempts to access any booking detail URL, **When** they navigate to it, **Then** they are redirected to the login screen.

---

### Edge Cases

- What if both actors act simultaneously? The first action to reach the server wins; the other actor sees the updated status and a brief error notification if their action was rejected.
- What if the booking transitions to a terminal state while the user is viewing it? Action buttons disappear and the terminal status is displayed in real time without requiring a reload.
- What if the booking ID in the URL does not exist? The screen shows a "Booking not found" message.
- What if an action fails due to a network error? The screen displays an error message, does not change the displayed status, and re-enables the action buttons so the user can retry.
- What if the user opens the screen while offline? No action buttons are enabled and an offline indicator is shown.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The screen MUST display the booking's current status using clear, human-readable labels: "Pending", "Accepted", "Rejected", "Cancelled", "Revoked".
- **FR-002**: The screen MUST show only the action buttons valid for the authenticated user's role and the current booking status:
  - Passenger + `pending` → "Cancel request"
  - Driver + `pending` → "Accept", "Reject"
  - Passenger + `accepted` → "Cancel booking"
  - Driver + `accepted` → "Revoke"
  - Any role + `rejected`, `cancelled`, or `revoked` → no action buttons
- **FR-003**: Every action button MUST require confirmation via a modal dialog (blocking overlay) that describes the action and provides Confirm and Cancel controls before the status change is submitted.
- **FR-004**: Action buttons MUST be disabled while a status change is in progress to prevent duplicate submissions.
- **FR-005**: After a successful status change, the displayed status and available action buttons MUST update immediately without a full page reload.
- **FR-006**: The booking status MUST reflect the other actor's changes within 5 seconds without the user manually refreshing. The preferred mechanism is a push-based connection (WebSocket or SSE); polling at ≤5-second intervals is acceptable as an interim implementation until push infrastructure exists. Push notifications (mobile/email) are explicitly out of scope.
- **FR-007**: When a passenger cancels a pending or accepted booking, the booking MUST no longer appear in their active bookings list after navigating away.
- **FR-008**: If a status change fails (network error or server-side conflict/forbidden), the screen MUST display a clear inline error message directly on the screen near the action area, restore the action buttons to their pre-action state, and show the current booking status as returned by the server.
- **FR-009**: Users who are neither the passenger nor the driver for a booking MUST be denied access to the detail screen; no booking data may be exposed to them.
- **FR-010**: Unauthenticated users MUST be redirected to the login screen when attempting to access any booking detail.

### Key Entities

- **Booking**: A passenger's seat request on a trip. Carries a status (`pending`, `accepted`, `rejected`, `cancelled`, `revoked`), a reference to the passenger, and a reference to the trip.
- **Trip**: Contains a reference to the driver. Used to determine whether the authenticated user is the driver of the trip associated with the booking.
- **Actor Role**: Derived at display time from the authenticated user — `passenger` if the user owns the booking, `driver` if the user owns the trip. Determines which actions are rendered.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can view the booking status and identify their available actions within 3 seconds of the screen loading.
- **SC-002**: After performing an action, the updated status appears on screen within 1 second.
- **SC-003**: Status changes made by the other actor are reflected on the current user's screen within 5 seconds without a manual refresh.
- **SC-004**: Zero cases where a user is shown an action button that the server would reject due to a role or state mismatch — the client-side action set is always consistent with the server-side state machine.
- **SC-005**: 100% of attempts by unrelated or unauthenticated users to access a booking detail result in an access-denied outcome with no booking data exposed.

---

## Assumptions

- The authenticated user's identity is available on every request via the existing session mechanism. No new authentication is introduced.
- A booking has exactly one passenger and one driver (via the trip). No admin or third-party roles are in scope for this feature.
- Real-time sync targets a push-based connection (WebSocket or SSE) as the long-term mechanism. Polling at ≤5-second intervals is the interim implementation (push infrastructure is not yet available in the stack). Push notifications (mobile/email) are out of scope.
- Confirmation before actions (Accept, Reject, Cancel, Revoke) is a modal dialog with Confirm and Cancel controls — single-step, no multi-step flow required.
- The booking detail screen is reached by navigating from an existing list view (e.g., active bookings for passengers, trip management for drivers). Direct URL access (deep links) is also supported.
- Both mobile and desktop viewports must be supported; responsive layout is expected.
