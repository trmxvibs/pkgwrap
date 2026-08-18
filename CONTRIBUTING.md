# Contributing to pkgwrap

Thanks for helping out. This project is small on purpose, so contributions
are easy to review when they follow a few conventions.

## Getting set up

```bash
git clone https://github.com/trmxvibs/pkgwrap.git
cd pkgwrap
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Ground rules

- **Target Python 3.9+.** Use `typing.List`/`Dict` rather than PEP 604 unions.
- **Never build a shell string.** Commands are lists passed to
  `subprocess.run(..., shell=False)`. This is the property that keeps user
  input from being interpreted.
- **Never force a non-interactive flag.** `-y`, `--noconfirm` and similar are
  added only when the user passed `-y`. If the tool has no prompt of its own,
  set `has_native_prompt = False` so pkgwrap adds one for removals.
- **Test what you change.** New behaviour needs a test; bug fixes need a test
  that fails without the fix.

## Adding a package manager

1. Create `src/pkgwrap/backends/<name>_backend.py` subclassing `Backend`.
2. Set `name`, `executable`, `requires_root` and `has_native_prompt`.
3. Implement `install`, `remove`, `refresh`, `upgrade`, `search`. Implement
   `list_installed`, `info` and `clean` if the tool supports them; leave them
   alone if it does not, and the base class will report them as unsupported.
   Do not invent a command that only half works.
4. Register the class in `src/pkgwrap/backends/__init__.py`.
5. Add the executable to `PRIORITY_MANAGERS` in `detector.py`, or to the
   OS-specific branch if the command name is ambiguous across systems.
6. Add a row to the README table.
7. Run `pytest`. The contract tests in `tests/backends/test_all_backends.py`
   pick up the new backend automatically.

In the PR, please say which system you verified the commands on. "Copied from
the wiki" is honest and useful information too, so we know what still needs
real-world confirmation.

## Releases

pkgwrap is distributed from source, not through a package index. A release is
a git tag plus a GitHub Release whose notes come from `CHANGELOG.md`. Please
do not add publishing steps or upload credentials to CI.

## Commit messages and PRs

- One logical change per PR.
- Update `CHANGELOG.md` under `## [Unreleased]`.
- Fill in the PR checklist.
