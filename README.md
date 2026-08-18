# 📦 pkgwrap

*One command. Every package manager.*

[![License](https://img.shields.io/github/license/trmxvibs/pkgwrap)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/tag/trmxvibs/pkgwrap?label=version)](https://github.com/trmxvibs/pkgwrap/releases)
[![Python Versions](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![CI](https://github.com/trmxvibs/pkgwrap/actions/workflows/ci.yml/badge.svg)](https://github.com/trmxvibs/pkgwrap/actions/workflows/ci.yml)
[![GitHub Stars](https://img.shields.io/github/stars/trmxvibs/pkgwrap?style=social)](https://github.com/trmxvibs/pkgwrap/stargazers)
[![Supported Platforms](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Termux%20%7C%20BSD-lightgrey)](#supported-platforms)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/trmxvibs/pkgwrap/pulls)

---

Remembering the exact syntax to install a package across different operating systems
(`apt`, `pacman`, `brew`, `apk`, `winget`) is a frustrating and error-prone chore.
`pkgwrap` gives you **one universal command** that detects your OS and translates
standard operations into native syntax.

```console
$ pkgwrap install nmap curl
→ Running: sudo apt install nmap curl
```

---

## Why pkgwrap?

- **Zero configuration.** Detects your OS and native package manager out of the box.
- **Muscle-memory saver.** Stop pausing to recall whether it is `pacman -S`, `apt install` or `dnf install`.
- **Safe by default.** pkgwrap never silences your package manager's own confirmation prompt
  unless you explicitly pass `-y`. Commands run with `shell=False`, so package names are
  never interpreted by a shell.
- **Ultra lightweight.** No dependencies, no network calls, no background services.

**Why not just memorise apt/pkg/pacman?** If you only use one OS, do exactly that.
But if you move between a Debian VPS, a macOS workstation, an Alpine container, a
Windows laptop and a Termux shell, `pkgwrap` removes the friction.

---

## Installation

pkgwrap is distributed **from source only** - it is not published on PyPI or
any other package index. Install it directly from this repository.

### Install script (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/trmxvibs/pkgwrap/main/install.sh -o install.sh
less install.sh          # always read a script before running it
bash install.sh
```

The script clones the repository to `~/.local/share/pkgwrap/src` and picks the
right install strategy for your system automatically: an active virtualenv,
then `pipx`, then `pip --user`, and finally a dedicated venv with
`pkgwrap`/`pkw` symlinked into `~/.local/bin`.

### From a clone you already have

```bash
git clone https://github.com/trmxvibs/pkgwrap.git
cd pkgwrap
bash install.sh --local
```

### Manual install

If you would rather run pip yourself:

```bash
git clone https://github.com/trmxvibs/pkgwrap.git
cd pkgwrap

pipx install .              # isolated, always on PATH
# or
pip install --user .
```

On modern Debian, Ubuntu and Fedora the system Python is *externally managed*
(PEP 668), so a plain `pip install .` is refused. Use `pipx`, `pip --user`, or
a virtual environment.

### Update

```bash
bash install.sh --update
```

### Uninstall

```bash
bash install.sh --uninstall
```

> **Note on PyPI.** Earlier builds were published as `pkgwrap-lokesh` on PyPI.
> That package is no longer maintained and will not receive further updates.
> If you installed it that way, remove it with
> `pip uninstall pkgwrap-lokesh` (or `pipx uninstall pkgwrap-lokesh`) and
> reinstall from source.

---

## Usage

```bash
pkgwrap install <package> [<package> ...]   # install one or more packages
pkgwrap remove  <package> [<package> ...]   # remove packages
pkgwrap refresh                             # refresh repository metadata only
pkgwrap upgrade                             # upgrade all installed packages
pkgwrap search  <query>                     # search the repositories
pkgwrap list                                # list installed packages
pkgwrap info    <package>                   # show package details
pkgwrap clean                               # clean the local package cache

pkw install <package>                       # short alias, identical behaviour
```

### Flags

| Flag | Meaning |
| ---- | ------- |
| `-y`, `--yes` | Non-interactive: skip pkgwrap's prompts and pass the package manager's own non-interactive flag |
| `-n`, `--dry-run` | Print the exact command that would run, without executing it |
| `--backend` | Print the detected backend and exit |
| `--backend NAME` | Force a specific backend for this run |
| `--no-cache` | Ignore the cached detection result and probe again |
| `--clear-cache` | Delete the cached detection result and exit |
| `--version` | Print the version |

### Command aliases

| Command | Aliases |
| ------- | ------- |
| `install` | `in`, `add` |
| `remove` | `uninstall`, `del`, `rm` |
| `refresh` | `sync` |
| `upgrade` | `up`, `update` |
| `search` | `find` |
| `list` | `ls` |
| `info` | `show` |

> **`refresh` vs `upgrade`.** `refresh` only updates repository metadata
> (`apt update`, `pacman -Sy`, `zypper refresh`). `upgrade` actually upgrades
> installed packages. They are separate commands on purpose, so nothing is
> upgraded by surprise.

### Environment variables

| Variable | Effect |
| -------- | ------ |
| `PKGWRAP_BACKEND` | Force a backend for every invocation |
| `NO_COLOR` / `PKGWRAP_NO_COLOR` | Disable coloured output |
| `FORCE_COLOR` | Force colour even when output is piped |
| `XDG_CONFIG_HOME` | Where the detection cache is stored (Unix) |

---

## Confirmation and privileges

pkgwrap tries never to leave you without a safety net:

1. If the operation needs root and you are not root, pkgwrap prefixes `sudo`
   and asks you to confirm. If `sudo` is missing, it says so instead of failing cryptically.
2. Without `-y`, pkgwrap does **not** pass `-y`/`--noconfirm` to the package
   manager, so the package manager's own confirmation still appears.
3. For package managers that never prompt (apk, brew, nix, MacPorts, winget,
   pkg_add), pkgwrap adds its own confirmation before removals.
4. With `-y`, both layers are skipped. Use it in scripts, knowingly.
5. `--dry-run` shows the exact command and executes nothing.

---

## Supported platforms

| OS / distro | Backend | Command | Root handling |
| ----------- | ------- | ------- | ------------- |
| Debian, Ubuntu, Mint | `apt` | `apt` | sudo |
| Termux (Android) | `pkg` | `pkg` | none needed |
| Arch, Manjaro, EndeavourOS | `pacman` | `pacman` | sudo |
| Fedora, RHEL 8+, CentOS Stream | `dnf` | `dnf` | sudo |
| RHEL 7, older CentOS, slim images | `yum` | `yum` | sudo |
| Alpine | `apk` | `apk` | sudo |
| openSUSE, SLE | `zypper` | `zypper` | sudo |
| Void Linux | `xbps` | `xbps-install` | sudo |
| Solus | `eopkg` | `eopkg` | sudo |
| Gentoo | `emerge` | `emerge` | sudo |
| NixOS / Nix profiles | `nix` | `nix-env` | none needed |
| macOS (Homebrew) | `brew` | `brew` | never root |
| macOS (MacPorts) | `port` | `port` | sudo |
| FreeBSD | `freebsd` | `pkg` | sudo |
| OpenBSD, NetBSD | `openbsd` | `pkg_add` | sudo |
| Windows | `winget` | `winget` | UAC |
| Windows (fallback) | `choco` | `choco` | elevated shell |

Notes:

- Termux and FreeBSD both expose a `pkg` command; they are distinguished by
  strict environment and OS checks, never by the command name alone.
- Homebrew refuses to run as root, so pkgwrap never escalates for it and warns
  if you are already root.
- On NixOS, system packages are managed declaratively in `configuration.nix`.
  This backend only touches the current user's `nix-env` profile.
- On Arch, installing without a recent sync can fail; run `pkgwrap upgrade`
  (`pacman -Syu`) rather than mixing a bare refresh with an install.
- Not every backend supports every command. `pkgwrap list` on Gentoo, for
  example, reports that the operation is unsupported instead of guessing.

---

## Architecture

```
User runs `pkgwrap install nmap curl`
       |
       v
  [cli.py] -- argparse, aliases, flags (-y, -n, --backend, --no-cache)
       |
       v
[validation.py] -- rejects flag-like or malformed package names
       |
       v
[detector.py] -- PKGWRAP_BACKEND -> validated cache -> Termux/BSD/Windows/macOS
                 checks -> prioritised shutil.which() probe
       |            ^
       |            |
       |      [config.py] -- versioned JSON cache in the user config dir
       v
[package_map.py] -- canonical name -> backend-specific name
       |
       v
[backends/__init__.py registry] -- name -> Backend subclass, executable lookup
       |
       v
[Backend subclass] -- builds the native argument list
       |
       v
[base.py _run_command()] -- sudo detection, confirmation, dry run,
                            subprocess.run(shell=False)
       |
       v
Native package manager executes
```

---

## Development

```bash
git clone https://github.com/trmxvibs/pkgwrap.git
cd pkgwrap
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

pytest              # run the test suite
ruff check .        # lint
```

Adding a package manager is a single file in `src/pkgwrap/backends/` plus one
line in the registry. The contract tests in `tests/backends/test_all_backends.py`
apply to it automatically. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

- [x] Core universal wrapper (17 backends)
- [x] Automatic sudo/root detection with confirmation
- [x] Termux-aware detection
- [x] Windows support (winget, Chocolatey fallback)
- [x] Package name mapping across backends
- [x] Multiple packages per command
- [x] `--dry-run`
- [x] Separate `refresh` and `upgrade`
- [ ] Shell completion (bash/zsh/fish)
- [ ] Language-level package managers (pip/npm/cargo)
- [ ] `snap` / `flatpak` / `rpm-ostree` support

## License

MIT — see [LICENSE](LICENSE).

Made with ❤️ for the terminal by [trmxvibs](https://github.com/trmxvibs)
