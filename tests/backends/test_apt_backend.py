"""Focused tests for the APT backend's exact command shapes."""

from unittest.mock import call, patch

import pytest

from pkgwrap.backends.apt_backend import AptBackend


@pytest.fixture
def backend():
    return AptBackend()


def test_name_and_executable(backend):
    assert backend.name == "apt"
    assert backend.executable == "apt"
    assert backend.requires_root is True


def test_install_without_yes_keeps_apt_prompt(backend):
    with patch.object(AptBackend, "_run_command") as run:
        backend.install(["cowsay"])
    assert run.call_args[0][0] == ["apt", "install", "cowsay"]
    assert run.call_args[1]["require_sudo"] is True


def test_install_with_yes_adds_the_flag(backend):
    with patch.object(AptBackend, "_run_command") as run:
        backend.install(["cowsay"], auto_yes=True)
    assert run.call_args[0][0] == ["apt", "install", "-y", "cowsay"]


def test_remove_multiple_packages(backend):
    with patch.object(AptBackend, "_run_command") as run:
        backend.remove(["cowsay", "sl"], auto_yes=True)
    assert run.call_args[0][0] == ["apt", "remove", "-y", "cowsay", "sl"]


def test_refresh_and_upgrade_are_separate_operations(backend):
    """`refresh` must never upgrade anything - that surprised users before."""
    with patch.object(AptBackend, "_run_command") as run:
        backend.refresh()
    assert run.call_args_list == [
        call(
            ["apt", "update"],
            require_sudo=True,
            already_root=False,
            auto_yes=False,
            dry_run=False,
        )
    ]

    with patch.object(AptBackend, "_run_command") as run:
        backend.upgrade(auto_yes=True)
    assert run.call_args[0][0] == ["apt", "upgrade", "-y"]


def test_search_does_not_require_sudo(backend):
    with patch.object(AptBackend, "_run_command") as run:
        backend.search("cowsay")
    assert run.call_args[0][0] == ["apt", "search", "cowsay"]
    assert run.call_args[1]["require_sudo"] is False


def test_list_and_info(backend):
    with patch.object(AptBackend, "_run_command") as run:
        backend.list_installed()
    assert run.call_args[0][0] == ["apt", "list", "--installed"]

    with patch.object(AptBackend, "_run_command") as run:
        backend.info("cowsay")
    assert run.call_args[0][0] == ["apt", "show", "cowsay"]
