"""Custom exceptions for the pkgwrap application.
Centralizes all error types for consistent handling across the CLI.
"""

class PkgwrapError(Exception):
    """Base exception class for all pkgwrap errors."""
    pass


class BackendNotFoundError(PkgwrapError):
    """Raised when a supported package manager backend cannot be detected."""
    pass


class UserCancelledError(PkgwrapError):
    """Raised when a user cancels an interactive prompt or operation."""
    pass


class SudoNotAvailableError(PkgwrapError):
    """Raised when an operation requires root privileges but 'sudo' is not installed."""
    pass


class CommandExecutionError(PkgwrapError):
    """Raised when a backend command fails to execute or returns a non-zero exit code.

    Attributes:
        command (str): The command that failed.
        returncode (int): The exit status of the command.
        stderr (str, optional): The standard error output, if captured.
    """

    def __init__(self, command: str, returncode: int, stderr: str = "") -> None:
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        
        message = f"Command '{command}' failed with exit code {returncode}."
        if stderr:
            message += f" Error details: {stderr}"
            
        super().__init__(message)