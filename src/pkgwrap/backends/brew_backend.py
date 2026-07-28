# src/pkgwrap/backends/brew_backend.py
"""Homebrew (macOS/Linux) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class BrewBackend(Backend):
    @property
    def name(self) -> str:
        return "brew"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["brew", "install", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["brew", "uninstall", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["brew", "update"], require_sudo=False, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["brew", "upgrade"], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["brew", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )