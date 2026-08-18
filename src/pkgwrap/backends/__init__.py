# src/pkgwrap/backends/__init__.py
"""Registry and factory for package manager backends.

Adding a new package manager means creating a module here that subclasses
:class:`~pkgwrap.backends.base.Backend` and registering it in ``_BACKENDS``.
Everything else - detection, cache validation and CLI routing - reads from
this registry, so no other file needs to change.
"""

from typing import Dict, List, Type

from pkgwrap.backends.apk_backend import ApkBackend
from pkgwrap.backends.apt_backend import AptBackend
from pkgwrap.backends.base import Backend
from pkgwrap.backends.brew_backend import BrewBackend
from pkgwrap.backends.choco_backend import ChocoBackend
from pkgwrap.backends.dnf_backend import DnfBackend
from pkgwrap.backends.eopkg_backend import EopkgBackend
from pkgwrap.backends.freebsd_backend import FreeBsdBackend
from pkgwrap.backends.gentoo_backend import GentooBackend
from pkgwrap.backends.macports_backend import MacPortsBackend
from pkgwrap.backends.nix_backend import NixBackend
from pkgwrap.backends.openbsd_backend import OpenBsdBackend
from pkgwrap.backends.pacman_backend import PacmanBackend
from pkgwrap.backends.pkg_backend import PkgBackend
from pkgwrap.backends.windows_backend import WindowsBackend
from pkgwrap.backends.xbps_backend import XbpsBackend
from pkgwrap.backends.yum_backend import YumBackend
from pkgwrap.backends.zypper_backend import ZypperBackend
from pkgwrap.errors import BackendNotFoundError

_BACKENDS: Dict[str, Type[Backend]] = {
    "apt": AptBackend,
    "pkg": PkgBackend,
    "pacman": PacmanBackend,
    "dnf": DnfBackend,
    "yum": YumBackend,
    "apk": ApkBackend,
    "brew": BrewBackend,
    "zypper": ZypperBackend,
    "xbps": XbpsBackend,
    "nix": NixBackend,
    "eopkg": EopkgBackend,
    "freebsd": FreeBsdBackend,
    "openbsd": OpenBsdBackend,
    "port": MacPortsBackend,
    "emerge": GentooBackend,
    "winget": WindowsBackend,
    "choco": ChocoBackend,
}


def available_backends() -> List[str]:
    """Return every registered backend name, sorted alphabetically."""
    return sorted(_BACKENDS)


def is_known_backend(name: str) -> bool:
    """Return True if ``name`` refers to a registered backend."""
    return name in _BACKENDS


def get_backend_class(name: str) -> Type[Backend]:
    """Return the class registered under ``name``.

    Raises:
        BackendNotFoundError: If the name is not registered.
    """
    backend_class = _BACKENDS.get(name)
    if backend_class is None:
        raise BackendNotFoundError(
            "Backend '{0}' is not recognized. Available backends: {1}.".format(
                name, ", ".join(available_backends())
            )
        )
    return backend_class


def get_executable(name: str) -> str:
    """Return the primary executable used to detect the given backend."""
    return get_backend_class(name).executable


def get_backend(name: str) -> Backend:
    """Return an instantiated backend by name.

    Raises:
        BackendNotFoundError: If the requested backend is not registered.
    """
    return get_backend_class(name)()
