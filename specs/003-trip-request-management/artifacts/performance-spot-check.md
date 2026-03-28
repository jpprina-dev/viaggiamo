# Performance Spot-check

Date: 2026-03-02

- Target operations: `createBooking`, `updateBooking` (driver decision flow)
- Environment: local development
- Status: **completed (focused backend spot-check)**

## Notes

- Command: `uv run pytest tests/test_graphql/test_booking_integration.py --durations=10 -q`
- Sample durations:
  - `createBooking` focused call path: ~`0.03s`
  - `updateBooking` focused call path: ~`0.01s`
- Full-stack end-user latency profiling is still pending due unrelated frontend baseline build issues.
