# AGENTS — garns-v9-6

Read and obey `../AGENTS_GWZ.md` and this file before doing any work.

## Current package state

This tree is the single convergent v9-6 product root selected by D8. W0 is a
mechanical promotion of the repaired and ratified v9-5 B2 implementation.
The manager accepted this baseline in `dev-docs/W0-ACCEPTANCE.md` after
registration and renewed verification. W1 must follow the accepted plan and
its decision gates; PostgreSQL and the async API remain future work.

The repository is registered with GWZ as `mem_garns_v9_6` at `garns-v9-6`.
Use the GWZ workflow for workspace operations; never edit `gwz.conf/` directly.

## Binding decisions

- CPython 3.11 and above; package metadata has no upper bound.
- PostgreSQL is the primary production direction, but it is not implemented by
  W0.
- SQLite is a supported secondary runtime, not test/development only, behind
  the same async-facing contract and an explicit capability matrix.
- PostgreSQL support starts at 15: initially test 15, 16, 17 and 18, adding
  subsequent stable majors with real-server verification before claiming them.
- The eventual public database API is async-only.
- v9-6 is governed-write only: external-write capture is deferred to a
  separate future project and is not a release dependency. Durable governed
  transactions, ledger, live delivery and replay remain required.
- Authentication enters core through an in-process provider-neutral trusted
  context. External cryptographic authentication belongs to another library or
  service boundary.
- There is one product implementation. Parallel work requires frozen
  interfaces and non-overlapping ownership from `docs/PRODUCT_LAYOUT.md`.

The binding support-tier and server-range record is
`dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md`; it is additive to the
hash-pinned plan and earlier D6a/D7/D8 decisions.

`dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md` closes D5 as deferred
and supersedes external-capture release obligations. Its operator decision is
binding; the exact scope tuple is accepted in
`dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md` after GO/GO.
W1 must implement those obligations in its reviewed contracts. W6/P6 are
deferred, not passing gates. The future effort is described in
`dev-docs/GarnsExternalWriteCapture-ProjectBrief.md` and is not launched.

## Preserved language and evidence rules

- `grammar/garns.lark` remains byte-identical to the ratified grammar during
  W0.
- `query` is static, expressive, fetch-only and one-shot.
- `question` is dynamic, closed-algebra, footprinted, bounded and live.
- `unenforced` remains a standalone link flag, not an `end` kind.
- No numbered-case execution, schema-name dispatch, expected-answer dispatch,
  corpus vocabulary default or guessed physical storage name is permitted.
- Generated evidence counts only when deletion and regeneration from source
  reproduces it byte-for-byte.

## W0 write and verification boundary

- W0 may write this root only. `../garns-v9-5/` is read-only evidence.
- Do not use network access or install dependencies during W0.
- Run Python commands with `PYTHONDONTWRITEBYTECODE=1`.
- The product gate is `tools/check.py`; `tools/check_product.py` replaces the
  old evaluation-lane scaffold check.
- D4 and D6b are closed by the later operator record above, not by W0.
  D5 is closed as deferred by the accepted governed-write scope amendment.
  W1 must freeze and independently review the scoped ADRs before handing off.
