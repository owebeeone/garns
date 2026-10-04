# W2 admission-lifetime base-plus-overlay design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`; composed replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, filesystem tuple pinned by four-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` at SHA-256 `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`. Sources were read directly from the manifested filesystem under the accepted no-Git exception; no Git snapshot, commit, or cleanliness claim was used.  
**Date:** 2026-10-04  
**Axis:** Consistency — internal coherence, agreement with the complete controlling graph, exact supersession, and satisfiability of lifecycle and evidence obligations. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three P2 findings block. P2-1 and P2-2 are new architectural roots; P2-3 is a bounded protocol-ordering contradiction. I pre-commit to GO on a revision that resolves P2-1, P2-2, and P2-3 as specified without reopening the retained base counterexamples.

---

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` returned exactly `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`.
- The composed object hashes remained:
  - base `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`;
  - overlay `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`;
  - controlling DRAFT `c12dadeb1f86715e520a702d6daf1ee6e719ba4676b98b0e419840222927505f`.
- Recursive `shasum -a 256 -c` verification passed every entry in:
  - `W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256`: 4/4;
  - `W2-AdmissionLifetimeRedesign-Inputs.sha256`: 11/11;
  - `W2-Design-MANIFEST-3.sha256`: 13/13;
  - `W2-DesignSourceInputs.sha256`: 48/48;
  - `W2-DesignControlInputs.sha256`: 13/13;
  - `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`: 26/26.
- Inventory counts remained exactly 4/11/13/48/13/26. No tuple movement occurred.

I read the complete workspace and product instructions, review-loop skill and canonical prompt template, replacement brief and DRAFT testimony, stopped base, replacement overlay, W2 stop, final stopped-object Consistency and Safety reports, originating closure reports, W2 execution brief, and parent plan §§15–16.

The consistency trace covered:

- base sections 1–12, especially trusted provenance and point-verifier lifetime at lines 410–482, validation/authority order at 484–518, live reuse at 558–583, verification vectors at 602–662, and prerequisite ownership at 664–711;
- overlay supersession map at lines 30–50;
- handle, lease, registry, verifier, and non-escape rules at 52–123;
- closed admission/binding/lease states at 125–188;
- acquisition, dispatch, owner transfer, publication, and lock order at 190–228;
- whole-operation barriers at 230–269;
- graceful drain, hard fence, final quiescence, close outcomes, and A7 knowledge at 271–332;
- deployment-wide migration fencing at 334–388;
- subscription, cursor, buffered delivery, and permit lifecycle at 390–447;
- W1 amendment and mixed-peer requirements at 449–487;
- closure vectors and future static checks at 489–558.

I checked the composed design against the complete accepted A2, A3, A6, A7, A8, A11, and A12 ADRs and the relevant complete W1 contract definitions, including:

- task-bound authority validation at `src/garns/backends/contracts/authority.py:42-75`;
- authority-bound post-await delivery at `authority.py:77-94`;
- current close grammar at `state.py:63-117`;
- A7/A8 worker commit fencing at `state.py:241-309`;
- current executable plan seams at `protocols.py:30-75`;
- migration request/outcome coupling at `operations.py:83-177`;
- plan and binding identity at `semantic.py:105-175`.

I also checked the exact quoted base clauses in overlay §1.1. The quotations accurately identify the intended base text, and the map preserves the base algebra, encoding, resource, result-role, footprint, lowering, and deferral clauses outside the named lifetime replacement.

No test, build, generator, database, service, dependency, file write, Git, or GWZ operation was run.

## 1. Findings

### [P2-1] Worker lease ownership has no authority-validation path compatible with frozen A11

**Classification:** new architectural root cause.

**Location:** overlay lines 83–94 and 101–109 define the lease owner and guarded-step API; lines 208–216 transfer ownership from the caller/runtime to the queued command and worker; lines 248–257 require `run_plan_step` to revalidate A11 authority before adapter/fetch boundaries. Overlay lines 451–468 say the future W1 amendment adds lifetime/result ownership but do not amend A11’s authority ownership rule. Controlling A11 lines 3–22 require the exact current runtime-task object, while `authority.py:42-67` records the issuing task and refuses validation whenever `current_task()` is not that exact object.

**Violated invariant:** the design must preserve both A11’s exact-task authority ownership and its zero-staleness checks before database effects while allowing A8’s dedicated worker to own and execute queued work. Transferring the operation lease does not transfer the `TrustedContext`, and the frozen A11 contract supplies no worker-valid authority derivative.

**Reproduction/state sequence:**

1. Runtime task `T` owns genuine context `C` and acquires lease `L`.
2. Dispatch atomically transfers `L` to worker command `W` and changes it to `QUEUED`; dequeue transfers ownership to the worker and marks it `RUNNING`.
3. Immediately before adapter start or a later fetch, overlay §5 requires `run_plan_step` to revalidate A11 authority.
4. If validation occurs in `W`, `RuntimeAuthority.validate(C)` compares the current task with recorded owner `T` and refuses `CONTEXT_OWNER_MISMATCH`.
5. If validation is moved back to `T` before enqueue, the command may remain queued until after `C` expires or is invalidated and then start an adapter effect without the required zero-staleness validation immediately before that effect.
6. Copying claims or context into the command is also unavailable: A11 deliberately keeps claims in the issuer registry and makes the handle noncopyable, nonserializable, and valid only for its issuing owner.

Thus one conforming implementation either refuses every worker-owned database step or weakens A11’s task ownership/expiry boundary. The future state-machine tests cannot satisfy both specifications as written.

**Impact:** SQLite execution cannot implement the designed success path while retaining the accepted trusted-context contract. An attempted workaround risks either systematic false refusal or database work after authority expiry/invalidation.

**Required correction:** define the exact authority handshake across dispatch and worker execution. It must state which trusted component performs the immediate pre-effect validation, how that validation is bound to the exact queued command/lease/operation/generation, how expiry or invalidation before worker start prevents the effect, and why the mechanism does not create a caller-copyable claim or transferable `TrustedContext`. If A11 itself must change, name a separately reviewed A11/W1 amendment explicitly rather than placing the change implicitly inside the lifetime amendment.

**Closure/regression test:** with context `C` owned by task `T`, pause before enqueue, after enqueue, after dequeue, and immediately before adapter invocation. Run success, expiry, host invalidation, wrong-task, cancellation, and delayed-worker cases. Genuine unexpired work must execute; expired/invalidated work must make zero adapter calls; worker execution must not require `C` to validate as though the worker were `T`; and no copied command capability may authorize another lease, operation, runtime, generation, or effect.

### [P2-2] A local runtime close is specified as a deployment-wide binding drain with no legal restoration path

**Classification:** new architectural root cause.

**Location:** overlay lines 129–163 define `DRAINING_OLD` as a deployment-binding state and provide binding transitions. Lines 275–280 say graceful drain changes “runtime/records to `DRAINING` and the binding to `DRAINING_OLD`” and blocks all new leases. Lines 300–325 require every runtime, pool, or connection close to install that graceful-drain barrier. Lines 334–350 separately establish that the binding/generation coordinator is deployment-wide across all runtimes and connections.

**Violated invariant:** closing one runtime, pool, or connection must drain the resources owned by that lifecycle object without converting the shared qualified deployment into a migration-only state or preventing unrelated healthy participants from acquiring work. Deployment binding transitions must remain distinct from local lifecycle transitions.

**Reproduction/state sequence:**

1. Two runtimes `R1` and `R2` are open on the same `QualifiedDeployment` and generation under binding `CURRENT`.
2. The caller closes only `R1` or one pool/connection belonging to it.
3. Section 7 directs that close to install the graceful-drain barrier; section 6 defines that barrier as changing the binding to deployment state `DRAINING_OLD`.
4. Because acquisition first takes the deployment generation gate and requires binding `CURRENT`, `R2` can no longer acquire new leases even though it is not closing.
5. After `R1` reaches `CLOSED`, the binding transition table has no ordinary-close edge from `DRAINING_OLD` back to `CURRENT`. The only such edge is described as migration pre-effect refusal/reopen with a new admission epoch.
6. Treating close as final retirement is worse: §6 says final fencing permits old-generation retirement, which would retire the shared deployment merely because one participant closed.

The state machine therefore either causes deployment-wide denial of service on any local close or requires an unstated binding transition that the text declares closed and exhaustive.

**Impact:** pool/connection lifecycle cannot compose with multiple participating runtimes. A normal local close can strand healthy peers or accidentally reuse migration recovery semantics, violating A3 lifecycle behavior and the overlay’s own correctly admitted success obligation.

**Required correction:** split local lifecycle draining from deployment migration draining. A local runtime/pool/connection close should mark only its own admission records and local acquisition gate `DRAINING`; the deployment binding should remain `CURRENT` for other participants. Reserve `DRAINING_OLD` for the coordinator’s migration transition. Define how local permits are charged and released, how the closing participant reaches its close outcome, and how other participants remain admitted without bypassing retained permits from nonquiescent work.

**Closure/regression test:** open two runtimes and multiple connections for one deployment. Close one connection, one pool, and one runtime in separate cases while issuing new work through the other runtime. The closing object must reject new local acquisitions and report `CLOSED`/`NONQUIESCENT` correctly; the other runtime must continue acquiring current-generation leases; the deployment binding must remain `CURRENT`; and a later migration must still see every retained permit from the closed-but-nonquiescent participant.

### [P2-3] The exact migration sequence places queued-buffer invalidation both before and after the zero-permit barrier

**Location:** overlay lines 352–373 declare migration ordering “exact.” Step 4 requires zero old-generation execution and delivery permits before step 6 migration effects, while step 9 invalidates queued buffers only after durable next-binding publication. Overlay lines 414–422 say each queued `BufferedDelivery` retains a generation permit and that migration drain invalidates queued envelopes and releases their permits before waiting for active deliveries. Lines 438–444 again require old buffered deliveries to be handed off or invalidated before migration effects.

**Violated invariant:** queued delivery permits must have one unambiguous, executable place in migration ordering. The prescribed sequence must allow an idle subscription’s queued buffer to be invalidated before the zero-permit precondition, while ensuring no old buffer survives cutover.

**Reproduction/state sequence:**

1. A refresh enqueues old-generation envelope `B` and atomically replaces its refresh charge with buffered-delivery permit `P`.
2. The consumer is idle, so `B` remains queued and `P` remains charged.
3. Migration enters `DRAINING_OLD` and reaches exact step 4, which waits for zero old-generation delivery permits.
4. If the implementation follows §8 literally, `P` cannot be released until step 9 invalidates old buffers, but step 9 is unreachable until after step 4, migration effects, and next-generation publication. The finite wait therefore refuses every such migration.
5. If the implementation follows §9 and invalidates `B` before step 4, it violates the declared exact ordering that places invalidation at step 9 and leaves unclear what step 9 still atomically invalidates with old handles and registrations.

The two descriptions cannot both be the exact protocol, and the future deterministic migration tests have no single expected transition trace.

**Impact:** migration behavior depends on which section an implementer follows. One reading causes needless finite-wait refusal whenever an idle subscription has a queued batch; the other silently changes the declared cutover transaction and its registration/buffer atomicity.

**Required correction:** put queued-envelope invalidation in one explicit migration step before the zero-permit assertion, with exact lock ownership and atomic relation to stopping refresh acquisition. Reserve the post-publication step for already-invalidated envelope cleanup and old registration/handle retirement, or move all related invalidation earlier and state what remains coupled to cutover. Update the state table and closure vectors to match that single sequence.

**Closure/regression test:** enqueue an old-generation buffer with an idle consumer, start migration, and assert the precise transitions: stop new refresh leases; invalidate the envelope once; release its permit once; reach zero permits; begin no migration effect before that point; publish the next binding; reject delayed/copy dequeue; and require the subscription’s new-generation A6 refetch/registration handshake. Repeat with a concurrently active delivery lease to prove only active handoff ownership, not an invalidated queue item, delays cutover.

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Exact supersession:** every quoted clause in overlay §1.1 corresponds to the stopped base’s verifier return, revocation, close, migration, live reuse, pipeline, tests, or W1 prerequisite text. No unrelated algebra, encoding, resource, function, result, footprint, lowering, or query/question clause is silently replaced.
- **Original lifetime counterexample:** the composed design no longer returns a raw plan after point verification. Lease acquisition precedes lowering, queueing, adapter work, fetch, assembly, and publication; hard fencing retains containment and generation permits; close and migration cannot treat resumable work as quiescent.
- **Raw-plan escapes:** the verifier’s lexical consumer boundary, forbidden raw-plan outputs/caches, guarded derived statements, and architecture/data-flow checks retain the base’s raw, extracted, copied, fabricated, and mixed-peer refusals.
- **Lease identity and completion:** exact-instance, noncopyable, nonserializable handles; monotonic operation identities; compare-and-transfer ownership; and idempotent versus conflicting completion rules provide a coherent basis for future implementation, apart from the authority-transfer defect above.
- **A7 knowledge separation:** operation identity and transaction identity remain distinct. Lease completion neither invents commit knowledge nor proves worker quiescence, and commit reconciliation does not release a resumable worker.
- **Non-killable workers:** force close suppresses later steps/publication but retains the lease, contained worker, registry evidence, and shared generation permit until authoritative quiescence.
- **Snapshot consistency:** rows, high-water cursor, and durable registration share one lease and generation. A fence before publication discards the whole candidate and yields typed refetch/refusal.
- **Idle subscriptions:** they hold no execution lease. Per-refresh, per-handoff, and buffered-envelope ownership avoid an immortal subscription lease, subject to the migration ordering correction in P2-3.
- **Cross-runtime/process generation fencing:** the coordinator is keyed to qualified deployment; PostgreSQL and file-backed SQLite require cross-participant coordination, while an instance unable to prove participation refuses rather than relying on local counts.
- **Migration failure grammar:** no effect before the exclusive permit; post-effect ambiguity becomes `MIGRATION_INDETERMINATE`; old reopening requires authoritative no-effect proof; next-generation publication remains coupled to the requested binding and accounting.
- **Mixed peers and staged enabling:** `plan_admission_lifetime_v1` is mandatory, and raw-plan, old point-verifier, old-handshake, missing-capability, and nonparticipating peers refuse before lowering or I/O.
- **W1 non-authority:** the overlay does not claim that current W1 bytes already express result roles, leases, operation-aware close outcomes, or new refusal codes. It makes a separately reviewed amendment a prerequisite.
- **Evidence satisfiability outside the findings:** pause-point tests, owner/count assertions, non-killable worker vectors, no-transaction reads, duplicate/conflicting completion, stale lease cases, and correctly admitted success are falsifiable design obligations rather than claims of existing implementation proof.
- **Preserved deferrals:** database/thread/async/crash evidence, backend operational proof, driver matrices, external capture, provider cryptography, public naming/Surface, and W1 P3 remain deferred without removing their required protocol shapes.

## 3. Risks and next action

Real coordinator locks, worker interruption, database effects, crash recovery, and supported-version behavior remain implementation-gate risks and were not treated as design findings. The retained stopped-base counterexamples remain mandatory regression obligations.

The single next action is one consolidated design correction resolving P2-1 through P2-3, followed by fresh peer-blind review of the revised base-plus-overlay tuple because P2-1 and P2-2 change authority and lifecycle architecture. No W1 amendment or implementation should begin on this revision.

