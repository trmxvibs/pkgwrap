<h1 align="center">📦 pkgwrap</h1>
<p align="center"><em>One command. Every package manager.</em></p>

<p align="center">
  <a href="https://github.com/trmxvibs/pkgwrap/blob/main/LICENSE"><img src="https://img.shields.io/github/license/trmxvibs/pkgwrap" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python Version"></a>
  <a href="https://pypi.org/project/pkgwrap/"><img src="https://img.shields.io/pypi/v/pkgwrap" alt="PyPI Version"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/stargazers"><img src="https://img.shields.io/github/stars/trmxvibs/pkgwrap?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/commits/main"><img src="https://img.shields.io/github/last-commit/trmxvibs/pkgwrap" alt="Last Commit"></a>
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Termux%20%7C%20FreeBSD-lightgrey" alt="Supported Platforms">
</p>

---

Remembering the exact syntax to install a package across different operating systems (`apt`, `pacman`, `brew`, `apk`) is a frustrating and error-prone chore. `pkgwrap` solves this context-switching fatigue by giving you **one universal command** that automatically detects your OS and translates standard package operations into native syntax.

---

##  Why pkgwrap?

*   **Zero Configuration:** Automatically detects your OS and native package manager out of the box—no setup required.
*   **Muscle Memory:** Stop pausing to remember if it's `pacman -S`, `apt install`, or `dnf install`. Just type `pkw install`.
*   **Smart Permissions:** Automatically prefixes commands with `sudo` when required and prompts for confirmation, but gracefully skips the prompt if you are already running as `root`.
*   **Lightweight:** No heavy dependencies, network API calls, or bloated background services. It simply wraps your local package manager safely.

**Why not just use apt/pkg directly?**
If you only ever use a single operating system, you probably should! But if you are a developer, sysadmin, or homelabber who frequently jumps between a Debian VPS, a macOS workstation, an Alpine Docker container, or a Termux shell on your phone, you know the pain of typing `apt install` on an Arch machine. `pkgwrap` eliminates that friction entirely.

---

##  Supported Platforms

| OS / Distribution | Backend | Status |
| :--- | :--- | :---: |
| Debian, Ubuntu, Pop!_OS, Mint | `apt` | ✅ Supported |
| Termux (Android) | `pkg` | ✅ Supported |
| Arch Linux, Manjaro, EndeavourOS | `pacman` | ✅ Supported |
| Fedora, RHEL, Rocky Linux | `dnf` | ✅ Supported |
| Alpine Linux | `apk` | ✅ Supported |
| macOS, Linux (Homebrew) | `brew` | ✅ Supported |
| openSUSE | `zypper` | ✅ Supported |
| Void Linux | `xbps` | ✅ Supported |
| NixOS / Nix | `nix` | ✅ Supported |
| Solus | `eopkg` | ✅ Supported |
| FreeBSD | `pkg` | ✅ Supported |

*(Note: `pkgwrap` intelligently distinguishes between FreeBSD `pkg` and Termux `pkg` under the hood based on OS detection).*

---

##  Installation

### Option 1: Via pip (Recommended)
If you already have Python 3.9+ and `pip` installed on your system:
```bash
pip install pkgwrap-lokesh
```
### Option 2: via Install Script
If you don't have Python or pip installed, this script will attempt to install them using your native package manager before installing pkgwrap:
```python
bash <(curl -s https://raw.githubusercontent.com/trmxvibs/pkgwrap/main/install.sh)
```


## Usage
pkgwrap provides two commands that behave identically: pkgwrap (descriptive) and pkw (a fast, 3-letter alias for daily use).
```sh
# Install a package
pkgwrap install <package>
pkw install <package>

# Remove a package
pkgwrap remove <package>
pkw remove <package>

# Update system packages and repositories
pkgwrap update
pkw update

# Search for a package
pkgwrap search <package>
pkw search <package>
```


### Pro-tips for Sudo & Confirmations:

You can use the `-y` or `--yes` flag (e.g., `pkw install vim -y`) to skip all `sudo` confirmation prompts.

If you execute `pkgwrap` while already logged in as a `root` user, confirmation prompts are skipped automatically.
## Example Output
```python
$ pkw install cowsay
ℹ The command 'sudo apt install -y cowsay' requires administrative privileges (sudo).
? Do you want to proceed with sudo? (y/N) y
→ Running: sudo apt install -y cowsay
Reading package lists... Done
Building dependency tree... Done
...
✔ Successfully finished installation process for 'cowsay'.
```

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

We are always looking to support new platforms (e.g., Windows via `winget`/`choco` is currently on the roadmap as a future addition). Pull requests adding new backends are highly encouraged!

## License
This project is licensed under the MIT License — see the LICENSE file for details.






























