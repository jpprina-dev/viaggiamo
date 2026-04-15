# Branching & Commit Conventions

> Last updated: 2026-02-28

## Branch Naming

Use a prefix that describes the type of work, followed by a short kebab-case description:

| Prefix | Purpose | Example |
|---|---|---|
| `feature/` | New features | `feature/add-trip-search` |
| `fix/` | Bug fixes | `fix/booking-duplicate` |
| `chore/` | Maintenance tasks | `chore/update-deps` |

## Conventional Commits

All commit messages **MUST** follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <short summary>
```

| Type | When to Use |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `chore:` | Maintenance |
| `docs:` | Documentation |
| `test:` | Tests |
| `refactor:` | Code restructuring |

**Example:**

```
feat: add fuzzy search to trip queries
```

## PR Workflow

1. Create a branch from `dev`:

```bash
git checkout dev
git pull origin dev
git checkout -b feature/my-change
```

2. Make changes and commit with conventional commits:

```bash
git add .
git commit -m "feat: add fuzzy search to trip queries"
```

3. Push the branch to the remote:

```bash
git push -u origin feature/my-change
```

4. Open a pull request targeting `dev`.
5. Wait for review and CI checks to complete.
6. Merge after approval.
