# API Reference

> Last updated: 2026-02-28

Viaggiamo exposes a **GraphQL-only API** — there are no REST endpoints. Every request flows through a single endpoint:

```
POST /graphql
```

## GraphiQL IDE

An interactive GraphiQL IDE is available during development at:

```
http://localhost:8000/graphql
```

Open it in your browser to explore the schema, run queries, and inspect documentation.

## Making Requests

Send a `POST` request to `/graphql` with `Content-Type: application/json` and a JSON body containing your GraphQL query:

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ health }"}'
```

For authenticated requests, include the `Authorization` header with a Bearer token:

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "{ me { id email username } }"}'
```

## Documentation

| Document | Description |
|----------|-------------|
| [Authentication](authentication.md) | Registration, login, OAuth, and token usage |
| [Queries](queries.md) | All read operations |
| [Mutations](mutations.md) | All write operations |

## Operations Summary

The API exposes 30 operations (16 queries and 14 mutations):

| Operation | Type | Auth Required |
|-----------|------|---------------|
| `register` | Mutation | No |
| `login` | Mutation | No |
| `loginWithOauth` | Mutation | No |
| `updateUser` | Mutation | Yes |
| `me` | Query | Yes |
| `user` | Query | No |
| `createVehicle` | Mutation | Yes |
| `updateVehicle` | Mutation | Yes |
| `deleteVehicle` | Mutation | Yes |
| `myVehicles` | Query | Yes |
| `vehicle` | Query | No |
| `createTrip` | Mutation | Yes |
| `updateTrip` | Mutation | Yes |
| `deleteTrip` | Mutation | Yes |
| `trips` | Query | No |
| `trip` | Query | No |
| `myTrips` | Query | Yes |
| `tripVehicle` | Query | No |
| `searchTrips` | Query | No |
| `cityOrigins` | Query | No |
| `cityDestinations` | Query | No |
| `createBooking` | Mutation | Yes |
| `updateBooking` | Mutation | Yes |
| `cancelBooking` | Mutation | Yes |
| `cancelPassengerBooking` | Mutation | Yes |
| `myBookings` | Query | Yes |
| `booking` | Query | Yes |
| `tripBookings` | Query | Yes |
| `hasDriverCancelledBooking` | Query | Yes |
| `health` | Query | No |
