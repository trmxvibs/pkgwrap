# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-08-18

### Security / safety

- **Non-interactive flags are no longer forced.** `-y`, `--noconfirm` and
  friends were previously hardcoded into every install/remove command, which
  silenced the package manager's own confirmation. Combined with automatic
  root detection this meant a destructive command could run with no prompt at
  all. They are now added only when the user passes `-y`.
- Package managers that never prompt (apk, brew, nix, MacPorts, winget,
  `pkg_add`) now get an explicit pkgwrap confirmation before removals.
- Package names are validated: anything that looks like a command-line flag,
  or contains characters outside a conservative allow-list, is rejected before
  it reaches the package manager.
- The detection cache is now validated against the backend registry, so a
  corrupted or hand-edited cache file can no longer steer detection.

### Fixed

- Unicode status symbols crashed with `UnicodeEncodeError` on legacy Windows
  code pages (cp1252/cp437). Symbols now fall back to ASCII automatically.
- Exit codes are normalised: a process killed by a signal reported a
  meaningless status (`-9` surfaced as 247) and now reports `128 + N`.
- `pkgwrap --backend install nmap` used to print the backend and silently skip
  the install. The ambiguous form is now rejected with a clear message.
- ANSI colour is no longer emitted when output is piped or redirected;
  `NO_COLOR`, `PKGWRAP_NO_COLOR`, `FORCE_COLOR` and `TERM=dumb` are honoured.
- `print_warning` genuinely exists now, instead of silently falling back to
  `print_info` through an import guard.
- Confirmation prompts no longer hang when stdin is not a terminal.

### Added

- Multiple packages per command: `pkgwrap install curl wget nmap`.
- `--dry-run` / `-n` prints the exact command without executing it.
- Separate `refresh` (metadata only) and `upgrade` (packages) commands, so
  `update` no longer performs a full system upgrade by surprise.
- New commands: `list`, `info`, `clean`.
- `--backend NAME` forces a backend; `PKGWRAP_BACKEND` does the same globally.
- `--no-cache` and `--clear-cache`.
- New backends: `yum`, `emerge` (Gentoo), `port` (MacPorts), `openbsd`
  (`pkg_add`, also NetBSD) and `choco` (Windows fallback).
- Explicit macOS detection with a helpful message when no package manager is
  present; the same for Windows.
- `XDG_CONFIG_HOME` is respected for the cache location.
- `py.typed` marker, full PyPI metadata, and a `dev` extra.
- GitHub Actions CI: pytest across Python 3.9-3.13 on Linux, macOS and
  Windows, plus ruff, shellcheck and a packaging check.

### Changed

- `install.sh` handles PEP 668 externally-managed environments (pipx, then
  `pip --user`, then a dedicated venv with shims), checks for `sudo` before
  using it, supports `--uninstall`, and no longer claims success when the
  command would not actually be on `PATH`.
- Backend interface: methods take a list of packages and accept `dry_run`;
  each backend declares `executable`, `requires_root` and `has_native_prompt`.
- The version is now defined once, in `pkgwrap/__init__.py`.

## [0.1.2] - 2026-08-07

- Initial public release: 11 backends, automatic sudo/root detection,
  Termux-aware detection, backend caching.
