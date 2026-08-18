import unittest
from pkgwrap.package_map import resolve_package_name


class TestPackageMap(unittest.TestCase):
    def test_known_package_known_backend(self):
        self.assertEqual(resolve_package_name("pip", "apt"), "python3-pip")
        self.assertEqual(resolve_package_name("pip", "pacman"), "python-pip")
        self.assertEqual(resolve_package_name("pip", "apk"), "py3-pip")

    def test_case_insensitive(self):
        self.assertEqual(resolve_package_name("PIP", "apt"), "python3-pip")

    def test_unknown_package_passthrough(self):
        self.assertEqual(resolve_package_name("some-random-tool", "apt"), "some-random-tool")

    def test_known_package_unknown_backend(self):
        self.assertEqual(resolve_package_name("pip", "nix"), "pip")


if __name__ == "__main__":
    unittest.main()