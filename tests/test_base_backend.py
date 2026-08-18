"""Tests for Backend._run_command - privilege escalation, prompts, dry runs.

This is the most safety-critical code in pkgwrap, so each branch is covered
explicitly.
"""

import subprocess
from unittest.mock import patch

import pytest

from pkgwrap.backends.base import Backend
from pkgwrap.errors import (
    CommandExecutionError,
    SudoNotAvailableError,
    UnsupportedOperationError,
    UserCancelledError,
)


class DummyBackend(Backend):
    """Minimal concrete backend used purely to exercise the base class."""

    name = "dummy"
    executable = "dummy"

    def install(self, packages, already_root=False, auto_yes=False, dry_run=False):
        return self._run_command(["dummy", "install"] + list(packages), require_sudo=True,
                                 already_root=already_root, auto_yes=auto_yes, dry_run=dry_run)

    def remove(self, packages, already_root=False, auto_yes=False, dry_run=False):
        return self._run_command(["dummy", "remove"] + list(packages), require_sudo=True,
                                 already_root=already_root, auto_yes=auto_yes, dry_run=dry_run)

    def refresh(self, already_root=False, auto_yes=False, dry_run=False):
        return self._run_command(["dummy", "refresh"], require_sudo=True,
                                 already_root=already_root, auto_yes=auto_yes, dry_run=dry_run)

    def upgrade(self, already_root=False, auto_yes=False, dry_run=False):
        return self._run_command(["dummy", "upgrade"], require_sudo=True,
                                 already_root=already_root, auto_yes=auto_yes, dry_run=dry_run)

    def search(self, query, already_root=False, auto_yes=False, dry_run=False):
        return self._run_command(["dummy", "search", query], require_sudo=False,
                                 already_root=already_root, auto_yes=auto_yes, dry_run=dry_run)


@pytest.fixture
def backend():
    return DummyBackend()


@pytest.fixture
def sudo_available():
    with patch("pkgwrap.backends.base.shutil.which", return_value="/usr/bin/sudo") as mock:
        yield mock


def _completed(returncode=0):
    return subprocess.CompletedProcess(["dummy"], returncode)


def test_sudo_prefix_added_when_not_root(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=True):
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()) as run:
            backend.install(["nmap"])
    assert run.call_args[0][0][0] == "sudo"


def test_no_sudo_prefix_when_already_root(backend):
    with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()) as run:
        backend.install(["nmap"], already_root=True)
    assert run.call_args[0][0] == ["dummy", "install", "nmap"]


def test_confirmation_required_without_yes(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=True) as ask:
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()):
            backend.install(["nmap"])
    ask.assert_called_once()


def test_declined_confirmation_raises_and_runs_nothing(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=False):
        with patch("pkgwrap.backends.base.subprocess.run") as run:
            with pytest.raises(UserCancelledError):
                backend.install(["nmap"])
    run.assert_not_called()


def test_auto_yes_skips_the_prompt(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation") as ask:
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()):
            backend.install(["nmap"], auto_yes=True)
    ask.assert_not_called()


def test_extra_confirm_prompt_is_asked(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=True) as ask:
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()):
            backend._run_command(["dummy", "del"], require_sudo=False, confirm="Remove x?")
    assert ask.call_args[0][0] == "Remove x?"


def test_dry_run_executes_nothing(backend):
    with patch("pkgwrap.backends.base.subprocess.run") as run:
        with patch("pkgwrap.backends.base.ask_confirmation") as ask:
            result = backend.install(["nmap"], dry_run=True)
    run.assert_not_called()
    ask.assert_not_called()
    assert result.returncode == 0


def test_missing_sudo_raises_clear_error(backend):
    with patch("pkgwrap.backends.base.shutil.which", return_value=None):
        with patch("pkgwrap.backends.base.subprocess.run") as run:
            with pytest.raises(SudoNotAvailableError):
                backend.install(["nmap"])
    run.assert_not_called()


def test_nonzero_exit_raises_command_execution_error(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=True):
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed(100)):
            with pytest.raises(CommandExecutionError) as excinfo:
                backend.install(["nmap"])
    assert excinfo.value.returncode == 100


def test_missing_executable_reports_127(backend):
    with patch("pkgwrap.backends.base.subprocess.run", side_effect=FileNotFoundError("dummy")):
        with pytest.raises(CommandExecutionError) as excinfo:
            backend.search("nmap")
    assert excinfo.value.returncode == 127


def test_shell_is_never_used(backend, sudo_available):
    with patch("pkgwrap.backends.base.ask_confirmation", return_value=True):
        with patch("pkgwrap.backends.base.subprocess.run", return_value=_completed()) as run:
            backend.install(["nmap"])
    assert run.call_args[1]["shell"] is False


def test_optional_operations_raise_unsupported(backend):
    with pytest.raises(UnsupportedOperationError):
        backend.list_installed()
    with pytest.raises(UnsupportedOperationError):
        backend.info("nmap")
    with pytest.raises(UnsupportedOperationError):
        backend.clean()
