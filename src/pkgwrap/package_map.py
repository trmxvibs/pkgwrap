"""Package name mapping across package managers.

The same software often ships under a different name on every distribution
(``python3-pip`` on apt, ``python-pip`` on pacman, ``py3-pip`` on apk). This
small curated table lets users type one canonical name and get the right one
for their system. Anything not listed is passed through untouched.
"""

from typing import Dict

# canonical name -> { backend name: name on that backend }
# A backend that is absent from an entry simply uses the canonical name.
PACKAGE_MAP: Dict[str, Dict[str, str]] = {
    "pip": {
        "apt": "python3-pip",
        "pkg": "python-pip",
        "dnf": "python3-pip",
        "yum": "python3-pip",
        "pacman": "python-pip",
        "apk": "py3-pip",
        "zypper": "python3-pip",
        "xbps": "python3-pip",
        "eopkg": "python3-pip",
        "brew": "python",
        "freebsd": "py39-pip",
        "winget": "Python.Python.3.12",
    },
    "python": {
        "apt": "python3",
        "pkg": "python",
        "dnf": "python3",
        "yum": "python3",
        "pacman": "python",
        "apk": "python3",
        "zypper": "python3",
        "xbps": "python3",
        "eopkg": "python3",
        "brew": "python",
        "freebsd": "python39",
        "port": "python312",
        "emerge": "dev-lang/python",
        "winget": "Python.Python.3.12",
        "choco": "python",
    },
    "nodejs": {
        "apt": "nodejs",
        "dnf": "nodejs",
        "yum": "nodejs",
        "pacman": "nodejs",
        "apk": "nodejs",
        "zypper": "nodejs20",
        "brew": "node",
        "port": "nodejs20",
        "emerge": "net-libs/nodejs",
        "winget": "OpenJS.NodeJS",
        "choco": "nodejs",
    },
    "vim": {
        "dnf": "vim-enhanced",
        "yum": "vim-enhanced",
        "emerge": "app-editors/vim",
        "winget": "vim.vim",
        "choco": "vim",
    },
    "git": {
        "emerge": "dev-vcs/git",
        "winget": "Git.Git",
        "choco": "git",
    },
    "curl": {
        "emerge": "net-misc/curl",
        "winget": "cURL.cURL",
        "choco": "curl",
    },
    "docker": {
        "apt": "docker.io",
        "brew": "docker",
        "emerge": "app-containers/docker",
        "winget": "Docker.DockerDesktop",
        "choco": "docker-desktop",
    },
    "build-essential": {
        "dnf": "@development-tools",
        "yum": "@development-tools",
        "pacman": "base-devel",
        "apk": "build-base",
        "zypper": "patterns-devel-base-devel_basis",
        "brew": "gcc",
    },
}


def resolve_package_name(package: str, backend_name: str) -> str:
    """Translate a canonical package name into its backend-specific name.

    Falls back to the original name when there is no mapping for it.
    """
    entry = PACKAGE_MAP.get(package.lower())
    if not entry:
        return package
    return entry.get(backend_name, package)
