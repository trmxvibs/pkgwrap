# src/pkgwrap/backends/windows_backend.py
"""Winget (Windows) backend implementation for pkgwrap.

Windows has no `sudo`. Instead, winget triggers its own UAC elevation
popup when a package needs admin rights, so we never pass
require_sudo=True here — that logic is Unix-specific.
"""

import subprocess
from pkgwrap.backends.base import Backend


class WindowsBackend(Backend):
    @property
    def name(self) -> str:
        return "winget"

    def install(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        command = ["winget", "install", package]
        if auto_yes:
            command += ["--accept-source-agreements", "--accept-package-agreements", "--silent"]
        return self._run_command(command, require_sudo=False, already_root=already_root, auto_yes=auto_yes)

    def remove(self, package: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        command = ["winget", "uninstall", package]
        if auto_yes:
            command += ["--silent"]
        return self._run_command(command, require_sudo=False, already_root=already_root, auto_yes=auto_yes)

    def update(self, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        command = ["winget", "upgrade", "--all"]
        if auto_yes:
            command += ["--accept-source-agreements", "--accept-package-agreements", "--silent"]
        return self._run_command(command, require_sudo=False, already_root=already_root, auto_yes=auto_yes)

    def search(self, query: str, already_root: bool = False, auto_yes: bool = False) -> subprocess.CompletedProcess:
        return self._run_command(
            ["winget", "search", query],
            require_sudo=False, already_root=already_root, auto_yes=auto_yes
        )