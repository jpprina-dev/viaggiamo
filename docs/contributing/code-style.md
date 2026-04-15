# Code Style & Quality Guide

> Last updated: 2026-02-28

## Backend (Python)

| Tool | Command | Purpose |
|---|---|---|
| Ruff | `uv run ruff check .` | Linter |
| Ruff (auto-fix) | `uv run ruff check . --fix` | Fix auto-fixable issues |
| mypy | `uv run mypy .` | Type checker (strict mode) |
| Black | `uv run black .` | Formatter (line length 88) |
| isort | `uv run isort .` | Import sorting (black-compatible profile) |

### Rules

- Functions must be **40 lines or fewer**.
- No dead code — remove unused imports, variables, and functions.
- No magic values — use **named constants** or **enums**.
- Descriptive naming — prefer clarity over brevity.
- No `Any` type without explicit justification in a comment.

## Frontend (TypeScript)

| Tool | Command | Purpose |
|---|---|---|
| TypeScript | `tsc --noEmit` | Type check (strict mode) |
| ESLint | `pnpm lint` | Lint with Next.js config |
| Prettier | `pnpm prettier --write .` | Format with Tailwind plugin |

### Rules

- **No `any` type** — use `unknown` and narrow with type guards.
- **Styling:** Tailwind CSS only. Use components from `src/components/ui/`; do not create ad-hoc inline styles that duplicate existing components.
- **Forms:** React Hook Form + Zod. Error messages must be user-readable, not raw API strings.
- **Accessibility:** All interactive elements MUST have accessible labels (`aria-label` or visible text). WCAG 2.1 AA contrast ratios are required.
- **State handling:** Loading, empty, and error states MUST be handled for every data-fetching operation.

## Pre-commit Hooks

Install from the repository root:

```bash
pre-commit install
```

The following checks run automatically on every commit:

- `ruff` — linting
- `mypy` — type checking
- `black` — formatting
- `isort` — import sorting

If a hook fails, fix the issue and commit again.

## Quality Gates

All of the following **MUST** pass before a PR can be merged:

| Gate | Command | Expected Result |
|---|---|---|
| Ruff | `uv run ruff check .` | Zero errors |
| mypy | `uv run mypy .` | Zero errors |
| Frontend build | `pnpm build` | Zero errors (includes `tsc`) |
| Tests | `uv run pytest` | All pass, coverage not decreased |
| Constitution | *(PR description)* | Compliance confirmed |
| Docs Sync | *(PR description + docs changes)* | Lifecycle impact reviewed in `docs/`; updates included when necessary |
