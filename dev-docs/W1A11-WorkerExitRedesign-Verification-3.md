# Worker-exit redesign: final manager verification

Date: 2026-10-04. Owner: manager. Scope: correction 2/2, design only.

## Exact object

- Design: `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`.
- DRAFT-3: `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`.
- Complete 115-entry MANIFEST-3: `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`.

The manager read the complete 1,121-line final design in sequential, nontruncated
chunks. It contains all 14 numbered sections and 28 paired fence delimiters.
The final design was not edited during or after review.

## Required review gate

All six reports were received, read and filed in full verbatim. Their stored
testimony was compared with the filed bytes; all seven report/erratum copies
match. No current-round reviewer relied on another current-round report.

| Final report | Verdict | Scope |
|---|---|---|
| ReviewConsistency-3 | GO | Same-origin closure of both Consistency-2 findings, cross-check of Safety-2 finding, six earlier design findings, changed-range attack |
| ReviewSafety-3 | GO | Same-origin closure of Safety-2 finding, cross-check of both Consistency-2 findings, six earlier design findings, changed-range attack |
| OriginConsistencyClosure-3 | GO | Preservation of all four original Consistency findings |
| OriginSafetyClosure-3 | GO | Preservation of both original Safety findings |
| OriginCodeClosure-3 plus Erratum | GO | Prospective failed-FIFO and participant-lifecycle source counterexample closure |
| OriginStateClosure-3 | GO | Prospective worker-exit, failed-FIFO, neutral-refresh and phase-proof source counterexample closure |

No final reviewer reports a new architectural root, bounded blocker or P0–P3
design finding. The three second-correction changes are independently classified
as bounded corrections within the selected sole-mutation-owner architecture.
Both corrections are consumed; no third patch or counter reset occurred.

The original Code report contains a transcription error in its Revision1 map
hash. It is preserved verbatim. The same reviewer separately re-hashed the
actual map and reverified 88/88 entries, confirmed the pinned SHA
`50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`,
and retained its GO. The manager independently obtained the same verification.
The separate verbatim Erratum, not an edited report, corrects the evidence
citation. It changes neither design nor correction count.

## Independent boundary verification

All checks below passed both the final pre-filing check and the post-report
boundary, from the product root. All reviewers also report START/END passes.

| Check set | Entries verified | Failures |
|---|---:|---:|
| Final MANIFEST-3 | 115/115 | 0 |
| RemInputs-2 | 25/25 | 0 |
| Revision2 product-root archive map | 100/100 | 0 |
| Revision1 product-root archive map | 88/88 | 0 |
| RemInputs-1 | 13/13 | 0 |
| Original redesign Inputs | 19/19 | 0 |
| Stopped source MANIFEST-3 | 71/71 | 0 |
| ReadOnly | 111/111 | 0 |
| ProductGuard | 614/614 | 0 |

Historical manifests were not evaluated against the replacement design:
their byte-identical archive copies and explicit rebased verification maps
were used. The actual `src`/`tests` inventory contains 62 files; the guard
union names those exact 62, with no additions or omissions. No
`__pycache__` directory exists in either tree.

No test, generator, database, service, installation, network, Git or GWZ
mutation was used for this design-only gate. Existing passing tests are not
evidence that the replacement design is implemented. Source, tests, accepted
ADRs, grammar, generated evidence and shipped baseline remain unchanged.

## Manager cross-check

- Worker failures reserve/record exact effects and contain before any later
  effect; receiver disappearance never requires that receiver to resume.
  A finite multi-command ledger keeps C1 tombstones isolated from C2.
- Iterator success has one specialized publication/FIFO/terminal/release
  commit. Generic completion cannot bypass it. Failed delivery retains its
  active charge through exact worker-and-iterator stop before terminal release;
  queued successor invalidation does not invent delivered progress.
- Neutral commit consumes its candidate and terminalizes/releases its refresh
  atomically without a batch or publication. Coalesced spans and replay are
  bounded; current candidate fields remain backed by charged operations.
  Evicted opaque handles uniformly return unavailable without side history.
- Membership joins only at exact activated open and leaves only after every
  retained obligation. Frozen migration attempt membership stays immutable.
- No-effect proof is exact to current phase, serial, request and successor.
  The additive pre-effect edge is explicit and unavailable after an effect.
- The exact supersession table, operation-kind grammar, finding maps,
  mandatory regressions and prospective ownership descriptions agree.
  A7 unresolved transaction knowledge remains separate from worker quiescence.

## Scope and next gate

This evidence supports acceptance of the replacement design only. All five
stopped source roots remain OPEN: worker exit, failed FIFO, participant
lifecycle, neutral refresh and phase-proof freshness. The old source STOP and
its exhausted correction history remain valid.

A later separately authorized contract/reference build needs an exact execution
brief, cohesive path ownership, deterministic causal/property regressions,
a new frozen source tuple and executable originating Code/State closure.
Real locks, async/thread scheduling, adapters, provenance, durability and crash
recovery remain later evidence gates; no backend/runtime/planner work is
authorized here.

The review-loop skill supplied the peer-blind and same-origin closure gates.
The split-files skill preserved the recorded 796-line atomic-owner exception:
no unrelated line-count split or broad migration was attempted.
