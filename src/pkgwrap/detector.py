"""OS and package manager detection logic.
Identifies the native package manager and manages caching.
"""

import os
import platform
import shutil

from pkgwrap.config import read_cached_backend, write_cached_backend
from pkgwrap.errors import BackendNotFoundError


def detect_backend() -> str:
    """Detects the native package manager backend for the current system.

    Checks a local cache first for speed. If not found, explicitly checks
    for Termux and FreeBSD environments before falling back to a prioritized
    list of generic package managers.

    Returns:
        str: The identifier of the detected backend.

    Raises:
        BackendNotFoundError: If no supported package manager is found.
    """
    cached_backend = read_cached_backend()

    if cached_backend:
        # Map backend names to their primary executables for cache validation
        executable = cached_backend
        if cached_backend == "freebsd":
            executable = "pkg"
        elif cached_backend == "nix":
            executable = "nix-env"
        elif cached_backend == "xbps":
            executable = "xbps-install"
            
        if shutil.which(executable):
            return cached_backend

    # 1. Termux OS Detection (Highest Priority)
    # Termux includes an 'apt' wrapper, so we MUST catch Termux before checking 'apt'.
    prefix = os.environ.get("PREFIX", "")
    termux_version = os.environ.get("TERMUX_VERSION")
    
    if "com.termux" in prefix or termux_version is not None:
        if shutil.which("pkg"):
            write_cached_backend("pkg")
            return "pkg"

    # 2. FreeBSD OS Detection
    # FreeBSD uses 'pkg', which needs to be routed to the freebsd_backend
    if platform.system().lower() == "freebsd":
        if shutil.which("pkg"):
            write_cached_backend("freebsd")
            return "freebsd"

    # 2.5 Windows OS Detection
    if platform.system().lower() == "windows":
        if shutil.which("winget"):
            write_cached_backend("winget")
            return "winget"
        raise BackendNotFoundError(
            "Windows detected but 'winget' was not found. Install 'App Installer' "
            "from the Microsoft Store, then try again."
        )

    # 3. Generic Package Managers Priority List
    # Maps the executable to check to the internal backend name
    priority_managers = [
        ("apt", "apt"),
        ("pacman", "pacman"),
        ("dnf", "dnf"),
        ("apk", "apk"),
        ("zypper", "zypper"),
        ("xbps-install", "xbps"),
        ("nix-env", "nix"),
        ("eopkg", "eopkg"),
        ("brew", "brew")
    ]

    for cmd, backend_name in priority_managers:
        if shutil.which(cmd):
            write_cached_backend(backend_name)
            return backend_name

    raise BackendNotFoundError(
        "Could not detect a supported package manager on this system."
    )