# Garns v9-6 governed write scope acceptance

**Status:** accepted at the exact tuple below after Consistency-2 and Safety-2
reported GO; accepts the governed-write release scope only  
**Date:** 2026-10-03  
**Owner:** manager

| Document | SHA-256 |
|---|---|
| `GarnsV9-6-GovernedWritesScopeAmendment.md` | `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe` |
| `GarnsExternalWriteCapture-ProjectBrief.md` | `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41` |
| `GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |
| `GarnsV9-6-OperatorDecisions-D6a-D7-D8.md` | `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f` |
| `GarnsV9-6-OperatorDecisions-D4-D6b.md` | `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce` |

Both read-only reviewers verified the tuple at start and end. Their complete
reports are filed verbatim:

- [Consistency focused re-verdict](GarnsV9-6-GovernedWritesScopeAmendment-ReviewConsistency-2.md): GO, no findings.
- [Safety focused re-verdict](GarnsV9-6-GovernedWritesScopeAmendment-ReviewSafety-2.md): GO, original P2-1 closed, no findings.

Initial Consistency was GO; initial Safety identified one schema-management
effect-accounting gap. One consolidated bounded correction explicitly covers
migration DML/backfills, DDL conversions/cascades and metadata-only generation
transitions. Safety verified its original counterexample on the corrected
tuple. One remediation round was used; no new architectural root cause remains.

D5 is closed as deferred. W6/P6 and capture-only identity/evidence requirements
are not release dependencies or passing gates. Governed durability, identity,
live/replay, schema-generation safety and independent final review remain
required. The future capture project is not launched.

W0 is already accepted. D1–D8 have their applicable decision artifacts, so W1
may draft A1–A15 and backend contracts under its execution brief. W1 itself
requires independent review before acceptance or a W2 handoff. No PostgreSQL
implementation, frozen public API or final release is accepted here.

This is SHA-pinned document acceptance in the inherited pre-initial-commit
review mode. It does not assert a Git commit, clean checkout or publication.
