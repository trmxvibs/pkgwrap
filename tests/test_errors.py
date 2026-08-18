"""Tests for error types and exit-code normalisation."""

import pytest

from pkgwrap.errors import (
    BackendNotFoundError,
    CommandExecutionError,
    PkgwrapError,
    UserCancelledError,
    normalize_exit_code,
)


def test_every_error_is_a_pkgwrap_error():
    for cls in (BackendNotFoundError, UserCancelledError, CommandExecutionError):
        assert issubclass(cls, PkgwrapError)


@pytest.mark.parametrize(
    "raw,expected",
    [(1, 1), (100, 100), (255, 255), (0, 1), (None, 1), (-9, 137), (-2, 130), (256, 1)],
)
def test_normalize_exit_code(raw, expected):
    assert normalize_exit_code(raw) == expected


def test_signal_return_code_is_not_leaked_as_negative():
    """sys.exit(-9) would surface as 247; it must become 128+9 instead."""
    error = CommandExecutionError("apt install nmap", -9)
    assert error.exit_code == 137


def test_message_includes_command_and_code():
    error = CommandExecutionError("apt install nmap", 100, stderr="boom")
    assert "apt install nmap" in str(error)
    assert "100" in str(error)
    assert "boom" in str(error)
