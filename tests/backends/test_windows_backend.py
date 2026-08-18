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


def test_install_already_up_to_date_is_treated_as_success(backend):
    """winget install on an already-current package fails with a specific
    exit code (0x8A15002B, APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE).
    From the user's perspective the package they asked for is already
    there, so this must not surface as a pkgwrap error."""
    from pkgwrap.errors import CommandExecutionError

    with patch.object(
        WindowsBackend,
        "_run_command",
        side_effect=CommandExecutionError("winget install nmap", 2316632107),
    ):
        result = backend.install(["nmap"])
    assert result.returncode == 0


def test_upgrade_already_up_to_date_is_treated_as_success(backend):
    from pkgwrap.errors import CommandExecutionError

    with patch.object(
        WindowsBackend,
        "_run_command",
        side_effect=CommandExecutionError("winget upgrade --all", -1978335189),
    ):
        result = backend.upgrade()
    assert result.returncode == 0


def test_other_winget_failures_still_raise(backend):
    """Only the specific no-applicable-update code is absorbed; every other
    failure must still propagate as a real error."""
    from pkgwrap.errors import CommandExecutionError

    with patch.object(
        WindowsBackend,
        "_run_command",
        side_effect=CommandExecutionError("winget install nmap", 1),
    ):
        with pytest.raises(CommandExecutionError):
            backend.install(["nmap"])
