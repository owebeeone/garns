# W1A11-WorkerExitRedesign — ORIGINATING STATE DESIGN CLOSURE 3

**Review object:** Corrected `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; correction 2 of 2, not accepted and not implementation authority. Complete object: `W1A11-WorkerExitRedesign-MANIFEST-3.sha256` at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`, 115 files.

**Controlling DRAFT:** `W1A11-WorkerExitRedesign-DRAFT-3.md` at SHA-256 `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`.

**Remediation authority:** `W1A11-WorkerExitRedesign-RemPlan-2.md` at SHA-256 `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`; RemInputs-2 at SHA-256 `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`, 25 entries.

**Baseline:** Revision-2 design at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`, verified through the 100-entry product-root archive map. The stopped source remains immutable evidence at MANIFEST-3 SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.

**Date:** 2026-10-04

**Axis:** Focused originating State prospective closure. I retraced the stopped-source worker-exit, failed-FIFO, neutral-refresh and phase-proof counterexamples against the correction-2 design. Current correction-2 re-verdict/origin reports and prompts were not inspected.

**Verdict: GO — prospective originating-State design closure only.** The correction-2 handoff barrier, neutral terminal transition and uniform bounded lookup do not reopen any of the four originating State counterexamples. No new architectural or bounded State root was found within this scope. Every stopped-source finding remains open; this verdict neither accepts the design nor authorizes or validates implementation.

---

## Prior-finding closure table

| Originating ID | Design disposition retraced | Original causal sequence retraced on the final tuple | Status |
|---|---|---|---|
| `ReviewState-3 P2-1` — missing post-dispatch result/failure ownership transition | Finite command ledger; exact effect reservation and exit; trusted receiver-loss containment; ordered cleanup; operation-kind-specific final barrier | Effect 1 raises while effect 2 is unused; exact worker-to-receiver success; C1-to-C2 isolation; cancellation/dequeue; receiver loss; cleanup races; replay, fence, late exit and A7/quiescence separation | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `ReviewState-3 P2-2` — refused handoff falsely advances delivered progress | Registration retirement/refetch plus a specialized sole success barrier and two-phase non-success settlement | `(0,1]` fails before publication while `(1,2]` is queued; delivered stays 0, the successor cannot cross, and the active charge survives through exact worker-plus-iterator stop | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `ReviewState-3 P2-3` — missing neutral no-batch transition | Sealed neutral commit atomically advances lineage, terminalizes/releases the refresh, and uses bounded current/replay records with uniform absence | Zero-queue neutral; neutral behind changed work; changed-neutral-changed; more than `R` commits; eviction, current-candidate invalidation and later changed work | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |
| `OriginStateClosure-2 State-Closure-P2-1`, retaining the earlier phase-proof residual | Explicit deployment-state × phase product and exact phase/serial/request/successor proof | Issue a DRAINING proof, enter `MIGRATING_PRE_EFFECT` on the same attempt, reject the stale proof, accept one exact current proof, then reject it after `EFFECT_BEGUN` | **PROSPECTIVELY CLOSED IN DESIGN; SOURCE OPEN** |

## Changed-range analysis

The complete 652-line unified diff from revision 2 was inspected.

Correction 2 makes two bounded state-machine corrections:

1. Iterator delivery now enters nonterminal `PUBLICATION_READY`. `settle_delivery_success` is the sole legal final barrier and atomically records publication, settles the FIFO head and following neutral span, terminalizes the handoff, and releases its one charge before exposure. Generic success and containment terminalizers structurally refuse delivery operations. Non-success instead performs retirement and queued invalidation first, retains the active charge through exact worker-and-iterator quiescence, and only then terminalizes and releases.

2. Neutral refresh now keeps at most one current candidate in each already-charged refresh operation, with `A <= L_refresh`, and at most `R == C` committed replay entries. Neutral commit atomically consumes the candidate, updates cursor/span/ring state, records terminal `SUCCEEDED`, releases once, and creates no batch, delivery permit or publication. Any candidate or receipt absent from the current record and replay ring uniformly returns `RefreshRecordUnavailable`; no evicted-identity side history survives.

These are bounded transition and lookup corrections inside the existing single lifetime-registry ownership architecture. They add no public surface, subsystem, independently mutable owner, compatibility rule or deployment architecture. They therefore are not new architectural roots.

The finite worker schedule, per-command ledger, effect reservation, cleanup ordering, task-loss observation and command replay grammar are unchanged except for routing the already-quiescent outer operation through the correct final barrier. Section 9 participant membership and §11 migration product are substantively unchanged. The correction does not reopen worker identity, participant membership, migration-phase or parent-permit guarantees.

The legitimate round-2 reports were read completely:

- Consistency-2, SHA-256 `740e14350efe532cce940c655ef4a03b76f9ffd46f96df353ef06503149d0dec`;
- Safety-2, SHA-256 `6d3785cdcddeb3b0e1589e28da3ceba5ece4d328707fe4c8449b665658d5f3ff`.

Their three findings were classified by their originating reviewers as bounded. This report verifies only that their correction ranges do not reopen my originating State counterexamples; it does not substitute for those reviewers’ focused re-verdicts.

## 0. Evidence base

The exact tuple and all supporting guards were verified from the product root at both START and END:

| Evidence | SHA-256 | START | END |
|---|---|---:|---:|
| MANIFEST-3 | `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737` | 115/115 | 115/115 |
| RemInputs-2 | `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993` | 25/25 | 25/25 |
| Revision-2 archive verification map | `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c` | 100/100 | 100/100 |
| Revision-1 archive verification map | `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8` | 88/88 | 88/88 |
| RemInputs-1 | `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c` | 13/13 | 13/13 |
| Original redesign Inputs | `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52` | 19/19 | 19/19 |
| Stopped source MANIFEST-3 | `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` | 71/71 | 71/71 |
| ReadOnly guard | `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` | 111/111 | 111/111 |
| ProductGuard | `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` | 614/614 | 614/614 |

At both boundaries the design remained at `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`, DRAFT-3 at `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`, and RemPlan-2 at `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`.

I read completely:

- workspace and product instructions;
- the review-loop skill and canonical reviewer template;
- the complete 1,121-line correction-2 design, DRAFT-3 and RemPlan-2;
- both legitimate round-2 full reviews;
- my complete `OriginStateClosure-2`, SHA-256 `8134142adbdf5228b3e3fb525339a94198f454ff44fdfc7d4fa86bf6f956259f`;
- the complete originating stopped-source `ReviewState-3`, SHA-256 `d827e94d3945163573fa2cc37d872e6be8381b7d93e15019f60b12defaa37712`;
- the complete revision-2-to-current design diff.

No current round-3 redesign peer/origin report or prompt was read. No helper was used. No tests were run because this is a prospective design retrace against deliberately immutable stopped source. Inspection used only read-only `pwd`, `wc`, `rg`, `sed`, `nl`, `diff` and `shasum`. No file, source, test, report, manifest, archive, Git/GWZ state, network, service, database, generator or bytecode state was modified.

## 1. Findings

No P0–P3 findings within this originating State prospective-closure scope.

## 2. Invariant analysis

### Worker effect failure still contains before another effect begins

The original effect-1/effect-2 sequence remains closed:

1. The exact active command is `RUNNING_IDLE`.
2. Reserving effect 1 atomically validates the live operation, command serial, authorization, worker, context, binding, generation and ordinal, then records `EFFECT_IN_FLIGHT` before invocation.
3. Effect 1 raises.
4. Before the exception escapes, the registry records the primary failure receipt and `BEGUN_UNCERTAIN`, revokes effect 2 and all other unused ordinals, transfers the outer lease to its preallocated containment owner, and retains the generation charge.
5. Effect 2, success exit, result acceptance and later command dispatch have no legal edge.
6. Trusted cleanup may add only bounded diagnostics; it cannot replace the primary receipt, owner or effect knowledge.
7. Exact executor stop establishes command quiescence. Only containment may then reach the operation-kind-specific terminal path, while A7 knowledge remains independent.

Correction 2 does not alter reservation or exception handling. For a delivery operation it strengthens the outer consequence: generic completion cannot release the contained handoff, and the active charge survives through both worker and iterator stop before specialized non-success settlement.

### Exact worker-to-receiver success remains closed

The command success chain remains:

```text
RUNNING_IDLE
  -> SUCCESS_PENDING
  -> QUIESCENT_SUCCESS
  -> RESULT_ACCEPTED
