# src/pkgwrap/backends/freebsd_backend.py
"""FreeBSD backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class FreeBsdBackend(Backend):
    @property
    def name(self) -> str:
        return "freebsd"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "delete", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["pkg", "update"], require_sudo=True, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["pkg", "upgrade", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )