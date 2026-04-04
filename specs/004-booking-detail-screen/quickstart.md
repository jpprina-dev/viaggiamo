# Quickstart: Booking Detail Screen Development

**Feature**: 004-booking-detail-screen | **Branch**: `004-booking-detail-screen`

---

## Prerequisites

- Docker Desktop running (backend, frontend, postgres, redis via `docker-compose up`)
- Node.js 18+ and pnpm installed
- Python 3.11 and `uv` installed

---

## Start the stack

```bash
# From repo root — starts all services
docker-compose up -d

# Or start backend and frontend separately for hot-reload:

# Backend (from repo root)
cd backend
uv sync --python 3.11
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from repo root)
cd frontend
pnpm install
pnpm dev
```

Services:
- GraphQL API: `http://localhost:8000/graphql`
- GraphQL Playground: `http://localhost:8000/graphql` (interactive)
- Frontend: `http://localhost:3000`

---

## Run backend tests

```bash
cd backend
uv run pytest                            # all tests
uv run pytest tests/unit/               # unit tests only
uv run pytest tests/test_graphql/       # integration tests only
uv run pytest -k "booking"              # filter by name
```

---

## Run frontend tests

```bash
cd frontend
pnpm test                               # watch mode
pnpm test --run                         # single pass (CI)
pnpm test --run src/features/bookings   # bookings feature only
```

---

## Apply DB migration (if adding Rating model)

```bash
cd backend

# Generate a new migration (fill in the message)
uv run alembic revision --autogenerate -m "004_rating_model"

# Review the generated file in alembic/versions/
# Then apply:
uv run alembic upgrade head
```

---

## Feature development order

Work in this order to enable independent testing at each step:

1. **`getAllowedActions` utility + unit tests** — pure function, no dependencies
2. **`BookingStatusBadge`** component + smoke test
3. **`useBookingDetail` hook** — polling, role derivation, `connectionError`
4. **`BookingActionPanel` + `ActionConfirmModal`** + smoke tests
5. **Booking detail page** — `app/(protected)/bookings/[id]/page.tsx`
6. **`useUpdateBookingStatus` hook** — mutation + error mapping
7. **Passenger tab filter fix** — narrow to `pending + accepted`
8. **Driver tab inline actions** — reuse `BookingActionPanel` in `DriverTripCard`
9. **`NotificationService` interface** + `useBookingNotifications` hook
10. **Rating backend** — `Rating` model + Alembic migration + `submitRating` mutation
11. **`RatingPrompt`** component + history tab integration
12. **End-to-end: real-time sync** — open two sessions, verify 5s polling

---

## Key files to know

| File | Role |
|------|------|
| `frontend/src/features/bookings/utils/getAllowedActions.ts` | Pure action-derivation function |
| `frontend/src/features/bookings/hooks/useBookingDetail.ts` | Polling hook |
| `frontend/src/features/bookings/hooks/useUpdateBookingStatus.ts` | Mutation hook |
| `frontend/src/features/bookings/components/BookingActionPanel.tsx` | Action buttons (reused on list + detail) |
| `frontend/src/features/bookings/components/ActionConfirmModal.tsx` | Confirmation modal |
| `frontend/src/features/bookings/components/BookingStatusBadge.tsx` | Status badge |
| `frontend/src/app/(protected)/bookings/[id]/page.tsx` | Booking detail page |
| `frontend/src/lib/notifications/NotificationService.ts` | Injectable interface |
| `frontend/src/features/bookings/hooks/useBookingNotifications.ts` | Notification hook |
| `frontend/src/features/ratings/components/RatingPrompt.tsx` | Rating UI |
| `backend/app/graphql/resolvers/rating.py` | submitRating resolver (new) |
| `backend/alembic/versions/004_rating_model.py` | Rating DB migration (new) |

---

## GraphQL playground — test queries

```graphql
# Get a booking detail (replace 1 with a real booking ID)
query {
  booking(bookingId: 1) {
    id status seatsRequested
    trip { origin destination driverId driver { name lastName } }
    passenger { id name lastName }
  }
}

# Update booking status
mutation {
  updateBookingStatus(bookingId: 1, status: accepted) {
    id status
  }
}

# Submit a rating
mutation {
  submitRating(bookingId: 1, score: 5, comment: "Great driver!") {
    id score bookingId
  }
}
```

---

## Lint and type-check

```bash
# Backend
cd backend && uv run ruff check . && uv run mypy .

# Frontend
cd frontend && pnpm build   # includes tsc --noEmit
```
