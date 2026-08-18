# src/pkgwrap/backends/windows_backend.py
"""Winget (Windows Package Manager) backend implementation for pkgwrap."""

import subprocess
from typing import List

from pkgwrap.backends.base import Backend
from pkgwrap.errors import CommandExecutionError
from pkgwrap.ui import print_info

#: winget's APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE (0x8A15002B).
#: `winget install` on an already-installed package tries to upgrade it
#: instead, and fails with this code when there is nothing newer available.
#: That is not a real failure - the package the user asked for is already
#: present - so pkgwrap treats it as success rather than a scary raw exit
#: code. subprocess may surface it as the unsigned 32-bit value or as its
#: signed twin depending on how the process return code is read, so both are
#: recognised.
_WINGET_NO_APPLICABLE_UPDATE = {2316632107, -1978335189}


class WindowsBackend(Backend):
    """Backend for winget. Windows has no sudo; winget raises its own UAC prompt when elevation
    is needed, so require_sudo is never used here.
    """

    name = "winget"
    executable = "winget"
    requires_root = False
    has_native_prompt = False

    def _run_or_treat_already_current_as_success(
        self, command: List[str], **kwargs
    ) -> subprocess.CompletedProcess:
        """Run a winget command, absorbing the "no applicable update" exit code.

        winget prints "Found an existing package already installed. Trying
        to upgrade the installed package..." and then fails with this code
        when the installed version is already the latest. From the user's
        point of view they asked to install something that is already
        there, which is success, not an error.
        """
        try:
            return self._run_command(command, **kwargs)
        except CommandExecutionError as exc:
            if exc.returncode in _WINGET_NO_APPLICABLE_UPDATE:
                print_info(
                    "winget reports no applicable update - the package is "
                    "already installed and up to date."
                )
                return subprocess.CompletedProcess(command, 0)
            raise

    def install(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Install one or more packages."""
        command: List[str] = ["winget", "install"]
        if auto_yes:
            command += [
                "--accept-source-agreements",
                "--accept-package-agreements",
                "--silent",
                "--disable-interactivity",
            ]
        command += list(packages)
        return self._run_or_treat_already_current_as_success(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def remove(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Remove one or more packages."""
        command: List[str] = ["winget", "uninstall"]
        if auto_yes:
            command += ["--silent", "--disable-interactivity"]
        command += list(packages)
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
            confirm="Remove {0}?".format(", ".join(packages)),
        )

    def refresh(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Refresh package lists / repository metadata."""
        command: List[str] = ["winget", "source", "update"]
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def upgrade(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Upgrade all installed packages."""
        command: List[str] = ["winget", "upgrade", "--all"]
        if auto_yes:
            command += [
                "--accept-source-agreements",
                "--accept-package-agreements",
                "--silent",
                "--disable-interactivity",
            ]
        return self._run_or_treat_already_current_as_success(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def search(
        self,
        query: str,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Search the repositories for a package."""
        command: List[str] = ["winget", "search"]
        command += [query]
        return self._run_command(
            command,
            require_sudo=False,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def list_installed(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """List packages installed on the system."""
        command: List[str] = ["winget", "list"]
        return self._run_command(
            command,
            require_sudo=False,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def info(
        self,
        package: str,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Show detailed information about a package."""
        command: List[str] = ["winget", "show"]
        command += [package]
        return self._run_command(
            command,
            require_sudo=False,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def clean(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Clean the package cache (not supported by this backend)."""
        return self._unsupported("clean")
