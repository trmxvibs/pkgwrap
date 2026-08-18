"""Tests for the configuration directory and backend cache."""

import json
import os
from unittest.mock import patch

from pkgwrap import config


def test_unix_config_dir_uses_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with patch("pkgwrap.config.platform.system", return_value="Linux"):
        assert config.get_config_dir() == os.path.join(str(tmp_path), "pkgwrap")


def test_unix_config_dir_falls_back_to_home(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    # Set both: expanduser("~") consults HOME on POSIX and USERPROFILE on
    # Windows. Setting only HOME let this test escape to the real home
    # directory when the suite ran on Windows.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with patch("pkgwrap.config.platform.system", return_value="Linux"):
        config_dir = config.get_config_dir()
    assert config_dir is not None
    assert config_dir.endswith(os.path.join(".config", "pkgwrap"))
    assert str(tmp_path) in config_dir


def test_windows_config_dir_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    with patch("pkgwrap.config.platform.system", return_value="Windows"):
        assert config.get_config_dir() == os.path.join(str(tmp_path), "pkgwrap")


def test_windows_config_dir_without_appdata(monkeypatch, tmp_path):
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with patch("pkgwrap.config.platform.system", return_value="Windows"):
        config_dir = config.get_config_dir()
    assert config_dir is not None
    assert config_dir.endswith(os.path.join("AppData", "Roaming", "pkgwrap"))


def test_unwritable_config_dir_disables_caching_without_crashing():
    with patch("pkgwrap.config.os.makedirs", side_effect=PermissionError("denied")), \
         patch("pkgwrap.config.print_warning") as warn:
        assert config.get_config_dir() is None
        assert config.get_cache_file() is None
        assert config.read_cached_backend() is None
        config.write_cached_backend("apt")  # must not raise
    assert warn.called


def test_write_then_read_round_trip():
    config.write_cached_backend("apt")
    assert config.read_cached_backend() == "apt"


def test_corrupted_cache_is_ignored():
    cache_file = config.get_cache_file()
    with open(cache_file, "w", encoding="utf-8") as handle:
        handle.write("{ this is not json")
    assert config.read_cached_backend() is None


def test_cache_from_an_older_format_is_ignored():
    cache_file = config.get_cache_file()
    with open(cache_file, "w", encoding="utf-8") as handle:
        json.dump({"backend": "apt"}, handle)  # no version key
    assert config.read_cached_backend() is None


def test_non_string_backend_is_ignored():
    cache_file = config.get_cache_file()
    with open(cache_file, "w", encoding="utf-8") as handle:
        json.dump({"version": config.CACHE_VERSION, "backend": 42}, handle)
    assert config.read_cached_backend() is None


def test_clear_cache():
    config.write_cached_backend("apt")
    assert config.clear_cache() is True
    assert config.read_cached_backend() is None
    assert config.clear_cache() is False