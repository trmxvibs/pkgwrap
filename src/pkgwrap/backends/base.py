"""Abstract base class for package manager backends.

Defines the interface every package manager must implement and centralises
the risky parts: privilege escalation, confirmation prompts, dry-run
handling and safe (shell-free) process execution.
"""

import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from pkgwrap.errors import (
    CommandExecutionError,
    SudoNotAvailableError,
    UnsupportedOperationError,
    UserCancelledError,
)
from pkgwrap.ui import ask_confirmation, print_command, print_info


class Backend(ABC):
    """Abstract base class defining the interface for all package managers."""

    #: Whether install/remove/update need root privileges on this platform.
    requires_root = True

    #: Whether the native package manager asks for confirmation on its own.
    #: When False, pkgwrap adds its own prompt before destructive operations
    #: so the user is never left without a safety net.
    has_native_prompt = True

    @property
    @abstractmethod
    def name(self) -> str:
        """str: The identifier of this backend (e.g. ``apt``)."""

    @property
    @abstractmethod
    def executable(self) -> str:
        """str: Primary executable used to detect and validate this backend."""

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------

    def _run_command(
        self,
        command: Sequence[str],
        require_sudo: bool = False,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
        confirm: Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        """Execute a command safely, without a shell.

        Args:
            command: The command and its arguments as a list.
            require_sudo: Whether the command needs root privileges.
            already_root: Whether the current process is already root.
            auto_yes: Skip pkgwrap's own confirmation prompts.
            dry_run: Print the command that would run and return without
                executing anything.
            confirm: Extra confirmation question asked before running.
                Used for destructive operations on package managers that do
                not prompt by themselves.

        Returns:
            subprocess.CompletedProcess: The result of the execution. For a
            dry run, a synthetic result with return code 0 is returned.

        Raises:
            UserCancelledError: The user declined a confirmation prompt.
            SudoNotAvailableError: Root is required but ``sudo`` is missing.
            CommandExecutionError: The command failed or was not found.
        """
        final_command: List[str] = list(command)
        needs_sudo = require_sudo and not already_root

        if needs_sudo and not dry_run:
            if not shutil.which("sudo"):
                raise SudoNotAvailableError(
                    "This operation requires root privileges but 'sudo' is not "
                    "installed. Install sudo or re-run this command as root."
                )

        if needs_sudo:
            final_command = ["sudo"] + final_command

        command_str = " ".join(final_command)

        if dry_run:
            print_info("Dry run - the following command would be executed:")
            print_command(command_str)
            return subprocess.CompletedProcess(final_command, 0)

        if not auto_yes:
            if confirm:
                print_info("About to run: {0}".format(command_str))
                if not ask_confirmation(confirm):
                    raise UserCancelledError("Operation cancelled by user.")
            elif needs_sudo:
                print_info(
                    "The command '{0}' requires administrative privileges (sudo).".format(
                        command_str
                    )
                )
                if not ask_confirmation("Do you want to proceed with sudo?"):
                    raise UserCancelledError("User denied sudo privileges.")

        print_command(command_str)

        try:
            # Output is intentionally not captured so the package manager's
            # own progress bars and prompts stream straight to the terminal.
            result = subprocess.run(final_command, shell=False, check=False)
        except FileNotFoundError as exc:
            if final_command and final_command[0] == "sudo":
                raise SudoNotAvailableError(
                    "This operation requires root privileges but 'sudo' is not "
                    "installed. Install sudo or re-run this command as root."
                ) from exc
            raise CommandExecutionError(
                command=command_str,
                returncode=127,
                stderr="Executable not found: {0}".format(exc),
            ) from exc
        except PermissionError as exc:
            raise CommandExecutionError(
                command=command_str,
                returncode=126,
                stderr="Permission denied: {0}".format(exc),
            ) from exc

        if result.returncode != 0:
            raise CommandExecutionError(command=command_str, returncode=result.returncode)

        return result

    def _unsupported(self, operation: str) -> "subprocess.CompletedProcess":
        """Raise a clear error for operations this backend cannot perform."""
        raise UnsupportedOperationError(
            "The '{0}' backend does not support the '{1}' operation.".format(
                self.name, operation
            )
        )

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    @abstractmethod
    def install(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Install one or more packages."""

    @abstractmethod
    def remove(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Remove one or more packages."""

    @abstractmethod
    def refresh(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Refresh package lists / repository metadata only."""

    @abstractmethod
    def upgrade(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Upgrade all installed packages."""

    @abstractmethod
    def search(
        self,
        query: str,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Search the repositories for a package."""

    # ------------------------------------------------------------------
    # Optional operations - backends override what they can support
    # ------------------------------------------------------------------

    def list_installed(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """List packages installed on the system."""
        return self._unsupported("list")

    def info(
        self,
        package: str,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Show detailed information about a package."""
        return self._unsupported("info")

    def clean(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Clean cached package archives."""
        return self._unsupported("clean")
