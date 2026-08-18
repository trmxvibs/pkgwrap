"""Shared pytest fixtures.

Every test runs against a temporary config directory so a developer's real
``~/.config/pkgwrap/backend.json`` is never read or written by the suite.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Point pkgwrap's config directory at a throwaway location."""
    config_home = tmp_path / "config"
    config_home.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.setenv("APPDATA", str(config_home))
    monkeypatch.delenv("PKGWRAP_BACKEND", raising=False)
    # os.path.expanduser reads HOME on POSIX but USERPROFILE on Windows, so
    # both must be redirected or the suite would touch the developer's real
    # home directory when a test forces the opposite platform.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    return config_home


@pytest.fixture
def not_root(monkeypatch):
    """Pretend the current process is an unprivileged user."""
    monkeypatch.setattr(os, "geteuid", lambda: 1000, raising=False)
