"""Tests for package-name validation."""

import pytest

from pkgwrap.errors import InvalidPackageNameError
from pkgwrap.validation import validate_package_name, validate_package_names


@pytest.mark.parametrize(
    "name",
    ["nmap", "python3-pip", "gcc@13", "Git.Git", "dev-lang/python", "foo=1.2.3", "lib_c++"[:5]],
)
def test_realistic_names_are_accepted(name):
    assert validate_package_name(name) == name


@pytest.mark.parametrize("name", ["-y", "--force-yes", "-rf"])
def test_flag_like_names_are_rejected(name):
    with pytest.raises(InvalidPackageNameError):
        validate_package_name(name)


@pytest.mark.parametrize("name", ["", "   ", "foo bar", "foo;rm -rf /", "foo$(id)", "foo`id`"])
def test_empty_or_unsafe_names_are_rejected(name):
    with pytest.raises(InvalidPackageNameError):
        validate_package_name(name)


def test_overly_long_name_rejected():
    with pytest.raises(InvalidPackageNameError):
        validate_package_name("a" * 500)


def test_duplicates_are_collapsed_but_order_kept():
    assert validate_package_names(["curl", "nmap", "curl"]) == ["curl", "nmap"]


def test_empty_list_rejected():
    with pytest.raises(InvalidPackageNameError):
        validate_package_names([])
