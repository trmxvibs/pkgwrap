"""Unit tests for the Windows (winget) backend.
Mocks the command execution to ensure correct arguments and flags are passed.
"""

import unittest
from unittest.mock import MagicMock, patch

from pkgwrap.backends.windows_backend import WindowsBackend


class TestWindowsBackend(unittest.TestCase):
    """Test suite for the Windows winget package manager backend."""

    def setUp(self) -> None:
        self.backend = WindowsBackend()

    def test_name_property(self) -> None:
        self.assertEqual(self.backend.name, "winget")

    @patch("pkgwrap.backends.windows_backend.WindowsBackend._run_command")
    def test_install(self, mock_run_command: MagicMock) -> None:
        self.backend.install("nmap")
        mock_run_command.assert_called_once_with(
            ["winget", "install", "nmap"],
            require_sudo=False,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.windows_backend.WindowsBackend._run_command")
    def test_install_auto_yes(self, mock_run_command: MagicMock) -> None:
        self.backend.install("nmap", auto_yes=True)
        mock_run_command.assert_called_once_with(
            ["winget", "install", "nmap", "--accept-source-agreements",
             "--accept-package-agreements", "--silent"],
            require_sudo=False,
            already_root=False,
            auto_yes=True
        )

    @patch("pkgwrap.backends.windows_backend.WindowsBackend._run_command")
    def test_remove(self, mock_run_command: MagicMock) -> None:
        self.backend.remove("nmap")
        mock_run_command.assert_called_once_with(
            ["winget", "uninstall", "nmap"],
            require_sudo=False,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.windows_backend.WindowsBackend._run_command")
    def test_search(self, mock_run_command: MagicMock) -> None:
        self.backend.search("nmap")
        mock_run_command.assert_called_once_with(
            ["winget", "search", "nmap"],
            require_sudo=False,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.windows_backend.WindowsBackend._run_command")
    def test_update(self, mock_run_command: MagicMock) -> None:
        self.backend.update()
        mock_run_command.assert_called_once_with(
            ["winget", "upgrade", "--all"],
            require_sudo=False,
            already_root=False,
            auto_yes=False
        )


if __name__ == "__main__":
    unittest.main()