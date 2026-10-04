# W1A11-WorkerExitRedesign — ORIGINATING CONSISTENCY CLOSURE 3

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; operator-authorized correction 2/2 design candidate, not accepted or implementation authority; 2026-10-04.  
**Baseline:** approved filesystem-SHA exception, read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`; 115-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-3.sha256` at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`. Comparison baseline was archived Revision 2 design SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`, verified through its rebased 100-entry archive map. Revision 1 was separately verified through its 88-entry archive map. The stopped 71-file source remains evidence only and unaccepted.  
**Date:** 2026-10-04  
**Axis:** Same-origin focused Consistency preservation — retrace originating `Consistency-1 P2-1` through `P2-4`, with full emphasis on the neutral-capacity/replay root and preservation of migration, command-ledger and cleanup closure across correction 2. Independent, adversarial, read-only. Current full re-verdicts run separately; nothing here relies on them. Filed verbatim by the lane owner.

**Verdict: GO** — all four originating Consistency findings are prospectively closed and preserved on the correction-2 tuple. The neutral root now includes exact terminal/release conservation and implementable bounded opaque-identity replay behavior. No new blocking or architectural root was found in the Revision 2 changed ranges. This is not final design acceptance, source closure, or implementation authority and does not substitute for the required full Consistency/Safety re-verdict pair.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| `Consistency-1 P2-1` | Explicitly supersede accepted overlay §3.1 and §8.2 steps 6–8; define one deployment-state × attempt-phase product with exactly one proof-gated pre-effect return from `MIGRATING`. | Retraced the original sequence in §11. A `DRAINING_OLD` proof becomes stale when `begin_migration` increments the phase serial and enters `MIGRATING × MIGRATING_PRE_EFFECT`. A newly issued exact pre-effect proof can reopen the old binding once under a new admission epoch. The first effect first enters `MIGRATING × EFFECT_BEGUN`, where that edge is absent. Replay and wrong phase/request/successor/attempt/coordinator refuse mutation-free. Correction 2 did not change this product or its proof grammar. | **CLOSED AND PRESERVED** |
| `Consistency-1 P2-2` | Replace the singular command record with a finite operation-owned ledger, unique serials, one active command, per-command authority/state and retained tombstones under one outer permit. | Retraced C1→C2 through §§3–6. C1 reaches `RESULT_ACCEPTED`, retains its record and tombstone, and clears the active serial before C2 can allocate its distinct record. C1 replay remains confined to C1; C1 authorization and ordinals cannot validate against C2. Premature or out-of-order C2 dispatch refuses. Correction 2’s operation-kind publication split occurs only after required serial `M` is accepted and does not overwrite command records or acquire another permit. Generic and specialized terminal paths each release the one outer charge only at their applicable final outcome. | **CLOSED AND PRESERVED** |
| `Consistency-1 P2-3` | Commit non-effect body failure before cleanup; make cleanup-only failure primary; retain first-commit ordering and bounded later diagnostics. | Retraced body-only, cleanup-only, body+cleanup, effect+cleanup and cancellation/cleanup sequences in §5. A non-effect body failure commits before cleanup; an effect failure is already primary; cleanup-only failure creates the sole primary receipt; later failures occupy only finite `K`-step/race diagnostic slots. Correction 2 leaves this ordering intact. Delivery non-success additionally retains its active charge through worker/iterator cleanup and exact stop, without replacing the primary failure or effect knowledge. | **CLOSED AND PRESERVED** |
| `Consistency-1 P2-4` | Coalesce neutral intervals by changed-work gap; derive finite lineage, replay and per-mutation work bounds from live capacity; give deterministic bounded replay/eviction behavior without a zero-permit side queue. | Retraced the delayed-head sequence through §§8 and 10, including the bounded defects subsequently found by fresh `Consistency-2`. Queued capacity is positive `Q`, changed-lineage capacity is `C = Q + 1`, and replay capacity is `R = C`. More than `C` neutral commits behind one delayed head extend one span for that gap and retain at most `C` replay entries. Each neutral commit atomically consumes its current candidate, updates cursor/span/ring, records refresh terminal `SUCCEEDED`, releases its charged operation once and creates no batch, publication or buffer permit. Current candidates exist only in charged operation records with `A <= L_refresh`; evicted candidates and receipts leave no history. Any opaque identity absent from the current field and replay ring uniformly returns `RefreshRecordUnavailable`. Eventual successful handoff atomically publishes, removes the changed head, folds its one following neutral span, terminalizes and releases before exposure; failed handoff retirement discards bounded successors without inventing delivery. | **CLOSED PROSPECTIVELY, INCLUDING CORRECTION-2 REFINEMENTS** |

## Changed-range analysis

The complete Revision 2-to-current unified diff contains 652 lines; the design grew from 937 to 1,121 lines. Material changes are confined to the three bounded correction-2 dispositions and their supersession, regression, ownership and review-gate mappings.

Neutral refresh changes in §10 are **bounded contract corrections, not architectural changes**:

- A current issued candidate and its semantic fields live only in an already charged refresh-operation record. The exact additional-state invariant is `A <= L_refresh`; this creates no zero-permit history structure.
- Candidate lookup checks only that current operation field and the `R == C` replay ring. An absent candidate or receipt receives uniform `RefreshRecordUnavailable`; the design no longer promises impossible reconstruction of an evicted opaque identity’s former cursor or registration.
- Neutral commit now makes candidate consumption, cursor/span/ring mutation, terminal `SUCCEEDED` and one operation release a single transition. In-window replay reads the committed outcome and cannot release again.
- Known unusable current candidates have complete conservation paths: unchanged-owner refusal, quiescent terminal refusal/release, or containment with the charge retained until exact stop.
- Retirement work remains bounded by `2C` lineage records, `C` replay records and actual queued permits. It installs one marker rather than copying current candidates into registration history; each charged operation then performs constant-work lifecycle settlement.

The new handoff rules in §§2 and 4–8 are also a **bounded state-machine correction, not a new architectural root**. They add internal empty identities and distinguish operation kind, but retain the same sole lifetime-registry mutation owner, one handoff lease and one shared permit. `settle_delivery_success` is now the only iterator-delivery final barrier and commits publication, FIFO settlement, terminal success and release together. Generic completion structurally refuses delivery operations. Non-success retirement retains the active charge through exact worker-plus-iterator stop and releases only during specialized final settlement. No owner, subsystem, public surface, compatibility model or mutation boundary was added.

The original migration product in §11, command-ledger grammar in §§3–6 and cleanup schedule in §5.3 are unchanged in substance. Correction 2 adds operation-kind-specific publication references around them but does not alter their original legal sequences, tombstone isolation or primary-failure ordering.

I found no change outside the accepted correction-2 dispositions and no new architectural root. The large textual expansion spells out bounded transitions and future evidence inside the selected architecture; it does not restart or evade the 2/2 correction cap.

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-3.sha256` matched `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`; all 115/115 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-2.sha256` matched `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`; all 25/25 entries verified.
- The Revision 2 archive map matched `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c`; all 100/100 entries verified.
- The Revision 1 archive map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`; all 88/88 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; all 13/13 entries verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; all 19/19 entries verified.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; all 71/71 entries verified.
- `ReadOnly` matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; all 111/111 entries verified.
- `ProductGuard` matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; all 614/614 entries verified.

The final object remained at `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; DRAFT-3 remained at `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`; RemPlan-2 remained at `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`.

The authorized prior reports remained:

- `ReviewConsistency-2` at `740e14350efe532cce940c655ef4a03b76f9ffd46f96df353ef06503149d0dec`;
- `ReviewSafety-2` at `6d3785cdcddeb3b0e1589e28da3ceba5ece4d328707fe4c8449b665658d5f3ff`;
- `OriginConsistencyClosure-2` at `df5d155b127a584df20915ec089fc2cfe52e3fb046bcbf71e1c2f2cbfa2d5c7e`.

I read completely:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill and canonical prompt/report template;
- the complete 1,121-line candidate design, DRAFT-3 and RemPlan-2;
- both complete prior full Revision 2 reports and my complete prior originating Consistency closure;
- the archived Revision 2 design and its complete diff against the current candidate;
- the accepted W2 ownership/publication and subscription-lifecycle clauses plus A6’s neutral movement, finite queue and coalescing requirements.

Principal comparisons were current §§2–8 at lines 54–642, §10 at lines 709–895, preserved §11 at lines 897–995, and the correction/ownership/gate maps at lines 997–1121.

No current-round report, originating closure or prompt was read. No helper was used. No test was run because this is prospective design review and the stopped source cannot establish design closure. No file, source, test, ADR, report, manifest, archive, generated artifact, bytecode, Git/GWZ state, network, service or database was modified.

## 2. Invariant analysis

The original attacks now hold on the final candidate:

- Migration has one explicit closed product grammar. The pre-effect exception is exact, named as a supersession and structurally unavailable after `EFFECT_BEGUN`.
- Sequential commands retain distinct records and tombstones under one operation. The correction-2 delivery barrier occurs after serial `M` acceptance and cannot route C1 authority into C2 or create another operation charge.
- Failure precedence remains temporal and single-owner. Cleanup and delivery retirement cannot overwrite an earlier body/effect/cancel receipt or release before authoritative quiescence.
- A delayed changed head plus arbitrarily many neutral refreshes retains at most one neutral span in that gap and at most `C` replay entries. Each refresh is nevertheless a complete charged finite operation whose neutral success releases exactly once.
- Current candidate state is proportional to currently charged operations, not lifetime history. No evicted handle, tombstone or semantic field survives outside the bounded replay ring and live operation ledger.
- Empty opaque identities are treated uniformly when absent. The interface does not infer history or provenance from identity bytes and cannot use an unknown handle to select or complete an arbitrary lease.
- Neutral progress cannot overtake a changed head. Successful specialized handoff folds only the head’s immediately following span in the same publication/FIFO/terminal/release commit; failure retires the registration with delivered progress unchanged.
- Close, migration, overflow and receiver-loss paths cannot observe a neutral success with a leaked refresh charge or an iterator success with a released permit and unsettled FIFO head.
- The one lifetime mutation owner, task-bound claim-free public context, no-raw-`Plan` seam, pinned parameters/result roles, parent-owned commands, and separation of A7 truth from worker quiescence remain intact.
- The mandated prospective traces are now satisfiable with finite authoritative records and exact unchanged-state assertions.

## 3. Risks and next action

This verdict reviews design text only. It does not establish production executor ordering, concrete lock behavior, async/thread cancellation, adapter/database behavior, crash durability, cross-process or physical fencing, candidate provenance, deployment activation or implementation completeness. Those remain expressly deferred evidence gates.

The next action is completion of the same-reviewer full `Consistency-2` and `Safety-2` re-verdicts and the other required originating retraces on this exact 115-entry tuple. Only the required combined GO results may accept the replacement design. The source remains stopped/open and requires separate implementation authority and review.
