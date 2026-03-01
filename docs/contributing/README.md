# Contributing to Viaggiamo

> Last updated: 2026-02-28

Thank you for your interest in contributing to Viaggiamo! This is a carpooling MVP aiming to make shared rides easy, safe, and affordable. Whether you're fixing a bug, adding a feature, or improving documentation, every contribution matters.

## Quick-Start Checklist

1. Fork the repository (or create a branch if you have write access).
2. Create a feature branch (`feature/my-change`).
3. Make your changes following the [code style guide](code-style.md).
4. Write tests for new features.
5. Run linting and type checks.
6. Submit a pull request.

## Pull Request Requirements

Every PR description **MUST** confirm compliance with the four core principles from the project constitution:

| Principle | What to Confirm |
|---|---|
| **Code Quality** | Linting and type checks pass with zero errors. |
| **Test-First** | New behaviour has tests; coverage has not decreased. |
| **UX Consistency** | UI follows the design system and accessibility standards. |
| **Performance** | No regressions; new queries are efficient. |

Additional rules:

- Any **UI change** MUST include a screenshot or screen recording.
- Any **new GraphQL resolver** MUST include query execution times.
- **Tests MUST pass** and **coverage MUST NOT decrease**.

## Detailed Guides

- [Branching & Commits](branching.md) — branch naming, conventional commits, and PR workflow.
- [Testing](testing.md) — how and what to test, TDD cycle, coverage rules.
- [Code Style](code-style.md) — linters, formatters, type checkers, and quality gates.
