# src/pkgwrap/backends/xbps_backend.py
"""XBPS (Void Linux) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class XbpsBackend(Backend):
    @property
    def name(self) -> str:
        return "xbps"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["xbps-install", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["xbps-remove", "-y", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["xbps-install", "-Su", "-y"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["xbps-query", "-Rs", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )