# W1A11-WorkerExitRedesign — ORIGINATING CONSISTENCY CLOSURE 2

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; operator-authorized correction 1/2 design candidate, not accepted or implementation authority; 2026-10-04.  
**Baseline:** approved filesystem-SHA exception, read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`; 100-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-2.sha256` at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`. Comparison baseline was the archived Revision 1 design at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`, verified through the rebased 88-entry archive map rather than the changed live paths. The stopped 71-file source remains evidence only and unaccepted.  
**Date:** 2026-10-04  
**Axis:** Same-origin focused Consistency closure — retrace only originating `Consistency-1 P2-1` through `P2-4`, inspect correction ranges for new roots, and classify architectural versus bounded change. Independent, adversarial, read-only. Fresh full axes run separately; nothing here relies on them. Filed verbatim by the lane owner.

**Verdict: GO** — all four originating Consistency findings are prospectively closed on the corrected design, and no new blocking root was found in their correction ranges. This fulfills the originating reviewer’s conditional pre-commit to GO. It is not an overall design acceptance, fresh-axis verdict, stopped-source closure, or implementation authority.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| `Consistency-1 P2-1` | Explicitly supersede accepted overlay §3.1’s deployment-state/legal-edge grammar and §8.2 steps 6–8; define one deployment-state × attempt-phase product with exactly one proof-gated pre-effect return from `MIGRATING`. | Retraced the original sequence. A proof issued in `DRAINING_OLD × DRAINING_OLD` becomes stale when `begin_migration` changes the phase serial/request and enters `MIGRATING × MIGRATING_PRE_EFFECT`. A newly issued exact pre-effect proof may consume once and move to `CURRENT(old,new epoch) × NONE`. The first effect first moves the product to `MIGRATING × EFFECT_BEGUN`, from which that edge is structurally absent. Replay and wrong phase/request/successor/attempt/coordinator refuse without mutation. §§2 and 11 now name the accepted clauses being replaced, and proposed A16/source are explicitly evidence rather than authority. | **CLOSED** |
| `Consistency-1 P2-2` | Replace singular command fields with a finite operation-owned ordered ledger, unique command serials, one active record, per-command schedules and retained tombstones under one outer permit. | Retraced C1→C2. C1 allocates its own ledger record, authorization, worker, effect/cleanup schedules and exit serial. Exact stop and acceptance leave C1 terminal at `RESULT_ACCEPTED`, retain its tombstone and clear the active serial. Only then may C2 allocate the next record without another operation/generation permit. C1 replay resolves solely against C1; C1 authorization or ordinals cannot validate against C2. Premature, out-of-order or beyond-`M` dispatch refuses. Publication requires required serial `M` accepted and no active command; the outer charge releases only at terminal publication or authoritative containment completion. | **CLOSED** |
| `Consistency-1 P2-3` | Commit non-effect body failure before cleanup; cleanup-only failure is primary; retain first-commit ordering and bounded diagnostics for body/effect/cancel plus cleanup races. | Retraced all original schedules. A non-effect body `BaseException` now calls `worker_exit_failure` before cleanup starts. An effect exception already has its primary receipt from `run_effect`. Later cleanup failures occupy only their finite step diagnostics. If the body succeeded, the first cleanup failure creates the sole primary receipt and discards the private result. Cancellation racing cleanup is registry-lock first-commit-wins, with the loser restricted to its bounded race/step diagnostic. Effect knowledge, owner transfer, ordinal revocation and A7 truth cannot be replaced by a diagnostic. | **CLOSED** |
| `Consistency-1 P2-4` | Coalesce neutral intervals by changed-work gap; derive finite lineage/replay/work bounds from live capacity; define deterministic eviction, stale replay and typed retirement. | Retraced the delayed-head sequence. Validated queued capacity is positive `Q`; active-plus-queued changed capacity is `C = Q + 1`; neutral replay capacity is `R = C`. More than `C` neutral commits behind one delayed changed head extend one `NEUTRAL_SPAN` rather than append lineage and evict at most one oldest replay record per commit. Across all gaps, lineage is at most `2C` and replay at most `C`, with no auxiliary candidate/receipt table. A later changed range preserves the gap boundary; normal success folds at most one changed record and one span. Capacity overflow retires/refetches before candidate consumption or cursor movement, and retirement/close/migration work is explicitly bounded. | **CLOSED** |

## Changed-range analysis

The archived Revision 1 and corrected design differ across 730 unified-diff lines, concentrated in the exact remediation areas plus their test/finding/ownership mappings.

The following are architectural corrections required by the consolidated plan:

- §§2 and 11 replace part of the accepted migration compatibility grammar with a closed deployment-state × attempt-phase product. This is an architectural contract change, but it is the prescribed correction for `P2-1`, not a new root. The supersession boundary is now explicit and preserves all post-effect indeterminacy.
- §§3–6 replace the singular command tuple with an operation-owned command schedule and ledger. This changes private record shape, dispatch edges and replay routing, so it is architectural. It directly resolves `P2-2` without creating a second mutation owner or permit.
- The receiving-task lifecycle observation and its state-specific transitions are also architectural, but they are the planned `Safety-1 P2-1` correction. I inspected their integration only for consistency with the four sequences: they invalidate the same operation binding, route through the sole lifetime owner, preserve per-command tombstones and do not reopen any command or alter A7 truth. This focused report does not independently close the Safety finding.

The following are bounded corrections within the selected architecture:

- §5.3’s body/cleanup ordering and finite `K`-step diagnostics are a local ordering/bounded-retention correction for `P2-3`.
- §10’s `Q`, `C`, `R`, coalesced spans, replay ring and bounded retirement work are a finite resource-contract correction for shared `P2-4`/`Safety-1 P2-2`. They add no new owner or unbounded side ledger.

The remaining changed ranges update mandatory traces, finding maps, future file ownership and review-gate language to match those corrections. I found no unrelated behavioral expansion and no new architectural root cause in the changed ranges. Because the migration product, command ledger and receiver-lifecycle boundary materially alter architecture, the correction properly requires fresh full Consistency/Safety review in addition to this same-origin closure.

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-2.sha256` matched `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`; all 100/100 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; all 13/13 entries verified.
- The Revision 1 archive verification map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`; all 88/88 original entries verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; all 19/19 entries verified.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; all 71/71 entries verified.
- `ReadOnly` matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; all 111/111 entries verified.
- `ProductGuard` matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; all 614/614 entries verified.

The corrected design remained at `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; DRAFT-2 remained at `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`; RemPlan-1 remained at `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`.

The archived originals remained:

- design `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`;
- DRAFT `e8fd137970df5dc62ce5e838b6ca8f267a43343167f32805da75c2d2650b76b7`;
- MANIFEST-1 `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`.

I read completely:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill and canonical prompt/report template;
- corrected `W1A11-WorkerExitRedesign.md`, DRAFT-2 and RemPlan-1;
- both complete filed round-1 reports, whose hashes remained `67ac6f8e…` for Consistency and `d8ad5f93…` for Safety;
- the archived Revision 1 design and the complete corrected-versus-archived diff;
- the accepted W2 command/lifetime clauses and A6/A16 text necessary to retrace the four original causal sequences.

The principal corrected ranges were §§2–7 at lines 53–485, §10 at lines 616–725, §11 at lines 727–825, and the disposition/ownership/review sections at lines 827–937.

No current-round fresh report, originating report or current-round prompt was read. No helper was used. No test was run because this is prospective design closure and the stopped source cannot evidence it. No file, source, test, manifest, generated artifact, bytecode, Git/GWZ state, service or database was modified.

## 2. Invariant analysis

The original four attacks now hold:

- The migration grammar has one authority. The accepted clauses being changed are named; the sole new pre-effect edge is product-state-specific, proof-gated and unavailable after effect start.
- Multi-command work retains one outer lease and generation permit while command authority remains exact per serial. Prior tombstones are retained until outer terminal state and cannot be overwritten by later command records.
- The finite positive closed operation schedule supplies an explicit maximum `M`; at most one record is nonterminal. Required-slot publication and serial-sensitive queue removal prevent later-command cancellation from erasing prior work.
- Failure ordering is temporal and single-owner: the body/effect/cancel transition that commits first owns the primary receipt and containment transfer. Finite cleanup and race slots cannot change primary facts.
- Neutral progress remains causal without consuming delivery permits. It cannot overtake a changed head, merge across a later changed entry, grow an unbounded lineage/replay structure, or silently translate an evicted cursor.
- The receiver-lifecycle integration does not create a second worker-state owner. Its observation is issuer-owned, exact and mutation-bound to the same registry; wrong/stale/copy/conflicting observations refuse, while exact replay is idempotent.
- Public `TrustedContext`, plan containment, pinned parameters, parent ownership of derived commands, result roles, one mutation owner and separation of A7 transaction knowledge from worker quiescence remain intact.
- The required future evidence is satisfiable as written: each original causal trace now has one legal expected transition and one finite set of unchanged-state assertions.

## 3. Risks and next action

This GO is prospective text closure only. It does not prove that a production executor can issue stop/task observations with the required atomic ordering, that concrete lowering constructs every closed schedule correctly, or that real queue, lock, async/thread, database, crash and physical-fence implementations satisfy the design. Those remain later implementation and evidence gates rather than defects in this focused correction.

The next action is to complete the independently running fresh full Consistency/Safety reviews and the separately required originating stopped-counterexample retracing on this exact 100-entry tuple. Only the required combined GO results may accept the replacement design. The 71-file source remains stopped and requires a separately authorized implementation brief and source review.
