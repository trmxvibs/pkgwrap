"""Tests for cross-backend package name mapping."""

from pkgwrap.package_map import PACKAGE_MAP, resolve_package_name


def test_known_package_known_backend():
    assert resolve_package_name("pip", "apt") == "python3-pip"
    assert resolve_package_name("pip", "pacman") == "python-pip"
    assert resolve_package_name("pip", "apk") == "py3-pip"


def test_case_insensitive():
    assert resolve_package_name("PIP", "apt") == "python3-pip"


def test_unknown_package_passthrough():
    assert resolve_package_name("some-random-tool", "apt") == "some-random-tool"


def test_known_package_unknown_backend_passthrough():
    assert resolve_package_name("pip", "emerge") == "pip"


def test_map_keys_are_lowercase():
    """resolve_package_name lowercases its input, so keys must be lowercase."""
    assert all(key == key.lower() for key in PACKAGE_MAP)


def test_mapped_backends_are_registered():
    from pkgwrap.backends import available_backends

    known = set(available_backends())
    for canonical, entry in PACKAGE_MAP.items():
        unknown = set(entry) - known
        assert not unknown, "{0} maps unknown backends: {1}".format(canonical, unknown)
