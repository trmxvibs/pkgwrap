# src/pkgwrap/backends/pacman_backend.py
"""Pacman (Arch Linux) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class PacmanBackend(Backend):
    @property
    def name(self) -> str:
        return "pacman"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pacman", "-S", "--noconfirm", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pacman", "-Rs", "--noconfirm", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pacman", "-Syu", "--noconfirm"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["pacman", "-Ss", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )