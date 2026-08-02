"""Unit tests for the package manager detector module.
Mocks platform, os.environ, shutil.which and caching to test logic safely.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from pkgwrap.detector import detect_backend
from pkgwrap.errors import BackendNotFoundError


class TestDetector(unittest.TestCase):
    """Test suite for backend detection logic in pkgwrap."""

    @patch("pkgwrap.detector.platform.system")
    @patch("pkgwrap.detector.write_cached_backend")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_cache_hit(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_write_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test that detection uses the cache if it is valid and available."""
        mock_system.return_value = "Linux"
        mock_read_cache.return_value = "apt"
        mock_which.side_effect = lambda cmd: "/usr/bin/apt" if cmd == "apt" else None
        
        backend_name = detect_backend()
        
        self.assertEqual(backend_name, "apt")
        mock_read_cache.assert_called_once()
        mock_which.assert_called_once_with("apt")
        mock_write_cache.assert_not_called()

    @patch("pkgwrap.detector.platform.system")
    @patch.dict("os.environ", {}, clear=True)
    @patch("pkgwrap.detector.write_cached_backend")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_cache_miss_fallback_linux(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_write_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test priority order detection when cache is empty on a standard Linux system."""
        mock_system.return_value = "Linux"
        mock_read_cache.return_value = None
        
        def which_mock(cmd: str) -> str:
            if cmd == "pacman":
                return "/usr/bin/pacman"
            return None
            
        mock_which.side_effect = which_mock
        
        backend_name = detect_backend()
        
        self.assertEqual(backend_name, "pacman")
        # Ensure 'apt' is checked before 'pacman'
        mock_which.assert_any_call("apt")
        mock_which.assert_any_call("pacman")
        mock_write_cache.assert_called_once_with("pacman")

    @patch("pkgwrap.detector.platform.system")
    @patch.dict("os.environ", {"PREFIX": "/data/data/com.termux/files/usr"}, clear=True)
    @patch("pkgwrap.detector.write_cached_backend")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_termux_environment(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_write_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test that Termux 'pkg' is prioritized when com.termux is in PREFIX."""
        mock_system.return_value = "Linux"
        mock_read_cache.return_value = None

        def which_mock(cmd: str) -> str:
            if cmd == "pkg":
                return "/data/data/com.termux/files/usr/bin/pkg"
            return None

        mock_which.side_effect = which_mock

        backend_name = detect_backend()

        self.assertEqual(backend_name, "pkg")
        mock_which.assert_called_once_with("pkg")
        mock_write_cache.assert_called_once_with("pkg")

    @patch("pkgwrap.detector.platform.system")
    @patch.dict("os.environ", {"TERMUX_VERSION": "0.118.0"}, clear=True)
    @patch("pkgwrap.detector.write_cached_backend")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_termux_with_apt_also_present(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_write_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test that Termux 'pkg' is selected even if 'apt' is also available on the system."""
        mock_system.return_value = "Linux"
        mock_read_cache.return_value = None

        def which_mock(cmd: str) -> str:
            if cmd == "pkg":
                return "/data/data/com.termux/files/usr/bin/pkg"
            if cmd == "apt":
                return "/data/data/com.termux/files/usr/bin/apt"
            return None

        mock_which.side_effect = which_mock

        backend_name = detect_backend()

        self.assertEqual(backend_name, "pkg")
        # 'apt' should NOT be checked because Termux detection returns early
        mock_which.assert_called_once_with("pkg")
        self.assertNotIn(unittest.mock.call("apt"), mock_which.call_args_list)
        mock_write_cache.assert_called_once_with("pkg")

    @patch("pkgwrap.detector.platform.system")
    @patch.dict("os.environ", {}, clear=True)
    @patch("pkgwrap.detector.write_cached_backend")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_freebsd_environment(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_write_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test that FreeBSD environment isolates 'pkg' to freebsd_backend."""
        mock_system.return_value = "FreeBSD"
        mock_read_cache.return_value = None

        def which_mock(cmd: str) -> str:
            if cmd == "pkg":
                return "/usr/sbin/pkg"
            return None

        mock_which.side_effect = which_mock

        backend_name = detect_backend()

        # In FreeBSD, it should map to 'freebsd' identifier, not 'pkg'
        self.assertEqual(backend_name, "freebsd")
        mock_which.assert_called_once_with("pkg")
        mock_write_cache.assert_called_once_with("freebsd")

    @patch("pkgwrap.detector.platform.system")
    @patch("pkgwrap.detector.read_cached_backend")
    @patch("pkgwrap.detector.shutil.which")
    def test_detect_backend_none_found(
        self, mock_which: MagicMock, mock_read_cache: MagicMock, mock_system: MagicMock
    ) -> None:
        """Test that BackendNotFoundError is raised when no manager is found."""
        mock_system.return_value = "Linux"
        mock_read_cache.return_value = None
        mock_which.return_value = None
        
        with self.assertRaises(BackendNotFoundError):
            detect_backend()

if __name__ == "__main__":
    unittest.main()