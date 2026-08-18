"""Tests for terminal output helpers: colour, encoding and prompts."""

import io
import sys

import pytest

from pkgwrap import ui


class FakeStream:
    """A text stream with a controllable encoding and TTY status.

    ``io.StringIO`` does not allow overriding ``encoding``, so this stands in
    for a real console instead.
    """

    def __init__(self, encoding="utf-8", tty=True):
        self._buffer = io.StringIO()
        self.encoding = encoding
        self._tty = tty

    def isatty(self):
        return self._tty

    def write(self, text):
        # Emulate a console that cannot represent some characters.
        text.encode(self.encoding)
        return self._buffer.write(text)

    def flush(self):
        self._buffer.flush()

    def getvalue(self):
        return self._buffer.getvalue()


def test_unicode_symbols_used_on_utf8_stream():
    stream = FakeStream("utf-8")
    assert ui.supports_unicode(stream) is True
    assert ui.symbol("success", stream) == "\u2714"


def test_ascii_fallback_on_legacy_codepage():
    """A cp1252 console must not raise UnicodeEncodeError."""
    stream = FakeStream("cp1252")
    assert ui.supports_unicode(stream) is False
    assert ui.symbol("success", stream) == "[OK]"

    ui.print_success("done", stream=stream)
    assert "[OK] done" in stream.getvalue()


def test_no_ansi_when_not_a_tty():
    stream = FakeStream("utf-8", tty=False)
    ui.print_info("hello", stream=stream)
    assert "\033[" not in stream.getvalue()


def test_no_color_env_disables_colour(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    stream = FakeStream("utf-8", tty=True)
    ui.print_info("hello", stream=stream)
    assert "\033[" not in stream.getvalue()


def test_force_color_env_enables_colour(monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    stream = FakeStream("utf-8", tty=False)
    ui.print_info("hello", stream=stream)
    assert "\033[" in stream.getvalue()


def test_dumb_terminal_disables_colour(monkeypatch):
    monkeypatch.setenv("TERM", "dumb")
    stream = FakeStream("utf-8", tty=True)
    ui.print_warning("careful", stream=stream)
    assert "\033[" not in stream.getvalue()


def test_print_warning_exists_and_writes():
    stream = FakeStream("utf-8", tty=False)
    ui.print_warning("careful", stream=stream)
    assert "careful" in stream.getvalue()


@pytest.mark.parametrize(
    "answer,expected",
    [("y", True), ("yes", True), ("Y", True), ("n", False), ("no", False), ("", False)],
)
def test_ask_confirmation_answers(monkeypatch, answer, expected):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr("builtins.input", lambda _prompt: answer)
    assert ui.ask_confirmation("Proceed?") is expected


def test_ask_confirmation_defaults_when_not_interactive(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
    assert ui.ask_confirmation("Proceed?") is False
    assert ui.ask_confirmation("Proceed?", default=True) is True
