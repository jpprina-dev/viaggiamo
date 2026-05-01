# Data Model

> Last updated: 2026-03-28

This document describes the core data entities in Viaggiamo and how they relate to each other. It is written for a non-technical audience — no SQL or code is included.

## Entity Relationship Overview

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     ├──── owns many ──────────────▶ ┌───────────┐
     │                               │  Vehicle   │
     │                               └─────┬─────┘
     │                                     │
     │  creates many (as driver)           │ used by one
     │                                     │
     ▼                                     ▼
┌──────────┐◀─────── uses one ───── ┌──────────┐
│   Trip   │                        │  Vehicle  │
└────┬─────┘                        └──────────┘
     │
     ├──── has many ───────────────▶ ┌───────────┐
     │                               │  Booking   │
     │                               └─────┬─────┘
     │                                     │
     │                                     ├── made by one (as passenger) ──▶ User
     │                                     │
     │                                     └── has many ──▶ ┌──────────────────────┐
     │                                                       │ RequestDecisionEvent │
     │                                                       └──────────────────────┘
     │
     └──── has many ───────────────▶ ┌───────────┐
                                     │  Rating    │
                                     └───────────┘
                                       connects a
                                     rater User to
                                     a rated User
                                     within a Trip
```

**Summary of relationships:**

- A **User** owns many **Vehicles** (one-to-many)
- A **User** (as driver) creates many **Trips** (one-to-many)
- A **Trip** uses one **Vehicle** (many-to-one)
- A **User** (as passenger) makes many **Bookings** (one-to-many)
- A **Trip** has many **Bookings** (one-to-many)
- A **Booking** has many **Request Decision Events** (one-to-many) — audit trail of all status changes
- A **Trip** has many **Ratings** (one-to-many)
- A **Rating** connects a rater to a rated person within the context of a specific trip

## User

A User represents a registered person on the platform. Every user has a unique email address and a unique username that identifies them.

**Key information stored:**

- **Identity:** email, username, first name, last name
- **Contact:** phone number
- **Profile:** profile picture, short biography
- **Account status:** active, suspended, or under review
- **Preferences:** trip preferences stored as a flexible set of options (e.g., smoking allowed, pets allowed, music preference)
- **Authentication:** supports both email/password sign-up and Google OAuth sign-in
- **Reputation:** an average driver rating computed automatically from ratings received on completed trips

## Vehicle

A Vehicle is a car registered by a user for use in carpooling trips.

**Key information stored:**

- **Car details:** make (e.g., "Toyota"), model (e.g., "Corolla"), year, color
- **Identification:** license plate number (unique across the platform)
- **Capacity:** number of available seats
- **Status:** whether the vehicle is currently active
- **Legal:** an acknowledgment that the vehicle meets legal requirements for carpooling

**Deletion behavior:** If a vehicle has been used in any trip, it is soft-deleted (marked as inactive but kept in the system for historical records). If it has never been used, it is permanently removed.

## Trip

A Trip is a ride offered by a driver from one city to another.

**Key information stored:**

- **Route:** origin city, destination city
- **Schedule:** departure date and time
- **Capacity:** total seats in the vehicle, currently available seats
- **Pricing:** price per seat
- **Details:** free-text description, trip preferences
- **Status:** active flag, completed flag
- **Legal:** an acknowledgment of legal compliance
- **Links:** the driver who created it, the vehicle being used

**Implicit state machine:**

| Active | Completed | Meaning |
|--------|-----------|---------|
| Yes | No | **Listed** — visible and bookable |
| No | No | **Cancelled** — removed before departure |
| No | Yes | **Completed** — the trip took place |

## Booking

A Booking is the passenger request and seat-allocation record for a specific trip.

**Key information stored:**

- **Reservation:** number of seats requested, total price (calculated automatically)
- **Status:** one of six canonical values (see state machine below)
- **Notes:** optional message from the passenger to the driver
- **Timing:** when the booking was made

**Status state machine:**

```
pending ──▶ accepted    (driver accepts; −1 seat)
pending ──▶ rejected    (driver rejects; 0 seats)
pending ──▶ canceled    (passenger withdraws; 0 seats — disappears from driver view)

rejected ──▶ revalidated  (driver re-enables; −1 seat)

accepted ──▶ revoked    (driver removes confirmed passenger; +1 seat)
accepted ──▶ canceled   (passenger exits; +1 seat — out of scope for this feature)

revalidated ──▶ revoked   (driver removes revalidated passenger; +1 seat)
revalidated ──▶ canceled  (passenger exits; +1 seat — out of scope for this feature)
```

Terminal states: `canceled` and `revoked` have no outgoing transitions.

**Seat-holding statuses:** `accepted` and `revalidated` both consume a seat. All other statuses do not.

**Business rules:**

- A passenger can have only **one active request** per trip. A `canceled` booking does not block a new request from the same passenger; a `revoked` booking does.
- Seats are consumed when a request transitions **into** `accepted` or `revalidated`.
- Seats are freed when a request transitions **out of** `accepted` or `revalidated` (to `revoked` or `canceled`).
- If a **driver revokes** a passenger (`revoked` status), that passenger **cannot re-join** the same trip.
- Passenger-withdrawn requests (`canceled`) are permanently hidden from the driver's request management view.

## Request Decision Event

A Request Decision Event is an audit record created each time a booking status changes.

**Key information stored:**

- **Booking:** which booking was changed
- **Prior status:** the status before the change
- **New status:** the status after the change
- **Actor:** which user triggered the change
- **Timestamp:** when the change occurred

All driver decisions (accept, reject, revalidate, revoke) and passenger withdrawals (cancel) generate a decision event, providing a complete, immutable history of every request lifecycle.

## Rating

A Rating is a review given after a completed trip. It connects a person giving the review to a person receiving it, within the context of a specific trip.

**Key information stored:**

- **Score:** 1 to 5 stars
- **Comment:** optional written feedback
- **Role:** whether the rated person was acting as a driver or a passenger on that trip
- **People:** the user who gave the rating and the user who received it

Ratings feed into the **average driver rating** displayed on user profiles, helping passengers choose trustworthy drivers.
