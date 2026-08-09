"""Tests for the command-line interface logic and routing."""

import sys
import unittest
from unittest.mock import MagicMock, patch

from pkgwrap.cli import main


class TestCLI(unittest.TestCase):

    def setUp(self) -> None:
        """Set up mocks for detection and backend retrieval."""
        self.patcher_detect = patch('pkgwrap.cli.detect_backend')
        self.patcher_get = patch('pkgwrap.cli.get_backend')
        self.patcher_success = patch('pkgwrap.cli.print_success')
        
        self.mock_detect = self.patcher_detect.start()
        self.mock_get = self.patcher_get.start()
        self.mock_success = self.patcher_success.start()
        
        self.mock_detect.return_value = 'mocked_backend'
        self.mock_backend = MagicMock()
        self.mock_get.return_value = self.mock_backend

    def tearDown(self) -> None:
        """Stop all started patchers."""
        self.patcher_detect.stop()
        self.patcher_get.stop()
        self.patcher_success.stop()

    def test_install_aliases(self) -> None:
        """Ensure install aliases route to the install backend handler."""
        for alias in ['install', 'in', 'add']:
            with self.subTest(alias=alias):
                self.mock_backend.reset_mock()
                with patch.object(sys, 'argv', ['pkgwrap', alias, 'curl']):
                    main()
                    self.mock_backend.install.assert_called_once()
                    self.assertEqual(self.mock_backend.install.call_args[0][0], 'curl')

    def test_remove_aliases(self) -> None:
        """Ensure remove aliases route to the remove backend handler."""
        # Testing all defined aliases including rm
        for alias in ['remove', 'uninstall', 'del', 'rm']:
            with self.subTest(alias=alias):
                self.mock_backend.reset_mock()
                with patch.object(sys, 'argv', ['pkgwrap', alias, 'curl']):
                    main()
                    self.mock_backend.remove.assert_called_once()
                    self.assertEqual(self.mock_backend.remove.call_args[0][0], 'curl')

    def test_update_aliases(self) -> None:
        """Ensure update aliases route to the update backend handler."""
        for alias in ['update', 'up', 'upgrade']:
            with self.subTest(alias=alias):
                self.mock_backend.reset_mock()
                with patch.object(sys, 'argv', ['pkgwrap', alias]):
                    main()
                    self.mock_backend.update.assert_called_once()

    def test_search_aliases(self) -> None:
        """Ensure search aliases route to the search backend handler."""
        for alias in ['search', 'find']:
            with self.subTest(alias=alias):
                self.mock_backend.reset_mock()
                with patch.object(sys, 'argv', ['pkgwrap', alias, 'curl']):
                    main()
                    self.mock_backend.search.assert_called_once()
                    self.assertEqual(self.mock_backend.search.call_args[0][0], 'curl')

    def test_invalid_upgrade_commands(self) -> None:
        """Ensure invasive upgrade commands are NOT silently aliased and raise argparse errors."""
        # Stop generic mocks to test pure argparse behavior on invalid input
        self.patcher_detect.stop()
        self.patcher_get.stop()
        self.patcher_success.stop()
        
        for invalid_cmd in ['full-upgrade', 'dist-upgrade']:
            with self.subTest(invalid_cmd=invalid_cmd):
                with patch.object(sys, 'argv', ['pkgwrap', invalid_cmd]):
                    with patch('sys.stderr'):  # Suppress argparse error output to keep test logs clean
                        with self.assertRaises(SystemExit) as cm:
                            main()
                        # argparse exits with status code 2 on invalid choice
                        self.assertEqual(cm.exception.code, 2)
                        
        # Restart mocks so tearDown doesn't throw a RuntimeError
        self.patcher_detect.start()
        self.patcher_get.start()
        self.patcher_success.start()


if __name__ == '__main__':
    unittest.main()