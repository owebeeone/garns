# W1A11-WorkerExitRedesign — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`; operator-authorized design candidate, not accepted or implementation authority; 2026-10-04.  
**Baseline:** approved filesystem-SHA exception, read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`; 88-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-1.sha256` at SHA-256 `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`. The stopped 71-file source remained pinned by `W1A11-ContractAmendment-MANIFEST-3.sha256` at `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; no Git revision or source acceptance is claimed.  
**Date:** 2026-10-04  
**Axis:** Consistency — internal coherence, agreement with the controlling graph, exact supersession, and satisfiable future evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — four P2 findings block. I pre-commit to GO on a revision that resolves `P2-1`, `P2-2`, `P2-3`, and `P2-4` as specified, provided it introduces no new blocking inconsistency.

---

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-1.sha256` matched `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`; all 88/88 entries verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; all 19/19 entries verified.
- The stopped source manifest verified 71/71, `ReadOnly` verified 111/111, and `ProductGuard` verified 614/614.
- The design remained at `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`; its controlling DRAFT remained at `e8fd137970df5dc62ce5e838b6ca8f267a43343167f32805da75c2d2650b76b7`.
- The canonical prompt remained at `b4608570ae5559e973f7761a56589ed5571a9d5be852269d1a85edd68acd1ac8`.

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill, and its canonical template.
- `W1A11-WorkerExitRedesign.md`, its DRAFT and Brief, and the complete Inputs19 list.
- The accepted composed W2 base and overlay, W1 and W2 acceptances, `PRODUCT_LAYOUT.md`, and ADRs A1–A16.
- Parent implementation-plan §§15–16.
- The stopped amendment, execution brief, both remediation plans, STOP decision, final prior-object `ReviewCode-3` and `ReviewState-3`, `FreshCodeClosure-2`, `OriginStateClosure-2`, `OriginCodeClosure-2`, and restart verification.
- The stopped source manifest and relevant lifetime, worker-authority, buffer, snapshot, migration, generation, admission and lifecycle source inventories.

The principal line-level comparisons were:

- Redesign §§2–7, lines 53–377: supersession, command records/states, effects, exit, cleanup, replay and publication.
- Redesign §10, lines 507–578: neutral lineage and its future tests.
- Redesign §11, lines 580–638: phase/request-exact no-effect proof.
- Redesign §§12–14, lines 640–737: finding disposition, implementation ownership, limits and review gate.
- Accepted W2 overlay §§3.2–5.1, lines 190–359; §§8.2–9, lines 537–675; and its legal deployment edges at lines 168–186.
- A6 lines 10–21 and A16 lines 64–86.
- Prior stopped-object counterexamples at `ReviewState-3:77–144`, `ReviewCode-3:105–189`, `FreshCodeClosure-2:44–70`, and `OriginStateClosure-2:66–113`.

No current WorkerExitRedesign peer report, originating report, or peer prompt was read. No helper was used. No file, bytecode, generated artifact, source, test, ADR, manifest, Git/GWZ state, service or database was modified. Optional tests were not run: this is a prospective design review, and the known stopped source cannot establish design closure.

## 1. Findings

### [P2-1] The phase-exact repair permits an edge that the retained accepted deployment grammar forbids

**Location:** Redesign §2 lines 53–72 and especially the supersession row at lines 66–67; §11 lines 590–597 and 625–638. Accepted W2 overlay §3.1 lines 168–186 and §8.2 steps 6–8 at lines 583–591.

The redesign says every accepted W2 clause not listed in §2 remains controlling. Its phase-proof row says only that overlay §8.2 step 6 is strengthened. That accepted step reopens from `DRAINING_OLD` before step 7 changes the deployment to `MIGRATING`. The accepted legal-edge grammar expressly omits `MIGRATING -> CURRENT(old)` and states that reopening the old generation is allowed only from `DRAINING_OLD`.

The redesign nevertheless requires a proof issued in `MIGRATING_PRE_EFFECT` after `begin_migration`, and its mandatory trace says that newly issued MIGRATING proof “reopens once.” This preserves the stopped A16/source behavior, but A16 and that source were never accepted. It is not additive to the accepted W2 grammar without an explicit supersession of the state table, legal edges and step 7.

**Violated invariant:** The design must name every accepted clause it changes and leave one closed migration state grammar. A retained accepted edge set and the replacement design cannot disagree about whether old-generation reopening is legal after entry into `MIGRATING`.

**Reproduction/state sequence:**

1. Begin an attempt in `DRAINING_OLD` and obtain all frozen participant acknowledgements.
2. Enter the redesign’s `MIGRATING_PRE_EFFECT` phase for the exact requested successor, without beginning an effect.
3. Release the exact phase request and issue a current phase/serial proof.
4. Present it to `reopen_no_effect`.

The redesign requires successful old-binding reopen. The retained accepted overlay requires refusal because the deployment has left `DRAINING_OLD`. Consequently the future state-machine test cannot both accept the redesign edge and reject every edge outside the accepted W2 table.

**Impact:** Migration recovery has two incompatible authorities. An implementation can either violate the accepted deployment grammar or fail the redesign’s required closure trace. Review acceptance would not determine the legal state transition being handed to the source builder.

**Required correction:** Explicitly supersede the accepted overlay’s deployment-state table, legal-edge paragraph and §8.2 step 7, then define one exact mapping between attempt phase and deployment state. If `MIGRATING_PRE_EFFECT` remains mapped to deployment `MIGRATING`, add exactly one proof-gated pre-effect edge back to old `CURRENT`, distinguish it structurally from `EFFECT_BEGUN`, and retain the prohibition after effect start. Do not rely on the unaccepted A16/source wording as implicit authority.

**Closure test:** Enumerate the corrected deployment and attempt-phase product. Prove that a DRAINING proof is stale after the phase transition, an exact current pre-effect proof reopens once, and that same proof refuses mutation-free after `EFFECT_BEGUN`. Assert exact binding, admission epoch, phase serial, request identity, queue markers, membership and permit counts on every refusal.

### [P2-2] The singular command record cannot represent the retained multi-command operation lifecycle

**Location:** Redesign §3 lines 97–108; §4.1 lines 130–175; §4.2 lines 179–196; §6 lines 316–328. Accepted W2 overlay §5.1 lines 342–345. The redesign also preserves parent-owned child/nested/total commands at lines 40–43 and explicitly allows “a later separately authorized command” at lines 170–175.

The purported complete lifetime tuple contains one closed command, one assigned worker, one authorization, one effect schedule, one command-exit phase and one exit/result record. A successful command reaches `RESULT_ACCEPTED`, closes its authorization and retains its immutable exit tombstone until the entire operation becomes terminal. No transition or private record shape then creates a second command record on the still-`RUNNING`, runtime-owned lease.

**Violated invariant:** One operation permit may cover multiple sequential fetch/child/total commands, each with its own command identity, worker, authorization and ordinals, while every earlier exit tombstone remains replay/conflict authority until operation termination.

**Reproduction/state sequence:**

1. Dispatch command C1, run its effects, observe stop and accept its result.
2. The lease returns to the runtime continuation in `RUNNING`; C1 is `RESULT_ACCEPTED`, its authorization is closed and its tombstone must remain live.
3. The same operation requires a later child/fetch command C2, as retained from the accepted overlay.
4. `dispatch_worker` must install C2.

If C2 overwrites the singular tuple, C1’s exact replay/conflict record is lost or can be confused with C2. If the tuple cannot be overwritten because `RESULT_ACCEPTED` and its tombstone remain, C2 cannot be dispatched. No legal edge, command sequence number, command-record collection or “at most one active command” rule resolves the choice.

**Impact:** The design cannot implement the accepted whole-operation command schedule without either dropping idempotency evidence or refusing legal later work. Cross-command receipt/authorization confusion could also mutate the wrong command’s owner, ordinal set or result.

**Required correction:** Define an operation-owned ordered command ledger keyed by monotonically unique exact command identity/serial, with at most one active command, a distinct effect schedule and state machine per command, and separately retained terminal tombstones. Specify the runtime-continuation-to-new-command dispatch edge after prior result acceptance, and ensure prior command receipts and authorizations can never act on the new command.

**Closure test:** Execute at least two sequential commands under one operation permit. While C2 is queued, running and accepted, replay C1’s success, failure, cancel and stop records and present C1’s authorization/ordinal against C2. All must be exact idempotent C1 replay or mutation-free conflict; C2 must remain unchanged. Also prove C2 cannot dispatch before C1 result acceptance and that the shared operation charge releases only at the outer terminal outcome.

### [P2-3] The cleanup schedule cannot preserve the first non-effect failure as the primary exit

**Location:** Redesign §5.2 lines 252–262; §5.3 lines 294–312; mandatory trace at line 371.

The text says a failure outside an active effect is contained by `worker_exit_failure`, the first failure/cancel exit is primary, and later cleanup failures are diagnostics. The required wrapper schedule instead captures a command-body outcome, runs cleanup, and instructs a cleanup `BaseException` to “atomically contain or append.” Only a fixed-effect exception is stated to be already contained before cleanup.

**Violated invariant:** The first `BaseException` must own the exact exit receipt, effect knowledge and one owner transfer; later failures may only append diagnostics. Cleanup ordering must not overwrite or precede an earlier unrecorded body failure.

**Reproduction/state sequence:**

1. No effect is active; the closed command body raises E1 outside `run_effect`.
2. The wrapper merely captures E1 and starts trusted cleanup while the command remains `RUNNING_IDLE`.
3. Cleanup raises E2.
4. The schedule tells E2 to atomically contain the command, creating the primary receipt and owner transfer.
5. The next line requires preserving E1 as the first exception “and its exact failure/cancel receipt,” but E1 has no receipt. Recording it now is either a conflicting second exit or an overwrite of E2.

The adjacent mandatory trace adds a second contradiction: when a body successfully computed a private result and cleanup supplies the only exception, it calls cleanup failure “secondary,” although it is the first and only failure.

**Impact:** The future wrapper cannot deterministically choose the primary error, receipt digest or replay answer. Implementations can lose the actual command-body failure, create two exit attempts, or violate first-commit-wins and exact owner-transfer rules.

**Required correction:** Give the schedule a single exact order. A body failure outside an effect must commit its failure receipt before cleanup begins; cleanup may then append only a diagnostic. An effect failure already contained follows the same diagnostic rule. If the body succeeded and cleanup alone fails, cleanup must be the primary failure and create the sole receipt. Update the mandatory trace wording accordingly.

**Closure test:** Cover: body-only failure, cleanup-only failure after a private result, body failure followed by cleanup failure, effect failure followed by cleanup failure, and cancellation racing cleanup. Assert the temporally first failure/cancel receipt remains primary, later errors are bounded diagnostics, effect knowledge is unchanged, there is one containment transfer, unused ordinals remain revoked, and the charge persists through exact stop observation.

### [P2-4] Zero-permit neutral lineage bypasses the bounded live queue with no alternative bound

**Location:** Redesign §10 lines 509–578, especially append/fold behavior at lines 534–562. A6 lines 18–21 bounds the live queue by authored `live bounded N`; accepted W2 overlay §9 lines 617–648 makes every retained changed unit participate in finite lease/permit accounting.

Every neutral refresh appends a `NEUTRAL(..., PENDING)` entry but creates no batch or permit. A neutral entry behind a queued or active changed head cannot fold until that head publishes. The design supplies neither coalescing nor a finite lineage/replay ceiling, and its mandatory tests cover neutral chains without asserting bounded retained metadata.

**Violated invariant:** A bounded question must not acquire an unbounded retained-state path outside its batch/permit capacity. Zero delivery permits must not mean unlimited pending lineage and receipt tombstones.

**Reproduction/state sequence:**

1. Dequeue a changed head and delay its caller-visible publication indefinitely.
2. Continue periodic refreshes whose sealed results are neutral over consecutive ranges.
3. Each refresh legally completes and releases its operation lease, advances `produced_through`, and appends another pending neutral entry.
4. The active changed head prevents every neutral entry from folding, while the authored queue capacity and generation permit count remain unchanged.
5. Repeat without bound.

**Impact:** A single stalled active handoff permits unbounded in-memory lineage and replay metadata despite `live bounded N`. This defeats the design’s stated resource-limit obligation and can exhaust the runtime without overflow/refetch or another typed bounded outcome.

**Required correction:** Define one bounded rule. Coalesce the pending neutral suffix into a bounded aggregate span and bound its exact receipt-replay metadata; when that bound would be exceeded, retire/refetch before consuming another candidate. State the finite bound/default and its interaction with `live bounded N`, close, migration and failed-head retirement. Neutral progress must still create no delivery batch or buffer permit.

**Closure test:** Stall one active changed head, commit more neutral refreshes than the declared bound, then add a changed range. Assert retained lineage/replay state stays within the bound or the registration atomically retires with `RefetchRequired`; no batch/permit/publication is invented, cursors remain causal, close/migration cleanup is exact-once, and a later changed range becomes eligible only after the defined bounded recovery.

## 2. Invariant analysis

The following attacks held:

- The design consistently keeps public `TrustedContext` task-bound and claim-free. Worker identity comes from trusted providers, and result acceptance requires the exact original receiving runtime task plus zero-staleness context validation.
- Worker authority, reservations, exit/stop receipts and containment identity are sealed and issuer-owned. No ordinary caller supplies worker, task, claims, epoch or containment-owner proof.
- Effect reservation precedes invocation, active reservations block nested/reentrant/concurrent use, and `BaseException` containment revokes unused ordinals before another effect may begin. Late worker completion cannot restore authority or change A7 truth.
- Success cannot publish from a worker receipt. Exact stop observation precedes result acceptance; acceptance and final publication revalidate ownership and barriers. Worker quiescence, outer operation terminal state and A7 transaction knowledge remain separate.
- The failed FIFO rule is otherwise closed and conservative: an unpublished head retires the registration, leaves delivered progress unchanged, invalidates queued successors, retains the active charge to quiescence and requires a complete A6 refetch baseline.
- Neutral classification itself is trusted, fixed, sealed and lease-bound; no caller boolean or empty-row guess selects the branch. Changed/neutral ordering prevents neutral progress from overtaking a prior changed head. Finding `P2-4` is the missing bound, not a causality or provenance failure.
- Participant membership is activation-bracketed, exact-token-based and quiescence-bound. Frozen attempt membership does not mutate; leave-pending members remain obligations only for their current attempt, and fully left runtimes disappear from later attempts.
- The phase serial/request/successor fields correctly defeat the originating stale same-attempt proof counterexample at the proof-record level. Finding `P2-1` concerns the unamended accepted deployment edge grammar, not those freshness fields.
- The design honestly distinguishes deterministic reference atomicity from future locks, threads, async execution, database durability, crash recovery, physical fencing and cross-process proof. It does not claim the stopped source findings closed or authorize implementation.
- The proposed cohesion boundary keeps one lifetime mutation owner and does not create a second mutable worker registry. Plan and claims containment, result roles, pinned parameters, parent-owned derived work and the existing A7 truth grammar are preserved.

Those successful attacks do not resolve the four contradictions and omissions above.

## 3. Risks and next action

Production worker/thread/async behavior, PostgreSQL and SQLite adapters, resolver/provenance and whole-program proof, durable crash/cross-process/physical-fence evidence, activation, credentials, public W3 Surface, external capture and Git remain explicitly deferred and are not findings. The frozen 71-file source remains stopped; this verdict does not demand implementation or claim any source closure.

The single next action is a consolidated design correction resolving `P2-1` through `P2-4`, followed by a new exact manifest and fresh peer-blind Consistency/Safety review plus retracing of the five originating stopped counterexamples. Acceptance, if later earned, remains design-only.
