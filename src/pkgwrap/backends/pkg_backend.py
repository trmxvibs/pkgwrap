# src/pkgwrap/backends/pkg_backend.py
"""PKG (Termux) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class PkgBackend(Backend):
    @property
    def name(self) -> str:
        return "pkg"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "install", "-y", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "uninstall", "-y", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "upgrade", "-y"], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pkg", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )