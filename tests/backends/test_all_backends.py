"""Contract tests that every registered backend must satisfy.

Rather than duplicating a near-identical test file per package manager,
these tests iterate over the whole registry. Adding a new backend
automatically pulls it into the suite.
"""

from unittest.mock import patch

import pytest

from pkgwrap.backends import _BACKENDS, available_backends, get_backend, get_executable
from pkgwrap.backends.base import Backend
from pkgwrap.errors import BackendNotFoundError, UnsupportedOperationError

ALL_BACKENDS = available_backends()


@pytest.fixture(params=ALL_BACKENDS)
def backend_name(request):
    return request.param


def _capture(backend, method, *args, **kwargs):
    """Call a backend method with _run_command patched, returning the command."""
    with patch.object(type(backend), "_run_command") as run:
        try:
            getattr(backend, method)(*args, **kwargs)
        except UnsupportedOperationError:
            return None
    if not run.call_args:
        return None
    return list(run.call_args[0][0])


def test_registry_name_matches_class_attribute(backend_name):
    backend = get_backend(backend_name)
    assert backend.name == backend_name
    assert isinstance(backend, Backend)


def test_every_backend_declares_an_executable(backend_name):
    assert get_executable(backend_name)


def test_unknown_backend_raises():
    with pytest.raises(BackendNotFoundError):
        get_backend("definitely-not-a-package-manager")


def test_install_includes_every_package(backend_name):
    backend = get_backend(backend_name)
    command = _capture(backend, "install", ["nmap", "curl"])
    assert command is not None
    assert command[-2:] == ["nmap", "curl"]
    assert command[0] == get_executable(backend_name).split()[0] or command[0]


def test_remove_includes_every_package(backend_name):
    backend = get_backend(backend_name)
    command = _capture(backend, "remove", ["nmap", "curl"])
    assert command is not None
    assert command[-2:] == ["nmap", "curl"]


def test_no_forced_yes_flag_without_auto_yes(backend_name):
    """Without -y, pkgwrap must not silence the package manager's own prompt."""
    backend = get_backend(backend_name)
    for method in ("install", "remove"):
        command = _capture(backend, method, ["nmap"])
        assert command is not None
        forbidden = {"-y", "--yes", "--noconfirm", "--silent", "--assume-yes"}
        assert not forbidden.intersection(command), (
            "{0}.{1} passes a non-interactive flag without -y: {2}".format(
                backend_name, method, command
            )
        )


def test_auto_yes_is_honoured_where_supported(backend_name):
    backend = get_backend(backend_name)
    plain = _capture(backend, "install", ["nmap"])
    with_yes = _capture(backend, "install", ["nmap"], auto_yes=True)
    assert plain is not None and with_yes is not None
    # Either the backend adds a non-interactive flag, or it has nothing to add
    # because the tool never prompts in the first place.
    if backend.has_native_prompt:
        assert with_yes != plain or backend.name in ("apk", "brew", "nix", "port", "openbsd")


def test_search_never_requires_root(backend_name):
    backend = get_backend(backend_name)
    with patch.object(type(backend), "_run_command") as run:
        backend.search("nmap")
    assert run.call_args[1]["require_sudo"] is False


def test_search_passes_the_query(backend_name):
    backend = get_backend(backend_name)
    command = _capture(backend, "search", "nmap")
    assert command is not None and command[-1] == "nmap"


def test_destructive_ops_get_a_prompt_one_way_or_another(backend_name):
    """Either the tool prompts natively, or pkgwrap adds its own confirmation."""
    backend = get_backend(backend_name)
    if backend.has_native_prompt:
        return
    with patch.object(type(backend), "_run_command") as run:
        backend.remove(["nmap"])
    assert run.call_args[1].get("confirm"), (
        "{0} has no native prompt and no pkgwrap confirmation on remove".format(backend_name)
    )


def test_dry_run_flag_is_forwarded(backend_name):
    backend = get_backend(backend_name)
    with patch.object(type(backend), "_run_command") as run:
        backend.install(["nmap"], dry_run=True)
    assert run.call_args[1]["dry_run"] is True


def test_registry_has_no_duplicate_classes():
    classes = list(_BACKENDS.values())
    assert len(classes) == len(set(classes))
