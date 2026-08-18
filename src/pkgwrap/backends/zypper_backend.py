# src/pkgwrap/backends/zypper_backend.py
"""Zypper (openSUSE and SUSE Linux Enterprise) backend implementation for pkgwrap."""

import subprocess
from typing import List

from pkgwrap.backends.base import Backend


class ZypperBackend(Backend):
    """Backend for the zypper package manager."""

    name = "zypper"
    executable = "zypper"
    requires_root = True
    has_native_prompt = True

    def install(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Install one or more packages."""
        command: List[str] = ["zypper", "install"]
        if auto_yes:
            command += ["-y"]
        command += list(packages)
        return self._run_command(
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
        command: List[str] = ["zypper", "remove"]
        if auto_yes:
            command += ["-y"]
        command += list(packages)
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )

    def refresh(
        self,
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Refresh package lists / repository metadata."""
        command: List[str] = ["zypper", "refresh"]
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
        command: List[str] = ["zypper", "update"]
        if auto_yes:
            command += ["-y"]
        return self._run_command(
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
        command: List[str] = ["zypper", "search"]
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
        command: List[str] = ["zypper", "search", "--installed-only"]
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
        command: List[str] = ["zypper", "info"]
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
        """Clean cached package archives."""
        command: List[str] = ["zypper", "clean"]
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )
