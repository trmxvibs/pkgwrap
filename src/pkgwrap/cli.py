"""Command-line interface for pkgwrap.

Parses arguments, resolves the backend (explicit override, environment
variable or auto-detection), maps package names, and routes the requested
operation to the backend. Every failure is translated into a stable exit
code instead of a traceback.
"""

import argparse
import os
import sys
from typing import List, Optional, Sequence

from pkgwrap import __version__
from pkgwrap.backends import available_backends, get_backend
from pkgwrap.config import clear_cache, get_cache_file
from pkgwrap.detector import detect_backend
from pkgwrap.errors import (
    CommandExecutionError,
    PkgwrapError,
    normalize_exit_code,
)
from pkgwrap.package_map import resolve_package_name
from pkgwrap.ui import print_error, print_info, print_success, print_warning
from pkgwrap.validation import validate_package_names

#: Sentinel used by the backwards-compatible ``--backend`` flag: when the
#: flag is given without a value it means "show me what you detected".
SHOW_BACKEND = "__show__"

EPILOG = """\
Command aliases:
  install : in, add
  remove  : uninstall, del, rm
  refresh : sync
  upgrade : up, update
  search  : find
  list    : ls
  info    : show

Examples:
  pkgwrap install nmap curl        install several packages at once
  pkgwrap remove nmap -y           skip pkgwrap's confirmation prompt
  pkgwrap upgrade --dry-run        print the command without running it
  pkgwrap --backend                show the detected package manager
  pkgwrap --backend apt search vim force a specific backend

Environment:
  PKGWRAP_BACKEND   force a backend for every invocation
  NO_COLOR          disable coloured output
"""


def build_parser() -> argparse.ArgumentParser:
    """Construct the full argument parser."""
    parser = argparse.ArgumentParser(
        prog="pkgwrap",
        description="A universal package-manager wrapper.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EPILOG,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {0}".format(__version__),
        help="Show the version number and exit",
    )
    parser.add_argument(
        "--backend",
        nargs="?",
        const=SHOW_BACKEND,
        # Validating the value here turns the otherwise confusing
        # `--backend install nmap` into a clear "invalid choice" message
        # instead of silently treating "install" as a backend name.
        choices=available_backends() + [SHOW_BACKEND],
        metavar="NAME",
        help=(
            "Without a value: print the detected backend and exit.\n"
            "With a value: force that backend for this run.\n"
            "Available: " + ", ".join(available_backends())
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore the cached backend and detect again",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Delete the cached backend detection and exit",
    )

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Run non-interactively: skip pkgwrap's prompts and pass the\n"
             "package manager's own non-interactive flag",
    )
    shared.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Print the command that would run, without executing it",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available package operations")

    install_parser = subparsers.add_parser(
        "install", aliases=["in", "add"], parents=[shared], help="Install one or more packages"
    )
    install_parser.add_argument("packages", nargs="+", help="Names of the packages to install")

    remove_parser = subparsers.add_parser(
        "remove",
        aliases=["uninstall", "del", "rm"],
        parents=[shared],
        help="Remove one or more packages",
    )
    remove_parser.add_argument("packages", nargs="+", help="Names of the packages to remove")

    subparsers.add_parser(
        "refresh",
        aliases=["sync"],
        parents=[shared],
        help="Refresh repository metadata only (no packages are changed)",
    )

    subparsers.add_parser(
        "upgrade",
        aliases=["up", "update"],
        parents=[shared],
        help="Upgrade all installed packages",
    )

    search_parser = subparsers.add_parser(
        "search", aliases=["find"], parents=[shared], help="Search for a package"
    )
    search_parser.add_argument("query", help="Search query or keyword")

    subparsers.add_parser(
        "list", aliases=["ls"], parents=[shared], help="List installed packages"
    )

    info_parser = subparsers.add_parser(
        "info", aliases=["show"], parents=[shared], help="Show details about a package"
    )
    info_parser.add_argument("package", help="Name of the package to describe")

    subparsers.add_parser(
        "clean", parents=[shared], help="Clean the local package cache"
    )

    return parser


#: Maps every accepted command spelling onto its canonical operation.
COMMAND_ALIASES = {
    "install": "install", "in": "install", "add": "install",
    "remove": "remove", "uninstall": "remove", "del": "remove", "rm": "remove",
    "refresh": "refresh", "sync": "refresh",
    "upgrade": "upgrade", "up": "upgrade", "update": "upgrade",
    "search": "search", "find": "search",
    "list": "list", "ls": "list",
    "info": "info", "show": "info",
    "clean": "clean",
}


