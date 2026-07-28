# src/pkgwrap/backends/zypper_backend.py
"""Zypper (openSUSE) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class ZypperBackend(Backend):
    @property
    def name(self) -> str:
        return "zypper"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["zypper", "install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["zypper", "remove", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["zypper", "refresh"], require_sudo=True, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["zypper", "update", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["zypper", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )