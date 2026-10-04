# Garns registry and containment redesign verification

**Status:** integrity and test matrix reproduced, review pending  
**Date:** 2026-10-03

The manager independently reproduced full 142/142 tests on each existing
CPython 3.11.14, 3.12.12, 3.13.12 and 3.14.3. Commands ran from the product
root with `PYTHONDONTWRITEBYTECODE=1`, cached Lark and `src` on `PYTHONPATH`,
using `-B -m unittest discover -s tests -t .`. No download or installation
occurred. No warning filter was used; inherited unclosed SQLite warnings
remain recorded W3 work, not fixed by these contracts.

All five product checks and all five inherited evidence entries passed.
Grammar, inherited IR/storage/engine/live and `pyproject.toml` digests match
pre-W1 values. Every entry in the complete 26-file redesign manifest matched
after tests. Comparing stopped and replacement checksum inventories showed
exactly the six authorized changed paths, with no additions or removals.

The current manifest is SHA-256
`fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff`;
the complete builder report is preserved verbatim at SHA-256
`d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd`.

This is pure contract/reference-model and inherited semantics evidence only,
not database, real worker, responsiveness, migration atomicity, restart or
fault-cut proof. Tests do not substitute for independent review verdicts.
