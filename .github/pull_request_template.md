## What does this change?

<!-- One or two sentences. Link the issue it closes, if any. -->

Closes #

## Checklist

- [ ] `pytest` passes locally
- [ ] `ruff check .` passes
- [ ] New or changed behaviour is covered by a test
- [ ] Docs updated (README / `--help` text) if the user-facing behaviour changed
- [ ] `CHANGELOG.md` updated under "Unreleased"

## For a new backend

- [ ] Added `src/pkgwrap/backends/<name>_backend.py`
- [ ] Registered it in `src/pkgwrap/backends/__init__.py`
- [ ] Set `requires_root` and `has_native_prompt` correctly
- [ ] Added it to the detector's probe order and to the README table
- [ ] Verified the commands on a real system (please say which)
