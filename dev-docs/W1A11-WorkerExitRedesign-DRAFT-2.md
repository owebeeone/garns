COMPLETE — correction 1/2 is drafted and writes are stopped.

Output: [W1A11-WorkerExitRedesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W1A11-WorkerExitRedesign.md)  
SHA-256: `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`  
Size: 937 lines, 61,950 bytes; 14 numbered sections; 28 balanced Markdown fences.

Correction dispositions:

- `Consistency-1 P2-1`: explicitly supersedes accepted W2 overlay §3.1’s deployment edge set and §8.2 steps 6–8. Defines one deployment-state × attempt-phase product and exactly one proof-gated `MIGRATING × MIGRATING_PRE_EFFECT -> CURRENT(old,new epoch)` edge. DRAINING proofs become stale after transition; `EFFECT_BEGUN` permanently disables this edge.
- `Consistency-1 P2-2`: replaces singular command fields with a finite operation-owned schedule and ordered ledger of at most `M` exact command records, one active serial, distinct per-command worker/authorization/effects/cleanup/exit state, retained tombstones, and one outer permit. Later command dispatch requires prior result acceptance. Removing queued C2 cannot erase C1 work or claim whole-operation `CANCELLED_CONFIRMED`.
- `Consistency-1 P2-3`: commits a non-effect body failure receipt before cleanup. Effect failure remains primary; cleanup-only failure is primary; body/effect/cancel winners retain primary status while later cleanup/race errors occupy bounded diagnostic slots.
- `Safety-1 P2-1`: adds a trusted provider-issued receiving-task lifecycle observation. Its one mutation invalidates the exact original context record and operation binding, then removes queued work or contains running, pending-success, quiescent-success, contained, or accepted-before-publication work. The containment owner can finish without the vanished task resuming.
- `Consistency-1 P2-4` and `Safety-1 P2-2`: defines queued capacity `Q = min(N, deployment ceiling)` or default `Q = N`, total changed-lineage capacity `C = Q + 1`, and replay bound `R = C`. Neutral ranges coalesce to one span per changed-work gap; storage is bounded to `2C` lineage records and `C` replay entries. Replay eviction, stale candidates, retired registrations, overflow and bounded fold/discard work have explicit typed behavior.

Proposed causal evidence now includes:

- Full migration product enumeration; stale DRAINING proof, exact current pre-effect success once, and post-effect/wrong/replayed/cross proof refusals.
- C1→C2 under one permit, premature C2 refusal, cross-command receipt/authorization/ordinal attacks, later-command queue removal, and one outer release.
- Body-only, cleanup-only, body+cleanup, effect+cleanup and cancellation/cleanup races.
- Receiver termination without application cancellation at every pause from queue insertion through prepublication, including wrong/copy/stale/replayed lifecycle observations.
- More than `C` neutral refreshes behind a delayed active head, multiple changed gaps, replay inside/outside `R`, later changed work, overflow, success/failure, close and migration.

The original five stopped source roots, initial 18 regressions, stopped-amendment correction-1 13 regressions, expanded revocation, no-raw-`Plan`, task-bound claim-free public context, A7 independence, result roles, pinned parameters, parent-owned derived commands and single mutation-owner boundary remain preserved.

Integrity passed at both START and END:

- RemInputs-1: 13/13, zero failures.
- Revision1 archive verification map: 88/88, zero failures.
- Original Inputs: 19/19, zero failures.
- Frozen source MANIFEST-3: 71/71, zero failures.
- ReadOnly guard: 111/111, zero failures.
- ProductGuard: 614/614, zero failures.

Pinned hashes:

- RemPlan-1: `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`
- RemInputs-1: `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`
- Revision1 verification map: `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`
- Archived revision-1 design: `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`

The original MANIFEST-1 was correctly verified through the rebased Revision1 archive map, not falsely checked against the intentionally revised live design.

I reread the complete workspace/product instructions, original brief, RemPlan-1, both full blocking reports, originating report, review-loop skill/template, split-files skill, exact accepted W2 clauses and relevant ADR text. Inspection used `sed`, `nl`, `rg`, `wc`, `awk`, `find`, `ls`, and `shasum`. No tests were run because this is prospective design correction only.

Only the authorized design file was edited, using `apply_patch`. The original DRAFT, archive, source, tests, ADRs, accepted W2 documents, reports and manifests were not edited. No helpers, Git/GWZ, network, install, service, database, bytecode, generator, runtime implementation or `tools/check.py` action occurred.

This is not acceptance or self-closure. All six correction findings and all stopped source findings remain open pending manager pinning as DRAFT-2, fresh Consistency/Safety review, same-origin retracing, and originating-counterexample review.
