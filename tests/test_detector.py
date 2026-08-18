"""Tests for backend detection: overrides, cache validation, OS branches."""

from unittest.mock import patch

import pytest

from pkgwrap.detector import detect_backend
from pkgwrap.errors import BackendNotFoundError


def _which(*found):
    """Build a shutil.which replacement that only knows about `found`."""
    found = set(found)

    def which(cmd):
        return "/usr/bin/" + cmd if cmd in found else None

    return which


@pytest.fixture
def no_cache():
    with patch("pkgwrap.detector.read_cached_backend", return_value=None), \
         patch("pkgwrap.detector.write_cached_backend") as write:
        yield write


def test_env_override_wins(monkeypatch, no_cache):
    monkeypatch.setenv("PKGWRAP_BACKEND", "pacman")
    with patch("pkgwrap.detector.shutil.which", _which("apt", "pacman")):
        assert detect_backend() == "pacman"


def test_env_override_rejects_unknown_backend(monkeypatch, no_cache):
    monkeypatch.setenv("PKGWRAP_BACKEND", "not-a-backend")
    with pytest.raises(BackendNotFoundError):
        detect_backend()


def test_valid_cache_is_used():
    with patch("pkgwrap.detector.read_cached_backend", return_value="apt"), \
         patch("pkgwrap.detector.shutil.which", _which("apt")), \
         patch("pkgwrap.detector.write_cached_backend") as write:
        assert detect_backend() == "apt"
    write.assert_not_called()


def test_cache_naming_an_unregistered_backend_is_ignored(monkeypatch):
    """A hand-edited or corrupted cache must not steer detection."""
    monkeypatch.delenv("PKGWRAP_BACKEND", raising=False)
    with patch("pkgwrap.detector.read_cached_backend", return_value="ls"), \
         patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which("ls", "apt")), \
         patch("pkgwrap.detector.write_cached_backend") as write:
        assert detect_backend() == "apt"
    write.assert_called_once_with("apt")


def test_cache_for_uninstalled_manager_is_ignored(monkeypatch):
    monkeypatch.delenv("PKGWRAP_BACKEND", raising=False)
    with patch("pkgwrap.detector.read_cached_backend", return_value="pacman"), \
         patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which("apt")), \
         patch("pkgwrap.detector.write_cached_backend"):
        assert detect_backend() == "apt"


def test_no_cache_flag_forces_redetection():
    with patch("pkgwrap.detector.read_cached_backend", return_value="apt") as read, \
         patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which("pacman")), \
         patch("pkgwrap.detector.write_cached_backend"):
        assert detect_backend(use_cache=False) == "pacman"
    read.assert_not_called()


def test_termux_beats_apt(monkeypatch, no_cache):
    monkeypatch.setenv("PREFIX", "/data/data/com.termux/files/usr")
    with patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which("pkg", "apt")):
        assert detect_backend() == "pkg"


def test_termux_version_variable_also_works(monkeypatch, no_cache):
    monkeypatch.setenv("TERMUX_VERSION", "0.118.0")
    with patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which("pkg", "apt")):
        assert detect_backend() == "pkg"


def test_freebsd_pkg_is_not_termux_pkg(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="FreeBSD"), \
         patch("pkgwrap.detector.shutil.which", _which("pkg")):
        assert detect_backend() == "freebsd"


def test_openbsd_uses_pkg_add(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="OpenBSD"), \
         patch("pkgwrap.detector.shutil.which", _which("pkg_add")):
        assert detect_backend() == "openbsd"


def test_windows_prefers_winget_then_choco(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="Windows"), \
         patch("pkgwrap.detector.shutil.which", _which("winget", "choco")):
        assert detect_backend() == "winget"

    with patch("pkgwrap.detector.platform.system", return_value="Windows"), \
         patch("pkgwrap.detector.shutil.which", _which("choco")):
        assert detect_backend() == "choco"


def test_windows_without_any_manager_explains_how_to_fix(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="Windows"), \
         patch("pkgwrap.detector.shutil.which", _which()):
        with pytest.raises(BackendNotFoundError) as excinfo:
            detect_backend()
    assert "winget" in str(excinfo.value)


def test_macos_prefers_brew_then_macports(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="Darwin"), \
         patch("pkgwrap.detector.shutil.which", _which("brew", "port")):
        assert detect_backend() == "brew"

    with patch("pkgwrap.detector.platform.system", return_value="Darwin"), \
         patch("pkgwrap.detector.shutil.which", _which("port")):
        assert detect_backend() == "port"


def test_macos_without_manager_points_at_homebrew(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="Darwin"), \
         patch("pkgwrap.detector.shutil.which", _which()):
        with pytest.raises(BackendNotFoundError) as excinfo:
            detect_backend()
    assert "brew.sh" in str(excinfo.value)


@pytest.mark.parametrize(
    "executable,expected",
    [
        ("apt", "apt"),
        ("pacman", "pacman"),
        ("dnf", "dnf"),
        ("yum", "yum"),
        ("zypper", "zypper"),
        ("apk", "apk"),
        ("xbps-install", "xbps"),
        ("eopkg", "eopkg"),
        ("emerge", "emerge"),
        ("nix-env", "nix"),
    ],
)
def test_linux_priority_probe(no_cache, executable, expected):
    with patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which(executable)):
        assert detect_backend() == expected


def test_nothing_found_raises(no_cache):
    with patch("pkgwrap.detector.platform.system", return_value="Linux"), \
         patch("pkgwrap.detector.shutil.which", _which()):
        with pytest.raises(BackendNotFoundError):
            detect_backend()
