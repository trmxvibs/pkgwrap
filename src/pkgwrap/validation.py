"""Validation helpers for user-supplied package names.

Commands are executed with ``shell=False``, so shell metacharacters are not
a code-execution risk. The remaining risk is *argument* injection: a name
that begins with a dash would be interpreted as an option by the underlying
package manager. These checks reject such input early, with a clear message.
"""

import re
from typing import Iterable, List

from pkgwrap.errors import InvalidPackageNameError

#: Characters allowed in a package name or specification. Deliberately wide
#: enough for real-world names such as ``python3-pip``, ``gcc@13``,
#: ``Git.Git``, ``dev-lang/python``, ``foo=1.2.3`` and ``nixpkgs.hello``.
_ALLOWED = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+@:/=~^-]*$")

_MAX_LENGTH = 200


def validate_package_name(name: str) -> str:
    """Validate a single package name.

    Args:
        name: The raw name supplied by the user.

    Returns:
        The name, unchanged, when it is acceptable.

    Raises:
        InvalidPackageNameError: If the name is empty, too long, looks like a
            command-line flag, or contains characters outside the allow-list.
    """
    if name is None or not name.strip():
        raise InvalidPackageNameError("Package name cannot be empty.")

    name = name.strip()

    if len(name) > _MAX_LENGTH:
        raise InvalidPackageNameError(
            "Package name is too long ({0} characters, maximum {1}).".format(
                len(name), _MAX_LENGTH
            )
        )

    if name.startswith("-"):
        raise InvalidPackageNameError(
            "'{0}' looks like a command-line option, not a package name. "
            "pkgwrap will not forward it to the package manager.".format(name)
        )

    if not _ALLOWED.match(name):
        raise InvalidPackageNameError(
            "'{0}' contains characters that are not valid in a package name.".format(name)
        )

    return name


def validate_package_names(names: Iterable[str]) -> List[str]:
    """Validate several package names, preserving order and removing duplicates."""
    validated: List[str] = []
    for name in names:
        clean = validate_package_name(name)
        if clean not in validated:
            validated.append(clean)

    if not validated:
        raise InvalidPackageNameError("At least one package name is required.")

    return validated
