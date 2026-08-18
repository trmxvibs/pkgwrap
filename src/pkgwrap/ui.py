"""UI helpers for terminal output and user prompts.

Centralises all terminal interaction so behaviour stays consistent:

* Colour is emitted only when the stream is a real TTY, and can be
  disabled with ``NO_COLOR`` / ``PKGWRAP_NO_COLOR`` or forced with
  ``FORCE_COLOR``.
* Unicode status symbols are downgraded to ASCII automatically when the
  console encoding cannot represent them (legacy Windows code pages such
  as cp1252/cp437 would otherwise raise ``UnicodeEncodeError``).
"""

import os
import sys
from typing import Optional, TextIO

# ANSI colour codes
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# Preferred (Unicode) symbols and their ASCII fallbacks
_SYMBOLS_UNICODE = {
    "success": "\u2714",   # heavy check mark
    "error": "\u2716",     # heavy multiplication x
    "info": "\u2139",      # information source
    "warning": "\u26a0",   # warning sign
    "arrow": "\u2192",     # rightwards arrow
}

_SYMBOLS_ASCII = {
    "success": "[OK]",
    "error": "[X]",
    "info": "[i]",
    "warning": "[!]",
    "arrow": "->",
}


def _stream_supports(stream: TextIO, text: str) -> bool:
    """Return True if ``text`` can be encoded with the stream's encoding."""
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return False
    try:
        text.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def supports_unicode(stream: Optional[TextIO] = None) -> bool:
    """Return True if the given stream can render the Unicode symbols."""
    stream = stream or sys.stdout
    probe = "".join(_SYMBOLS_UNICODE.values())
    return _stream_supports(stream, probe)


def symbol(kind: str, stream: Optional[TextIO] = None) -> str:
    """Return the best status symbol for ``kind`` on the given stream."""
    table = _SYMBOLS_UNICODE if supports_unicode(stream) else _SYMBOLS_ASCII
    return table.get(kind, "")


def supports_color(stream: Optional[TextIO] = None) -> bool:
    """Decide whether ANSI colour should be emitted on ``stream``.

    Colour is suppressed when output is piped or redirected, when
    ``NO_COLOR``/``PKGWRAP_NO_COLOR``/``TERM=dumb`` are set, and forced on
    when ``FORCE_COLOR`` is set.
    """
    stream = stream or sys.stdout

    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("PKGWRAP_NO_COLOR"):
        return False
    if os.environ.get("TERM", "").lower() == "dumb":
        return False

    try:
        return bool(stream.isatty())
    except Exception:
        return False


def _emit(kind: str, color: str, message: str, stream: TextIO) -> None:
    """Write a formatted status line, degrading gracefully on any failure."""
    prefix = symbol(kind, stream)
    line = "{0} {1}".format(prefix, message) if prefix else message

    if supports_color(stream):
        line = "{0}{1}{2}".format(color, line, COLOR_RESET)

    try:
        print(line, file=stream)
    except UnicodeEncodeError:
        # Last-resort fallback: strip anything the console cannot encode.
        encoding = getattr(stream, "encoding", None) or "ascii"
        safe = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(safe, file=stream)


def print_success(message: str, stream: Optional[TextIO] = None) -> None:
    """Print a success message (green)."""
    _emit("success", COLOR_GREEN, message, stream or sys.stdout)


def print_error(message: str, stream: Optional[TextIO] = None) -> None:
    """Print an error message (red) on standard error."""
    _emit("error", COLOR_RED, message, stream or sys.stderr)


def print_info(message: str, stream: Optional[TextIO] = None) -> None:
    """Print an informational message (blue)."""
    _emit("info", COLOR_BLUE, message, stream or sys.stdout)


def print_warning(message: str, stream: Optional[TextIO] = None) -> None:
    """Print a warning message (yellow) on standard error."""
    _emit("warning", COLOR_YELLOW, message, stream or sys.stderr)


def print_command(command: str, stream: Optional[TextIO] = None) -> None:
    """Print the exact command about to be executed."""
    _emit("arrow", COLOR_BLUE, "Running: {0}".format(command), stream or sys.stdout)


def ask_confirmation(prompt: str, default: bool = False) -> bool:
    """Prompt the user for a yes/no answer.

    Returns ``default`` when stdin is not interactive (piped input, cron,
    CI) so the caller can fail safely instead of hanging.
    """
    if not sys.stdin or not sys.stdin.isatty():
        print_warning(
            "No interactive terminal available for confirmation. "
            "Re-run with '-y' to proceed non-interactively."
        )
        return default

    suffix = "[Y/n]" if default else "[y/N]"
    marker = symbol("info", sys.stdout)
    if marker:
        question = "{0} {1} {2}: ".format(marker, prompt, suffix)
    else:
        question = "{0} {1}: ".format(prompt, suffix)
    if supports_color(sys.stdout):
        question = "{0}{1}{2}".format(COLOR_BLUE, question, COLOR_RESET)

    while True:
        try:
            response = input(question).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()  # keep the shell prompt on a clean line
            return False

        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print_error("Invalid input. Please enter 'y' or 'n'.")
