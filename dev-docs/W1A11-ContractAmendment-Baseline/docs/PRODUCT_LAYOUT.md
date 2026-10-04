# Garns v9-6 product layout and ownership

**Status:** W0 materialized layout  
**Delivery shape:** one convergent implementation

This is the canonical path and ownership map required by D8. A later boundary
change requires a reviewed plan amendment; builders do not infer ownership
from nearby files.

| Package | Writable paths | Read-only inputs | Handoff |
|---|---|---|---|
| W0 | entire new product root | repaired B2, F51 docs, accepted plan and reviews | clean baseline, stable evidence, this layout; manager accepts before W1 |
| W1 | `docs/adr/**`, `src/garns/backends/contracts/**`, matching contract tests | compiler, plan inputs and promoted evidence | accepted A1–A15 and frozen protocol tuple; manager integrates |
| W2 | `src/garns/plan/**`, `src/garns/compiler/plan_bridge/**`, `src/garns/backends/sqlite/lower/**`, matching tests | W1 protocols and compiler IR | exhaustive plan/dialect seam reviewed before W3/W4 |
| W3 | `src/garns/runtime/**`, SQLite runtime outside `lower/**`, matching tests, `docs/api/**` after interface freeze | W1 protocols and W2 plan tuple | frozen public async/trust/lifecycle surface |
| W4 | PostgreSQL execution excluding `live/**` and `capture/**`, matching execution tests | W1–W3 tuples | real-server execution/migration baseline |
| W5 | `src/garns/live/**`, PostgreSQL `live/**`, matching live/concurrency tests | W3 surface and W4 backend | accepted revision/replay/subscription implementation |
| W6 | PostgreSQL `capture/**`, selected-branch tests and capture operations docs | accepted A5 and W4–W5 tuples | one evidenced external-capture branch |
| W7 | release, packaging, evidence and documentation; source corrections only through a finding-linked repair list | accepted W0–W6 | one integrated release candidate and review tuple |
| W8 | paths named by a separately reviewed declaration change request | accepted v9-6 release | independent later package |

## Admitted parallel sub-lanes

| Sub-lane | Writable paths | Product and handoff |
|---|---|---|
| PostgreSQL service tooling | `tools/postgres/**`, `tests/support/postgres/**` | reviewed service contract handed to W4 |
| API documentation research | `research/api-docs/**` | non-mergeable notes handed to W3 |
| PostgreSQL codec research | `research/postgres-codecs/**` | non-mergeable experiments handed to W4 |
| Capture research | `research/capture/**` | non-mergeable experiments handed to W6 |

The shared plan, public API, transaction, revision and replay protocols each
have one writer and one manager/integration owner. Research artifacts never
enter a release artifact directly.

## Current infrastructure status

The product root is a Git repository registered with GWZ as
`mem_garns_v9_6` at `garns-v9-6`. The manager verified registration and reran
the baseline checks before issuing `../dev-docs/W0-ACCEPTANCE.md`.
