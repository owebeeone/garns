# Garns registry and containment redesign correction verification

**Status:** manager verification reproduced; independent review pending  
**Date:** 2026-10-03

The complete 26-file manifest is `W1-RegistryContainmentRedesign-MANIFEST-2.sha256`,
SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`.
Builder testimony is filed verbatim in `W1-RegistryContainmentRedesign-DRAFT-2.md`,
SHA-256 `f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8`.
All manifest entries matched before reviewer dispatch and after manager tests.

Manager independently reproduced full 146/146 tests on existing CPython 3.11,
3.12, 3.13 and 3.14. Each ran from the product root with cached Lark and `src`
on `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1` and
`-B -m unittest discover -s tests -t .`. Unlike the builder's filed command,
the manager did not filter ResourceWarnings; inherited unclosed SQLite
connection warnings remain visible on 3.13/3.14 and are not fixed by W1.
Every command exited zero. All five product checks and five inherited
evidence-manifest entries passed; evidence checked from its own directory.

Comparison with the initial replacement manifest shows exactly four changed
paths: `state.py`, contract tests, A8 and ADR README. No added or removed
manifest paths. The context/registry implementation and A11 are unchanged.
The original six-file boundary is respected. Grammar, inherited IR/storage,
engine/live and pyproject hashes remain unchanged. No bytecode caches exist.

Canonical-template prompts for fresh Code and State reviewers are filed beside
this record. Prior reports/remediation are legitimate inputs; current peer
testimony is excluded. Fresh review is required because close-result grammar
changed. All blocking findings remain pending independent closure; green
tests and builder testimony do not constitute acceptance.

This evidence proves pure contracts/reference models and inherited semantics
only, not real database/worker behavior, driver cancellation, migrations,
restart durability, responsiveness or PostgreSQL support. No Git landing,
dependency installation, service operation, W2 or external-capture launch.
