# Pre-commit Hooks Setup - Viaggiamo

## ✅ What was implemented

### 1. **Pre-commit Configuration** (`.pre-commit-config.yaml`)
- **Black**: Python code formatting with 88 character line length
- **isort**: Import organization following Black profile
- **Basic hooks**: Trailing whitespace, end-of-file fixes, YAML/JSON validation
- **Security checks**: Large file detection, merge conflict detection
- **Code quality**: Debug statement detection, case conflict detection

### 2. **Backend Configuration**
- **Flake8 configuration** (`.flake8`): Comprehensive linting rules
- **Updated pyproject.toml**: Added dev dependencies for code quality tools
- **Package structure**: Fixed hatchling build configuration

### 3. **Frontend Configuration**
- **ESLint config** (`.eslintrc.json`): TypeScript and Next.js linting rules
- **Prettier config** (`.prettierrc`): Code formatting with Tailwind CSS plugin

### 4. **Setup Script** (`scripts/setup-precommit.sh`)
- Automated installation of pre-commit hooks
- Dependency installation verification
- Hook testing and validation
- User-friendly error messages and instructions

### 5. **Makefile Integration**
- `make precommit-setup`: Install pre-commit hooks
- `make precommit-run`: Run hooks on all files
- `make precommit-update`: Update hook versions
- `make format`: Format code with black and isort
- `make lint`: Run linting checks

## 🚀 How to use

### Initial Setup
```bash
# Option 1: Use the setup script
make precommit-setup

# Option 2: Manual setup
cd backend
uv add --dev pre-commit
uv run pre-commit install
```

### Development Workflow
```bash
# Format code
make format

# Run linting
make lint

# Run pre-commit hooks manually
make precommit-run

# Update hooks to latest versions
make precommit-update
```

### Git Workflow
```bash
# Hooks run automatically on commit
git add .
git commit -m "your message"
# Pre-commit hooks will run and fix issues automatically

# If hooks fail, fix issues and commit again
git add .
git commit -m "your message"
```

## 📋 Hook Details

### Backend Hooks
- **Black**: Formats Python code to 88 characters per line
- **isort**: Organizes imports according to Black profile
- **Flake8**: Lints Python code (configured via .flake8 file)
- **Basic checks**: Whitespace, file endings, syntax validation

### Frontend Hooks
- **ESLint**: Lints TypeScript/JavaScript files
- **Prettier**: Formats code with Tailwind CSS support
- **JSON/YAML validation**: Ensures config files are valid

### General Hooks
- **Trailing whitespace**: Removes trailing spaces
- **End-of-file**: Ensures files end with newline
- **Large files**: Prevents accidentally committing large files
- **Merge conflicts**: Detects unresolved merge conflicts
- **Debug statements**: Finds leftover debug code

## ⚙️ Configuration Files

### `.pre-commit-config.yaml`
Main configuration file defining all hooks and their settings.

### `backend/.flake8`
Flake8 configuration with:
- 88 character line length (matches Black)
- Ignores conflicts with Black (E203, W503, E501)
- Disables docstring requirements for MVP
- Enables security and bug detection

### `frontend/.eslintrc.json`
ESLint configuration for:
- Next.js and TypeScript support
- React hooks rules
- Unused variable detection
- Console statement warnings

### `frontend/.prettierrc`
Prettier configuration with:
- 80 character line length
- Single quotes
- No semicolons
- Tailwind CSS plugin support

## 🔧 Troubleshooting

### Common Issues

1. **Hooks fail on commit**
   ```bash
   # Fix formatting issues
   make format

   # Add fixed files and commit again
   git add .
   git commit -m "your message"
   ```

2. **Pre-commit not found**
   ```bash
   # Reinstall hooks
   make precommit-setup
   ```

3. **Hook dependencies missing**
   ```bash
   # Install backend dependencies
   cd backend && uv sync --extra dev

   # Install frontend dependencies
   cd frontend && npm install
   ```

4. **Hook version conflicts**
   ```bash
   # Update to latest versions
   make precommit-update
   ```

### Manual Hook Execution
```bash
# Run all hooks
make precommit-run

# Run specific hook
uv run --directory backend pre-commit run black --all-files

# Skip hooks for emergency commits
git commit --no-verify -m "emergency fix"
```

## 📚 Benefits

1. **Code Consistency**: All code follows the same formatting standards
2. **Quality Assurance**: Catches common issues before commit
3. **Team Collaboration**: Everyone uses the same code style
4. **Automated Fixes**: Many issues are fixed automatically
5. **Security**: Prevents committing sensitive data or large files
6. **Maintainability**: Clean, consistent code is easier to maintain

## 🎯 Next Steps

1. **Add more hooks** as needed (mypy, security scans, etc.)
2. **Configure CI/CD** to run the same checks
3. **Add commit message linting** for conventional commits
4. **Include frontend hooks** when frontend is ready
5. **Add performance testing** hooks for critical paths

## 📖 Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)
