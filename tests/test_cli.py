"""Unit tests for the command-line interface.
Tests argument parsing, root privileges detection, and flag forwarding to the backend.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from pkgwrap.cli import main


class TestCLI(unittest.TestCase):
    """Test suite for the pkgwrap CLI command routing and logic."""

    @patch("pkgwrap.cli.os")
    @patch("pkgwrap.cli.get_backend")
    @patch("pkgwrap.cli.detect_backend")
    def test_cli_already_root(self, mock_detect: MagicMock, mock_get_backend: MagicMock, mock_os: MagicMock) -> None:
        """Test that already-root user passes already_root=True without prompting."""
        # Setup mocks
        mock_detect.return_value = "apt"
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend
        
        # Simulate user being root (hasattr(os, 'geteuid') is inherently true on MagicMock)
        mock_os.geteuid.return_value = 0

        # Simulate command line input
        with patch.object(sys, "argv", ["pkgwrap", "install", "cowsay"]):
            main()

        # Verify backend was called with correct flags
        mock_backend.install.assert_called_once_with(
            "cowsay", already_root=True, auto_yes=False
        )

    @patch("pkgwrap.cli.os")
    @patch("pkgwrap.cli.get_backend")
    @patch("pkgwrap.cli.detect_backend")
    def test_cli_non_root_with_yes_flag(self, mock_detect: MagicMock, mock_get_backend: MagicMock, mock_os: MagicMock) -> None:
        """Test that non-root user with -y flag passes auto_yes=True."""
        # Setup mocks
        mock_detect.return_value = "apt"
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend
        
        # Simulate normal user (non-root)
        mock_os.geteuid.return_value = 1000

        # Simulate command line input with -y flag
        with patch.object(sys, "argv", ["pkgwrap", "install", "cowsay", "-y"]):
            main()

        # Verify backend was called with correct flags
        mock_backend.install.assert_called_once_with(
            "cowsay", already_root=False, auto_yes=True
        )

    @patch("pkgwrap.cli.os")
    @patch("pkgwrap.cli.get_backend")
    @patch("pkgwrap.cli.detect_backend")
    def test_cli_non_root_without_yes_flag(self, mock_detect: MagicMock, mock_get_backend: MagicMock, mock_os: MagicMock) -> None:
        """Test that non-root user without -y flag passes default boolean flags."""
        # Setup mocks
        mock_detect.return_value = "apt"
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend
        
        # Simulate normal user (non-root)
        mock_os.geteuid.return_value = 1000

        # Simulate command line input without -y flag
        with patch.object(sys, "argv", ["pkgwrap", "install", "cowsay"]):
            main()

        # Verify backend was called with correct flags
        mock_backend.install.assert_called_once_with(
            "cowsay", already_root=False, auto_yes=False
        )

    @patch("pkgwrap.cli.get_backend")
    @patch("pkgwrap.cli.detect_backend")
    def test_cli_backend_flag(self, mock_detect: MagicMock, mock_get_backend: MagicMock) -> None:
        """Test that the --backend flag detects the backend, prints it, and exits cleanly."""
        # Setup mock
        mock_detect.return_value = "apt"

        # Simulate command line input
        with patch.object(sys, "argv", ["pkgwrap", "--backend"]):
            with self.assertRaises(SystemExit) as cm:
                main()

        # Verify execution flow
        self.assertEqual(cm.exception.code, 0)
        mock_detect.assert_called_once()
        mock_get_backend.assert_not_called()


if __name__ == "__main__":
    unittest.main()