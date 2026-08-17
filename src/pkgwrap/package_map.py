"""Package name mapping across different package manager backends.

Some packages have different names depending on the backend
(e.g. "python3-pip" on apt, "python-pip" on pacman, "py3-pip" on apk).
This is a small curated table so users don't need to remember
the exact name for their system.
"""

from typing import Dict

# canonical name -> { backend_name: actual name on that backend }
# if a backend isn't listed, the canonical name is used as-is
PACKAGE_MAP: Dict[str, Dict[str, str]] = {
    "pip": {
        "apt": "python3-pip",
        "dnf": "python3-pip",
        "pacman": "python-pip",
        "apk": "py3-pip",
        "zypper": "python3-pip",
        "xbps": "python3-pip",
        "brew": "python3",
        "winget": "Python.Python.3.12",
    },
    "python": {
        "apt": "python3",
        "dnf": "python3",
        "pacman": "python",
        "apk": "python3",
        "zypper": "python3",
        "xbps": "python3",
        "brew": "python3",
        "winget": "Python.Python.3.12",
    },
    "nodejs": {
        "apt": "nodejs",
        "dnf": "nodejs",
        "pacman": "nodejs",
        "apk": "nodejs",
        "brew": "node",
        "winget": "OpenJS.NodeJS",
    },
    "vim": {
        "dnf": "vim-enhanced",
        "winget": "vim.vim",
    },
    "git": {
        "winget": "Git.Git",
    },
}


def resolve_package_name(package: str, backend_name: str) -> str:
    """Translates a common package name into its backend-specific name.

    Falls back to the original name if there's no mapping.
    """
    entry = PACKAGE_MAP.get(package.lower())
    if not entry:
        return package
    return entry.get(backend_name, package)