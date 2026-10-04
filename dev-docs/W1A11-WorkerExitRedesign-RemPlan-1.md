# W1/A11 worker-exit redesign — consolidated correction 1

**Status:** authorized design-only correction 1 of at most 2; not acceptance
**Date:** 2026-10-04
**Owner:** manager

## 1. Exact reviewed object and verdict merge

Revision 1 design SHA-256:
`62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`.
Complete 88-entry MANIFEST-1:
`79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`.

- Consistency-1: NO-GO, four P2 findings; report SHA
  `67ac6f8e42755ec19446823071104f50fa3b357d402bab3d548185a26fab40d4`.
- Safety-1: NO-GO, two P2 findings; report SHA
  `d8ad5f935baf178ebd69999a9e00ef1585758935586e13241e1dd5d8a5303984`.
- OriginStateClosure-1: prospective GO only; report SHA
  `9ff6a67168df89ad967ddf1c0b239fa78a0bf778c827959a1f65ddc2079c3a73`.
  Its narrow GO does not override the full reviewers' blocking findings.

The two full axes independently converge on unbounded neutral lineage/replay.
There are five distinct roots across six IDs. All are accepted for correction,
none disputed, deferred or self-closed. Both full axes pre-commit to GO only
if their remedies are met without new blockers. Safety classifies its two
remedies as bounded within the chosen architecture. The necessary command
ledger, lifecycle observation and explicit migration-edge amendment materially
change contract shapes: fresh full dual review is required in addition to
same-origin focused closure, regardless of bounded-text edit classification.

## 2. One consolidated disposition

| ID(s) | Exact disposition in one design edit | Mandatory prospective closure |
|---|---|---|
| Consistency-1 P2-1 | Explicitly supersede the accepted W2 overlay §3.1 deployment-state table/legal edges and §8.2 step 7, not just step 6. Define one deployment-state × attempt-phase product. Add exactly the sealed-request-proof-gated pre-effect return to old CURRENT, forbidding it after EFFECT_BEGUN. A16/source remain unaccepted evidence, not authority. | Enumerate legal product edges, stale DRAINING proof after begin-migration, exact new pre-effect proof success once, and the same proof after effect start/wrong request/successor/replay mutation-free. Assert binding, epochs, phase serial, requests, queue markers, membership and permits. |
| Consistency-1 P2-2 | Replace singular command fields with an operation-owned ordered exact command ledger, unique command serial, at most one active command, per-command schedule/worker/auth/reservation/exit and retained prior tombstones. Define the runtime-continuation dispatch edge for subsequent derived commands without resetting prior states or acquiring another operation permit. State finite command/tombstone retention tied to the operation's bounded closed schedule. | At least C1 then C2 under one permit; reject C2 before C1 acceptance; replay C1 exit/stop and use C1 ordinal/auth against every C2 state without C2 mutation; one outer terminal release. |
| Consistency-1 P2-3 | Commit every non-effect body failure/cancel receipt before cleanup starts; already-contained effect failure remains primary. Cleanup-only failure after successful body is primary; later cleanup failures are bounded diagnostics. Define ordering for racing cancellation and fix the contradictory mandatory trace. | Body-only, cleanup-only, body+cleanup, effect+cleanup, cancel/cleanup race: one first authoritative receipt, one transfer, unchanged primary effect knowledge, revoked unused ordinals and charge retained to exact stop. |
| Safety-1 P2-1 | Introduce an issuer-owned exact receiving-task lifecycle observation from trusted task provider, not a caller identity or callback. Task-done/cancelled must invalidate original authority explicitly and atomically remove queued or contain running/pending/quiescent-success/accepted-before-publication work. Specify request/dequeue race, replay/conflict and eventual containment terminalization without requiring the vanished task to resume. | Terminate exact receiver without application cancellation request at every listed pause from queue through prepublication; no value, one owner, revocation, preserved A7, correct quiescence and one eventual release. Wrong/stale/copy/replay task observations are exact refusal/idempotency. |
| Consistency-1 P2-4 AND Safety-1 P2-2 | Coalesce consecutive neutral intervals within the same changed-work gap; choose explicit finite bounds/defaults for lineage, replay receipts and per-mutation fold/discard work derived from validated live capacity. Specify deterministic stale/evicted receipt behavior, no unlimited candidate/tombstone side table, and typed overflow/retirement before consuming another candidate. Preserve zero batches/permits, exact classification/consumption and changed-neutral-changed causality. | Delay active changed head and exceed authored/replay bound by many refreshes; bounded state or exact retirement, no false delivery/permit/publication. Test multiple gaps, later changed work, old receipt/candidate replay, success/failure/close/migration and finite settlement work. |

Retain the original five stopped source roots and all initial 18/correction-1
13 causal regressions plus expanded revocation. Update supersession, methods,
records, transitions, mandatory traces, finding map and ownership sections
coherently; do not append a guard that leaves earlier contradictory text live.

## 3. Write boundary and preserved invariants

The sole drafter may edit ONLY:
`dev-docs/W1A11-WorkerExitRedesign.md`.

Return complete stop-writing testimony; manager files it as DRAFT-2.
No source/test/ADR/accepted W2/old reports/checkpoint edits, no helpers, no
implementation, public surface freeze, planner/backend/runtime/activation,
external capture, Git/GWZ/network/install/services/database/generator work.

One lifetime mutation owner; coordinator generation ownership and lock order;
no raw Plan or arbitrary per-invocation effect callback; exact sealed identities;
task-bound claim-free public context; original result roles and pinned parameters;
parent-owned derived commands and one operation permit; unchanged A7 transaction
truth independent of worker quiescence; governed-write scope remain controlling.

Use review-loop and split-files guidance, preserving the 796-line atomic-owner
exception rather than starting an unrelated source refactor. Read all six full
blocking findings and their complete causal sequences, not just this table.

## 4. Revision archive and guard protocol

Revision1 holds byte-identical copies of the original design, DRAFT and original
MANIFEST-1. The remaining 86 inputs are unchanged live pinned evidence, not copied
source. VERIFY-from-product-root.sha256 deliberately rebases only the two mutable
design/testimony paths to the archive and verifies all 88 original hashes from
the PRODUCT ROOT. It is a derived verification map, not a rewritten review tuple.
Its hash is `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`.

At start and end verify new RemInputs, revision1 verification map88,
Inputs19, stopped MANIFEST-3 source71, ReadOnly111 and ProductGuard614.
The original MANIFEST-1 cannot be checked against revised live design bytes;
check its original entries through the explicitly rebased archive map.
No tests are required or claimed as prospective design closure.

## 5. Next gate and cap

After stop-writing, manager pins complete revision2 and new DRAFT-2, generates
canonical prompts, runs fresh peer-blind Consistency/Safety, and asks the prior
full reviewers to retrace their own findings. Originating stopped worker/four
bounded attacks must still receive prospective retracing at the final tuple.

Correction count becomes 1/2 when this edit is delivered. No finding closes on
drafter claims. A new architectural root after two corrections triggers STOP,
not a hidden third correction. Exact GO/GO plus originating closure permits
design-only acceptance; source findings remain open and implementation requires
a separately authorized exact brief.

