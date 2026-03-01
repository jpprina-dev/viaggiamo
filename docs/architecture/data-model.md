# Data Model

> Last updated: 2026-02-28

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
     │                                     │ made by one (as passenger)
     │                                     ▼
     │                               ┌──────────┐
     │                               │   User   │
     │                               └──────────┘
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

A Booking is a seat reservation made by a passenger on a specific trip.

**Key information stored:**

- **Reservation:** number of seats requested, total price (calculated automatically)
- **Status:** pending → confirmed → cancelled (follows a defined lifecycle)
- **Notes:** optional message from the passenger to the driver
- **Timing:** when the booking was made
- **Cancellation details** (if cancelled): who cancelled (the passenger, the driver, or the system), reason for cancellation, time of cancellation

**Business rules:**

- A passenger can have only **one active booking** per trip.
- If a **driver cancels** a passenger's booking, that passenger **cannot re-book** the same trip.
- When a booking is cancelled, the reserved seats are **automatically restored** to the trip's available count.

## Rating

A Rating is a review given after a completed trip. It connects a person giving the review to a person receiving it, within the context of a specific trip.

**Key information stored:**

- **Score:** 1 to 5 stars
- **Comment:** optional written feedback
- **Role:** whether the rated person was acting as a driver or a passenger on that trip
- **People:** the user who gave the rating and the user who received it

Ratings feed into the **average driver rating** displayed on user profiles, helping passengers choose trustworthy drivers.
