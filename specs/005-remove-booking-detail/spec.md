# Feature Specification: Remove Booking Detail Screen

**Feature Branch**: `005-remove-booking-detail`
**Created**: 2026-04-11
**Status**: Draft
**Input**: User description: "I want to remove the booking detail screen. I want the booking lifecycle to be handled from the /booking page and the /trip detail screen. Remove everything related to the booking detail screen, and when users click on cards in /booking, they should be redirected to the /trip detail screen."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate from Bookings to Trip Detail (Priority: P1)

A passenger who has booked a trip visits the /bookings page to review their bookings. When they click on any booking card, they are taken directly to the associated trip's detail screen where they can view full trip information and manage their booking.

**Why this priority**: This is the core navigation change that replaces the removed booking detail screen. Without this, clicking on a booking card leads nowhere useful.

**Independent Test**: Navigate to /bookings, click any booking card, verify redirection to the correct trip detail page.

**Acceptance Scenarios**:

1. **Given** a logged-in passenger on the /bookings page with at least one booking, **When** they click on a booking card, **Then** they are redirected to the trip detail page corresponding to that booking.
2. **Given** a logged-in passenger on the /bookings page, **When** they click a booking card for a trip with an inactive or unavailable status, **Then** they are still redirected to the trip detail page which handles the state gracefully.
3. **Given** a passenger who has arrived at a trip detail page by clicking a booking card on /bookings, **When** they look at the back navigation, **Then** the back button reads "Mis reservas" and links to /bookings (not to the search results).

---

### User Story 2 - Manage Booking Lifecycle from Trip Detail (Priority: P2)

A passenger who arrives at a trip detail page (via the /bookings redirect or direct URL) can perform all booking-related actions — such as cancelling a booking or viewing booking status — directly on that page without needing a separate booking detail screen.

**Why this priority**: The trip detail screen must absorb the functionality that was previously on the booking detail screen. This ensures no regression in available actions.

**Independent Test**: Access a trip detail page for a trip the user has booked. Verify that booking status and available actions (e.g., cancel) are visible and functional.

**Acceptance Scenarios**:

1. **Given** a logged-in passenger on a trip detail page for a trip they have booked, **When** they view the page, **Then** they see their booking status and any applicable actions.
2. **Given** a logged-in passenger on a trip detail page, **When** they perform a booking action (e.g., cancel), **Then** the action completes successfully and the page reflects the updated state.

---

### User Story 3 - No Broken Links or Dead Ends from Booking Detail Removal (Priority: P3)

Any links, routes, or references to the former booking detail screen are removed or updated so that no user can land on a dead or broken page.

**Why this priority**: Cleanup is important for platform integrity. However, the core navigation (P1 and P2) must work first.

**Independent Test**: Confirm no internal links point to the removed screen and that any former booking detail URL resolves appropriately.

**Acceptance Scenarios**:

1. **Given** any user attempts to access a URL that previously corresponded to the booking detail screen, **When** they navigate there, **Then** they are redirected to the corresponding trip detail page for that booking.
2. **Given** any page in the application, **When** it is reviewed, **Then** no link points to the removed booking detail route.

---

### Edge Cases

- What happens when a booking's associated trip has been deleted or cancelled by the driver? The trip detail page must handle this gracefully with a clear message rather than crashing.
- What if a user has bookings in multiple states (pending, confirmed, cancelled, completed)? All booking card types must redirect correctly to the trip detail page regardless of status.
- What if the /bookings page is empty (no bookings)? The page must show an appropriate empty state with no broken navigation elements.
- What if a user deep-links directly to a former booking detail URL they previously saved? The system must redirect them rather than showing a broken screen.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The booking detail screen and its associated route MUST be removed from the application.
- **FR-002**: All booking cards on the /bookings page MUST redirect users to the corresponding trip detail page when clicked.
- **FR-003**: The trip detail page MUST display the current user's booking status and all booking actions when the user has a booking for that trip. When the user has no booking, the page MUST show the standard booking creation view (existing behavior — no new state required).
- **FR-004**: The trip detail page MUST provide full feature parity with the removed booking detail screen — every action and piece of information that was available there (including cancel booking, booking status display, and any other actions) MUST be accessible from the trip detail page.
- **FR-005**: Any internal navigation links, buttons, or references pointing to the removed booking detail screen MUST be updated or removed.
- **FR-006**: Former booking detail URLs MUST redirect to the corresponding trip detail page for that booking.
- **FR-007**: The /bookings page MUST continue to display all bookings with their status as before — no loss of booking list functionality.

### Key Entities

- **Booking**: A record linking a passenger to a trip, with a lifecycle status (pending, confirmed, cancelled, completed). The booking data model is unchanged; only its UI entry point changes.
- **Trip**: The core entity whose detail page will now serve as the primary screen for booking lifecycle management for passengers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of booking cards on the /bookings page navigate to the correct trip detail page upon click — zero dead ends or broken navigations.
- **SC-002**: All booking lifecycle actions previously available on the booking detail screen are accessible from the trip detail page, with zero functional regression.
- **SC-003**: No broken or unreachable routes related to the removed booking detail screen remain in the application.
- **SC-004**: Users can complete a booking action (e.g., cancel) from the trip detail page in the same number of steps or fewer compared to the old booking detail screen.
- **SC-005**: The /bookings page retains 100% of its pre-existing booking list display and status functionality after the removal.

## Clarifications

### Session 2026-04-11

- Q: Where should former booking detail URLs redirect? → A: Always to the corresponding trip detail page for that booking.
- Q: Which booking lifecycle actions must appear on the trip detail page? → A: Full parity with the removed booking detail screen — all actions and information, not just cancel.
- Q: What does a non-booked user see on the trip detail page? → A: Standard "book this trip" view (existing behavior) — no new booking section or message.

## Assumptions

- The trip detail page already exists and is accessible at a known route (e.g., /trips/[id] or similar).
- Booking data includes a reference to the associated trip, enabling correct redirection from the /bookings page.
- Booking lifecycle actions (cancel, confirm, etc.) are already supported at the data layer and only need to be surfaced in the trip detail UI.
- No permanent deletion of booking data is involved — only the UI screen and its route are removed.
- The /bookings page lists bookings for the currently authenticated passenger only.
- The driver's view (if any) of booking management on the trip detail page is out of scope for this feature and is assumed to already be handled separately.
