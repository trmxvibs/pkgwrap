# src/pkgwrap/backends/dnf_backend.py
"""DNF (Fedora/RHEL) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class DnfBackend(Backend):
    @property
    def name(self) -> str:
        return "dnf"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["dnf", "install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["dnf", "remove", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["dnf", "upgrade", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["dnf", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )