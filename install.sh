#!/usr/bin/env bash

set -e

echo "=> Checking for python3 in PATH..."

# Set up sudo if script is not running as root
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

if ! command -v python3 &> /dev/null; then
    echo "=> python3 is not found."
    echo "=> Attempting to install python3 and pip using your native package manager..."

    if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]] && command -v pkg &> /dev/null; then
        echo "=> Detected Termux environment."
        echo "=> Running: pkg install python -y"
        pkg install python -y

    elif command -v apt-get &> /dev/null || command -v apt &> /dev/null; then
        echo "=> Detected Debian/Ubuntu environment (apt)."
        echo "=> Running: $SUDO apt-get update && $SUDO apt-get install python3 python3-pip -y"
        $SUDO apt-get update
        $SUDO apt-get install python3 python3-pip -y

    elif command -v pacman &> /dev/null; then
        echo "=> Detected Arch Linux environment (pacman)."
        echo "=> Running: $SUDO pacman -S python python-pip --noconfirm"
        $SUDO pacman -Sy
        $SUDO pacman -S python python-pip --noconfirm

    elif command -v dnf &> /dev/null; then
        echo "=> Detected Fedora environment (dnf)."
        echo "=> Running: $SUDO dnf install python3 python3-pip -y"
        $SUDO dnf install python3 python3-pip -y

    elif command -v apk &> /dev/null; then
        echo "=> Detected Alpine Linux environment (apk)."
        echo "=> Running: $SUDO apk add python3 py3-pip"
        $SUDO apk add python3 py3-pip

    elif command -v brew &> /dev/null; then
        echo "=> Detected macOS/Linux environment with Homebrew (brew)."
        echo "=> Running: brew install python3"
        brew install python3

    elif [[ "$(uname -s)" == "Darwin" ]]; then
        echo "✖ Error: macOS detected, but Homebrew (brew) is not installed."
        echo "=> Please install Python 3 manually from: https://www.python.org/downloads/mac-osx/"
        echo "=> Or install Homebrew first from https://brew.sh/ and run this script again."
        exit 1

    else
        echo "✖ Error: Could not detect a supported package manager (pkg, apt, pacman, dnf, apk, brew)."
        echo "=> Please install Python 3 and pip manually from your operating system's package manager,"
        echo "=> or download it directly from: https://www.python.org/downloads/"
        exit 1
    fi
else
    echo "✔ python3 is already installed."
fi

# Ensure pip is actually available before attempting the install
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "✖ Error: python3 is installed, but pip is missing."
    echo "=> Please install pip for your system manually."
    exit 1
fi

echo "=> Installing pkgwrap via pip..."
python3 -m pip install pkgwrap-lokesh

echo ""
echo "✔ Installation complete!"
echo "=> You can now use 'pkgwrap' or 'pkw' commands in your terminal."
echo "=> Note: Ensure your pip user bin directory (usually ~/.local/bin) is in your PATH if the commands are not found."