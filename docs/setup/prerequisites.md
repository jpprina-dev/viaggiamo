# Prerequisites

> Last updated: 2026-02-28

This page lists every tool you need to install before working on Viaggiamo, with minimum versions and verification commands.

## Required Tools

### Git

Version control for the codebase.

```bash
# Verify
git --version   # 2.30+ recommended
```

### Docker & Docker Compose

Runs the full stack (PostgreSQL, Redis, backend, frontend) in containers.

```bash
# Linux/WSL2
# Follow https://docs.docker.com/engine/install/

# macOS
# Install Docker Desktop from https://www.docker.com/products/docker-desktop/

# Verify
docker --version          # 20.10+ recommended
docker compose version    # v2.0+ required (note: no hyphen)
```

> **Windows users**: Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) first, then install Docker Desktop with the WSL2 backend enabled. Run all commands from within the WSL2 terminal.

### Python 3.11+

Required for backend development.

```bash
# Linux/WSL2
sudo apt update && sudo apt install python3.11 python3.11-venv

# macOS
brew install python@3.11

# Verify
python3 --version   # 3.11.0+
```

### uv (Python package manager)

Manages Python dependencies. Replaces pip/poetry.

```bash
# Linux/macOS/WSL2
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

> See the [uv documentation](https://docs.astral.sh/uv/) for alternative installation methods.

### Node.js 18+

Required for frontend development.

```bash
# Linux/WSL2 (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# macOS
brew install node@18

# Verify
node --version   # 18.0.0+
```

### pnpm

Node.js package manager used by the frontend.

```bash
# After Node.js is installed
npm install -g pnpm

# Verify
pnpm --version   # 8.0+
```

## Quick Verification

Run all checks at once:

```bash
git --version && \
docker --version && \
docker compose version && \
python3 --version && \
uv --version && \
node --version && \
pnpm --version
```

All commands should succeed without errors. If any fail, install the missing tool using the instructions above.

## Next Steps

- [Configure environment variables](environment.md)
- [Set up backend-only development](backend-only.md)
- [Run the full stack with Docker](full-stack.md)
