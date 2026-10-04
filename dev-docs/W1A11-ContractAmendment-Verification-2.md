# W1/A11 amendment — manager verification after remediation 1

Status: verified candidate only; acceptance awaits independent reviewers.
Date: 2026-10-04.

Frozen complete59 manifest SHA-256:
7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b.
Amendment21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b.
Verbatim DRAFT-2d5c45f54f4fb1ed6105dd227050229b6a2c35b7517208df7156f36a041d4e58c.

## Independently reproduced commands

From the product root, with PYTHONDONTWRITEBYTECODE=1,
PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb
(cached Lark1.3.1), each authorized interpreter ran -B:

- -m unittest discover -s tests/contracts -t .: 85/85
- -m unittest discover -s tests -t .: 188/188
- tools/check_product.py: 5/5

All twelve commands exited0 on Python3.11/3.12/3.13/3.14. Exact interpreter
paths are in the execution brief. No warning filters. Existing SQLite
ResourceWarnings remain visible on3.13/3.14; no warning-free claim.

AST parsing passed23 contract/test modules; no compiler/runtime implementation
imports in contract foundations. No py_compile/compileall.

Hash checks passed complete59, RemInputs13, Inputs9, Control3, accepted
Baseline120, ReadOnly111 and ProductGuard614. Initial complete47 verifies from
inside Revision1, not against superseded live source. Historical accepted
source remains separately preserved in Baseline. Product inventory631 has zero
unowned additions or missing paths against prebuild inventory and expanded
exact allowlist. Cache search returned no .pyc or __pycache__ files.

## Limits

Green deterministic model tests do not independently close reviewer findings.
No production planner/lowering, async runtime, Postgres backend, live engine,
canonical provenance implementation, thread/cross-process synchronization,
physical activation/fencing, database/server compatibility or crash/restart
proof is claimed. Original W1 P3 remains deferred to W3. No Git/GWZ mutations,
network/install/services, generated evidence regeneration or live tools/check.py
execution occurred. Cohesive modules separate consumer, generation, buffer,
worker and recovery contracts; the611-line atomic lifetime graph has an explicit
exception/revisit point, not an under500-lines claim.

