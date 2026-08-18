"""Configuration and backend caching for pkgwrap.

The detected backend is cached so repeated invocations do not have to probe
the filesystem again. Every read is defensive: a missing, unreadable,
corrupted or outdated cache simply means "detect again", never a crash.
"""

import json
import os
import platform
from typing import Any, Dict, Optional

from pkgwrap.ui import print_warning

#: Bumped whenever the on-disk cache format changes, so old files are ignored
#: instead of being misinterpreted.
CACHE_VERSION = 2

CACHE_FILENAME = "backend.json"


def get_config_dir(create: bool = True) -> Optional[str]:
    """Return the pkgwrap configuration directory.

    Uses ``%APPDATA%\\pkgwrap`` on Windows, ``$XDG_CONFIG_HOME/pkgwrap`` when
    set, and ``~/.config/pkgwrap`` otherwise.

    Args:
        create: Whether to create the directory when it does not exist.

    Returns:
        The directory path, or None if it cannot be created.
    """
    if platform.system().lower() == "windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_dir = os.path.join(appdata, "pkgwrap")
        else:
            config_dir = os.path.expanduser(os.path.join("~", "AppData", "Roaming", "pkgwrap"))
    else:
        xdg_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_home:
            config_dir = os.path.join(xdg_home, "pkgwrap")
        else:
            config_dir = os.path.expanduser(os.path.join("~", ".config", "pkgwrap"))

    if not create:
        return config_dir

    try:
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    except Exception as exc:
        print_warning(
            "Could not create config directory '{0}' ({1}). Caching disabled.".format(
                config_dir, exc
            )
        )
        return None


def get_cache_file(create: bool = True) -> Optional[str]:
    """Return the path of the backend cache file, or None if unavailable."""
    config_dir = get_config_dir(create=create)
    if config_dir is None:
        return None
    return os.path.join(config_dir, CACHE_FILENAME)


def read_cache() -> Optional[Dict[str, Any]]:
    """Return the raw cache payload, or None when it is unusable."""
    cache_file = get_cache_file(create=False)
    if not cache_file or not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        # Corrupted JSON, permission problems, partial writes: fall back to
        # re-detection rather than failing the user's command.
        return None

    if not isinstance(data, dict):
        return None
    if data.get("version") != CACHE_VERSION:
        return None
    return data


def read_cached_backend() -> Optional[str]:
    """Return the cached backend name, or None if there is no usable cache.

    The value is only returned when it is a plain string; validating that the
    name is actually a registered backend is the detector's job (this module
    must not import the registry, to avoid a circular import).
    """
    data = read_cache()
    if data is None:
        return None

    backend = data.get("backend")
    if isinstance(backend, str) and backend.strip():
        return backend.strip()
    return None


def write_cached_backend(backend_name: str) -> None:
    """Persist the detected backend, warning but never failing on error."""
    cache_file = get_cache_file()
    if not cache_file:
        return

    payload = {"version": CACHE_VERSION, "backend": backend_name}

    try:
        with open(cache_file, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except Exception as exc:
        print_warning("Could not write cache file '{0}' ({1}).".format(cache_file, exc))


def clear_cache() -> bool:
    """Delete the cache file.

    Returns:
        True if a cache file was removed, False if there was nothing to do.
    """
    cache_file = get_cache_file(create=False)
    if not cache_file or not os.path.exists(cache_file):
        return False

    try:
        os.remove(cache_file)
        return True
    except Exception as exc:
        print_warning("Could not remove cache file '{0}' ({1}).".format(cache_file, exc))
        return False
