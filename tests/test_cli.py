"""Tests for CLI parsing, routing and exit codes."""

from unittest.mock import MagicMock, patch

import pytest

from pkgwrap.cli import main
from pkgwrap.errors import CommandExecutionError, UserCancelledError


@pytest.fixture
def backend():
    """Patch detection and the registry, yielding the mocked backend."""
    mock_backend = MagicMock()
    with patch("pkgwrap.cli.detect_backend", return_value="apt"), \
         patch("pkgwrap.cli.get_backend", return_value=mock_backend), \
         patch("pkgwrap.cli._is_root", return_value=False):
        yield mock_backend


@pytest.mark.parametrize("alias", ["install", "in", "add"])
def test_install_aliases(backend, alias):
    assert main([alias, "curl"]) == 0
    backend.install.assert_called_once()
    assert backend.install.call_args[0][0] == ["curl"]


@pytest.mark.parametrize("alias", ["remove", "uninstall", "del", "rm"])
def test_remove_aliases(backend, alias):
    assert main([alias, "curl"]) == 0
    backend.remove.assert_called_once()


@pytest.mark.parametrize("alias", ["upgrade", "up", "update"])
def test_upgrade_aliases(backend, alias):
    assert main([alias]) == 0
    backend.upgrade.assert_called_once()


@pytest.mark.parametrize("alias", ["refresh", "sync"])
def test_refresh_aliases(backend, alias):
    assert main([alias]) == 0
    backend.refresh.assert_called_once()
    backend.upgrade.assert_not_called()


@pytest.mark.parametrize("alias", ["search", "find"])
def test_search_aliases(backend, alias):
    assert main([alias, "curl"]) == 0
    assert backend.search.call_args[0][0] == "curl"


def test_list_and_info_and_clean(backend):
    assert main(["list"]) == 0
    backend.list_installed.assert_called_once()
    assert main(["info", "curl"]) == 0
    assert backend.info.call_args[0][0] == "curl"
    assert main(["clean"]) == 0
    backend.clean.assert_called_once()


def test_multiple_packages_are_accepted(backend):
    assert main(["install", "curl", "wget", "nmap"]) == 0
    assert backend.install.call_args[0][0] == ["curl", "wget", "nmap"]


def test_duplicate_packages_are_collapsed(backend):
    assert main(["install", "curl", "curl"]) == 0
    assert backend.install.call_args[0][0] == ["curl"]


def test_yes_flag_is_forwarded(backend):
    assert main(["install", "curl", "-y"]) == 0
    assert backend.install.call_args[1]["auto_yes"] is True


def test_dry_run_flag_is_forwarded(backend):
    assert main(["install", "curl", "--dry-run"]) == 0
    assert backend.install.call_args[1]["dry_run"] is True


def test_package_name_mapping_is_applied(backend):
    assert main(["install", "pip"]) == 0
    assert backend.install.call_args[0][0] == ["python3-pip"]


def test_flag_like_package_is_rejected(backend, capsys):
    # argparse itself rejects a leading dash before we ever reach validation.
    with pytest.raises(SystemExit):
        main(["install", "--force-yes"])


def test_backend_flag_alone_reports_detection(backend, capsys):
    assert main(["--backend"]) == 0
    assert "apt" in capsys.readouterr().out


def test_backend_flag_with_command_is_an_error_not_a_silent_skip(backend):
    """Previously `--backend install nmap` printed the backend and silently
    skipped the install. Now the ambiguous form is rejected outright."""
    with pytest.raises(SystemExit) as excinfo:
        main(["--backend", "install", "nmap"])
    assert excinfo.value.code == 2
    backend.install.assert_not_called()


def test_backend_override_is_used():
    mock_backend = MagicMock()
    with patch("pkgwrap.cli.get_backend", return_value=mock_backend) as get, \
         patch("pkgwrap.cli.detect_backend") as detect, \
         patch("pkgwrap.cli._is_root", return_value=False):
        assert main(["--backend", "pacman", "install", "nmap"]) == 0
    detect.assert_not_called()
    get.assert_called_once_with("pacman")


@pytest.mark.parametrize("command", ["full-upgrade", "dist-upgrade", "nonsense"])
def test_unknown_commands_still_exit_with_2(command):
    with pytest.raises(SystemExit) as excinfo:
        main([command])
    assert excinfo.value.code == 2


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "usage" in capsys.readouterr().out.lower()


def test_user_cancellation_exit_code(backend):
    backend.install.side_effect = UserCancelledError("nope")
    assert main(["install", "curl"]) == 4


def test_command_failure_propagates_exit_code(backend):
    backend.install.side_effect = CommandExecutionError("apt install curl", 100)
    assert main(["install", "curl"]) == 100


def test_signal_death_becomes_128_plus_n(backend):
    backend.install.side_effect = CommandExecutionError("apt install curl", -9)
    assert main(["install", "curl"]) == 137


def test_keyboard_interrupt_exit_code(backend):
    backend.install.side_effect = KeyboardInterrupt()
    assert main(["install", "curl"]) == 130


def test_clear_cache_flag():
    with patch("pkgwrap.cli.clear_cache", return_value=True) as clear:
        assert main(["--clear-cache"]) == 0
    clear.assert_called_once()


def test_no_cache_flag_is_forwarded():
    mock_backend = MagicMock()
    with patch("pkgwrap.cli.get_backend", return_value=mock_backend), \
         patch("pkgwrap.cli.detect_backend", return_value="apt") as detect, \
         patch("pkgwrap.cli._is_root", return_value=False):
        assert main(["--no-cache", "install", "curl"]) == 0
    assert detect.call_args[1]["use_cache"] is False