```

Success exit requires the exact current worker, no active reservation, all required effects returned, completed trusted cleanup and a closed issuer-owned result. It closes the command authorization, revokes unused optional ordinals, transfers ownership to pending-result escrow and exposes nothing.

Only the bound executor’s stop receipt establishes quiescence. Result acceptance then requires the privately recorded receiving task, its still-valid original context, the exact receipt/result and current barriers. Wrong task, child task, stale receipt, wrong worker or changed binding/generation refuses without mutation.

For non-delivery, the runtime continuation reaches the generic atomic publication/terminal/release barrier. For iterator delivery, it instead creates nonterminal `PUBLICATION_READY` and must use the specialized §8 barrier. Thus the correction cannot make worker success itself publish or release, nor can it reopen the command after `RESULT_ACCEPTED`.

If the receiving task disappears before the applicable final commit, the trusted lifecycle observation invalidates the original context binding, closes private output and transfers the outer operation to containment. A delivery then retires through §8 without reopening the accepted command. After the atomic final commit, task loss cannot relabel success.

### Cancellation, cleanup, replay, fences and late exit remain fail-closed

Queued cancellation still competes with dequeue under the queue lock. Removal of a first command before any operation work can prove whole-operation cancellation; removal of a later command cannot erase prior work and yields only containment/`REFUSED`.

After dequeue, cancellation revokes unused ordinals and records `NOT_BEGUN`, `RETURNED` or `BEGUN_UNCERTAIN` from authoritative reservation history. The outer charge remains until stop. Body failure commits before cleanup; cleanup-only failure becomes primary; later cleanup and cancel-race failures occupy only finite diagnostic slots.

Every replay remains scoped by operation and command serial. Exact replay reads the retained tombstone; cross-command, cross-worker, cross-authorization, cross-result, cross-binding and cross-generation variants refuse. A late success after failure, cancellation, task loss or fence remains diagnostic only and cannot restore authority, ordinals, publication or ownership.

Barrier-first prevents reservation. Reservation-first records begun uncertainty and containment. Success-exit-first still must pass receiver acceptance and the operation-kind-specific publication barrier. Neither specialized handoff settlement nor neutral terminalization changes A7: command stop and operation terminal state do not manufacture `KNOWN_ABORTED` or `KNOWN_COMMITTED`, and unresolved A7 identities remain separately retained.

### Failed FIFO delivery cannot invent progress or expose a false zero count

For queued changed ranges `(0,1]` and `(1,2]`, let the first become the active head and then fail before the specialized success commit:

1. `begin_delivery_non_success` leaves `delivered_through` at 0.
2. It marks the head failed and the registration `RETIRING_REFETCH`.
3. It invalidates `(1,2]` and every other queued successor and releases only their real queued permits, once.
4. It prevents further refresh, enqueue, dequeue and handoff on that registration.
5. It revokes remaining worker/iterator authority and retains the active handoff under containment.
6. The charge remains while either worker command or iterator frame may resume.
7. Exact `DeliveryStopObservation` establishes both are stopped.
8. Only specialized final non-success settlement records terminal `REFUSED`, removes active ownership, releases the one active charge and returns `RefetchRequired`.
9. Recovery requires a complete new A6 snapshot/high-water/registration baseline; it never resumes from the abandoned produced cursor.

The second range therefore cannot cross the failed first range, and no non-success advances delivery.

The correction also closes the last-permit success race without weakening that failure rule. From `PUBLICATION_READY`, the sole success mutation records publication, removes the exact head, advances `delivered_through`, folds only the adjacent neutral span, terminalizes the handoff and releases its one charge. Exposure occurs only after that indivisible commit. Migration, close, fence or receiver loss therefore sees either:

- the precommit state, with the handoff still charged and eligible only for retirement; or
- the fully settled terminal success, with no unsettled head.

Generic completion refuses delivery operations. Exact settlement replay cannot move the cursor, expose again or release twice; conflicting success/non-success loses to the already committed outcome. The special barrier therefore strengthens, rather than reopens, the original `ReviewState-3 P2-2` causal fix.

### Neutral progress is terminal, bounded and cannot overtake delivery

For a charged neutral candidate `(0,1]` with no earlier changed work, one atomic commit:

- consumes the current candidate;
- advances `produced_through`;
- immediately folds the neutral interval so `delivered_through` advances consistently;
- updates the bounded replay ring;
- records the refresh lease terminal `SUCCEEDED`;
- releases its ancestry/generation charge exactly once;
- creates no batch, envelope, delivery permit or publication.

An in-window candidate or receipt replay reads the stored terminal/release facts and performs no second mutation.

Behind an active or queued changed record, the neutral commit advances only `produced_through` and extends that changed record’s single coalesced span. The changed handoff or queued entry retains its real permit, so releasing the neutral refresh cannot create false zero-count quiescence. `delivered_through` stays behind the changed record until exact caller-visible publication; the specialized success commit then folds that record and its one adjacent span together. Failure instead retires and discards the bounded successor lineage without inventing delivery.

Storage remains bounded:

- `Q` queued changed entries;
- `C == Q + 1` active-plus-queued changed entries;
- at most `C` pending neutral spans and `2C` lineage records;
- at most `R == C` committed replay entries;
- at most one current candidate in each already-charged live refresh record, with `A <= L_refresh`;
- no candidate or receipt table outside those records.

After substantially more than `R` neutral commits, an evicted candidate, evicted receipt, cross-registration identity, retired-registration identity or counterfeit is absent from the bounded authoritative records and receives only `RefreshRecordUnavailable`. That result is mutation-free and cannot select an arbitrary lease, reconstruct a cursor or recover former provenance. A current candidate remains distinguishable only because its charged operation record still owns it.

If close, fence, migration, overflow or cursor divergence invalidates a known current candidate before commit, the design gives the refresh lease an explicit disposition: unchanged live ownership for a presentation-only refusal; terminal `REFUSED` plus one release when already quiescent; or containment with the charge retained until exact stop. Commit-first is already a complete atomic success. These routes preserve the original neutral no-batch transition while repairing the prior terminal leak and impossible post-eviction lookup.

### Migration proof and membership remain preserved

The correction does not change §11’s closed product.

The originating phase trace still behaves as required:

1. Enter `DRAINING_OLD × DRAINING_OLD` and issue its exact proof.
2. Enter `MIGRATING × MIGRATING_PRE_EFFECT` on the same attempt. The phase serial increments and a new phase request binds the exact requested successor.
3. Present the old DRAINING proof. It refuses because phase, serial and request are stale, with binding, epochs, queues, membership and counts unchanged.
4. Release the exact current pre-effect request and issue its proof.
5. That proof alone may return to `CURRENT(old,new epoch) × NONE`, invalidating old admissions and buffers before queues reopen.
6. If the first migration effect wins, the phase becomes `EFFECT_BEGUN` before invocation; the pre-effect proof is permanently unusable.
7. Replay, wrong request/successor, cross-attempt and cross-coordinator proofs refuse mutation-free.

The specialized handoff barrier preserves this proof rather than bypassing it: a delivery’s last charge cannot disappear until FIFO settlement or quiescent retirement is complete. Neutral refresh release occurs only with its complete atomic cursor/terminal outcome; any changed work still retains its separate permit. Neither path manufactures a migration acknowledgement or no-effect proof.

Section 9’s activation-bracketed membership is unchanged. Pre-join admission still refuses, a leave-pending participant remains in the frozen current attempt, and only a locally closed participant with no retained operation, delivery, containment, registration-close or A7 obligation may become `LEFT`. Correction 2 supplies no alternate membership or migration owner.

## 3. Risks and next action

This is a narrow originating prospective GO. It does not replace the required focused Consistency-2 and Safety-2 re-verdicts, accept the replacement design, close any source finding, accept the stopped 71-file candidate, or authorize implementation.

Real executor ordering, async/thread/process synchronization, locks, PostgreSQL/SQLite behavior, durability, crash recovery, physical and cross-process fencing, provenance, credentials, activation, packaging and public W3 surface remain deferred evidence rather than claims made here.

The next action is manager completion of the design-only gate on this exact tuple. Acceptance requires every required peer and originating verdict on the same bytes. Any later contract/reference implementation requires a separate frozen source tuple, explicit execution authority, deterministic regressions and originating executable source closure.
