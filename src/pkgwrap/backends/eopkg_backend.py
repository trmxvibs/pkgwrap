# src/pkgwrap/backends/eopkg_backend.py
"""Eopkg (Solus) backend implementation for pkgwrap."""

import subprocess
from typing import List

from pkgwrap.backends.base import Backend


class EopkgBackend(Backend):
    """Backend for the Solus eopkg package manager."""

    name = "eopkg"
    executable = "eopkg"
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
        command: List[str] = ["eopkg", "install"]
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
        command: List[str] = ["eopkg", "remove"]
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
        command: List[str] = ["eopkg", "update-repo"]
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
        command: List[str] = ["eopkg", "upgrade"]
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
        command: List[str] = ["eopkg", "search"]
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
        command: List[str] = ["eopkg", "list-installed"]
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
        command: List[str] = ["eopkg", "info"]
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
        command: List[str] = ["eopkg", "delete-cache"]
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )
