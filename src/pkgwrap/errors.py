"""Custom exceptions for pkgwrap.

Centralises every error type so the CLI can map them onto clean, stable
exit codes instead of leaking tracebacks.
"""

from typing import Optional


class PkgwrapError(Exception):
    """Base exception class for all pkgwrap errors."""

    #: Default process exit code for this error class.
    exit_code = 1


class BackendNotFoundError(PkgwrapError):
    """Raised when a supported package manager backend cannot be detected."""

    exit_code = 3


class UserCancelledError(PkgwrapError):
    """Raised when a user declines an interactive prompt."""

    exit_code = 4


class SudoNotAvailableError(PkgwrapError):
    """Raised when root privileges are required but 'sudo' is unavailable."""

    exit_code = 5


class UnsupportedOperationError(PkgwrapError):
    """Raised when a backend does not implement a requested operation."""

    exit_code = 6


class InvalidPackageNameError(PkgwrapError):
    """Raised when a package name looks like a flag or contains unsafe characters."""

    exit_code = 7


class CommandExecutionError(PkgwrapError):
    """Raised when a backend command fails or cannot be executed.

    Attributes:
        command (str): The command that failed.
        returncode (int): The raw exit status reported by :mod:`subprocess`.
        stderr (str): Captured standard error, when available.
    """

    def __init__(self, command: str, returncode: int, stderr: str = "") -> None:
        self.command = command
        self.returncode = returncode
        self.stderr = stderr

        message = "Command '{0}' failed with exit code {1}.".format(command, returncode)
        if stderr:
            message += " Error details: {0}".format(stderr)

        super().__init__(message)

    @property
    def exit_code(self) -> int:  # type: ignore[override]
        """Return a POSIX-safe exit code for this failure.

        ``subprocess`` reports a negative value when a child is killed by a
        signal (for example ``-9`` for SIGKILL). Passing that straight to
        :func:`sys.exit` produces a meaningless status (``-9`` becomes 247),
        so signals are translated to the conventional ``128 + N`` and every
        result is clamped into the valid 1-255 range.
        """
        return normalize_exit_code(self.returncode)


def normalize_exit_code(returncode: Optional[int]) -> int:
    """Translate a subprocess return code into a valid process exit status."""
    if returncode is None:
        return 1
    if returncode < 0:
        return min(128 + abs(returncode), 255)
    if returncode == 0:
        # A "failure" with status 0 should still be a failure for the caller.
        return 1
    return returncode % 256 or 1
