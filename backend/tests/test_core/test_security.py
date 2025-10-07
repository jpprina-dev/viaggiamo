"""Unit tests for security.py - Security utilities for authentication."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    password_hash,
    verify_password,
)


@pytest.mark.unit
class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_get_password_hash_returns_string(self):
        """Test that get_password_hash returns a string."""
        password = "TestPass123!"  # Short password (< 72 bytes for bcrypt)
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_returns_different_hash_for_same_password(self):
        """Test that hashing the same password twice gives different results (salt)."""
        password = "TestPass123!"  # Short password
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Due to salt, hashes should be different
        assert hash1 != hash2

    def test_get_password_hash_creates_argon2_hash(self):
        """Test that password hash uses argon2 format."""
        password = "TestPass123!"  # Short password
        hashed = get_password_hash(password)

        # Argon2 hashes start with $argon2id$
        assert hashed.startswith("$argon2")

    def test_password_hash_is_not_plain_text(self):
        """Test that hashed password is not the same as plain text."""
        password = "TestPass123!"  # Short password
        hashed = get_password_hash(password)

        assert hashed != password

    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "Pass123!"  # Short passwords
        password2 = "Pass456!"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2


@pytest.mark.unit
class TestPasswordVerification:
    """Tests for password verification functionality."""

    def test_verify_password_returns_true_for_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "TestPass123!"  # Short password
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_returns_false_for_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "TestPass123!"  # Short password
        wrong_password = "WrongPass!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_is_case_sensitive(self):
        """Test that password verification is case sensitive."""
        password = "TestPass123!"  # Short password
        wrong_case = "testpass123!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_case, hashed) is False

    def test_verify_password_handles_special_characters(self):
        """Test that password verification handles special characters."""
        password = "p@ss!#$%"  # Short password with special chars
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_handles_unicode(self):
        """Test that password verification handles unicode characters."""
        password = "pásswórd"  # Short unicode password (under 72 bytes)
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_returns_false_for_empty_password(self):
        """Test that verifying empty password against hash returns False."""
        password = "TestPass123!"  # Short password
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False


@pytest.mark.unit
class TestPasswordHashContext:
    """Tests for password hash configuration."""

    def test_password_hash_is_configured(self):
        """Test that password hash is properly configured."""
        assert password_hash is not None
        assert hasattr(password_hash, "hash")
        assert hasattr(password_hash, "verify")


@pytest.mark.unit
class TestAccessTokenCreation:
    """Tests for JWT access token creation."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        token = create_access_token(subject="user@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_subject(self):
        """Test that token contains the subject in payload."""
        subject = "user@example.com"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == subject

    def test_create_access_token_contains_expiration(self):
        """Test that token contains expiration timestamp."""
        token = create_access_token(subject="user@example.com")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))

    def test_create_access_token_uses_default_expiration(self):
        """Test that token uses default expiration time from settings."""
        token = create_access_token(subject="user@example.com")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # Should expire around ACCESS_TOKEN_EXPIRE_MINUTES from now
        expected_expiry = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        # Allow 5 seconds tolerance
        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        assert time_diff < 5

    def test_create_access_token_accepts_custom_expiration(self):
        """Test that token accepts custom expiration delta."""
        custom_delta = timedelta(hours=1)
        token = create_access_token(
            subject="user@example.com", expires_delta=custom_delta
        )

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        expected_expiry = datetime.now(timezone.utc) + custom_delta

        # Allow 5 seconds tolerance
        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        assert time_diff < 5

    def test_create_access_token_uses_correct_algorithm(self):
        """Test that token uses correct algorithm from settings."""
        token = create_access_token(subject="user@example.com")

        # Decoding with wrong algorithm should fail
        with pytest.raises(InvalidTokenError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])

    def test_create_access_token_uses_secret_key(self):
        """Test that token uses secret key from settings."""
        token = create_access_token(subject="user@example.com")

        # Decoding with wrong secret should fail
        with pytest.raises(InvalidTokenError):
            jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])

    def test_create_access_token_handles_integer_subject(self):
        """Test that token handles integer subject (user ID)."""
        subject = 12345
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Subject is converted to string
        assert payload["sub"] == str(subject)

    def test_create_access_token_different_subjects_create_different_tokens(self):
        """Test that different subjects create different tokens."""
        token1 = create_access_token(subject="user1@example.com")
        token2 = create_access_token(subject="user2@example.com")

        assert token1 != token2


@pytest.mark.unit
class TestTokenDecoding:
    """Tests for JWT token decoding validation."""

    def test_valid_token_can_be_decoded(self):
        """Test that a valid token can be decoded."""
        subject = "user@example.com"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == subject
        assert "exp" in payload

    def test_expired_token_raises_error(self):
        """Test that an expired token raises InvalidTokenError."""
        # Create token that expired 1 hour ago
        expired_delta = timedelta(hours=-1)
        token = create_access_token(
            subject="user@example.com", expires_delta=expired_delta
        )

        with pytest.raises(InvalidTokenError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    def test_invalid_token_raises_error(self):
        """Test that an invalid token raises InvalidTokenError."""
        invalid_token = "invalid.token.here"

        with pytest.raises(InvalidTokenError):
            jwt.decode(
                invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

    def test_tampered_token_raises_error(self):
        """Test that a tampered token raises InvalidTokenError."""
        token = create_access_token(subject="user@example.com")

        # Tamper with token by modifying it
        tampered_token = token[:-5] + "xxxxx"

        with pytest.raises(InvalidTokenError):
            jwt.decode(
                tampered_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )


@pytest.mark.unit
class TestSecurityIntegration:
    """Integration tests for security utilities."""

    def test_password_hash_and_verify_workflow(self):
        """Test complete workflow of hashing and verifying password."""
        plain_password = "SecurePass123!"  # Short password

        # Hash the password
        hashed_password = get_password_hash(plain_password)

        # Verify correct password
        assert verify_password(plain_password, hashed_password) is True

        # Verify incorrect password
        assert verify_password("WrongPass!", hashed_password) is False

    def test_token_creation_and_validation_workflow(self):
        """Test complete workflow of creating and validating token."""
        user_email = "user@example.com"

        # Create token
        token = create_access_token(subject=user_email)

        # Decode and validate token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload["sub"] == user_email
        assert "exp" in payload

        # Verify token is not expired
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc)

    def test_multiple_users_have_unique_tokens(self):
        """Test that multiple users get unique tokens."""
        users = ["user1@example.com", "user2@example.com", "user3@example.com"]
        tokens = [create_access_token(subject=user) for user in users]

        # All tokens should be unique
        assert len(tokens) == len(set(tokens))

        # All tokens should decode to correct subjects
        for token, user in zip(tokens, users):
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            assert payload["sub"] == user
