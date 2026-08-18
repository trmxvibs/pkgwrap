"""Configuration and caching module for pkgwrap.
Handles reading and writing the detected backend to a cache file
to speed up subsequent executions. Includes graceful fallbacks for
environments where directory creation is restricted.
"""

import json
import os
import platform
from typing import Optional

try:
    from pkgwrap.ui import print_warning
except ImportError:
    # Fallback to print_info or print_error if print_warning isn't explicitly defined in ui.py
    from pkgwrap.ui import print_info as print_warning


def get_config_dir() -> Optional[str]:
    """Get the path to the configuration directory for pkgwrap.
    Uses %APPDATA%/pkgwrap on Windows, and ~/.config/pkgwrap on Unix-like systems.
    Creates the directory if it does not exist.

    Returns:
        str: The path to the config directory, or None if creation fails.
    """
    if platform.system().lower() == "windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_dir = os.path.join(appdata, "pkgwrap")
        else:
            # Fallback if APPDATA is somehow missing from environment
            config_dir = os.path.expanduser(os.path.join("~", "AppData", "Roaming", "pkgwrap"))
    else:
        config_dir = os.path.expanduser(os.path.join("~", ".config", "pkgwrap"))

    try:
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    except Exception as e:
        print_warning(f"Warning: Could not create config directory '{config_dir}' ({e}). Caching disabled.")
        return None


def get_cache_file() -> Optional[str]:
    """Get the path to the backend cache file.

    Returns:
        str: The path to the cache file, or None if the config dir is unavailable.
    """
    config_dir = get_config_dir()
    if config_dir is None:
        return None
    return os.path.join(config_dir, "backend.json")


def read_cached_backend() -> Optional[str]:
    """Read the detected backend from the cache file.

    Returns:
        str: The name of the cached backend, or None if not found or unreadable.
    """
    cache_file = get_cache_file()
    if not cache_file or not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("backend")
    except Exception:
        # Silently fail on read errors (corrupted JSON, permissions, etc.)
        # so we can seamlessly fall back to re-detecting.
        return None


def write_cached_backend(backend_name: str) -> None:
    """Write the detected backend to the cache file.

    Args:
        backend_name (str): The name of the backend to cache.
    """
    cache_file = get_cache_file()
    if not cache_file:
        return

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"backend": backend_name}, f)
    except Exception as e:
        # Don't crash the program if writing to the cache fails
        print_warning(f"Warning: Could not write cache file '{cache_file}' ({e}).")