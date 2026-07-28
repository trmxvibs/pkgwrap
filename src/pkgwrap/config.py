"""Configuration and cache management for pkgwrap.
Handles storing and retrieving the detected backend from ~/.config/pkgwrap/backend.json.
"""

import json
import time
from pathlib import Path
from typing import Optional

CACHE_EXPIRY_SECONDS = 7 * 24 * 60 * 60  # 7 days in seconds


def get_config_dir() -> Path:
    """Gets the path to the pkgwrap configuration directory.

    Creates the directory if it does not exist.

    Returns:
        Path: The pathlib.Path object representing the configuration directory.
    """
    config_dir = Path.home() / ".config" / "pkgwrap"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_file() -> Path:
    """Gets the path to the backend cache file.

    Returns:
        Path: The pathlib.Path object representing the cache file.
    """
    return get_config_dir() / "backend.json"


def read_cached_backend() -> Optional[str]:
    """Reads the cached backend name if it is still valid.

    Checks ~/.config/pkgwrap/backend.json. If the file exists, is valid JSON,
    contains the required fields, and the timestamp is less than 7 days old,
    it returns the backend name. Otherwise, it returns None.

    Returns:
        Optional[str]: The cached backend name, or None if the cache is expired/missing.
    """
    cache_file = get_cache_file()
    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        backend_name = data.get("backend")
        timestamp = data.get("timestamp")

        if not backend_name or not isinstance(timestamp, (int, float)):
            return None

        current_time = time.time()
        if current_time - timestamp > CACHE_EXPIRY_SECONDS:
            return None  # Cache expired

        return str(backend_name)
    except (json.JSONDecodeError, OSError):
        return None


def write_cached_backend(backend_name: str) -> None:
    """Writes the detected backend name and current timestamp to the cache.

    Args:
        backend_name (str): The name of the detected backend (e.g., 'apt', 'pacman').
    """
    cache_file = get_cache_file()
    data = {
        "backend": backend_name,
        "timestamp": time.time()
    }

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        # If cache writing fails (e.g., due to permissions), we fail silently
        # to prevent disrupting the core application functionality.
        pass