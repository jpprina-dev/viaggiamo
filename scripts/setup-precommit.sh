#!/bin/bash

# Setup script for pre-commit hooks
# This script installs and configures pre-commit hooks for the Viaggiamo project

set -e

echo "🔧 Setting up pre-commit hooks for Viaggiamo..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "backend/pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if pre-commit is available
if ! uv run --directory backend pre-commit --version &> /dev/null; then
    echo "📦 Installing pre-commit..."
    cd backend
    uv add --dev pre-commit
    cd ..
fi

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
uv run --directory backend pre-commit install

# Install additional hooks for different stages
echo "🔗 Installing pre-commit hooks for push stage..."
uv run --directory backend pre-commit install --hook-type pre-push

# Update pre-commit hooks to latest versions
echo "🔄 Updating pre-commit hooks to latest versions..."
uv run --directory backend pre-commit autoupdate

# Test the hooks
echo "🧪 Testing pre-commit hooks..."
uv run --directory backend pre-commit run --all-files || {
    echo "⚠️  Some hooks failed. This is expected if there are code style issues."
    echo "💡 Run 'make format' to fix formatting issues, then try again."
}

echo "✅ Pre-commit hooks setup complete!"
echo ""
echo "📋 What happens now:"
echo "   • Black will format your Python code"
echo "   • isort will organize your imports"
echo "   • flake8 will check for style issues"
echo "   • mypy will check type hints"
echo "   • ESLint and Prettier will format frontend code"
echo "   • Tests will run automatically on commit"
echo ""
echo "🚀 Commands you can use:"
echo "   • make format     - Format all code"
echo "   • make lint       - Check code quality"
echo "   • make test       - Run all tests"
echo ""
echo "💡 If hooks fail during commit:"
echo "   • Fix the issues shown"
echo "   • Stage the fixed files: git add <file>"
echo "   • Commit again: git commit -m 'your message'"
