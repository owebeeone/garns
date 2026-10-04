# Garns registry/containment bounded correction 2

**Status:** one accepted blocking P2; no architecture redesign  
**Date:** 2026-10-03  
**Replacement-object remediation round:** 2; architecture root count remains 1

Fresh Code reports GO with nonblocking P3-1; State reports NO-GO with one
bounded, non-architectural P2-1. Both verify all earlier replacement findings
and original stopped-W1 roots closed. Originating reviewers separately verified
the three initial replacement findings. Full reports remain verbatim.

| Finding | Disposition | Correction and independent closure test |
|---|---|---|
| State-2 P2-1 | Accept; bounded entry validation | Require exact OperationPhase/AbortEvidence at cancellation entry and exact ReconcileFinding at reconciliation entry, before producing knowledge. Exhaustive valid member relation plus matching raw strings, ints, bools, objects and foreign enums must refuse without dropping contained identity. Preserve committed same-scope revision and indeterminate rules. |
| Code-2 P3-1 | Accept; recorded nonblocking follow-up, deferred to W3 reference-model integration | Terminal idempotency currently permits the wrong finish_without_commit call after a known commit, without changing terminal truth. W3 must enforce method-specific preconditions before terminal fast return and add the stated regression. This is not a new package or blocker; no opportunistic P3 patch in this correction. |

One sole-owner patch, only state.py and matching contract tests within the
existing six-file boundary. No changed interface/return algebra/call graph,
new lifecycle state, ADR representation, dependency or backend work is needed.
Do not amend the trust promises or external-capture deferral. No source writes
after reporting complete. Full 3.11–3.14 plus focused tests and integrity gates.

Manager pins a complete manifest and draft. Continue the SAME round-2 State
reviewer for its original counterexample and focused re-verdict, and SAME
round-2 Code reviewer for unchanged-GO confirmation and changed-range review.
No peer current-round testimony is shared. A new architectural root cause
would invoke the review-loop cap, not authorize further redesign automatically.
No W2 launch or Git landing is authorized.
