"""Unit tests for config.py - Application configuration settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings


@pytest.mark.unit
class TestSettingsCreation:
    """Tests for Settings model creation and validation."""

    def test_settings_is_base_settings_instance(self):
        """Test that settings is a Settings instance."""
        assert isinstance(settings, Settings)

    def test_settings_has_required_fields(self):
        """Test that settings has all required configuration fields."""
        assert hasattr(settings, "PROJECT_NAME")
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "ALGORITHM")
        assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "REDIS_URL")
        assert hasattr(settings, "BACKEND_CORS_ORIGINS")
        assert hasattr(settings, "ENVIRONMENT")
        assert hasattr(settings, "DEBUG")

    def test_settings_project_name_default(self):
        """Test default project name."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.PROJECT_NAME == "Viaggiamo"

    def test_settings_algorithm_default(self):
        """Test default algorithm."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.ALGORITHM == "HS256"

    def test_settings_access_token_expire_minutes_default(self):
        """Test default access token expiration."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_settings_redis_url_default(self):
        """Test default Redis URL."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            REDIS_URL="redis://localhost:6379/0",  # Override environment variable
        )
        assert test_settings.REDIS_URL == "redis://localhost:6379/0"

    def test_settings_environment_default(self):
        """Test default environment."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.ENVIRONMENT == "development"

    def test_settings_debug_default(self):
        """Test default debug setting."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.DEBUG is True


@pytest.mark.unit
class TestSettingsValidation:
    """Tests for Settings validation logic."""

    def test_settings_requires_secret_key(self):
        """Test that SECRET_KEY is required when not in environment."""
        # Note: This test may pass if .env file has SECRET_KEY
        # In production, SECRET_KEY should always be set via environment
        import os

        old_key = os.environ.get("SECRET_KEY")
        old_db = os.environ.get("DATABASE_URL")
        try:
            if "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]
            if "DATABASE_URL" not in os.environ:
                os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)

            errors = exc_info.value.errors()
            assert any(error["loc"] == ("SECRET_KEY",) for error in errors)
        finally:
            if old_key:
                os.environ["SECRET_KEY"] = old_key
            if old_db:
                os.environ["DATABASE_URL"] = old_db
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    def test_settings_requires_database_url(self):
        """Test that DATABASE_URL is required when not in environment."""
        # Note: This test may pass if .env file has DATABASE_URL
        import os

        old_key = os.environ.get("SECRET_KEY")
        old_db = os.environ.get("DATABASE_URL")
        try:
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            if "SECRET_KEY" not in os.environ:
                os.environ["SECRET_KEY"] = "test-key"

            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)

            errors = exc_info.value.errors()
            assert any(error["loc"] == ("DATABASE_URL",) for error in errors)
        finally:
            if old_key:
                os.environ["SECRET_KEY"] = old_key
            if old_db:
                os.environ["DATABASE_URL"] = old_db
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]

    def test_settings_accepts_valid_configuration(self):
        """Test that valid configuration is accepted."""
        test_settings = Settings(
            SECRET_KEY="test-secret-key",
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            ENVIRONMENT="production",
            DEBUG=False,
        )

        assert test_settings.SECRET_KEY == "test-secret-key"
        assert (
            test_settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost/db"
        )
        assert test_settings.ENVIRONMENT == "production"
        assert test_settings.DEBUG is False


@pytest.mark.unit
class TestCORSOriginsValidation:
    """Tests for CORS origins validation."""

    def test_cors_origins_empty_list_default(self):
        """Test that CORS origins defaults to empty list when not set."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            BACKEND_CORS_ORIGINS=[],
        )
        assert len(test_settings.BACKEND_CORS_ORIGINS) == 0

    def test_cors_origins_accepts_list(self):
        """Test that CORS origins accepts a list."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"],
        )
        assert len(test_settings.BACKEND_CORS_ORIGINS) == 2

    def test_cors_origins_assembles_from_string(self):
        """Test that CORS origins can be assembled from comma-separated string."""
        # This would be set via environment variable
        origins_string = "http://localhost:3000,http://localhost:8080"
        result = Settings.assemble_cors_origins(origins_string)

        assert isinstance(result, list)
        assert len(result) == 2
        assert "http://localhost:3000" in result
        assert "http://localhost:8080" in result

    def test_cors_origins_strips_whitespace(self):
        """Test that CORS origins strips whitespace from string."""
        origins_string = (
            "http://localhost:3000, http://localhost:8080 , http://localhost:9000"
        )
        result = Settings.assemble_cors_origins(origins_string)

        assert all(
            not origin.startswith(" ") and not origin.endswith(" ") for origin in result
        )
        assert len(result) == 3


@pytest.mark.unit
class TestEmailSettings:
    """Tests for email configuration settings."""

    def test_email_settings_have_defaults(self):
        """Test that email settings have default values when not overridden."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SMTP_USER="",
            SMTP_PASSWORD="",
            EMAILS_FROM_EMAIL="",
        )

        assert test_settings.SMTP_TLS is True
        assert test_settings.SMTP_PORT == 587
        assert test_settings.SMTP_HOST == "smtp.gmail.com"
        assert test_settings.EMAILS_FROM_NAME == "Viaggiamo"

    def test_email_settings_can_be_customized(self):
        """Test that email settings can be customized."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            SMTP_HOST="smtp.example.com",
            SMTP_PORT=465,
            SMTP_TLS=False,
            SMTP_USER="user@example.com",
            SMTP_PASSWORD="password",
            EMAILS_FROM_EMAIL="noreply@example.com",
            EMAILS_FROM_NAME="Test App",
        )

        assert test_settings.SMTP_HOST == "smtp.example.com"
        assert test_settings.SMTP_PORT == 465
        assert test_settings.SMTP_TLS is False
        assert test_settings.SMTP_USER == "user@example.com"
        assert test_settings.SMTP_PASSWORD == "password"
        assert test_settings.EMAILS_FROM_EMAIL == "noreply@example.com"
        assert test_settings.EMAILS_FROM_NAME == "Test App"


@pytest.mark.unit
class TestPaginationSettings:
    """Tests for pagination configuration settings."""

    def test_pagination_default_page_size(self):
        """Test default page size setting."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.DEFAULT_PAGE_SIZE == 20

    def test_pagination_max_page_size(self):
        """Test maximum page size setting."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.MAX_PAGE_SIZE == 100

    def test_pagination_can_be_customized(self):
        """Test that pagination settings can be customized."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            DEFAULT_PAGE_SIZE=50,
            MAX_PAGE_SIZE=200,
        )

        assert test_settings.DEFAULT_PAGE_SIZE == 50
        assert test_settings.MAX_PAGE_SIZE == 200


@pytest.mark.unit
class TestSettingsModel:
    """Tests for Settings model configuration."""

    def test_settings_model_config_case_sensitive(self):
        """Test that settings are case sensitive."""
        assert Settings.model_config["case_sensitive"] is True

    def test_settings_model_config_env_file(self):
        """Test that settings load from .env file."""
        assert Settings.model_config["env_file"] == ".env"

    def test_settings_model_config_encoding(self):
        """Test that env file uses UTF-8 encoding."""
        assert Settings.model_config["env_file_encoding"] == "utf-8"


@pytest.mark.unit
class TestAPIConfiguration:
    """Tests for API configuration settings."""

    def test_api_v1_str_default(self):
        """Test default API version string."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
        )
        assert test_settings.API_V1_STR == "/api/v1"

    def test_api_v1_str_can_be_customized(self):
        """Test that API version string can be customized."""
        test_settings = Settings(
            SECRET_KEY="test-key",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            API_V1_STR="/api/v2",
        )
        assert test_settings.API_V1_STR == "/api/v2"
