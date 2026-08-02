"""Abstract base class for package manager backends.
Defines the standard interface that all package managers must implement,
including enhanced sudo and auto-yes handling.
"""

import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import List

from pkgwrap.errors import CommandExecutionError, SudoNotAvailableError, UserCancelledError
from pkgwrap.ui import ask_confirmation, print_info


class Backend(ABC):
    """Abstract base class defining the interface for all package managers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """str: The name of the package manager backend."""
        pass

    def _run_command(
        self, 
        command: List[str], 
        require_sudo: bool = False,
        already_root: bool = False,
        auto_yes: bool = False
    ) -> subprocess.CompletedProcess:
        """Executes a command using subprocess safely without shell injection.

        Args:
            command (List[str]): The command and its arguments as a list.
            require_sudo (bool, optional): Whether the command needs root/sudo privileges. Defaults to False.
            already_root (bool, optional): Whether the current user is executing as root. Defaults to False.
            auto_yes (bool, optional): Whether to skip the sudo confirmation prompt. Defaults to False.

        Returns:
            subprocess.CompletedProcess: The result of the executed command.

        Raises:
            UserCancelledError: If the user denies the sudo confirmation prompt.
            SudoNotAvailableError: If sudo is required but not installed on the system.
            CommandExecutionError: If the command fails (non-zero exit code) or the executable is missing.
        """
        final_command = command.copy()

        if require_sudo:
            if not already_root:
                # Proactive check before attempting execution
                if not shutil.which("sudo"):
                    raise SudoNotAvailableError(
                        "This system requires root privileges but 'sudo' is not installed. "
                        "Please install sudo or run this command as root."
                    )
                
                final_command = ["sudo"] + final_command
                if not auto_yes:
                    print_info(f"The command '{' '.join(final_command)}' requires administrative privileges (sudo).")
                    if not ask_confirmation("Do you want to proceed with sudo?"):
                        raise UserCancelledError("User denied sudo privileges.")

        # Always print the exact command being executed for transparency
        command_str = " ".join(final_command)
        print_info(f"→ Running: {command_str}")

        try:
            # Output is intentionally not captured so the package manager's native
            # progress bars and interactive prompts stream directly to the terminal.
            result = subprocess.run(final_command, shell=False, check=False)
            
            if result.returncode != 0:
                raise CommandExecutionError(command=command_str, returncode=result.returncode)
            
            return result
        except FileNotFoundError as e:
            # Reactive check if shutil.which missed it or was bypassed
            if final_command[0] == "sudo":
                raise SudoNotAvailableError(
                    "This system requires root privileges but 'sudo' is not installed. "
                    "Please install sudo or run this command as root."
                )
                
            raise CommandExecutionError(
                command=command_str, 
                returncode=127, 
                stderr=f"Executable not found: {e}"
            )

    @abstractmethod
    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        """Installs a package.

        Args:
            package (str): The name of the package to install.
            already_root (bool, optional): Whether the current user is already root. Defaults to False.
            auto_yes (bool, optional): Whether to skip the sudo confirmation prompt. Defaults to False.

        Returns:
            subprocess.CompletedProcess: The result of the execution.
        """
        pass

    @abstractmethod
    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        """Removes a package.

        Args:
            package (str): The name of the package to remove.
            already_root (bool, optional): Whether the current user is already root. Defaults to False.
            auto_yes (bool, optional): Whether to skip the sudo confirmation prompt. Defaults to False.

        Returns:
            subprocess.CompletedProcess: The result of the execution.
        """
        pass

    @abstractmethod
    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        """Updates the system packages and package lists.

        Args:
            already_root (bool, optional): Whether the current user is already root. Defaults to False.
            auto_yes (bool, optional): Whether to skip the sudo confirmation prompt. Defaults to False.

        Returns:
            subprocess.CompletedProcess: The result of the execution.
        """
        pass

    @abstractmethod
    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        """Searches for a package.

        Args:
            query (str): The search query.
            already_root (bool, optional): Whether the current user is already root. Defaults to False.
            auto_yes (bool, optional): Whether to skip the sudo confirmation prompt. Defaults to False.

        Returns:
            subprocess.CompletedProcess: The result of the execution.
        """
        pass