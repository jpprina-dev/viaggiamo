# Testing Guide

> Last updated: 2026-02-28

## Backend Testing

All commands run from the `backend/` directory.

| Task | Command |
|---|---|
| Run all tests | `uv run pytest` |
| Run with coverage | `uv run pytest --cov=app` |
| Run a single test | `uv run pytest tests/test_file.py::test_name -v` |
| Run only unit tests | `uv run pytest -m unit` |
| Skip slow tests | `uv run pytest -m "not slow"` |

### Conventions

- **File naming:** `test_*.py` or `*_test.py`.
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`.
- **Async tests:** use `pytest-asyncio` with `asyncio_mode = "auto"`.

## Frontend Verification

| Task | Command |
|---|---|
| Type check (includes `tsc`) | `pnpm build` |
| Lint | `pnpm lint` |
| Type check only | `pnpm type-check` |

## What to Test

Match the scope of your tests to the kind of change you're making:

| Change Type | Required Tests |
|---|---|
| New GraphQL resolver | Unit test + integration test + contract test (schema shape + error responses) |
| New service or model | At least one unit test |
| UI component | Smoke render test |
| User-facing flow (auth, booking, trip creation) | End-to-end coverage |
| Bug fix | Regression test that reproduces the bug |

## TDD Cycle — Red-Green-Refactor

1. **Red** — Write a failing test first.
2. **Green** — Write the minimum code to make it pass.
3. **Refactor** — Clean up while keeping tests green.

## Coverage Rules

- PRs **MUST NOT** decrease overall test coverage.
- Generate an HTML coverage report:

```bash
uv run pytest --cov=app --cov-report=html
```

- Open `htmlcov/index.html` in your browser to review the report.
