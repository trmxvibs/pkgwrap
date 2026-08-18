# src/pkgwrap/backends/apk_backend.py
"""APK (Alpine Linux) backend implementation for pkgwrap."""

import subprocess
from typing import List

from pkgwrap.backends.base import Backend


class ApkBackend(Backend):
    """Backend for Alpine's apk package manager. apk never prompts, so pkgwrap adds its own
    confirmation for removals.
    """

    name = "apk"
    executable = "apk"
    requires_root = True
    has_native_prompt = False

    def install(
        self,
        packages: List[str],
        already_root: bool = False,
        auto_yes: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        """Install one or more packages."""
        command: List[str] = ["apk", "add"]
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
        command: List[str] = ["apk", "del"]
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
        command: List[str] = ["apk", "update"]
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
        command: List[str] = ["apk", "upgrade"]
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
        command: List[str] = ["apk", "search"]
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
        command: List[str] = ["apk", "info"]
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
        command: List[str] = ["apk", "info", "-a"]
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
        command: List[str] = ["apk", "cache", "clean"]
        return self._run_command(
            command,
            require_sudo=self.requires_root,
            already_root=already_root,
            auto_yes=auto_yes,
            dry_run=dry_run,
        )
