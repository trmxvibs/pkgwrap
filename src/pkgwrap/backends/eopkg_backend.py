# src/pkgwrap/backends/eopkg_backend.py
"""Eopkg (Solus) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class EopkgBackend(Backend):
    @property
    def name(self) -> str:
        return "eopkg"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["eopkg", "install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["eopkg", "remove", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["eopkg", "upgrade", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["eopkg", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )