# src/pkgwrap/backends/apk_backend.py
"""APK (Alpine Linux) backend implementation for pkgwrap."""

import subprocess
from pkgwrap.backends.base import Backend

class ApkBackend(Backend):
    @property
    def name(self) -> str:
        return "apk"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apk", "add", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apk", "del", package], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        self._run_command(["apk", "update"], require_sudo=True, already_root=already_root, auto_yes=auto_yes)
        return self._run_command(
            ["apk", "upgrade"], 
            require_sudo=True, already_root=already_root, auto_yes=auto_yes
        )

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["apk", "search", query], 
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )