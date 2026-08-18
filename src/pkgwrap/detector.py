"""OS and package manager detection.

Detection order, highest priority first:

1. ``PKGWRAP_BACKEND`` environment variable (explicit user override).
2. A cached result, but only when it names a registered backend whose
   executable still exists on this machine.
3. Environment-specific checks (Termux, FreeBSD, OpenBSD/NetBSD, Windows,
   macOS) that would otherwise be ambiguous.
4. A prioritised probe of generic Linux package managers.
"""

import os
import platform
import shutil
from typing import List, Optional, Tuple

from pkgwrap.backends import get_executable, is_known_backend
from pkgwrap.config import read_cached_backend, write_cached_backend
from pkgwrap.errors import BackendNotFoundError
from pkgwrap.ui import print_warning

#: Probe order for generic Linux systems: (executable to look for, backend).
#: apt is checked first because Termux and FreeBSD are already handled above.
PRIORITY_MANAGERS: List[Tuple[str, str]] = [
    ("apt", "apt"),
    ("pacman", "pacman"),
    ("dnf", "dnf"),
    ("yum", "yum"),
    ("zypper", "zypper"),
    ("apk", "apk"),
    ("xbps-install", "xbps"),
    ("eopkg", "eopkg"),
    ("emerge", "emerge"),
    ("nix-env", "nix"),
    ("brew", "brew"),
]

ENV_OVERRIDE = "PKGWRAP_BACKEND"


def _is_termux() -> bool:
    """Return True when running inside Termux on Android."""
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix or os.environ.get("TERMUX_VERSION") is not None


def _cached_backend_if_valid() -> Optional[str]:
    """Return the cached backend when it is still registered and installed."""
    cached = read_cached_backend()
    if not cached:
        return None

    if not is_known_backend(cached):
        # Stale or hand-edited cache naming a backend we do not ship.
        return None

    if shutil.which(get_executable(cached)):
        return cached
    return None


def detect_backend(use_cache: bool = True) -> str:
    """Detect the native package manager for this system.

    Args:
        use_cache: When False, ignore any cached result and probe again.

    Returns:
        The identifier of the detected backend.

    Raises:
        BackendNotFoundError: If no supported package manager is found.
    """
    override = os.environ.get(ENV_OVERRIDE, "").strip()
    if override:
        if not is_known_backend(override):
            raise BackendNotFoundError(
                "{0} is set to '{1}', which is not a supported backend.".format(
                    ENV_OVERRIDE, override
                )
            )
        if not shutil.which(get_executable(override)):
            print_warning(
                "{0} is set to '{1}' but '{2}' was not found in PATH.".format(
                    ENV_OVERRIDE, override, get_executable(override)
                )
            )
        return override

    if use_cache:
        cached = _cached_backend_if_valid()
        if cached:
            return cached

    system = platform.system().lower()

    # 1. Termux ships an apt wrapper, so it must be caught before apt.
    if _is_termux() and shutil.which("pkg"):
        write_cached_backend("pkg")
        return "pkg"

    # 2. FreeBSD also has a 'pkg' command, but a completely different one.
    if system == "freebsd" and shutil.which("pkg"):
        write_cached_backend("freebsd")
        return "freebsd"

    # 3. OpenBSD and NetBSD use pkg_add / pkg_delete.
    if system in ("openbsd", "netbsd") and shutil.which("pkg_add"):
        write_cached_backend("openbsd")
        return "openbsd"

    # 4. Windows: winget first, Chocolatey as a fallback.
    if system == "windows":
        if shutil.which("winget"):
            write_cached_backend("winget")
            return "winget"
        if shutil.which("choco"):
            write_cached_backend("choco")
            return "choco"
        raise BackendNotFoundError(
            "Windows detected but neither 'winget' nor 'choco' was found. Install "
            "'App Installer' from the Microsoft Store (for winget) or Chocolatey, "
            "then try again."
        )

    # 5. macOS: Homebrew first, MacPorts second.
    if system == "darwin":
        if shutil.which("brew"):
            write_cached_backend("brew")
            return "brew"
        if shutil.which("port"):
            write_cached_backend("port")
            return "port"
        raise BackendNotFoundError(
            "macOS detected but no package manager was found. Install Homebrew "
            "from https://brew.sh (or MacPorts), then try again."
        )

    # 6. Generic Linux and anything else.
    for executable, backend_name in PRIORITY_MANAGERS:
        if shutil.which(executable):
            write_cached_backend(backend_name)
            return backend_name

    raise BackendNotFoundError(
        "Could not detect a supported package manager on this system. "
        "Set {0} to force one of: {1}.".format(
            ENV_OVERRIDE, ", ".join(name for _, name in PRIORITY_MANAGERS)
        )
    )
