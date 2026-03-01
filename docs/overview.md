# Project Overview

> Last updated: 2026-02-28

## What is Viaggiamo?

Viaggiamo is a carpooling platform that connects **drivers** offering rides with **passengers** looking for shared transportation. It's designed as a minimum viable product (MVP) to validate the core carpooling experience: finding a ride, booking a seat, and rating the experience.

## Who is it for?

- **Drivers** — People with a vehicle who want to share their commute or long-distance trips, offset fuel costs, and meet fellow travelers.
- **Passengers** — People looking for affordable, convenient rides between cities who prefer a shared travel experience over buses or trains.

## Core Features

### Trip Management
Drivers create trips by specifying an origin, destination, departure time, price per seat, and the vehicle they'll use. Passengers browse and search for trips that match their route and schedule.

### Search & Discovery
A search engine with fuzzy text matching lets passengers find trips even with approximate city names. Results are ranked by relevance, considering factors like date proximity, price, and text similarity.

### Booking System
Passengers book seats on a trip. The system tracks available seats, prevents duplicate bookings, and supports cancellation by both passengers and drivers — with seat restoration on cancellation.

### Vehicle Registration
Drivers register their vehicles with details like make, model, year, license plate, and seat count. Vehicles can be reused across multiple trips.

### Ratings & Reviews
After a trip, both drivers and passengers can rate each other on a 1–5 star scale with optional comments. Average ratings are displayed on user profiles to build trust.

### Authentication
Users register with email/password or sign in with Google OAuth. All authenticated actions use JWT (JSON Web Token) for secure, stateless session management.

## Tech Stack at a Glance

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React) with TypeScript and Tailwind CSS |
| Backend | FastAPI (Python) with Strawberry GraphQL |
| Database | PostgreSQL with full-text search |
| Cache | Redis |
| Infrastructure | Docker Compose for local development |
| Package Management | `uv` (Python), `pnpm` (Node.js) |

The frontend communicates with the backend exclusively through **GraphQL** — a query language that lets clients request exactly the data they need in a single request.

## Repository Structure

```
viaggiamo/
├── backend/          # FastAPI + GraphQL API
├── frontend/         # Next.js web application
├── infra/            # Database initialization scripts
├── docs/             # This documentation
├── scripts/          # Utility scripts
└── docker-compose.yml
```

## Next Steps

- [Set up your development environment](setup/prerequisites.md)
- [Explore the API](api/README.md)
- [Understand the architecture](architecture/overview.md)
