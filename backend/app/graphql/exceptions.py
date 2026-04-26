"""Domain exceptions for the GraphQL layer."""


class AuthenticationError(Exception):
    """Raised when an unauthenticated request hits a resolver that requires auth (401)."""

    code = "UNAUTHENTICATED"


class BookingStateConflictError(Exception):
    """Raised when a transition is attempted from a terminal state (409 Conflict)."""

    code = "CONFLICT"


class BookingPermissionError(Exception):
    """Raised when the actor does not have permission for the transition (403 Forbidden)."""

    code = "FORBIDDEN"


class BookingTransitionError(Exception):
    """Raised when the requested transition is not valid (422 Unprocessable)."""

    code = "UNPROCESSABLE"
