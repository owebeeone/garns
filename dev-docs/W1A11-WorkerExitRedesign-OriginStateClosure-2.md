# W1A11-WorkerExitRedesign — ORIGINATING STATE DESIGN CLOSURE 2

**Review object:** Corrected `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; correction 1 of at most 2, not accepted and not implementation authority. Complete object: `W1A11-WorkerExitRedesign-MANIFEST-2.sha256` at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`, 100 files.

**Remediation authority:** `W1A11-WorkerExitRedesign-RemPlan-1.md` at SHA-256 `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`; RemInputs-1 at `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`, 13 entries.

**Baseline:** Revision-1 design at `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`, verified through the 88-entry product-root archive map. The stopped source remains immutable evidence at MANIFEST-3 SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.

**Date:** 2026-10-04

**Axis:** Focused originating State prospective closure. I retraced my stopped-source worker-exit, failed-FIFO, neutral-refresh, and phase-proof counterexamples against the corrected design. Current round-2 fresh, peer, and originating reports and prompts were not read.

**Verdict: GO — prospective design closure only.** The corrected design preserves and strengthens the prospective closure of all four originating State counterexamples. The multi-command ledger, receiver-loss transition, cleanup ordering, bounded neutral grammar, and explicit deployment-state × attempt-phase product introduce no new architectural or bounded State root within this originating scope. Every source finding remains open.

---

## Prior-finding closure table

| Originating ID | Disposition claimed | Original counterexample retraced on corrected design | Status |
|---|---|---|---|
| `ReviewState-3 P2-1` — missing post-dispatch result/failure ownership transition | Finite per-operation command ledger; exact worker exit; trusted receiver-loss containment; corrected cleanup ordering | Effect 1 raises while effect 2 is unused; exact worker→receiver success; C1→C2; cancellation/dequeue; receiver loss; body/effect/cleanup races; replay, fences, late exit and A7/quiescence separation | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `ReviewState-3 P2-2` — refused handoff falsely advances delivered progress | Registration retirement/refetch remains the sole failed-head rule | `(0,1]` fails before publication while `(1,2]` is queued; delivered cursor must remain 0 and successor must not cross | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `ReviewState-3 P2-3` — no neutral no-batch transition | Sealed neutral commit plus capacity-derived coalesced lineage and bounded replay | Zero-queue neutral, neutral behind active/queued changed work, changed-neutral-changed, more than `C` neutrals, stale replay and later changed work | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `OriginStateClosure-2 State-Closure-P2-1` residual, retaining OriginStateClosure-1 | Explicit migration-product supersession plus exact phase/serial/request/successor proof | Issue DRAINING proof, advance the same attempt to MIGRATING_PRE_EFFECT, present stale proof, then issue exact current proof; repeat after EFFECT_BEGUN | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |

## Changed-range analysis

Correction 1 changes only the design and testimony. Source, tests, accepted ADRs, stopped reports, and the 71-file stopped candidate remain unchanged.

The design correction integrates all RemPlan-1 dispositions:

- §§3–6 replace singular worker-command fields with a bounded operation schedule and ordered command ledger.
- §§3–7 add an issuer-owned receiving-task lifecycle observation and exact state-specific task-loss behavior.
- §5 commits non-effect body failure before cleanup and bounds later diagnostics.
- §10 replaces unbounded neutral entries with capacity-derived coalesced spans and a finite replay window.
- §§2 and 11 explicitly supersede the conflicting accepted migration edge and define one deployment-state × attempt-phase product.

These changes touch the causal neighborhood of the originating worker and neutral findings, so I retraced rather than relying on my round-1 prospective GO.

No changed range reopens the failed-FIFO rule. No new architectural or bounded State root was found.

## 0. Evidence base

At START and END:

| Evidence | Exact hash | Verification |
|---|---|---:|
| MANIFEST-2 | `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653` | 100/100 |
| RemInputs-1 | `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c` | 13/13 |
| Revision-1 archive verification map | `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8` | 88/88 |
| Original Inputs | `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52` | 19/19 |
| Stopped source MANIFEST-3 | `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` | 71/71 |
| ReadOnly | `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` | 111/111 |
| ProductGuard | `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` | 614/614 |

The corrected design remained at `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; DRAFT-2 remained at `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`; RemPlan-1 remained at `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`.

The original MANIFEST-1 entries are product-root-relative. A direct check from inside the archive could not resolve those paths; the explicit rebased `VERIFY-from-product-root.sha256` map was then used as prescribed and verified all 88 original entries.

I read completely:

- workspace and product instructions;
- the review-loop skill and canonical template;
- the corrected 937-line design, RemPlan-1, and DRAFT-2;
- both legitimate round-1 full design reports;
- my complete `W1A11-WorkerExitRedesign-OriginStateClosure-1.md`;
- the relevant stopped-source State3 and phase-proof counterexamples retained in that report;
- the revision-1/current design diff.

No current round-2 report or prompt was read. No helper was used.

No tests were run because this remains a prospective design correction against deliberately unchanged stopped source. No file write, Git/GWZ mutation, network access, service, database, dependency installation, generator, bytecode action, or `tools/check.py` occurred.

## 1. Findings

No P0–P3 findings within this originating State prospective-closure scope.

## 2. Invariant analysis

### Worker exception still contains before another effect can begin

For the original effect-1/effect-2 sequence:

1. The active command record is `RUNNING_IDLE`.
2. Effect 1 reservation atomically binds the exact operation, command serial, authorization, worker, context record, binding, generation and ordinal before invocation.
3. Effect 1 raises.
4. Before the exception escapes, the registry commits the primary failure receipt, records `BEGUN_UNCERTAIN`, revokes effect 2 and every other unused ordinal, transfers the outer lease to the operation’s preallocated containment owner, and retains the generation charge.
5. Effect 2, success exit, later command dispatch, and result acceptance have no legal edge.
6. Exact stop observation changes the record to quiescent containment.
7. Only the containment owner may terminalize it, with A7 truth independently retained.

The new command ledger strengthens this sequence: the failure is attached to the exact active command serial, prior tombstones cannot mutate it, and no later slot can dispatch after containment.

### Multi-command ledger preserves one operation owner and permit

The corrected record now owns a finite exact operation schedule of `M` slots and a ledger of at most `M` command records. At most one record is nonterminal.

For C1 followed by C2:

- C2 refuses before C1 reaches exact `RESULT_ACCEPTED`.
- C1 acceptance clears only C1’s active serial and returns ownership to the runtime continuation.
- C2 receives a new serial, command, worker, authorization, effect schedule and tombstone without resetting the outer lease or acquiring another operation permit.
- C1’s authorization or ordinal cannot validate against C2.
- C1 exact exit/stop replay is answered only by C1’s retained tombstone.
- A conflicting C1 failure/cancel attempt cannot change C2.
- Removing queued C2 cannot erase C1’s earlier work or claim whole-operation `CANCELLED_CONFIRMED`; it yields quiescent containment and only `REFUSED`.
- One outer terminal publication or containment completion releases the shared operation permit.

This preserves the original worker-exit correction while removing the singular-record ambiguity identified in round 1.

### Exact worker-to-receiver success remains closed

For each command:

```text
RUNNING_IDLE
  -> SUCCESS_PENDING
  -> QUIESCENT_SUCCESS
  -> RESULT_ACCEPTED
```

Success exit requires exact current worker, no active reservation, all required effects returned, and an issuer-owned result. It closes that command’s authorization, revokes unused optional ordinals, transfers ownership to pending-result escrow, and exposes nothing.

Only the bound executor’s stop receipt establishes quiescence. Exact acceptance then requires the privately recorded receiving task, its still-valid original context, the exact command receipt/result, and current outer barriers. Acceptance records the command terminally and returns ownership to the runtime continuation.

Final publication is legal only when schedule slot `M` is accepted, no command remains active, the receiver is live, and every outer barrier still holds. Worker success alone never publishes or releases the permit.

### Receiver disappearance has a fail-closed path at every required pause

The new `ReceivingTaskLifecycleObservation` is issued only by the trusted task provider and binds the exact task and lifecycle serial. It is not an application callback or caller-supplied identity.

Its one accepted registry mutation invalidates the exact original context and operation binding, forbids later schedule dispatch, and then:

- removes queued work under the dequeue lock;
- contains `RUNNING_IDLE` or `EFFECT_IN_FLIGHT`, revoking unused ordinals;
- preserves an existing containment primary;
- closes a `SUCCESS_PENDING` result and waits for stop;
- changes `QUIESCENT_SUCCESS` directly to quiescent containment;
- closes accepted-but-unpublished runtime assembly/output without reopening the command;
- does not relabel terminal publication.

If task loss races C1 acceptance/C2 dispatch, the same mutation boundary gives a closed outcome: task loss first invalidates dispatch; dispatch first creates a queued C2 that the observation removes.

Exact replay is idempotent. Wrong task, context, operation, serial, copied identity, stale task reuse, or conflicting outcome refuses mutation-free. The containment owner completes without requiring the vanished receiver to resume. A7 knowledge remains unchanged.

### Cleanup ordering preserves one primary exit

The corrected wrapper order removes the prior ambiguity:

- A fixed-effect exception is already contained by `run_effect`.
- A non-effect body exception commits `worker_exit_failure` before cleanup begins.
- If no primary exists, the first cleanup exception becomes primary and discards any private result.
- If a body, effect, cancellation, or receiver-loss primary already exists, cleanup failures occupy only bounded diagnostic slots.
- A cancellation/cleanup race is first-commit-wins under the registry lock.
- No diagnostic changes ownership, ordinals, effect knowledge, A7 truth, or the primary receipt.

The cleanup schedule is finite (`K`), bounding retained diagnostics to one per cleanup step plus one cancellation-race slot. Stop cannot be observed before cleanup and the command frame exit.

This preserves the original requirement that an exception leaves the state safe before it escapes and prevents cleanup from restoring success or causing a second containment transfer.

### Replay, fences, late exits and A7 separation remain intact

Command serial is now part of every replay comparison. Exact replay is local to that command record; cross-command, cross-worker, cross-authorization, cross-result, cross-binding and cross-generation presentations are conflicts without mutation.

A barrier winning before reservation prevents the effect. Reservation winning first creates begun uncertainty and later containment. A fence after success exit closes the private result; a fence after command acceptance still blocks outer publication.

A late worker return after failure, cancellation, receiver loss, or fence remains diagnostic only. It cannot restore ordinals, ownership, result visibility or terminal state.

Executor stop proves only worker-command quiescence. It does not prove database abort, commit, retry permission or rollback. A7 remains `KNOWN_ABORTED`, `KNOWN_COMMITTED` or `INDETERMINATE`, and unresolved A7 identities remain independently retained after operation terminalization.

### Failed FIFO delivery remains fail-closed

The §8 rule is unchanged in its causal essentials.

For changed ranges `(0,1]` and `(1,2]`, any legal non-success of the first before caller-visible publication:

- leaves `delivered_through` at 0;
- marks the head failed and registration `RETIRING_REFETCH`;
- invalidates the second and every queued successor;
- releases queued permits once;
- retains the active operation charge until quiescence;
- permits no further use of that registration;
- requires a complete new A6 snapshot/high-water/registration baseline.

Only an exact committed publication receipt plus terminal `SUCCEEDED` advances delivery. Failure after committed publication and success after retirement are conflicts. The corrected worker, cleanup and receiver-loss paths all feed this same non-success settlement rather than bypassing it.

### Neutral no-batch progress is now causally and spatially bounded

The original neutral transition remains:

- sealed candidate and trusted fixed classification;
- candidate consumed once;
- `produced_through` advances;
- no batch, envelope, buffer permit or publication;
- immediate semantic delivery advance only when no earlier changed work blocks it.

The correction adds exact capacity:

- queued changed capacity `Q = min(N, deployment ceiling)`, or `Q = N`;
- total active-plus-queued changed capacity `C = Q + 1`;
- replay window `R = C`;
- at most one neutral span per changed-work gap;
- at most `C` spans, `2C` lineage records and `C` replay entries;
- no auxiliary candidate/receipt table outside those bounds.

More than `C` consecutive neutral refreshes behind one delayed changed head extend one span while the replay ring evicts oldest entries. Produced progress remains monotonic; delivered progress does not overtake the head; no delivery permit or publication is invented.

A changed commit that would exceed capacity retires/refetches before consuming the candidate or moving either cursor. Normal settlement processes at most one changed entry and one span. Overflow, failure, close or migration discards at most the declared bounded lineage/replay state and releases only actual permits.

An evicted candidate is stale; an evicted or unknown receipt returns `NeutralReplayUnavailable`. Neither recreates old state or translates a cursor. Thus bounded replay does not reopen the original no-batch or ordering counterexample.

### Explicit migration product preserves the phase-proof fix

The design now expressly supersedes the conflicting accepted edge and defines one closed deployment-state × attempt-phase product.

The original residual trace now behaves as required:

1. Enter `DRAINING_OLD × DRAINING_OLD` and issue its exact proof.
2. Enter `MIGRATING × MIGRATING_PRE_EFFECT`; the phase serial increments and a new request identity binds the requested successor.
3. Present the old DRAINING proof. It refuses because phase, serial and request no longer match, with binding, epochs, queue markers, membership and counts unchanged.
4. Release the exact current pre-effect request and issue a current proof.
5. That proof alone may perform the explicitly superseded edge back to `CURRENT(old,new epoch) × NONE`, invalidating old admissions and buffers before queues reopen.
6. If the first migration effect wins, phase changes to `EFFECT_BEGUN` before invocation. The pre-effect proof is then permanently unusable.
7. Replay, wrong successor/request, cross-attempt and cross-coordinator variants refuse mutation-free.

The new product edge therefore resolves the round-1 authority contradiction without weakening the originating stale-proof fix or A7/post-effect indeterminacy.

## 3. Risks and next action

This is a narrow originating prospective GO. It does not substitute for the fresh round-2 Consistency/Safety verdicts or same-origin closure of their six correction IDs.

It does not close any source finding, accept MANIFEST-3, authorize implementation, or establish real async/thread/executor, lock, database, durability, physical-fence, crash/restart, or cross-process behavior. All stopped-source findings remain open.

The next action is manager completion of the corrected design gate. Only exact required design verdicts on this same tuple can permit design-only acceptance. Any later implementation requires its own explicit execution brief, write boundary, frozen source tuple, deterministic regressions, and originating executable source closure.
