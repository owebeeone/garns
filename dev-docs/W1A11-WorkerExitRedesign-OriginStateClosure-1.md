# W1A11-WorkerExitRedesign — ORIGINATING STATE DESIGN CLOSURE 1

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`; operator-authorized replacement-design candidate, not accepted and not implementation authority. The complete filesystem object is `W1A11-WorkerExitRedesign-MANIFEST-1.sha256` at SHA-256 `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`, 88 files.

**Baseline:** The stopped 71-file source candidate remains immutable evidence at MANIFEST-3 SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`. This review evaluates prospective design closure only; it does not close or accept that source.

**Date:** 2026-10-04

**Axis:** Originating State review of worker-exit ownership and retained State counterexamples: closed state grammar, fail-closed progress, quiescence, A7 separation, replay, fencing, and recovery evidence. Independent, adversarial, read-only. Current Consistency and Safety reports and prompts were not read.

**Verdict: GO — prospective design closure only.** The design supplies a coherent prospective correction for `ReviewState-3 P2-1`, `P2-2`, `P2-3`, and the `OriginStateClosure-2 State-Closure-P2-1` phase residual. No new P0–P3 design finding arose from retracing those counterexamples. Every corresponding source finding remains open until a separately authorized implementation and originating executable closure.

---

## Prior-finding prospective closure table

| Originating finding | Original counterexample retraced against design | Prospective design status | Source status |
|---|---|---|---|
| `ReviewState-3 P2-1` — missing post-dispatch result/failure ownership transition | Effect 1 raises while effect 2 remains unused; exact worker-to-receiver success; cancellation, cleanup, replay, fence, late-exit and quiescence schedules | **PROSPECTIVELY CLOSED** by §§3–7 | **OPEN** on MANIFEST-3 |
| `ReviewState-3 P2-2` — refused active handoff advances delivered progress | Two ranges `(0,1]`, `(1,2]`; first fails before caller-visible publication; second must not cross the gap | **PROSPECTIVELY CLOSED** by §8 | **OPEN** on MANIFEST-3 |
| `ReviewState-3 P2-3` — neutral refresh has no no-batch transition | Neutral `(0,1]`, followed by later changed work, with zero/one/multiple earlier changed ranges | **PROSPECTIVELY CLOSED** by §10 | **OPEN** on MANIFEST-3 |
| `OriginStateClosure-2 State-Closure-P2-1` residual, retaining OriginStateClosure-1 | DRAINING proof is issued, the same attempt advances to MIGRATING, and the stale prior-phase proof is presented | **PROSPECTIVELY CLOSED** by §11 | **OPEN** on MANIFEST-3 |

## Changed-scope analysis

This is a replacement design authorized after the stopped amendment exhausted its architecture corrections. It changes no source, tests, accepted ADR, or stopped report.

The additive design assigns one mutation owner—the lifetime registry—for lease ownership, worker authorization, effect reservation, worker exit, containment, result acceptance, and terminal release. It completes:

- worker command and effect state grammar in §§3–7;
- failed FIFO retirement/refetch in §8;
- activation-bracketed participant membership in §9;
- ordered neutral-refresh lineage in §10;
- phase- and request-exact migration proof in §11.

Deployment generation remains a separate coordinator-owned domain composed through sealed permits and the retained lock order. `worker_authority.py` is prospectively limited to identities and validation helpers rather than becoming a second mutable owner.

The original stopped source remains unchanged and unsafe for the originating counterexamples. This report is not an implementation re-verdict.

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-1.sha256` remained at `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`; 88 entries; 88/88 verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` remained at `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; 19/19 verified.
- The stopped MANIFEST-3 remained at `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71/71 verified.
- ReadOnly remained at `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 verified.
- ProductGuard remained at `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 verified.

The controlling design files remained:

- design: `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`;
- brief: `9ba4854b5ce14c86b22b76f1b1a42c05acef228723aa427999c7a5123b1f6a56`;
- DRAFT testimony: `e8fd137970df5dc62ce5e838b6ca8f267a43343167f32805da75c2d2650b76b7`.

I read completely:

- workspace and product instructions;
- the review-loop skill and canonical reviewer template;
- the 737-line redesign, brief, DRAFT, and Inputs manifest;
- my original `W1A11-ContractAmendment-ReviewState-3.md`;
- `W1A11-ContractAmendment-OriginStateClosure-2.md`;
- A7’s complete isolation/retry/commit-knowledge grammar;
- the relevant accepted W2 worker ownership, containment, quiescence, publication, close, and migration clauses.

No current WorkerExitRedesign Consistency/Safety report or prompt was read. No helper was used.

No tests were run: this is a design object, and the source is deliberately frozen. The review used textual causal state sequences against the original executable counterexamples. No filesystem write, Git/GWZ operation, network request, service, generator, bytecode command, dependency installation, or `tools/check.py` occurred.

## 1. Findings

No P0–P3 design findings.

## 2. Invariant analysis

### Worker effect exception: effect 1 raises while effect 2 is unused

The original source failure was:

```text
effect 1 raises
lease remains RUNNING
effect 2 remains usable
no worker-to-containment owner transfer exists
```

The redesigned causal sequence is closed:

1. The command is `RUNNING_IDLE` under the exact assigned worker.
2. `run_effect(authorization, 1)` atomically validates the runtime, operation, lease, command, authorization, current worker, original context record, binding, generation, local barriers, and ordinal.
3. It consumes ordinal 1, creates a sealed `WorkerEffectReservation`, and enters `EFFECT_IN_FLIGHT` before invoking the fixed issuer-owned effect.
4. If that effect raises any `BaseException`, the wrapper atomically:
   - creates the primary failure exit receipt;
   - records `BEGUN_UNCERTAIN`;
   - revokes effect 2 and every other unused ordinal;
   - enters `CONTAINED`;
   - transfers ownership from the worker to the preallocated registry-held `WorkerContainmentOwner`;
   - retains the generation charge.
5. Only after state is safe does the original exception escape.
6. A later effect-2 request, success exit, worker completion, or result acceptance has no legal edge and refuses.
7. An executor-issued exact stop receipt moves the command to `QUIESCENT_CONTAINED`.
8. The containment owner may then terminalize the operation as `REFUSED`; it cannot claim `CANCELLED_CONFIRMED` for a begun-uncertain effect.

This directly resolves the original “effect 1 raises/effect 2 still runs” counterexample without trusting an ordinary caller, callback-supplied identity, or worker argument.

The effect seam is also corrected from the stopped per-call arbitrary callback. Production uses an immutable issuer-owned `WorkerEffectSchedule` of exact closed commands. A caller cannot supply an effect, worker, task, context, claims, clock, generation, or containment owner per invocation.

### Exact worker-to-receiver success

The successful ownership chain is explicit:

```text
RUNNING_IDLE
  -> SUCCESS_PENDING
  -> QUIESCENT_SUCCESS
  -> RESULT_ACCEPTED
  -> outer guarded assembly/publication
```

`worker_exit_success` requires:

- the exact current assigned worker;
- no active reservation;
- every required ordinal returned;
- a closed issuer-owned result;
- the exact live authorization and command tuple.

Its atomic commit closes the authorization, revokes unused optional ordinals, creates one exit receipt, and transfers ownership from the worker to registry-held pending-result escrow. It does not publish, expose the result, or release a permit.

Only the bound executor may issue the stop receipt, and only after the command stack and trusted cleanup cannot resume. Stop observation establishes `QUIESCENT_SUCCESS`.

Result acceptance then requires the exact privately recorded receiving runtime task, the original task-bound context at zero staleness, the exact receipt/result, and current lease, admission, resource, binding, generation, and fence barriers. It changes ownership to `RuntimeContinuationOwner` and returns only closed result data.

Wrong task, child task, wrong receipt, wrong command, stale context, or changed barrier cannot acquire the result. No context or claims move to the worker or result receipt. Publication remains a later outer lease barrier and is not implied by worker success.

The command grammar has no edge back to worker ownership. `RESULT_ACCEPTED` is one-shot; any later command requires separately authorized dispatch.

### Cancellation and dequeue races

Queued cancellation is authoritative only if exact queue removal wins. It then revokes the authorization and completes `CANCELLED_CONFIRMED` once. If dequeue wins, cancellation follows the running-command grammar.

For running cancellation:

- the cancellation source is either the exact recorded receiving task obtained from the trusted current-task provider while its original context is live, or an issuer-internal expiry/fence/close event;
- no caller supplies an owner or claims proof;
- unused ordinals are revoked;
- ownership transfers to containment;
- the active charge persists until stop observation.

If cancellation wins after reservation but before invocation, that reserved effect may still begin and is conservatively `BEGUN_UNCERTAIN`; no second effect may reserve. If cancellation wins before any reservation, it records `NOT_BEGUN`. If all earlier effects returned, it records `RETURNED`. None of these command facts manufactures A7 database knowledge.

A cancellation after success-receipt creation but before result acceptance closes the private result and transitions `SUCCESS_PENDING` or `QUIESCENT_SUCCESS` to containment. It cannot publish the tombstoned success.

### Cleanup failure

Trusted cleanup executes outside the state lock and before success-exit creation. No conceptual method accepts an ordinary caller cleanup callback.

If command work computes a private result but cleanup raises, the result is discarded and the command enters failure containment. Therefore cleanup cannot fail after a publishable success receipt exists.

If an effect exception already created the primary failure receipt, a later cleanup failure is appended only as a bounded diagnostic. It cannot replace the primary effect knowledge, create another owner transfer, restore ordinals, or alter A7 truth.

The executor may issue stop only after cleanup and the command frame exit. A return, exception, `finally`, or cleanup callback is not itself quiescence.

### Replay, conflicts, and late exits

Each command exit has a monotonically unique command-local serial and an immutable tombstone retained until operation terminalization.

- Exact same-kind exit replay is idempotent.
- Stop replay is idempotent.
- A differing kind, receipt, result/failure identity, serial, lease, command, authorization, worker, receiver, runtime, binding, or generation is an outcome conflict with no mutation.
- Failure/cancel races are first-commit-wins; the loser is diagnostic only.
- Late worker success after failure or cancellation cannot expose a result, change ownership, restore ordinals, alter effect knowledge, publish, or change terminal outcome.
- Publication replay is idempotent only for the same committed receipt; conflicting completion refuses.

These rules preserve one owner, one primary exit, one result, and one generation charge.

### Fence and invalidation races

The design distinguishes the race winner at every boundary:

- A barrier that wins before reservation causes refusal before ordinal consumption or effect invocation.
- A reservation that wins first is already a begun/uncertain effect; a later hard fence or cancellation transfers to containment and retains the charge through stop.
- A fence after success-exit creation but before acceptance closes the private result.
- A fence after result acceptance is handled by the outer lease grammar and still must prevent publication.
- Old-generation drain cannot complete solely from a worker exit or stop receipt.

No worker result receipt crosses admission, resource, generation, context, or publication revalidation.

### Quiescence remains independent of A7 transaction truth

Only an exact executor-issued stop receipt proves that the command stack and trusted cleanup cannot resume. Worker return, exception, cancellation, success receipt, result acceptance, and cleanup completion are not individually quiescence.

After stop:

- command quiescence permits containment-owned operation terminalization;
- it does not prove database abort, commit, or retry safety;
- `BEGUN_UNCERTAIN`, `RETURNED`, and `NOT_BEGUN` are worker facts only;
- A7 remains exactly `KNOWN_ABORTED`, `KNOWN_COMMITTED`, or `INDETERMINATE`;
- unresolved A7 identities remain retained independently after the operation lease is terminal.

The design preserves the accepted close distinctions:

- live operation: `NONQUIESCENT`;
- no live operation but unresolved A7 identity: `UNRESOLVED`;
- neither: `CLOSED`.

A known commit does not prove worker quiescence, and worker quiescence does not authorize retry or manufacture rollback.

### Failed FIFO delivery

The design selects one rule rather than leaving a menu: unpublished head failure retires the registration and requires a complete A6 refetch.

For queued `(0,1]` and `(1,2]`, if the first head fails before caller-visible publication:

- `delivered_through` remains 0;
- the head is marked failed;
- the registration becomes `RETIRING_REFETCH`;
- all queued successors are invalidated and their permits released once;
- no new refresh, enqueue, dequeue, or handoff may use that registration;
- the active handoff charge remains until iterator/worker quiescence;
- retirement then makes every later use return `RefetchRequired`;
- only a complete new snapshot/high-water/registration handshake establishes a new baseline.

Success settlement requires the exact publication receipt and terminal `SUCCEEDED`. Failure after committed publication and success after retirement are conflicts. Repeated identical failure settlement is idempotent. Close and migration use the same retirement mutation without double release.

This prevents the original false delivered-cursor advance and successor gap crossing.

### Neutral refresh

The original no-batch counterexample is resolved by a single atomic `commit_refresh(exact_sealed_candidate)` operation. A fixed trusted comparator—not an ordinary caller—chooses exactly one changed or neutral branch.

Neutral commit:

- consumes the candidate once;
- advances `produced_through`;
- appends a zero-permit neutral lineage entry;
- creates no batch, envelope, buffer permit, or publication;
- returns a sealed `NeutralRefreshReceipt`;
- completes only the refresh lease.

With no earlier changed work, neutral `(0,1]` folds immediately and advances the semantic delivered frontier because caller-visible state did not change. With queued or active earlier changed work, it advances only produced progress and waits in lineage order. After the prior changed head publishes, the neutral prefix folds before a later changed range becomes eligible.

If an earlier changed head fails, registration retirement discards pending neutral and changed successors without inventing delivery. This closes both the simple neutral case and the overtaking case that a standalone cursor update would have introduced.

Fabrication, copying, cross-lease/registration use, stale cursor, wrong generation, fences, migration invalidation, replay, and changed-after-neutral conflict all have specified mutation-free behavior.

### Phase- and request-exact no-effect proof

The prior residual sequence was:

```text
issue proof in DRAINING_OLD
advance same attempt to MIGRATING
reuse old proof
old proof incorrectly reopens
```

The redesign records exact phase, monotonically increasing phase serial, exact phase request identity, and requested successor.

Entering `MIGRATING_PRE_EFFECT` increments the serial and allocates a new request identity bound to the exact successor. This makes every DRAINING proof stale. A MIGRATING proof can be issued only after the exact current request is released with no effect begun.

`reopen_no_effect` validates all of the following before mutation:

- coordinator and attempt;
- current phase and phase serial;
- phase request identity;
- old and requested binding;
- activation and admission epochs;
- frozen acknowledgements;
- no-effect state;
- unconsumed proof.

The old DRAINING proof therefore refuses after `begin_migration` with phase, binding, epoch, queues, membership, counts, and evidence unchanged. A newly issued exact MIGRATING proof may reopen once; replay, wrong request, wrong successor, cross-attempt, cross-coordinator, and prior-phase variants refuse.

This prospectively closes the exact OriginStateClosure-2 residual.

## 3. Risks and next action

This GO is deliberately narrow:

- It does not accept the redesign; fresh peer-blind Consistency and Safety GO/GO remain mandatory.
- It does not close `ReviewState-3 P2-1`, `P2-2`, `P2-3`, or the phase-proof residual on source.
- It does not authorize implementation.
- It does not establish real executor, thread, cancellation, lock, database, durability, physical-fence, crash/restart, or cross-process evidence.
- Participant lifecycle and Code-only originating findings remain for their assigned review and later implementation closure; I did not substitute this State-origin report for those reviewers.

The next action is manager completion of the independent design gate. If the redesign receives exact Consistency/Safety GO/GO, it may be accepted as design authority only. A later implementation still requires a separate exact execution brief, explicit write boundary, frozen source tuple, deterministic causal regressions for every mapped finding, and originating source re-verdicts.
