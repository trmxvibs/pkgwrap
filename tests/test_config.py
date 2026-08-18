"""Tests for the configuration and caching logic."""

import os
import unittest
from unittest.mock import patch

from pkgwrap.config import (
    get_cache_file,
    get_config_dir,
    read_cached_backend,
    write_cached_backend,
)
from pkgwrap.detector import detect_backend


class TestConfig(unittest.TestCase):
    """Test suite for config directory resolution and cache handling."""

    @patch('pkgwrap.config.os.makedirs')
    @patch('pkgwrap.config.os.environ.get')
    @patch('pkgwrap.config.platform.system')
    def test_windows_config_dir_with_appdata(self, mock_system, mock_env_get, mock_makedirs):
        """Ensure Windows uses APPDATA environment variable when available."""
        mock_system.return_value = "Windows"
        mock_env_get.return_value = "C:\\Users\\Test\\AppData\\Roaming"
        
        expected_path = os.path.join("C:\\Users\\Test\\AppData\\Roaming", "pkgwrap")
        self.assertEqual(get_config_dir(), expected_path)
        mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)

    @patch('pkgwrap.config.os.makedirs')
    @patch('pkgwrap.config.os.path.expanduser')
    @patch('pkgwrap.config.os.environ.get')
    @patch('pkgwrap.config.platform.system')
    def test_windows_config_dir_without_appdata(self, mock_system, mock_env_get, mock_expanduser, mock_makedirs):
        """Ensure Windows falls back to expanduser if APPDATA is missing."""
        mock_system.return_value = "Windows"
        mock_env_get.return_value = None
        mock_expanduser.return_value = "C:\\Users\\Test\\AppData\\Roaming\\pkgwrap"
        
        self.assertEqual(get_config_dir(), "C:\\Users\\Test\\AppData\\Roaming\\pkgwrap")
        mock_expanduser.assert_called_once_with(os.path.join("~", "AppData", "Roaming", "pkgwrap"))

    @patch('pkgwrap.config.os.makedirs')
    @patch('pkgwrap.config.os.path.expanduser')
    @patch('pkgwrap.config.platform.system')
    def test_unix_config_dir(self, mock_system, mock_expanduser, mock_makedirs):
        """Ensure Unix-like systems use ~/.config/pkgwrap."""
        mock_system.return_value = "Linux"
        mock_expanduser.return_value = "/home/test/.config/pkgwrap"
        
        self.assertEqual(get_config_dir(), "/home/test/.config/pkgwrap")
        mock_expanduser.assert_called_once_with(os.path.join("~", ".config", "pkgwrap"))

    @patch('pkgwrap.config.print_warning')
    @patch('pkgwrap.config.os.makedirs')
    def test_permission_error_returns_none(self, mock_makedirs, mock_warning):
        """Ensure directory creation failures gracefully return None and warn."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        self.assertIsNone(get_config_dir())
        mock_warning.assert_called_once()
        self.assertIn("Could not create config directory", mock_warning.call_args[0][0])

    @patch('pkgwrap.config.os.makedirs')
    def test_cache_functions_handle_none(self, mock_makedirs):
        """Ensure cache read/write functions safely no-op when config_dir is None."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        # Suppress warning for clean test output
        with patch('pkgwrap.config.print_warning'):
            self.assertIsNone(get_cache_file())
            self.assertIsNone(read_cached_backend())
            
            try:
                write_cached_backend("apt")
            except Exception as e:
                self.fail(f"write_cached_backend crashed with None config_dir: {e}")

    @patch('pkgwrap.detector.shutil.which')
    @patch('pkgwrap.detector.platform.system')
    @patch('pkgwrap.config.os.makedirs')
    def test_detect_backend_resilience(self, mock_makedirs, mock_system, mock_which):
        """Ensure detect_backend succeeds even if config directory creation fails."""
        # Force config directory creation to fail
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        # Mock detector environment so it successfully detects 'apt'
        mock_system.return_value = "Linux"
        
        def mock_which_impl(cmd):
            return "/usr/bin/apt" if cmd == "apt" else None
            
        mock_which.side_effect = mock_which_impl
        
        with patch.dict('os.environ', {}, clear=True):  # Clear termux variables
            with patch('pkgwrap.config.print_warning'):  # Suppress warning output
                try:
                    backend = detect_backend()
                    self.assertEqual(backend, "apt")
                except Exception as e:
                    self.fail(f"detect_backend crashed due to config error: {type(e).__name__}: {e}")


if __name__ == '__main__':
    unittest.main()