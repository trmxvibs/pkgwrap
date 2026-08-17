# src/pkgwrap/backends/__init__.py
"""Registry and factory for package manager backends.
Maps string identifiers to their respective Backend implementations.
"""

from typing import Dict, Type

from pkgwrap.backends.base import Backend
from pkgwrap.backends.apt_backend import AptBackend
from pkgwrap.backends.pkg_backend import PkgBackend
from pkgwrap.backends.pacman_backend import PacmanBackend
from pkgwrap.backends.dnf_backend import DnfBackend
from pkgwrap.backends.apk_backend import ApkBackend
from pkgwrap.backends.brew_backend import BrewBackend
from pkgwrap.backends.zypper_backend import ZypperBackend
from pkgwrap.backends.xbps_backend import XbpsBackend
from pkgwrap.backends.nix_backend import NixBackend
from pkgwrap.backends.eopkg_backend import EopkgBackend
from pkgwrap.backends.freebsd_backend import FreeBsdBackend
from pkgwrap.backends.windows_backend import WindowsBackend
from pkgwrap.errors import BackendNotFoundError

# Map backend string names to their respective classes
_BACKENDS: Dict[str, Type[Backend]] = {
    "apt": AptBackend,
    "pkg": PkgBackend,
    "pacman": PacmanBackend,
    "dnf": DnfBackend,
    "apk": ApkBackend,
    "brew": BrewBackend,
    "zypper": ZypperBackend,
    "xbps": XbpsBackend,
    "nix": NixBackend,
    "eopkg": EopkgBackend,
    "freebsd": FreeBsdBackend,
    "winget": WindowsBackend,
}


def get_backend(name: str) -> Backend:
    """Retrieves an instantiated backend by its name.

    Args:
        name (str): The identifier of the backend (e.g., 'apt', 'pacman').

    Returns:
        Backend: An instance of the requested backend.

    Raises:
        BackendNotFoundError: If the requested backend is not registered.
    """
    backend_class = _BACKENDS.get(name)
    if not backend_class:
        raise BackendNotFoundError(f"Backend '{name}' is not recognized or supported.")
    
    return backend_class()