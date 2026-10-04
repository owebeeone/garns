# W1A11-WorkerExitRedesign — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; operator-authorized correction 1/2 design candidate, not accepted or implementation authority, dated 2026-10-04.  
**Baseline:** Revision 1 was read from `dev-docs/W1A11-WorkerExitRedesign-Revision1/W1A11-WorkerExitRedesign.md` at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`. The corrected DRAFT and remediation plan matched SHA-256 `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85` and `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`. The 100-entry correction manifest remained at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`. Sources were read directly from the current filesystem under the approved no-Git filesystem-SHA exception.  
**Date:** 2026-10-04  
**Axis:** Same-origin focused Safety closure of `Safety-1 P2-1` and `Safety-1 P2-2`, including changed-range inspection for new Safety roots. Independent, adversarial, read-only. Fresh full-axis reviews run independently; nothing here relies on them. Filed verbatim by the lane owner.

**Verdict: GO** — both prior Safety findings are closed prospectively on the corrected design, and the changed range introduces no new Safety root. This focused re-verdict is neither overall design acceptance nor source acceptance.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| `Safety-1 P2-1` | Add a provider-issued exact receiving-task lifecycle observation; invalidate the original context/operation binding atomically; remove queued work or contain every post-dequeue/prepublication state; preserve effect and A7 truth; make wrong, stale, copied and conflicting observations mutation-free. | Re-traced the original success-to-task-loss sequence and every required pause. The exact provider observation now closes the private result and moves `QUIESCENT_SUCCESS` directly to `QUIESCENT_CONTAINED`; `SUCCESS_PENDING` transfers to containment and waits for stop; queued, running, active-effect and accepted-before-publication states have explicit fail-closed dispositions. The containment owner terminalizes and releases without receiver resumption. | **CLOSED** |
| `Safety-1 P2-2` | Derive finite lineage and replay bounds from validated live capacity; coalesce consecutive neutrals per changed-work gap; bound replay retention and settlement/retirement work; return typed stale/unavailable/refetch outcomes outside the retained window. | Re-traced the original delayed changed head followed by arbitrarily many neutral commits. All neutrals in that gap extend one span, replay state remains a FIFO ring of `R == C`, lineage remains at most `2C`, and old replay becomes typed stale/unavailable. Head settlement handles one changed record plus one span; retirement discards at most `2C + C` records and releases at most `C` permits. | **CLOSED** |

## Changed-range analysis

The complete diff from archived Revision 1 to the corrected object is material but disposition-bounded.

The `Safety-1 P2-1` range adds `ReceivingTaskLifecycleObservation`, a task lifecycle serial, atomic original-context and operation-binding invalidation, state-specific receiver-loss transitions, serial-sensitive queued removal, result closure through accepted-before-publication, exact replay/conflict behavior and mandatory receiver-termination traces. This is an architectural state-machine completion inside the already selected single lifetime-registry ownership model; it adds no second mutable owner or callback seam.

The `Safety-1 P2-2` range replaces lifetime-long per-neutral lineage/replay with validated `Q`, total capacity `C == Q + 1`, replay capacity `R == C`, at most `C` changed records, at most `C` neutral spans, at most `2C` lineage records, coalescing within each changed-work gap, deterministic eviction and typed stale/unavailable/refetch outcomes. This is a bounded capacity and retention correction, not a new ownership architecture.

The remaining material changes implement the four filed Consistency dispositions: a finite multi-command operation ledger, command-exact tombstones and replay isolation, primary failure ordering before cleanup, and an explicitly superseded migration product edge. I inspected those ranges for Safety regressions. They remain mapped to the remediation plan, preserve the one-owner and one-outer-permit rules, and introduce no new stuck-state, premature-release, unbounded-retention or irreversible-transition root.

No change falls outside the six filed correction dispositions except status, authority and regression-accounting text. No new root-cause candidate was found, so there is no new architectural-root counter increment. The material contract-shape changes still justify the independently running fresh full review pair; this same-origin focused GO cannot substitute for it.

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop `SKILL.md` and canonical reviewer template.
- Corrected `W1A11-WorkerExitRedesign.md`, `W1A11-WorkerExitRedesign-DRAFT-2.md` and `W1A11-WorkerExitRedesign-RemPlan-1.md`.
- Both filed round-1 reports: Safety at SHA-256 `d8ad5f935baf178ebd69999a9e00ef1585758935586e13241e1dd5d8a5303984` and Consistency at SHA-256 `67ac6f8e42755ec19446823071104f50fa3b357d402bab3d548185a26fab40d4`.
- The archived Revision-1 design and its complete verification map.
- The complete corrected-versus-Revision-1 diff.

I did not read any current round-2 fresh/origin report, current round-2 reviewer prompt, or newly filed Origin State closure.

At both review boundaries:

- `W1A11-WorkerExitRedesign-MANIFEST-2.sha256` matched `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653` and verified 100/100.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c` and verified 13/13.
- The Revision-1 archive verification map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8` and verified 88/88.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52` and verified 19/19.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` and verified 71/71.
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` and verified 111/111.
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` and verified 614/614.

The end-boundary object, DRAFT and remediation-plan hashes still matched the pinned tuple.

Inspection used only permitted read-only `shasum`, `wc`, `rg`, `sed`, `nl` and `diff` commands. No test was run because this is a prospective design closure and the optional existing suite exercises stopped source rather than these new state rules. No file, manifest, source, test, Git/GWZ state, service or database was modified. No helper was used.

## 2. Invariant analysis

The original `Safety-1 P2-1` causal sequence now closes:

1. The original receiving task dispatches under an exact task identity and monotonically unique lifecycle serial.
2. The worker may reach `SUCCESS_PENDING`, and exact stop may advance it to `QUIESCENT_SUCCESS`.
3. If the receiver terminates without application cancellation, only the trusted task provider can issue the exact lifecycle observation.
4. One lifetime-owner mutation validates issuer, runtime, operation, context record, task and serial, then invalidates both the original context record and operation binding.
5. In `QUIESCENT_SUCCESS`, the mutation closes the result and transfers directly to `QUIESCENT_CONTAINED`. In `SUCCESS_PENDING`, it transfers to containment and retains the stop requirement.
6. The containment owner, not a replacement task or vanished receiver, terminalizes the quiescent operation and releases the permit once. A7 knowledge remains independent.

The broader pause attack also holds. Queue insertion competes under the same queue lock; first-command removal may prove whole-operation `CANCELLED_CONFIRMED`, while later-command removal preserves prior work and permits only quiescent `REFUSED`. `RUNNING_IDLE` and `EFFECT_IN_FLIGHT` revoke unused ordinals and retain correct `NOT_BEGUN`, `RETURNED` or `BEGUN_UNCERTAIN` knowledge. Existing containment preserves its primary receipt. Receiver loss after result acceptance but before atomic publication closes assembly/output and contains the outer lease. After terminal publication it cannot relabel success. Exact duplicate observation is idempotent; wrong task, context, lifecycle serial, copy, prior-task reuse or conflicting outcome refuses mutation-free. These rules are explicit at corrected design lines 134–144, 316–365, 430–450 and 464–485.

The original `Safety-1 P2-2` causal sequence now remains bounded:

1. Hold one changed head active so `delivered_through` cannot advance.
2. Commit substantially more than `C` contiguous neutral refreshes behind it.
3. Every neutral advances `produced_through` but extends the same single `NEUTRAL_SPAN`; no per-neutral lineage record, batch or permit is created.
4. The replay ring retains only the newest `R == C` records and evicts exactly one oldest entry per full-window commit.
5. An evicted candidate is stale against the advanced produced cursor, and an evicted or unknown receipt returns `NeutralReplayUnavailable`; neither path mutates state or translates a cursor.
6. Head success folds only the changed record and its one coalesced span. Head failure, overflow, close or migration retires bounded state: at most `2C` lineage records, `C` replay records and `C` real permits.

Multiple changed gaps remain bounded because there are at most `C` unabsorbed changed records and at most one neutral span per gap. Neutrals with no prior unabsorbed changed work fold immediately. Opposite sides of a later changed record cannot merge, preserving causal boundaries. The design explicitly prohibits auxiliary candidate or receipt tables outside these bounds. These rules are explicit at corrected design lines 618–725.

The changed-range attacks also held:

- The receiver-loss repair uses the existing lifetime owner and pre-existing containment owner; it does not introduce an independently mutable task-lifecycle state owner.
- Multi-command records retain one finite schedule, one active command and one outer operation/generation permit. Earlier tombstones cannot authorize later commands or cause a second release.
- Primary body/effect/cancellation failure commits before cleanup can compete; cleanup diagnostics are bounded by the finite trusted cleanup schedule.
- Neutral retirement releases only real permits and cannot infer publication or delivery from neutral cursor progress.
- Migration changes retain exact phase, serial, request and successor validation and do not weaken post-effect indeterminacy.
- Publication, worker quiescence and A7 transaction truth remain independent.

## 3. Risks and next action

Trusted task-provider integration, real async cancellation delivery, executor stop evidence, lock ordering, durable crash behavior, database adapters, cross-process fencing and production atomicity remain deferred implementation evidence. They are not defects in this prospective design closure. The mandatory causal and property tests remain requirements for a later authorized contract/reference build.

The stopped source remains stopped and unaccepted. The single next action is to file this report verbatim and complete the independently running fresh full Consistency/Safety pair and the other originating closures on the exact 100-entry tuple. Only the required combined gate may accept the corrected replacement design; this focused GO neither self-accepts the design nor authorizes source implementation.
