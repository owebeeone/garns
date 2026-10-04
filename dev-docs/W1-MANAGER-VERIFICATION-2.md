# Garns W1 manager verification — corrected tuple

**Status:** tests and integrity reproduced; not review acceptance  
**Date:** 2026-10-03

The manager verified all 26 owned paths in `W1-MANIFEST-2.sha256`, manifest
SHA-256 `3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6`.
The complete builder testimony is preserved verbatim in `W1-DRAFT-2.md`,
SHA-256 `d78c83ddcce4e1660bed3ab3e36b3b473b05c5e28d0fc2c638479abc4a9b4569`.

From the product root, the manager independently ran the full suite with
`PYTHONDONTWRITEBYTECODE=1`, cached Lark and `src` on `PYTHONPATH`, using
`-B -m unittest discover -s tests -t .`:

| Existing interpreter | Full suite | Exit |
|---|---|---|
| CPython 3.11.14, uv-managed | 129/129 | 0 |
| CPython 3.12.12, uv-managed | 129/129 | 0 |
| CPython 3.13.12, Homebrew | 129/129 | 0 |
| CPython 3.14.3, Homebrew | 129/129 | 0 |

No dependency/interpreter download or installation occurred. Unlike the
builder's warning-suppressed matrix, manager runs did not suppress inherited
unclosed SQLite `ResourceWarning`s on 3.13/3.14. They remain recorded W3
lifecycle work, not fixed by this contract package.

`tools/check_product.py` passed all five checks. Grammar, inherited IR,
storage, engine, live runtime and `pyproject.toml` digests match pre-W1 values.
All 26 manifest entries still matched after the tests.

This establishes pure contract/reference-model and inherited semantic checks
only, not event-loop responsiveness, PostgreSQL execution, migration atomicity,
fault recovery, real four-major server provisioning, packaging installation,
Git cleanliness or a committed checkpoint. Independent Code/State verdicts
control W1 acceptance; the manager does not self-close review findings.
