#!/usr/bin/env bash
#
# pkgwrap installer.
#
#   bash install.sh              install from PyPI (recommended)
#   bash install.sh --source     install from a git clone, in editable mode
#   bash install.sh --uninstall  remove pkgwrap again
#
# The script never installs into a system Python that is marked as
# externally managed (PEP 668). It prefers pipx, then a --user install, and
# only falls back to a dedicated virtual environment with launcher shims.

set -euo pipefail

REPO_URL="https://github.com/trmxvibs/pkgwrap.git"
PACKAGE_NAME="pkgwrap-lokesh"
INSTALL_DIR="${PKGWRAP_HOME:-$HOME/.local/share/pkgwrap}"
BIN_DIR="${PKGWRAP_BIN:-$HOME/.local/bin}"
MODE="pip"

info()  { printf '=> %s\n' "$1"; }
ok()    { printf '[OK] %s\n' "$1"; }
warn()  { printf '[!] %s\n' "$1" >&2; }
fail()  { printf '[X] %s\n' "$1" >&2; exit 1; }

while [ "$#" -gt 0 ]; do
    case "$1" in
        --source|-s)    MODE="source" ;;
        --uninstall|-u) MODE="uninstall" ;;
        --help|-h)
            sed -n '3,12p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) fail "Unknown option: $1 (try --help)" ;;
    esac
    shift
done

have() { command -v "$1" >/dev/null 2>&1; }

# Run a command with sudo only when needed and available.
as_root() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif have sudo; then
        sudo "$@"
    else
        fail "This step needs root privileges but 'sudo' is not installed. Re-run as root."
    fi
}

is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || case "${PREFIX:-}" in *com.termux*) return 0 ;; esac
    return 1
}

install_python_if_missing() {
    if have python3; then
        ok "python3 is already installed."
        return
    fi

    info "python3 not found, attempting to install it..."

    if is_termux; then
        pkg install python git -y
    elif have apt; then
        as_root apt install python3 python3-pip python3-venv git -y
    elif have pacman; then
        as_root pacman -S python python-pip git --noconfirm
    elif have dnf; then
        as_root dnf install python3 python3-pip git -y
    elif have yum; then
        as_root yum install python3 python3-pip git -y
    elif have zypper; then
        as_root zypper install -y python3 python3-pip git
    elif have apk; then
        as_root apk add python3 py3-pip git
    elif have brew; then
        brew install python3 git
    else
        fail "Could not detect a supported package manager. Install Python 3 and pip manually, then re-run."
    fi
}

# True when this interpreter refuses plain `pip install` (PEP 668).
is_externally_managed() {
    python3 - <<'PY'
import sys, sysconfig, os
stdlib = sysconfig.get_paths().get("stdlib", "")
marker = os.path.join(stdlib, "EXTERNALLY-MANAGED")
sys.exit(0 if os.path.exists(marker) else 1)
PY
}

in_virtualenv() {
    python3 -c 'import sys; sys.exit(0 if sys.prefix != sys.base_prefix else 1)'
}

link_shims() {
    local venv_dir="$1"
    mkdir -p "$BIN_DIR"
    for cmd in pkgwrap pkw; do
        if [ -x "$venv_dir/bin/$cmd" ]; then
            ln -sf "$venv_dir/bin/$cmd" "$BIN_DIR/$cmd"
        fi
    done
    ok "Linked 'pkgwrap' and 'pkw' into $BIN_DIR"
}

install_target() {
    # $1 is either the PyPI package name or a local path for editable installs.
    local target="$1"
    local editable="${2:-}"
    local pip_args=()
    [ -n "$editable" ] && pip_args+=("-e")

    if in_virtualenv; then
        info "Virtual environment detected, installing into it..."
        python3 -m pip install "${pip_args[@]}" "$target"
        ok "Installed into the active virtual environment."
        return
    fi

    # pipx has no editable mode, so it is skipped for source installs.
    if have pipx && [ -z "$editable" ]; then
        info "Installing with pipx (isolated, always on PATH)..."
        pipx install --force "$target"
        ok "Installed with pipx."
        return
    fi

    if is_termux || ! is_externally_managed; then
        info "Installing with pip --user..."
        python3 -m pip install --user "${pip_args[@]}" "$target"
        ok "Installed with pip --user."
        return
    fi

    warn "This Python is externally managed (PEP 668), so a plain pip install would fail."
    info "Creating a dedicated virtual environment at $INSTALL_DIR/venv ..."
    mkdir -p "$INSTALL_DIR"
    python3 -m venv "$INSTALL_DIR/venv"
    "$INSTALL_DIR/venv/bin/python" -m pip install --upgrade pip >/dev/null
    "$INSTALL_DIR/venv/bin/python" -m pip install "${pip_args[@]}" "$target"
    link_shims "$INSTALL_DIR/venv"
}

uninstall() {
    local removed=0

    if have pipx && pipx list 2>/dev/null | grep -q "$PACKAGE_NAME"; then
        pipx uninstall "$PACKAGE_NAME" && removed=1
    fi

    if python3 -m pip show "$PACKAGE_NAME" >/dev/null 2>&1; then
        python3 -m pip uninstall -y "$PACKAGE_NAME" && removed=1
    fi

    for cmd in pkgwrap pkw; do
        if [ -L "$BIN_DIR/$cmd" ]; then
            rm -f "$BIN_DIR/$cmd" && removed=1
        fi
    done

    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR" && removed=1
    fi

    rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/pkgwrap/backend.json" 2>/dev/null || true

    if [ "$removed" -eq 1 ]; then
        ok "pkgwrap has been removed."
    else
        info "Nothing to uninstall."
    fi
}

main() {
    info "pkgwrap installer"
    echo

    if [ "$MODE" = "uninstall" ]; then
        uninstall
        return
    fi

    install_python_if_missing

    if [ "$MODE" = "source" ]; then
        have git || fail "git is required for a source install but was not found."

        local src_dir="$INSTALL_DIR/src"
        if [ -d "$src_dir/.git" ]; then
            info "Existing clone found at $src_dir, updating..."
            git -C "$src_dir" pull --ff-only || warn "Could not fast-forward; keeping the existing checkout."
        else
            mkdir -p "$INSTALL_DIR"
            git clone "$REPO_URL" "$src_dir"
        fi

        install_target "$src_dir" editable
    else
        install_target "$PACKAGE_NAME"
    fi

    echo
    ok "Installation complete."
    info "Try: pkgwrap --backend"

    case ":$PATH:" in
        *":$BIN_DIR:"*) ;;
        *) warn "$BIN_DIR is not in your PATH. Add this to your shell profile:"
           printf '      export PATH="%s:$PATH"\n' "$BIN_DIR" ;;
    esac
}

main
