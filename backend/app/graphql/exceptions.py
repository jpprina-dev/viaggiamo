"""Domain exceptions for the GraphQL layer.

All errors inherit from ``ValueError`` so that legacy callers/tests using
``pytest.raises(ValueError)`` continue to work, while the typed subclasses
let new code branch on category (auth / not-found / permission / validation /
state-conflict) and expose a stable ``.code`` for the GraphQL transport layer.
"""


class AuthenticationError(ValueError):
    """Raised when an unauthenticated request hits a resolver that requires auth (401)."""

    code = "UNAUTHENTICATED"


class NotFoundError(ValueError):
    """Raised when a referenced entity does not exist (404 Not Found)."""

    code = "NOT_FOUND"


class ForbiddenError(ValueError):
    """Raised when the user is authenticated but lacks permission for the operation (403)."""

    code = "FORBIDDEN"


class ValidationError(ValueError):
    """Raised when input fails business-rule validation (422 Unprocessable Entity)."""

    code = "UNPROCESSABLE"


class BookingStateConflictError(ValueError):
    """Raised when a transition is attempted from a terminal state (409 Conflict)."""

    code = "CONFLICT"


class BookingPermissionError(ForbiddenError):
    """Raised when the actor does not have permission for the transition (403 Forbidden)."""

    code = "FORBIDDEN"


class BookingTransitionError(ValidationError):
    """Raised when the requested transition is not valid (422 Unprocessable)."""

    code = "UNPROCESSABLE"
