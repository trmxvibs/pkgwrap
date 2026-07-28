# src/pkgwrap/backends/apt_backend.py
"""APT (Debian/Ubuntu) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class AptBackend(Backend):
    @property
    def name(self) -> str:
        return "apt"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apt", "install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apt", "remove", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["apt", "update"], require_sudo=True, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["apt", "upgrade", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apt", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )