# Garns W1 manager verification final correction

**Status:** integrity and unit matrix reproduced, review pending  
**Date:** 2026-10-03

The 26-file `W1-MANIFEST-3.sha256` has SHA-256
`3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`.
Verbatim builder testimony in `W1-DRAFT-3.md` has SHA-256
`6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566`.

Manager independently reproduced focused 34/34 tests on Python 3.14.3 and
full 137/137 tests on each existing interpreter: 3.11.14, 3.12.12, 3.13.12,
3.14.3. All returned exit 0. Commands from the product root used
`PYTHONDONTWRITEBYTECODE=1`, the existing cached Lark directory and `src` on
`PYTHONPATH`, and `-B -m unittest discover -s tests -t .` (focused:
`-s tests/contracts`). No warning filter was applied; inherited unclosed
SQLite ResourceWarnings recur on 3.13/3.14 and remain W3 work.

`tools/check_product.py` passed all five checks; every manifest entry matched
again after execution. No interpreter, dependency or service was installed.

This is pure contract/reference-model and inherited semantic verification,
not PostgreSQL execution, SQLite responsiveness, migration atomicity,
driver cancellation or real fault-cut evidence. Code/State review decides
acceptance. No clean Git commit or W2 launch is claimed.
