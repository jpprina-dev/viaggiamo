"""Unit tests for BookingStateMachine — pure Python, no DB required."""

import pytest

from app.graphql.exceptions import (
    BookingPermissionError,
    BookingStateConflictError,
    BookingTransitionError,
)
from app.models.booking import BookingStatus
from app.models.booking_audit_log import ActorRole
from app.services.booking_state_machine import BookingStateMachine

# ── Valid transitions ───────────────────────────────────────────────────────


def test_driver_can_accept_pending_booking() -> None:
    BookingStateMachine.validate(
        BookingStatus.pending, BookingStatus.accepted, ActorRole.driver
    )


def test_driver_can_reject_pending_booking() -> None:
    BookingStateMachine.validate(
        BookingStatus.pending, BookingStatus.rejected, ActorRole.driver
    )


def test_passenger_can_cancel_pending_booking() -> None:
    BookingStateMachine.validate(
        BookingStatus.pending, BookingStatus.cancelled, ActorRole.passenger
    )


def test_passenger_can_cancel_accepted_booking() -> None:
    BookingStateMachine.validate(
        BookingStatus.accepted, BookingStatus.cancelled, ActorRole.passenger
    )


def test_driver_can_revoke_accepted_booking() -> None:
    BookingStateMachine.validate(
        BookingStatus.accepted, BookingStatus.revoked, ActorRole.driver
    )


# ── Terminal state conflicts (409 CONFLICT) ─────────────────────────────────


@pytest.mark.parametrize(
    "terminal_status",
    [BookingStatus.rejected, BookingStatus.cancelled, BookingStatus.revoked],
)
def test_any_transition_from_terminal_state_raises_conflict(
    terminal_status: BookingStatus,
) -> None:
    with pytest.raises(BookingStateConflictError):
        BookingStateMachine.validate(
            terminal_status, BookingStatus.pending, ActorRole.driver
        )


# ── Wrong role (403 FORBIDDEN) ─────────────────────────────────────────────


def test_passenger_cannot_accept_pending_booking() -> None:
    with pytest.raises(BookingPermissionError):
        BookingStateMachine.validate(
            BookingStatus.pending, BookingStatus.accepted, ActorRole.passenger
        )


def test_passenger_cannot_reject_pending_booking() -> None:
    with pytest.raises(BookingPermissionError):
        BookingStateMachine.validate(
            BookingStatus.pending, BookingStatus.rejected, ActorRole.passenger
        )


def test_driver_cannot_cancel_pending_booking() -> None:
    with pytest.raises(BookingPermissionError):
        BookingStateMachine.validate(
            BookingStatus.pending, BookingStatus.cancelled, ActorRole.driver
        )


def test_driver_cannot_cancel_accepted_booking() -> None:
    with pytest.raises(BookingPermissionError):
        BookingStateMachine.validate(
            BookingStatus.accepted, BookingStatus.cancelled, ActorRole.driver
        )


def test_passenger_cannot_revoke_accepted_booking() -> None:
    with pytest.raises(BookingPermissionError):
        BookingStateMachine.validate(
            BookingStatus.accepted, BookingStatus.revoked, ActorRole.passenger
        )


# ── Invalid transitions (422 UNPROCESSABLE) ────────────────────────────────


def test_pending_to_revoked_is_invalid() -> None:
    with pytest.raises(BookingTransitionError):
        BookingStateMachine.validate(
            BookingStatus.pending, BookingStatus.revoked, ActorRole.driver
        )


def test_accepted_to_pending_is_invalid() -> None:
    with pytest.raises(BookingTransitionError):
        BookingStateMachine.validate(
            BookingStatus.accepted, BookingStatus.pending, ActorRole.driver
        )


def test_accepted_to_rejected_is_invalid() -> None:
    with pytest.raises(BookingTransitionError):
        BookingStateMachine.validate(
            BookingStatus.accepted, BookingStatus.rejected, ActorRole.driver
        )


def test_pending_to_pending_is_invalid() -> None:
    with pytest.raises(BookingTransitionError):
        BookingStateMachine.validate(
            BookingStatus.pending, BookingStatus.pending, ActorRole.passenger
        )


def test_accepted_to_accepted_is_invalid() -> None:
    with pytest.raises(BookingTransitionError):
        BookingStateMachine.validate(
            BookingStatus.accepted, BookingStatus.accepted, ActorRole.driver
        )


# ── String input tolerance ──────────────────────────────────────────────────


def test_validate_accepts_string_inputs() -> None:
    """validate() should coerce plain strings to enums."""
    BookingStateMachine.validate("pending", "accepted", "driver")


def test_validate_rejects_unknown_string_status() -> None:
    """Unknown status strings should raise ValueError from StrEnum coercion."""
    with pytest.raises(ValueError):
        BookingStateMachine.validate("pending", "unknown_status", "driver")
