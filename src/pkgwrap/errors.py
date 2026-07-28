"""Custom exceptions for the pkgwrap CLI tool.
Defines all domain-specific errors used throughout the application.
"""


class PkgwrapError(Exception):
    """Base class for all pkgwrap custom exceptions."""
    pass


class BackendNotFoundError(PkgwrapError):
    """Raised when no supported package manager backend can be detected on the system."""
    pass


class CommandExecutionError(PkgwrapError):
    """Raised when a package manager command fails to execute properly.

    Args:
        command (str): The command that failed to execute.
        returncode (int): The exit code returned by the command.
        stderr (str, optional): The standard error output, if any. Defaults to "".
    """

    def __init__(self, command: str, returncode: int, stderr: str = "") -> None:
        """Initializes the CommandExecutionError."""
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        message = f"Command '{command}' failed with exit code {returncode}."
        if stderr:
            message += f" Error: {stderr.strip()}"
        super().__init__(message)


class UserCancelledError(PkgwrapError):
    """Raised when a user cancels an operation (e.g., denying a sudo prompt)."""
    pass


class UnsupportedCommandError(PkgwrapError):
    """Raised when a requested command is not supported by the detected backend."""
    pass