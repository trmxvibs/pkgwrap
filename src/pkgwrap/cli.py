"""Command-line interface entry point for pkgwrap.
Parses arguments and routes commands to the appropriately detected package manager backend.
Handles root privileges detection and automatic confirmation flags.
"""

import argparse
import os
import sys

from pkgwrap import __version__
from pkgwrap.backends import get_backend
from pkgwrap.detector import detect_backend
from pkgwrap.errors import CommandExecutionError, PkgwrapError, UserCancelledError
from pkgwrap.ui import print_error, print_info, print_success


def main() -> None:
    """Main entry point for the CLI application.
    Parses command-line arguments and executes the corresponding backend methods.
    Checks for root privileges and handles automatic yes/confirmation logic.
    """
    epilog_text = (
        "Command aliases:\n"
        "  install : in, add\n"
        "  remove  : uninstall, del, rm\n"
        "  update  : up, upgrade\n"
        "  search  : find\n\n"
        "Note: 'full-upgrade' and 'dist-upgrade' are intentionally not supported yet \n"
        "(planned as a separate future command, not an alias).\n"
        "Use 'pkgwrap <command> --help' for more information on a specific command."
    )

    parser = argparse.ArgumentParser(
        prog="pkgwrap",
        description="A universal package-manager wrapper.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog_text
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit"
    )
    
    parser.add_argument(
        "--backend", 
        action="store_true", 
        help="Detect and print the current system package manager backend, then exit"
    )

    # Parent parser for shared arguments across subcommands
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument(
        "-y", "--yes", 
        action="store_true", 
        help="Skip sudo confirmation prompts"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available package operations")

    # Install command
    install_parser = subparsers.add_parser(
        "install", 
        aliases=["in", "add"], 
        parents=[shared_parser], 
        help="Install a package"
    )
    install_parser.add_argument("package", help="Name of the package to install")

    # Remove command
    remove_parser = subparsers.add_parser(
        "remove", 
        aliases=["uninstall", "del", "rm"], 
        parents=[shared_parser], 
        help="Remove a package"
    )
    remove_parser.add_argument("package", help="Name of the package to remove")

    # Update command
    subparsers.add_parser(
        "update", 
        aliases=["up", "upgrade"], 
        parents=[shared_parser], 
        help="Update system packages and repositories"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search", 
        aliases=["find"], 
        parents=[shared_parser], 
        help="Search for a package"
    )
    search_parser.add_argument("query", help="Search query or keyword")

    args = parser.parse_args()

    # Determine if current user is already root
    # Use hasattr to avoid AttributeError on Windows systems
    is_root = hasattr(os, 'geteuid') and os.geteuid() == 0

    # Handle the standalone --backend flag
    if args.backend:
        try:
            backend_name = detect_backend()
            print_info(f"Active backend detected: {backend_name}")
            sys.exit(0)
        except PkgwrapError as e:
            print_error(str(e))
            sys.exit(1)

    # If no command is provided (and no standalone flag like --backend was used)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route subcommands (checking against both primary names and aliases)
    try:
        backend_name = detect_backend()
        backend = get_backend(backend_name)
        auto_yes = getattr(args, "yes", False)
        
        if args.command in ("install", "in", "add"):
            backend.install(args.package, already_root=is_root, auto_yes=auto_yes)
            print_success(f"Successfully finished installation process for '{args.package}'.")
            
        elif args.command in ("remove", "uninstall", "del", "rm"):
            backend.remove(args.package, already_root=is_root, auto_yes=auto_yes)
            print_success(f"Successfully finished removal process for '{args.package}'.")
            
        elif args.command in ("update", "up", "upgrade"):
            backend.update(already_root=is_root, auto_yes=auto_yes)
            print_success("System packages updated successfully.")
            
        elif args.command in ("search", "find"):
            backend.search(args.query, already_root=is_root, auto_yes=auto_yes)
            # No print_success here as search usually outputs its own list directly
            
    except UserCancelledError as e:
        print_error(str(e))
        sys.exit(1)
    except CommandExecutionError as e:
        print_error(str(e))
        sys.exit(e.returncode)
    except PkgwrapError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print()  # newline for clean prompt return
        print_error("Operation cancelled by user (KeyboardInterrupt).")
        sys.exit(130)


if __name__ == "__main__":
    main()