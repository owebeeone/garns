# Garns W1 manager verification

**Status:** draft tuple verified, not architecture acceptance  
**Date:** 2026-10-03

The manager verified all 22 entries in `W1-MANIFEST.sha256`, whose digest is
`5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`.
The builder report remains preserved verbatim in `W1-DRAFT.md`.

The builder reported Python 3.11/3.12 unavailable. The manager subsequently
located existing interpreters with `uv python find --no-python-downloads`.
This supplements that historical report without changing the reviewed bytes.

From the product root, with existing cached Lark and source on `PYTHONPATH`,
the manager ran `-B -m unittest discover -s tests -t .` with
`PYTHONDONTWRITEBYTECODE=1`:

| Interpreter | Full unit suite | Exit |
|---|---|---|
| CPython 3.11.14 | 128/128 | 0 |
| CPython 3.12.12 | 128/128 | 0 |
| CPython 3.13.12 | 128/128 | 0 |
| CPython 3.14.3 | 128/128 | 0 |

The existing dependency directory was
`/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`.
Python 3.11/3.12 were existing uv-managed runtimes; Python 3.13/3.14 were the
Homebrew executable. No download or installation was performed.

`tools/check_product.py` passed all five product checks. Grammar, inherited
IR/storage/engine/live and dependency metadata digests remained unchanged from
the manager's pre-W1 checks. The inherited unclosed SQLite ResourceWarnings
recurred under Python 3.13/3.14 and remain deferred to lifecycle implementation.

These results establish declaration/reference-model and inherited semantic
test execution only. They do not establish PostgreSQL behavior, event-loop
responsiveness, driver cancellation, four-major service provisioning, packaging
installation, a clean Git commit or architecture review acceptance.