def _is_root() -> bool:
    """Return True when the current process already has root privileges."""
    # os.geteuid is absent on Windows, so guard the lookup.
    return hasattr(os, "geteuid") and os.geteuid() == 0


def _resolve_backend_name(args: argparse.Namespace) -> str:
    """Return the backend to use, honouring an explicit override."""
    if args.backend and args.backend != SHOW_BACKEND:
        return args.backend
    return detect_backend(use_cache=not args.no_cache)


def _handle_clear_cache() -> int:
    """Delete the detection cache and report what happened."""
    path = get_cache_file(create=False)
    if clear_cache():
        print_success("Cleared cached backend detection ({0}).".format(path))
    else:
        print_info("No cached backend detection to clear.")
    return 0


def _run_operation(operation: str, args: argparse.Namespace, backend_name: str) -> None:
    """Dispatch a single operation to the resolved backend."""
    backend = get_backend(backend_name)
    auto_yes = getattr(args, "yes", False)
    dry_run = getattr(args, "dry_run", False)
    already_root = _is_root()

    common = {"already_root": already_root, "auto_yes": auto_yes, "dry_run": dry_run}

    if operation in ("install", "remove"):
        packages = validate_package_names(args.packages)
        resolved: List[str] = []
        for package in packages:
            mapped = resolve_package_name(package, backend_name)
            if mapped != package:
                print_info(
                    "Mapped '{0}' -> '{1}' for {2}".format(package, mapped, backend_name)
                )
            resolved.append(mapped)

        if operation == "install":
            backend.install(resolved, **common)
            if not dry_run:
                print_success("Finished installing: {0}.".format(", ".join(resolved)))
        else:
            backend.remove(resolved, **common)
            if not dry_run:
                print_success("Finished removing: {0}.".format(", ".join(resolved)))

    elif operation == "refresh":
        backend.refresh(**common)
        if not dry_run:
            print_success("Repository metadata refreshed.")

    elif operation == "upgrade":
        backend.upgrade(**common)
        if not dry_run:
            print_success("System packages upgraded.")

    elif operation == "search":
        backend.search(args.query, **common)

    elif operation == "list":
        backend.list_installed(**common)

    elif operation == "info":
        package = validate_package_names([args.package])[0]
        backend.info(resolve_package_name(package, backend_name), **common)

    elif operation == "clean":
        backend.clean(**common)
        if not dry_run:
            print_success("Package cache cleaned.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the ``pkgwrap`` and ``pkw`` commands.

    Returns:
        The process exit code. ``0`` on success, a non-zero, POSIX-safe code
        on failure.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.clear_cache:
        return _handle_clear_cache()

    try:
        # `--backend` with no value is an informational request; combining it
        # with a command would be ambiguous, so say so rather than silently
        # ignoring one of the two.
        if args.backend == SHOW_BACKEND:
            if args.command:
                print_error(
                    "'--backend' without a value only reports the detected backend. "
                    "To force one, write '--backend <name> {0} ...'.".format(args.command)
                )
                return 2
            detected = detect_backend(use_cache=not args.no_cache)
            print_info("Active backend detected: {0}".format(detected))
            return 0

        if not args.command:
            parser.print_help()
            return 0

        operation = COMMAND_ALIASES.get(args.command)
        if operation is None:
            parser.error("Unknown command '{0}'.".format(args.command))

        backend_name = _resolve_backend_name(args)

        if args.backend and args.backend != SHOW_BACKEND:
            print_warning(
                "Using forced backend '{0}' instead of auto-detection.".format(backend_name)
            )

        _run_operation(operation, args, backend_name)
        return 0

    except CommandExecutionError as exc:
        print_error(str(exc))
        return exc.exit_code
    except PkgwrapError as exc:
        print_error(str(exc))
        return getattr(exc, "exit_code", 1)
    except KeyboardInterrupt:
        print()  # keep the shell prompt on its own line
        print_error("Operation cancelled by user (KeyboardInterrupt).")
        return 130
    except BrokenPipeError:
        # e.g. `pkgwrap list | head`
        return 0
    except OSError as exc:
        print_error("Unexpected system error: {0}".format(exc))
        return normalize_exit_code(1)


def run() -> None:
    """Console-script wrapper that turns the return value into an exit status."""
    sys.exit(main())


if __name__ == "__main__":
    run()
