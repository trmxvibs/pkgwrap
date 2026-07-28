"""OS and backend package manager detection with caching support.
Detects the system's package manager taking OS specific constraints into account.
"""

import os
import platform
import shutil

from pkgwrap.config import read_cached_backend, write_cached_backend
from pkgwrap.errors import BackendNotFoundError


def detect_backend() -> str:
    """Detects the available package manager on the system.

    Handles OS-specific logic (e.g., distinguishing FreeBSD 'pkg' from Termux 'pkg').
    Checks the cached backend first. If invalid or expired, checks system PATH
    using a strict priority order.

    Returns:
        str: The name of the detected backend identifier (e.g., 'apt', 'freebsd', 'xbps').

    Raises:
        BackendNotFoundError: If no supported package manager is found on the system.
    """
    system = platform.system()
    
    # Define priority order as a list of tuples: (backend_identifier, executable)
    candidates = []

    if system == "FreeBSD":
        candidates.append(("freebsd", "pkg"))
    else:
        # Check for Termux environment
        is_termux = system == "Linux" and "com.termux" in os.environ.get("PREFIX", "")
        
        if is_termux:
            candidates.append(("pkg", "pkg"))
            
        # Priority order for Linux and other platforms
        candidates.extend([
            ("apt", "apt"),
            ("pacman", "pacman"),
            ("dnf", "dnf"),
            ("apk", "apk"),
            ("zypper", "zypper"),
            ("xbps", "xbps-install"),
            ("nix", "nix-env"),
            ("eopkg", "eopkg"),
            ("brew", "brew")
        ])

    # Convert candidates to a dictionary for quick executable lookup by backend_name
    valid_backends = {b_name: exe for b_name, exe in candidates}

    cached_backend = read_cached_backend()
    if cached_backend and cached_backend in valid_backends:
        # Verify the cached command is still available in PATH
        executable = valid_backends[cached_backend]
        if shutil.which(executable):
            return cached_backend

    # Cache miss, expired, or executable removed; re-detect
    for b_name, exe in candidates:
        if shutil.which(exe):
            write_cached_backend(b_name)
            return b_name

    raise BackendNotFoundError(
        "No supported package manager could be found on this system."
    )