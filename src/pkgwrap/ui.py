"""UI helpers for colored terminal output and user prompts.
Centralizes terminal interactions to maintain a consistent user experience.
"""

import sys

# ANSI color codes for terminal output
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

# Symbols for visual feedback
SYMBOL_SUCCESS = "✔"
SYMBOL_ERROR = "✖"
SYMBOL_INFO = "ℹ"


def print_success(message: str) -> None:
    """Prints a success message with a green checkmark.

    Args:
        message (str): The success message to display.
    """
    print(f"{COLOR_GREEN}{SYMBOL_SUCCESS} {message}{COLOR_RESET}")


def print_error(message: str) -> None:
    """Prints an error message with a red cross to standard error.

    Args:
        message (str): The error message to display.
    """
    print(f"{COLOR_RED}{SYMBOL_ERROR} {message}{COLOR_RESET}", file=sys.stderr)


def print_info(message: str) -> None:
    """Prints an informational message in blue.

    Args:
        message (str): The information message to display.
    """
    print(f"{COLOR_BLUE}{SYMBOL_INFO} {message}{COLOR_RESET}")


def ask_confirmation(prompt: str) -> bool:
    """Prompts the user for a yes/no confirmation.

    This is particularly useful for confirming sudo/root actions.

    Args:
        prompt (str): The question or prompt to display to the user.

    Returns:
        bool: True if the user confirmed (y/yes), False otherwise (n/no or empty).
    """
    while True:
        try:
            response = input(f"{COLOR_BLUE}{SYMBOL_INFO} {prompt} [y/N]: {COLOR_RESET}").strip().lower()
            if response in ("y", "yes"):
                return True
            if response in ("n", "no", ""):
                return False
            print_error("Invalid input. Please enter 'y' or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print()  # Print a newline for clean terminal exit
            return False