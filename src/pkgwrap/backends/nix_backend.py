# src/pkgwrap/backends/nix_backend.py
"""Nix (NixOS/Nix package manager) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class NixBackend(Backend):
    @property
    def name(self) -> str:
        return "nix"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["nix-env", "-i", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["nix-env", "-e", package], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["nix-channel", "--update"], require_sudo=False, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["nix-env", "-u"], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["nix-env", "-qaP", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )