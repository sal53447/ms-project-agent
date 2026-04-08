class PlannerError(Exception):
    """Base exception for Planner API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class PlannerNotFoundError(PlannerError):
    """Resource not found (404)."""


class PlannerForbiddenError(PlannerError):
    """Access denied (403)."""


class PlannerConflictError(PlannerError):
    """ETag conflict after retry exhausted (409/412)."""


class PlannerThrottledError(PlannerError):
    """Rate limited after retries exhausted (429)."""
