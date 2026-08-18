# Security Policy

## Supported versions

Only the latest released version receives fixes.

| Version | Supported |
| ------- | --------- |
| 0.2.x   | yes |
| < 0.2   | no |

## Reporting a vulnerability

Please report security issues privately, not in a public issue:

1. Preferred: open a [private security advisory](https://github.com/trmxvibs/pkgwrap/security/advisories/new).
2. Otherwise, contact the maintainer through their GitHub profile.

Please include the pkgwrap version, `pkgwrap --backend` output, your OS, and a
minimal reproduction. A first response should arrive within seven days.

## Distribution

pkgwrap is installed from source from this repository only. It is not
published on PyPI or any other package index, so any package with a similar
name on an index is **not** produced by this project. Verify that you are
cloning `https://github.com/trmxvibs/pkgwrap` before installing.

## Threat model

pkgwrap runs the system package manager on the user's behalf, so the areas
that matter most are:

- **Command construction.** Every command is a list executed with
  `shell=False`; pkgwrap never builds a shell string. Package names are
  validated to reject option-like input, so a name cannot become a flag.
- **Privilege escalation.** `sudo` is added only for operations that need it,
  and only after a confirmation, unless `-y` is given or the process is
  already root.
- **Confirmation.** pkgwrap does not pass a package manager's non-interactive
  flag unless the user asked for it. For managers that never prompt, pkgwrap
  adds its own confirmation before removals.
- **Cached state.** The detection cache lives in the user's config directory
  and is validated against the backend registry on read, so an edited cache
  cannot cause an arbitrary program to be executed.

Out of scope: vulnerabilities in the underlying package managers, and anything
that requires an attacker to already have write access to the user's account.
