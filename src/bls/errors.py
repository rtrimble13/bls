"""Exception hierarchy and process exit codes.

Every error raised by this package derives from :class:`BLSError` and carries an
``exit_code`` so the CLI can map failures to stable, documented exit statuses
(see ``docs/agents.md``).
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Process exit codes used by the ``bls`` CLI."""

    OK = 0
    ERROR = 1  # unexpected / generic failure
    USAGE = 2  # bad arguments (also used by the argument parser)
    API = 3  # the API answered but reported a failure
    QUOTA = 4  # daily request threshold or rate limit exceeded
    NETWORK = 5  # transport-level problem: DNS, timeout, TLS, connection reset
    NO_DATA = 6  # --strict was given and at least one series returned nothing
    CONFIG = 7  # missing/invalid configuration (e.g. a flag that needs an API key)


class BLSError(Exception):
    """Base class for all errors raised by the package."""

    exit_code: ExitCode = ExitCode.ERROR

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        return self.message


class BLSConfigError(BLSError):
    """Configuration is missing or invalid."""

    exit_code = ExitCode.CONFIG


class BLSNetworkError(BLSError):
    """The request never produced an HTTP response."""

    exit_code = ExitCode.NETWORK


class BLSHTTPError(BLSError):
    """The server answered with a non-success HTTP status."""

    exit_code = ExitCode.API

    def __init__(self, status_code: int, message: str, *, hint: str | None = None) -> None:
        super().__init__(message, hint=hint)
        self.status_code = status_code


class BLSAPIError(BLSError):
    """The API returned ``status != REQUEST_SUCCEEDED``."""

    exit_code = ExitCode.API

    def __init__(self, status: str, messages: list[str], *, hint: str | None = None) -> None:
        detail = "; ".join(messages) if messages else "no detail provided"
        super().__init__(f"BLS API request failed ({status}): {detail}", hint=hint)
        self.status = status
        self.messages = messages


class BLSQuotaError(BLSAPIError):
    """The daily request threshold (or a rate limit) was exceeded."""

    exit_code = ExitCode.QUOTA


class BLSNoDataError(BLSError):
    """Raised in ``--strict`` mode when a requested series returned no observations."""

    exit_code = ExitCode.NO_DATA
