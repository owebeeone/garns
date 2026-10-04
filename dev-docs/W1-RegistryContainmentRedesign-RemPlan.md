# Garns registry containment redesign consolidated correction

**Status:** three accepted P2 findings, one correction authorized  
**Date:** 2026-10-03  
**Replacement-object remediation round:** 1 of at most 2 architectural rounds

Both independent reviewers verified the two original stop counterexamples
closed, but both report NO-GO. Their full reports are preserved verbatim.
No redesign or W1 acceptance occurs yet. All three current findings are accepted.

| Finding | Disposition and correction | Required closure test |
|---|---|---|
| Code P2-1 | Accept, bounded lifecycle validation: refuse duplicate active or terminally reused identity at worker admission, before changing state. Repeated resolution remains idempotent for the original operation; publication retry does not authorize fresh worker work. | Duplicate active begin and begin after terminal resolution refuse without mutation; repeat/conflicting resolution; equal IDs in distinct qualified scopes; no stranded or collapsed command identities. |
| State P2-1 | Accept, bounded validation: enforce closed CommitKnowledge and knowledge/revision relation at construction and again before worker resolution mutation. Malformed knowledge must not count as terminal. | All valid members and malformed strings/integers/bools/custom objects; preserve containment on refusal and on indeterminate. Manager independently reproduced string `indeterminate` incorrectly clearing containment, converging with the State review's fabricated-knowledge trace. |
| State P2-2 | Accept, architectural close-state completion: worker quiescence is independent of pending transaction knowledge. Add typed nonquiescent outcome admitting zero or more unresolved identities; CLOSED requires quiescence and no pending identities. | Exhaustive quiescence × pending-count/phase/final-resolution product, including never-begun and terminally resolved but still running worker. No invented identity, no exception for an accepted reachable state, no final transaction relabeled uncertain. |

Same sole architecture owner; existing six-file redesign boundary applies.
One consolidated patch, no authority redesign needed: empty handle and registry
stay unchanged unless an actual correction requires it. Close-state additions
stay in `state.py`; update A8 and ADR index diagrams. No shared protocol,
backend/worker/service, grammar, dependency, installation or Git work.

Retain all old regressions and run focused/full Python 3.11–3.14 suites plus
product/integrity checks. Return full testimony and stop writes for pinning.
The manager files a new complete manifest and draft; old tuple/reports remain.
Source changes are not acceptance or builder self-closure.

The close-state algebra changes a shared return contract, so the review-loop
skill requires fresh peer-blind Code/State reviewers after this patch. They
verify original counterexamples and changed ranges. One further architecture
remediation allowance remains for this explicitly operator-authorized object;
historical W1's exhausted count remains recorded separately. Any cap escalation
stops for operator direction, not another silent redesign.
