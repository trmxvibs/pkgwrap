<h1 align="center">📦 pkgwrap</h1>
<p align="center"><em>One command. Every package manager.</em></p>

<p align="center">
  <a href="https://github.com/trmxvibs/pkgwrap/blob/main/LICENSE"><img src="https://img.shields.io/github/license/trmxvibs/pkgwrap" alt="License"></a>
  <a href="https://pypi.org/project/pkgwrap-lokesh/"><img src="https://img.shields.io/pypi/v/pkgwrap-lokesh" alt="PyPI Version"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python Versions"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/stargazers"><img src="https://img.shields.io/github/stars/trmxvibs/pkgwrap?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/network/members"><img src="https://img.shields.io/github/forks/trmxvibs/pkgwrap?style=social" alt="GitHub Forks"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/commits/main"><img src="https://img.shields.io/github/last-commit/trmxvibs/pkgwrap" alt="Last Commit"></a>
  <a href="https://github.com/trmxvibs/pkgwrap/issues"><img src="https://img.shields.io/github/issues/trmxvibs/pkgwrap" alt="Open Issues"></a>
  <img src="https://img.shields.io/github/languages/code-size/trmxvibs/pkgwrap" alt="Code Size">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Termux%20%7C%20FreeBSD-lightgrey" alt="Supported Platforms">
  <a href="https://github.com/trmxvibs/pkgwrap/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome"></a>
  <img src="https://img.shields.io/badge/maintained-yes-success" alt="Maintained">
</p>

---

Remembering the exact syntax to install a package across different operating systems (`apt`, `pacman`, `brew`, `apk`) is a frustrating and error-prone chore. `pkgwrap` solves this context-switching fatigue by giving you **one universal command** that automatically detects your OS and translates standard operations into native syntax.

---

##  Why pkgwrap?

*   **Zero Configuration:** Automatically detects your OS and native package manager out of the box—no setup required.
*   **Muscle Memory Saver:** Stop pausing to remember if it's `pacman -S`, `apt install`, or `dnf install`. Just type `pkw install`.
*   **Smart Permissions:** Automatically prefixes commands with `sudo` when required and prompts for confirmation, gracefully skipping if you're already running as `root`.
*   **Ultra Lightweight:** No heavy dependencies, network API calls, or bloated background services. It simply wraps your local package manager safely.

**Why not just memorize apt/pkg/pacman?**
If you only ever use a single operating system, you probably should! But if you are a developer, sysadmin, or homelabber who frequently jumps between a Debian VPS, a macOS workstation, an Alpine Docker container, or a Termux shell on your phone, you know the pain of typing `apt install` on an Arch machine. `pkgwrap` eliminates that friction entirely
##  Architecture

`pkgwrap` operates on a clean, layered design. Input is processed at the CLI layer and passed to a detector that intelligently identifies the host system. The detector requests the appropriate backend from a registry, and the selected backend implementation handles the translation. Finally, the base class manages root privileges and user confirmation before executing the native process safely.

```text
User runs `pkgwrap install nmap`
       |
       v
  [cli.py] -- argparse, flags (-y, --backend)
       |
       v
[detector.py] -- checks PREFIX/TERMUX_VERSION, platform.system(),
                 then shutil.which() in priority order
       |
       v
[backends/__init__.py registry] -- maps backend name to class
       |
       v
[Backend subclass] (apt/pkg/pacman/dnf/apk/brew/zypper/xbps/nix/
                    eopkg/freebsd)
       |
       v
[base.py _run_command()] -- sudo/root detection, confirmation,
                            subprocess.run(shell=False)
       |
       v
Native package manager executes
```
###  Supported Platforms

| OS/Distro | Backend | Package Manager Command | Status |
| :--- | :--- | :--- | :--- |
| **Debian/Ubuntu** | apt | `apt` | ✅ Supported |
| **Termux/Android** | pkg | `pkg` | ✅ Supported |
| **Arch Linux** | pacman | `pacman` | ✅ Supported |
| **Fedora** | dnf | `dnf` | ✅ Supported |
| **Alpine** | apk | `apk` | ✅ Supported |
| **macOS** | brew | `brew` | ✅ Supported |
| **openSUSE** | zypper | `zypper` | ✅ Supported |
| **Void Linux** | xbps | `xbps` | ✅ Supported |
| **NixOS** | nix | `nix` | ✅ Supported |
| **Solus** | eopkg | `eopkg` | ✅ Supported |
| **FreeBSD** | pkg | `pkg` | ✅ Supported |
- Note: FreeBSD and Termux are automatically distinguished even though both can expose a pkg command, via strict OS/environment detection.

##  Installation

### Via pip
```bash
pip install pkgwrap-lokesh
```

### Via install script (no pip needed)
```bash
curl -fsSL https://raw.githubusercontent.com/trmxvibs/pkgwrap/main/install.sh | bash
```

### From source (for contributors)
```bash
git clone https://github.com/trmxvibs/pkgwrap.git
cd pkgwrap
bash install.sh --source
```

##  Usage

```bash
pkgwrap install <package>
pkgwrap remove <package>
pkgwrap update
pkgwrap search <package>
pkw install <package>         # short alias, identical behavior
pkgwrap install <package> -y  # skip confirmation
```

> **Note:** If you are already running as root (or use sudo directly), confirmation prompts are skipped automatically. Use the `--backend` flag to see which package manager pkgwrap has detected for your system.

##  Example

```plaintext
\$ pkgwrap install cowsay
ℹ The command 'sudo apt install -y cowsay' requires administrative privileges (sudo).
? Do you want to proceed with sudo? (y/N) y
→ Running: sudo apt install -y cowsay
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  cowsay
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
...
✔ Successfully finished installation process for 'cowsay'.
```


##  Contributing

Contributions, issues, and feature requests are always welcome! Adding support for a new package manager is as simple as creating a new file in the `backends/` directory that implements the `Backend` interface. Feel free to open a ticket or submit a PR on our [issues page](https://github.com/trmxvibs/pkgwrap/issues).

##  Roadmap

- [x] Core universal wrapper (11 backends)
- [x] Automatic sudo/root detection
- [x] Termux-aware detection
- [ ] Windows support (winget/choco)
- [ ] Package name mapping across backends
- [ ] Shell completion (bash/zsh)

##  License

MIT — see [LICENSE](LICENSE) file for details.

<br>
<p align="center">
  Made with ❤️ for the terminal by <a href="https://github.com/trmxvibs">trmxvibs</a>
</p>



















