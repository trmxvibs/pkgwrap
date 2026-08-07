#!/usr/bin/env bash
set -e

echo "=> pkgwrap installer"
echo ""

REPO_URL="https://github.com/trmxvibs/pkgwrap.git"
PACKAGE_NAME="pkgwrap-lokesh"
MODE="pip"

if [ "$1" == "--source" ] || [ "$1" == "-s" ]; then
    MODE="source"
fi

install_python_if_missing() {
    if command -v python3 >/dev/null 2>&1; then
        echo "✔ python3 is already installed."
        return
    fi

    echo "=> python3 not found, attempting to install it..."

    if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
        pkg install python git -y
    elif command -v apt >/dev/null 2>&1; then
        sudo apt install python3 python3-pip python3-venv git -y
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S python python-pip git --noconfirm
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install python3 python3-pip git -y
    elif command -v apk >/dev/null 2>&1; then
        sudo apk add python3 py3-pip git
    elif command -v brew >/dev/null 2>&1; then
        brew install python3 git
    else
        echo "✖ Could not detect a supported package manager."
        echo "  Please install Python 3 and pip manually, then re-run this script."
        exit 1
    fi
}

install_python_if_missing

if [ "$MODE" == "source" ]; then
    echo "=> Installing pkgwrap from source..."

    if ! command -v git >/dev/null 2>&1; then
        echo "✖ git is required for source install but was not found."
        exit 1
    fi

    INSTALL_DIR="$HOME/pkgwrap-src"
    if [ -d "$INSTALL_DIR" ]; then
        echo "=> Existing source found at $INSTALL_DIR, pulling latest..."
        git -C "$INSTALL_DIR" pull
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi

    python3 -m venv "$INSTALL_DIR/venv"
    source "$INSTALL_DIR/venv/bin/activate"
    pip install -e "$INSTALL_DIR"

    echo ""
    echo "✔ Installed from source in editable mode."
    echo "=> Activate it anytime with: source $INSTALL_DIR/venv/bin/activate"
else
    echo "=> Installing pkgwrap via pip..."
    python3 -m pip install "$PACKAGE_NAME"
fi

echo ""
echo "✔ Installation complete!"
echo "=> You can now use 'pkgwrap' or 'pkw' commands in your terminal."
echo "=> Note: Ensure your pip user bin directory (usually ~/.local/bin) is in your PATH if the commands are not found."