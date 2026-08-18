"""Focused tests for the winget backend."""

from unittest.mock import patch

import pytest

from pkgwrap.backends.windows_backend import WindowsBackend


@pytest.fixture
def backend():
    return WindowsBackend()


def test_metadata(backend):
    assert backend.name == "winget"
    assert backend.executable == "winget"
    # Windows has no sudo; winget raises its own UAC prompt.
    assert backend.requires_root is False


def test_install_plain(backend):
    with patch.object(WindowsBackend, "_run_command") as run:
        backend.install(["nmap"])
    assert run.call_args[0][0] == ["winget", "install", "nmap"]
    assert run.call_args[1]["require_sudo"] is False


def test_install_auto_yes_adds_agreement_flags(backend):
    with patch.object(WindowsBackend, "_run_command") as run:
        backend.install(["nmap"], auto_yes=True)
    command = run.call_args[0][0]
    assert "--accept-package-agreements" in command
    assert "--disable-interactivity" in command
    assert command[-1] == "nmap"


def test_remove_asks_for_confirmation(backend):
    with patch.object(WindowsBackend, "_run_command") as run:
        backend.remove(["nmap"])
    assert run.call_args[1]["confirm"]


def test_clean_is_unsupported(backend):
    from pkgwrap.errors import UnsupportedOperationError

    with pytest.raises(UnsupportedOperationError):
        backend.clean()
