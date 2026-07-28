"""Unit tests for the APT backend.
Mocks the command execution to ensure correct arguments and flags are passed.
"""

import unittest
from unittest.mock import MagicMock, call, patch

from pkgwrap.backends.apt_backend import AptBackend


class TestAptBackend(unittest.TestCase):
    """Test suite for the Debian/Ubuntu apt package manager backend."""

    def setUp(self) -> None:
        """Set up the test case with an instance of AptBackend."""
        self.backend = AptBackend()

    def test_name_property(self) -> None:
        """Test that the backend name is correct."""
        self.assertEqual(self.backend.name, "apt")

    @patch("pkgwrap.backends.apt_backend.AptBackend._run_command")
    def test_install(self, mock_run_command: MagicMock) -> None:
        """Test the install command formatting and privileges."""
        self.backend.install("cowsay")
        mock_run_command.assert_called_once_with(
            ["apt", "install", "-y", "cowsay"],
            require_sudo=True,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.apt_backend.AptBackend._run_command")
    def test_remove(self, mock_run_command: MagicMock) -> None:
        """Test the remove command formatting and privileges."""
        self.backend.remove("cowsay")
        mock_run_command.assert_called_once_with(
            ["apt", "remove", "-y", "cowsay"],
            require_sudo=True,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.apt_backend.AptBackend._run_command")
    def test_search(self, mock_run_command: MagicMock) -> None:
        """Test the search command formatting and privileges."""
        self.backend.search("cowsay")
        mock_run_command.assert_called_once_with(
            ["apt", "search", "cowsay"],
            require_sudo=False,
            already_root=False,
            auto_yes=False
        )

    @patch("pkgwrap.backends.apt_backend.AptBackend._run_command")
    def test_update(self, mock_run_command: MagicMock) -> None:
        """Test the update command runs both update and upgrade sequentially."""
        self.backend.update()
        
        # Verify both commands were executed in the correct order
        expected_calls = [
            call(["apt", "update"], require_sudo=True, already_root=False, auto_yes=False),
            call(["apt", "upgrade", "-y"], require_sudo=True, already_root=False, auto_yes=False)
        ]
        mock_run_command.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(mock_run_command.call_count, 2)


if __name__ == "__main__":
    unittest.main()