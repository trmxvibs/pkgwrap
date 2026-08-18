# src/pkgwrap/backends/pacman_backend.py
"""Pacman (Arch Linux and derivatives) backend implementation for pkgwrap."""

import subprocess
from typing import List

from pkgwrap.backends.base import Backend


class PacmanBackend(Backend):
    """Backend for Arch Linux's pacman package manager."""

    name = "pacman"
    executable = "pacman"
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
        command: List[str] = ["pacman", "-S"]
        if auto_yes:
            command += ["--noconfirm"]
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
        command: List[str] = ["pacman", "-Rs"]
        if auto_yes:
            command += ["--noconfirm"]
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
        command: List[str] = ["pacman", "-Sy"]
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
        command: List[str] = ["pacman", "-Syu"]
        if auto_yes:
            command += ["--noconfirm"]
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
        command: List[str] = ["pacman", "-Ss"]
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
        command: List[str] = ["pacman", "-Q"]
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
        command: List[str] = ["pacman", "-Si"]
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
        command: List[str] = ["pacman", "-Sc"]
        if auto_yes:
            command += ["--noconfirm"]
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )
