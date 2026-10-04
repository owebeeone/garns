# W1A11-WorkerExitRedesign — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`; operator-authorized design candidate, correction 0/2, not accepted or implementation authority, dated 2026-10-04.  
**Baseline:** Approved no-Git filesystem-SHA exception. The 88-entry review manifest `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-1.sha256` remained at SHA-256 `79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`. Sources and controlling documents were read directly from the current filesystem; no Git state was used. The controlling DRAFT remained at SHA-256 `e8fd137970df5dc62ce5e838b6ca8f267a43343167f32805da75c2d2650b76b7`.  
**Date:** 2026-10-04  
**Axis:** Safety — degraded paths, irreversible transitions, retained ownership, stuck states, bounded resource behavior and fail-closed adversity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block. Both have bounded, text-fixable remedies within the selected architecture. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the complete review-loop `SKILL.md` and canonical reviewer template.
- `W1A11-WorkerExitRedesign.md`, its DRAFT and complete operator brief.
- The accepted composed W2 base and lifetime overlay, their acceptance record, W1 acceptance, `PRODUCT_LAYOUT.md`, ADRs A1–A16 and the ADR index.
- The stopped amendment, execution brief, both remediation plans, STOP record, final Code/State reports, Fresh Code closure, Origin State closure, Origin Code closure and restart verification.
- Parent implementation-plan §§15–16 governing the filesystem-SHA review exception and bounded review loop.
- The stopped contract/reference source and test tuple as supporting evidence only; no frozen-code defect is reported here as a defect in the prospective design.

Exact supersession claims were compared with their original accepted clauses, including worker result/containment transfer, immediate ordinal consumption, authoritative quiescence, participant joining, neutral refresh, FIFO delivery and no-effect reopen.

Integrity evidence:

- At both review boundaries, `W1A11-WorkerExitRedesign-MANIFEST-1.sha256` matched its exact hash and all 88/88 entries verified.
- The object and DRAFT matched their exact hashes at the end.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52` and verified 19/19.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` and verified 71/71.
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` and verified 111/111.
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` and verified 614/614.

Inspection used only permitted `shasum`, `wc`, `rg`, `sed`, `nl` and `cat` commands. No test was run: the optional existing suite exercises the known stopped source, not the prospective design, and cannot close or refute these textual state sequences. No file, bytecode, manifest, source, test, Git/GWZ state, service or database was modified; no helper was used.

## 1. Findings

### [P2-1] Receiving-task disappearance has no exact transition out of pending or quiescent success

**Location:** `W1A11-WorkerExitRedesign.md:110-124`, `:150-162`, `:241-250`, `:264-292`, and `:372-376`; retained accepted requirement at `W2-AdmissionLifetimeRedesign.md:204-213`.

**Root cause:** The result path binds acceptance exclusively to the original receiving runtime task, but the closed command grammar defines no trusted receiving-task-done/disappearance observation. Cancellation has only two stated sources: a request by that exact still-live receiving task, or an issuer-internal fence/expiry/close event. The accepted overlay separately requires task disappearance after dispatch to transfer ownership to containment; the redesign neither names disappearance as an internal invalidation event nor gives it an edge or regression.

**Violated invariant:** Every post-dispatch state must have one authoritative owner and a reachable fail-closed terminal path. Exact task binding may prevent another task from accepting a result, but it may not make the vanished task the only entity capable of initiating the transfer that releases retained ownership.

**Reproduction:**

1. The original receiving task validly dispatches a worker command.
2. The worker completes cleanup, commits `SUCCESS_PENDING`, exits, and the exact executor stop receipt advances it to `QUIESCENT_SUCCESS`.
3. Before calling `accept_worker_result`, the receiving task is externally cancelled or terminates without executing `request_worker_cancel`. Its context has not expired, and no runtime close, hard fence or generation fence occurs.
4. The task can no longer request cancellation or accept the result. Any replacement, child or recovery task fails the exact receiver check mutation-free.
5. The state machine has no receiver-disappearance edge from `SUCCESS_PENDING` or `QUIESCENT_SUCCESS`. The containment owner cannot terminalize because ownership never transferred to containment.

The lease and generation permit can therefore remain retained indefinitely despite authoritative worker quiescence. Local close reports retained work and migration cannot reach zero until an unrelated expiry or fence happens; a context with a distant deadline makes this an avoidable prolonged outage.

**Impact:** A normal receiving-task failure can strand a quiescent operation and block close or deployment migration. This regresses the accepted overlay’s explicit task-disappearance containment rule and makes task identity a liveness dependency rather than only an authority boundary.

**Required correction:** Add an issuer-owned, exact receiving-task lifecycle observation. An exact task-done/cancelled event must be obtained from a trusted task provider, never supplied by an ordinary caller, and must:

- authoritatively remove queued work or transfer running/pending success to containment;
- revoke unused effect ordinals;
- preserve any active-effect uncertainty and A7 truth;
- move `QUIESCENT_SUCCESS` directly to `QUIESCENT_CONTAINED`;
- preserve `RESULT_ACCEPTED` handling under the outer lease grammar if disappearance occurs after acceptance;
- reject wrong-task, stale, copied and replay-conflicting observations without mutation.

The text should state explicitly whether task completion invalidates the original context record; it must not leave that relationship implicit.

**Closure test:** Pause at queue insertion, dequeue, idle running, effect-in-flight, success-exit commit, stop observation, result acceptance and pre-publication. At each pause, terminate the exact receiving task without allowing its application frame to request cancellation. Assert one retained owner, exact ordinal revocation, no publication, correct `NONQUIESCENT` versus quiescent containment, one eventual permit release, and unchanged A7 knowledge. Wrong-task and duplicate task-done observations must be mutation-free or idempotent as appropriate.

### [P2-2] Zero-permit neutral lineage and replay records are unbounded behind delayed changed work

**Location:** `W1A11-WorkerExitRedesign.md:507-570`, especially `:509-515`, `:534-545`, `:554-560` and `:564-570`; controlling bounded/coalescing requirements at `docs/adr/A6-subscription-snapshot.md:18-21`.

**Root cause:** Every neutral refresh appends a distinct `NEUTRAL(..., PENDING)` lineage entry and returns an exact replayable receipt, while consuming no buffer permit and no stated capacity. Folding stops behind any queued or active changed entry. The design defines neither coalescing of consecutive neutral spans, a lineage/receipt limit, an overflow/refetch transition, nor bounded tombstone retention for its promised idempotent neutral replay.

**Violated invariant:** A bounded live question must not acquire an unbounded internal queue merely by classifying work as neutral. A6 bounds the authored queue and requires duplicate wakeups/revision ranges to coalesce by cursor. Zero outward batches and zero permits do not make internal lineage storage or atomic fold work free.

**Reproduction:**

1. Commit changed range `(0,1]`, dequeue it, and delay its active caller-visible handoff.
2. While that head remains active, perform neutral refreshes for `(1,2]`, `(2,3]`, and so on through `(n-1,n]`.
3. Each refresh passes `previous == produced_through`, advances `produced_through`, appends a distinct pending neutral entry, returns a distinct receipt and consumes no buffer permit.
4. Because the changed head is still active, `delivered_through` remains zero and none of the neutral entries folds.
5. The authored buffer bound and deployment permit count never stop the sequence. Memory and private replay state grow with `n`.
6. When the head finally publishes or fails, one registry mutation must fold or discard the entire unbounded prefix while holding the lifetime-state mutation boundary.

This creates unbounded memory retention and unbounded lock-held work in a path described as bounded. It can delay close, migration barriers and unrelated registry operations even though permit accounting remains numerically correct. The same lifetime-long growth exists for absorbed neutral receipts if exact replay remains valid without a finite retention rule.

**Impact:** A delayed consumer plus ordinary neutral refresh traffic can exhaust memory or monopolize the registry mutation boundary without ever filling the authored queue. The design therefore widens the denial-of-service surface beyond the accepted bounded subscription model.

**Required correction:** Define a bounded neutral-lineage and replay grammar. At minimum:

- coalesce consecutive pending neutral intervals within the same changed-work gap by advancing one sealed interval’s `observed_through`;
- prove the number of neutral gap records is bounded by the active/queued changed capacity;
- define how exact receipt replay remains deterministic after coalescing without retaining one unbounded private record per refresh;
- specify a finite tombstone/receipt retention rule or a typed overflow/refetch outcome;
- bound the amount of folding/discard work performed in one mutation.

Coalescing must preserve exact candidate consumption, produced/delivered truth and the `changed-neutral-changed` causal boundary; it must not silently translate a stale cursor.

**Closure test:** Hold one changed head active and commit substantially more neutral refreshes than the authored live bound. Assert constant or explicitly bounded lineage/receipt state, zero extra permits/batches/publications, monotonic produced progress, unchanged delivered progress and bounded settlement work. Repeat with multiple queued changed gaps, neutral-neutral-changed chains, replay of old neutral inputs, head success, head failure, close and migration.

## 2. Invariant analysis

The following attacks held:

- Effect reservation precedes invocation, active reservation prevents nested/reentrant/concurrent effects, and `BaseException` or running cancellation transfers to containment before another ordinal can reserve.
- Worker success remains private until authoritative executor stop observation and exact receiving-task acceptance. Wrong worker, task, authorization, lease, command, binding and generation attacks are mutation-free.
- A late worker result cannot escape containment, restore ordinals or manufacture A7 transaction knowledge.
- Operation permits survive worker return, exit receipt, result acceptance and stop observation; terminal publication or authoritative contained completion is the release boundary.
- The design explicitly keeps worker quiescence, operation terminal state and A7 commit truth independent.
- Failed FIFO heads do not advance delivered progress. Registration retirement/refetch invalidates successors, conserves queued and active permits, and resumes only from a complete newly published A6 baseline.
- The success-settlement ordering attack did not produce a finding because §8 explicitly assigns buffer, handoff, operation and generation-count changes to one lifetime-registry mutation. A later implementation must preserve that single transaction and cannot treat settlement as a callback after permit release.
- Neutral classification is sealed, lease-bound and selected by a trusted fixed comparator; ordinary callers cannot choose “neutral” or infer it from empty rows. Changed/neutral ordering preserves causal delivery semantics. The failure is its missing resource bound, not its cursor meaning.
- Participant membership is activation-bracketed, frozen attempts do not mutate, retained obligations prevent premature leave, and quiescent final leave prevents closed idle runtimes from becoming permanent future participants.
- Migration no-effect proof binds exact attempt, current phase, phase serial, phase request and requested successor. A prior DRAINING proof cannot authorize MIGRATING reopen; proof consumption and old-admission invalidation are atomic.
- The document proposes one mutation owner, keeps worker-authority helpers non-owning, preserves the no-raw-`Plan` and task-bound public-context boundaries, and is honest about deterministic reference versus deferred production evidence.

These successful attacks do not close P2-1 or P2-2.

## 3. Risks and next action

Real async/thread workers, PostgreSQL/SQLite adapters, durable crash behavior, cross-process fencing, database truth, production locks, resolver/provenance proof, activation, credentials, public naming and mixed-version operation remain expressly deferred and are not findings. The stopped source remains unaccepted; a design GO would not close it.

The single next action is a bounded design revision that adds the trusted receiving-task-disappearance transition and a finite/coalesced neutral-lineage/receipt grammar, with the causal regressions specified above. Freeze a new exact tuple and return it for focused Safety re-verdict plus the independently required parallel-axis verdict.
