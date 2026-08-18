"""Regression tests for command shapes confirmed against upstream documentation.

Each test here exists because the command it pins was wrong at some point, or
because getting it wrong would be dangerous. The docstrings record *why* the
shape is what it is, so a future change has to argue with the reason rather
than just the assertion.
"""

from unittest.mock import patch

import pytest

from pkgwrap.backends.choco_backend import ChocoBackend
from pkgwrap.backends.gentoo_backend import GentooBackend
from pkgwrap.backends.macports_backend import MacPortsBackend
from pkgwrap.backends.openbsd_backend import OpenBsdBackend
from pkgwrap.backends.yum_backend import YumBackend


def _command(backend, method, *args, **kwargs):
    with patch.object(type(backend), "_run_command") as run:
        getattr(backend, method)(*args, **kwargs)
    return list(run.call_args[0][0]), run.call_args[1]


# ---------------------------------------------------------------------------
# Chocolatey
# ---------------------------------------------------------------------------


def test_choco_list_does_not_pass_local_only():
    """Chocolatey CLI v2.0.0 removed --local-only / -lo.

    Passing it is rejected with 'Invalid argument --local-only', so the flag
    must never come back. On v2+ a bare `choco list` already lists only
    locally installed packages.
    """
    command, _ = _command(ChocoBackend(), "list_installed")
    assert command == ["choco", "list"]
    assert "--local-only" not in command
    assert "-lo" not in command


def test_choco_search_is_used_for_remote_queries():
    """From v2.0.0, remote package queries must use `choco search`."""
    command, _ = _command(ChocoBackend(), "search", "curl")
    assert command == ["choco", "search", "curl"]


def test_choco_install_and_remove():
    command, _ = _command(ChocoBackend(), "install", ["curl"], auto_yes=True)
    assert command == ["choco", "install", "-y", "curl"]

    command, _ = _command(ChocoBackend(), "remove", ["curl"], auto_yes=True)
    assert command == ["choco", "uninstall", "-y", "curl"]


# ---------------------------------------------------------------------------
# Gentoo / Portage
# ---------------------------------------------------------------------------


def test_gentoo_remove_uses_depclean_not_unmerge():
    """--unmerge (-C) removes packages without checking what depends on them.

    The Gentoo wiki warns that it can remove packages the system needs, with
    no warning. --depclean is the dependency-aware removal: it refuses to
    remove anything still required. pkgwrap must never emit --unmerge.
    """
    command, _ = _command(GentooBackend(), "remove", ["nano"])
    assert "--depclean" in command
    assert "--unmerge" not in command
    assert "-C" not in command
    assert command[-1] == "nano"


def test_gentoo_asks_before_acting_when_not_auto_yes():
    """emerge installs immediately with no confirmation unless --ask is given."""
    command, _ = _command(GentooBackend(), "install", ["nano"])
    assert "--ask" in command

    command, _ = _command(GentooBackend(), "install", ["nano"], auto_yes=True)
    assert "--ask" not in command


def test_gentoo_upgrade_is_the_documented_world_update():
    command, _ = _command(GentooBackend(), "upgrade", auto_yes=True)
    assert command == ["emerge", "--update", "--deep", "--newuse", "@world"]


# ---------------------------------------------------------------------------
# OpenBSD / NetBSD
# ---------------------------------------------------------------------------


def test_openbsd_uses_capital_i_for_non_interactive():
    """pkg_add(1)/pkg_delete(1): -I forces non-interactive mode.

    Lowercase -i means the opposite (force interactive), so the case matters.
    """
    command, _ = _command(OpenBsdBackend(), "install", ["curl"], auto_yes=True)
    assert command == ["pkg_add", "-I", "curl"]

    command, _ = _command(OpenBsdBackend(), "remove", ["curl"], auto_yes=True)
    assert command == ["pkg_delete", "-I", "curl"]


def test_openbsd_stays_interactive_without_yes():
    """Without -y, pkg_add must be left to prompt on ambiguous choices."""
    command, kwargs = _command(OpenBsdBackend(), "install", ["curl"])
    assert command == ["pkg_add", "curl"]

    _, kwargs = _command(OpenBsdBackend(), "remove", ["curl"])
    assert kwargs.get("confirm")


def test_openbsd_upgrade_uses_pkg_add_u():
    command, _ = _command(OpenBsdBackend(), "upgrade", auto_yes=True)
    assert command == ["pkg_add", "-u", "-I"]


# ---------------------------------------------------------------------------
# MacPorts and yum
# ---------------------------------------------------------------------------


def test_macports_commands():
    command, _ = _command(MacPortsBackend(), "install", ["curl"])
    assert command == ["port", "install", "curl"]

    command, kwargs = _command(MacPortsBackend(), "remove", ["curl"])
    assert command == ["port", "uninstall", "curl"]
    # port does not prompt, so pkgwrap must add its own confirmation.
    assert kwargs.get("confirm")


def test_yum_refresh_uses_makecache_not_check_update():
    """`yum check-update` exits with status 100 when updates are available.

    That would be reported as a command failure, so makecache is used instead.
    """
    command, _ = _command(YumBackend(), "refresh")
    assert command == ["yum", "makecache"]
    assert "check-update" not in command


@pytest.mark.parametrize("method,expected", [
    ("install", ["yum", "install", "-y", "curl"]),
    ("remove", ["yum", "remove", "-y", "curl"]),
])
def test_yum_install_remove(method, expected):
    command, _ = _command(YumBackend(), method, ["curl"], auto_yes=True)
    assert command == expected