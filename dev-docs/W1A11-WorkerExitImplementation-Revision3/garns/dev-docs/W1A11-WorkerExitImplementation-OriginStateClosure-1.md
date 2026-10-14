# W1A11-WorkerExitImplementation — STATE-AXIS REVIEW: ORIGINATING EXECUTABLE CLOSURE 1

**Review object:** The candidate worker-exit internal contracts and reference implementation, compared with the archived 20-file baseline.
- Approved filesystem tuple: `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`, SHA-256 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544`, 117 entries. This is the approved no-Git tuple, not a Git commit.
- Controlling DRAFT: `dev-docs/W1A11-WorkerExitImplementation-DRAFT.md` at `e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`.
- Status: unaccepted candidate. The implementation correction count is 0 of 2.

**Baseline:**
- Archived originals live under `dev-docs/W1A11-WorkerExitImplementation-Baseline/`. Their map has SHA-256 `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a` and verified 20/20.
- All sources were read directly from the filesystem tuple at `/Volumes/projects/limbo/garns-wz/garns`. Git was not used.
- This tree was relocated byte-exact on 2026-10-04 from `/Volumes/projects/limbo/datascad/garns-v9-6`. DRAFT links that name the datascad path refer to the same bytes.

**Date:** 2026-10-04

**Axis:** State: durable-state semantics and adversity. This report does two things:
- It is the originating executable closure for ReviewState-3 P2-1, P2-2 and P2-3, and for OriginStateClosure-2 State-Closure-P2-1, on the new source object.
- It is a full State attack on the changed range.

The review is independent, adversarial and read-only. The other axis runs in parallel; nothing here relies on it. The lane owner files this report verbatim.

**Reviewer provenance (replacement disclosure):** I am a fresh replacement reviewer: a Claude subagent dispatched with model parameter "opus".
- I am not the agent that wrote ReviewState-3, OriginStateClosure-2 or OriginStateClosure-3. That agent ran in another harness; its model is recorded as "gpt-5.6-sol high". Its context did not survive the handoff, and I claim no part of it.
- I reconstructed every result below from the filed reports and re-executed it on this tuple.
- For the three ReviewState-3 IDs, this is the State lane's same-origin closure, performed by a replacement agent.
- For State-Closure-P2-1, the originating context was already lost before the design round (see the STOP record). Here this is the accepted fresh-review replacement after a material design change, as plan §16 allows.
- I closed the original sequences by re-running them through the replacement APIs, not by citing removed APIs or happy paths. Nothing here accepts production code, the manager's tuple or source.

**Verdict: NO-GO** — seven P2 findings block (P2-1 to P2-7). Three P3 findings do not block.
- All four original counterexample sequences are closed when re-run through the replacement APIs.
- However, the executable object contains new State counterexamples in three of the same roots: worker exit, FIFO retirement and neutral refresh.
- Every blocker is a bounded code and test correction inside the accepted single-lifetime-owner architecture. None requires a change to the accepted design, ownership, architecture or compatibility, so none triggers a STOP.

**I pre-commit to GO on a revision that resolves P2-1, P2-2, P2-3, P2-4, P2-5, P2-6 and P2-7 as specified.**

---

## Prior-finding closure table

| Original ID | Original counterexample | What the re-run through the replacement APIs showed on MANIFEST-1 | Status |
|---|---|---|---|
| ReviewState-3 P2-1 (worker exit) | Effect 1 raises. The lease stays RUNNING, effect 2 is still accepted, and there is no result or containment transfer. | **Failure path.** Effect 1 raised, once as `RuntimeError` and once as a `BaseException` subclass. Before the exception escaped, the lease was CONTAINED under `containment_owner`, the ordinals were `(∅,∅)`, knowledge was `BEGUN_UNCERTAIN` and the count was 1. A nested `run_effect(2)` during the effect refused without consuming an ordinal. Afterwards, effect 2, success exit, transfer, complete by worker or caller, and publish all refused, with state unchanged. After the exact stop, `complete_contained` gave REFUSED and the count dropped to 0. **Success path.** The command went to SUCCESS_PENDING with the owner held in escrow. Accept before stop refused. Accept by the wrong task refused with state unchanged. The exact receiver's accept succeeded and passed ownership to the continuation owner. **Two commands.** C2 refused until C1 was accepted. C2 then got a new serial, worker and authorization without a new permit. C1 replay, conflict, effect and dequeue attacks did not affect C2. Dispatch beyond M refused. | **Original sequence CLOSED. Root OPEN:** P2-1 to P2-5 are new executable counterexamples in this root. |
| ReviewState-3 P2-2 (failed FIFO) | Range (0,1] fails before publication, delivered progress advances to 1, and (1,2] dequeues. | **Literal sequence.** The context expired before PUBLICATION. Generic `complete` and `complete_contained` refused. A renewed-context dequeue of (1,2] refused, and the cursors stayed (2,0). Phase 1 dropped the count from 2 to 1 and moved the registration to RETIRING_REFETCH. Settlement refused before stop. After the delivery stop it returned `RefetchRequired` with count 0 and cursors (2,0). Replay was idempotent. A refresh on the retired registration refused, and a new registration worked. **Nine-cause matrix.** I repeated the run for worker failure, expiry at commit, hard fence, receiver cancel after dequeue, cleanup failure, receiver loss at PUBLICATION_READY, migration barrier, graceful close and `revoke_generation`. Every cause conserved: count 2→1→0, delivered stayed 0, the successor was refused, publications +0, and a late success refused. | **Original sequence CLOSED. Root OPEN:** P2-4 (a receiver cancel of a still-queued delivery command has no cause record) and P2-5 (generic containment skips phase 1). |
| ReviewState-3 P2-3 (neutral refresh) | A neutral candidate cannot advance the cursor without creating an envelope or permit. | Neutral range (0,1] produced a receipt. The lease went SUCCEEDED, the count dropped from 1 to 0, publications +0, no queued buffer was created, the cursors went to (1,1) and the replay ring held 1 entry. Candidate and receipt replay returned the same receipt. The next changed range from 1 succeeded and was delivered through 2. Fabricated and cross-registry identities returned `RefreshRecordUnavailable`; copy and pickle refused. 28 neutral commits behind an active head kept the count at exactly 1 and coalesced into one span, which folded on head success. | **Original closure test CLOSED. Root OPEN:** P2-6 (an unusable known candidate gets no disposition) and P2-7 (unbounded retained history and work). |
| OriginStateClosure-2 State-Closure-P2-1 (phase proof) | A DRAINING proof is accepted after the same attempt enters MIGRATING. | I issued a DRAINING proof, then moved the same attempt to MIGRATING_PRE_EFFECT (serial 2, new request). The stale proof, the stale drain request, a fabricated request or proof, a cross-coordinator proof and a cross-attempt request all refused. The full state vector stayed unchanged: state, generation, admission epoch, phase/serial/request, count, queue markers, membership and proof table. The exact current proof reopened once (epoch 1→2). Replay and the old proof then refused. Queues reopened only afterwards. EFFECT_BEGUN disabled all pre-effect proofs. | **CLOSED.** P3-2 records separate product-closure gaps. |

I re-executed the retained obligations rather than citing them:

| Retained set | Re-executed result |
|---|---|
| Initial 18 — State P2-1 (forged or wrong-owner permit release) | Raised `ValueError`; count unchanged; migration got `DEADLINE_EXCEEDED` while the lease was live. Held. |
| State P2-2 (CLOSED with a live buffer permit) | Subscription close reported CLOSED with count 0; a later dequeue refused. Held. |
| State P2-3 (cross-provenance exchange) | Cross-registration and cross-admission dequeues refused; count unchanged. Held. |
| State P2-4, including expanded revocation | Publication from ACQUIRED refused. Publication after context invalidation refused, the lease went CONTAINED, and publications stayed 0. Held. |
| State P2-5 (absence as activation proof) | `recover(None)` raised `TypeError`; withdrawal with the wrong fence refused; the exact withdrawal worked once; epoch reuse was refused. Held. |
| State P2-6 (post-effect recovery) | Missing and mismatched proofs refused; the three exact outcomes (requested-next, full rollback, non-reuse) worked. Held. |
| State P2-7 (capability) | A query handle could not acquire REFRESH; a QUERY-only context could not acquire REFRESH; `ITERATOR_HANDOFF` via `acquire` refused. Held. |
| State P2-8 (parameters) | Only acquisition pins parameters. Held. |
| State-Supplement P2-1 | An illegal queued transfer left state unchanged. Held. |
| Code P2-1, P2-3, P2-4, P2-7, P2-8 (spot checks) | A plain callable consumer refused. Backward and duplicate steps refused before any mutation. Old admissions and leases were invalid after no-effect reopen. Operation kinds are closed. Close without drain refused. Held. |
| Correction-1 F2, F3, F4, F5, F6, F7, F8, F9, F10 | F2: two-range FIFO success; later-before-earlier refused. F3: same-fence withdrawal. F4: duplicate or after-reopen acknowledgement refused; count zero without acknowledgement refused. F5: candidate provenance attacks refused. F6: derived commands are ordered, carry one parent charge and cannot replay. F7: the recovery proof enforces the exact successor. F8: see above. F9: issuing-task impersonation left state unchanged. F10: a closed destination queue refused. F1: the raw-Plan source rule and consumer issuer hold. All held. |

## Changed-range analysis

**What changed against the archived baseline.**
- 15 of the 20 writable files changed. 5 are byte-identical: `authority.py`, `consumers.py`, `lifetime.py`, `protocols.py` and `__init__.py`.
- Three files are new: `test_worker_exit_contracts.py` (841 lines), `test_contract_source_rules.py` (187) and `W1A11-WorkerExitImplementation.md` (155).
- All changed paths are inside the brief's write allowlist.

**State-critical deltas.**
- `lifetime_reference.py` grew from 796 to 1,780 lines (+1,076/−92). It adds the command schedule and ledger, reservation, exit/stop/accept, containment, receiver loss, delivery publication and retirement, and refresh commit and disposition.
- `buffer_reference.py`: 333 → 502 (+173/−4). Adds Q, C and R, neutral spans, the replay ring and two-phase retirement.
- `generation_reference.py`: 440 → 561 (+141/−20). Adds join and leave, the phase product and request identities.
- `migration_reference.py`: 111 → 127.
- `worker_authority.py`: 223 → 143. It is now a stateless façade plus sealed identities.
- Smaller changes: `snapshot_reference.py` +21, `values.py` +18, `admission.py` +2.

**Classification.** This is a new executable object after a material design change, so I replaced every old proof with fresh execution.
- Every defect below sits inside the accepted architecture: one mutable lifetime-registry owner, a buffer subledger and a separate coordinator domain.
- No fix needs a new owner, subsystem, public surface, compatibility rule or accepted-design change.
- All seven P2 and three P3 findings are therefore bounded implementation corrections. There is no new architectural root cause and no STOP trigger.

## 0. Evidence base

**Tuple verification.** I ran these checks from the product root at START (10:44 UTC) and END (11:14 UTC).

| Check | SHA-256 | START | END |
|---|---|---:|---:|
| MANIFEST-1 | `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` | 117/117 | 117/117 |
| Inputs | `89ee484c8a4980972f0cc7e0cc0f12577a8f00dd5aba07c0eb8c7b83ab884cb5` | 31/31 | 31/31 |
| Baseline | `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a` | 20/20 | 20/20 |
| ReadOnly | `53d32f0522a5c0ff7434cfa97ac569fe064ac180f2ccb1294355588ea254d1da` | 741/741 | 741/741 |
| Legacy WorkerExitRedesign MANIFEST-3 | `bf833027135fd6fc6035f23089246438bde9506a7fef652336e0e9ac78d9107d` | 115/115 | 115/115 |
| Legacy ContractAmendment MANIFEST-3 | `cf98a3195dccb14859a01628c892df3cfd21d39d6422112344a511b169600f57` | 71/71 | 71/71 |
| Legacy ContractAmendment ReadOnly | `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` | 111/111 | 111/111 |
| Legacy ContractAmendment ProductGuard | `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` | 614/614 | 614/614 |
| Design AcceptanceEvidence | `882a3fec6ddecf7a7230a9e332e649be29020a326fe917b75ac523a691c84854` | 13/13 | 13/13 |
| `.pyc` / `.pyo` / `__pycache__` | — | 0 | 0 |

My prompt (`ccb3c419fcc4f998f5ddeaef23c7e6edf45ee10bf8a8708eb3c90ff8963c51cc`) and the DRAFT were unchanged at both ends. The tuple did not move.

**Documents read completely.**
- Process: the review-loop skill and canonical template, `AGENTS_GWZ.md`, product `AGENTS.md`, and program plan §§15–18.
- This build: the ExecutionBrief, the DRAFT, the implementation record, and Verification-1 plus the outline of its logs.
- Accepted design and composition: the accepted design (1,121 lines) and its ACCEPTANCE; the W2 overlay (853 lines) and its ACCEPTANCE; the W2 base (711 lines); W1-ACCEPTANCE; `PRODUCT_LAYOUT`; A16; the ADR README.
- Stopped source history: STOP, ReviewCode-3, ReviewState-3, FreshCodeClosure-2, OriginStateClosure-2, RemPlan, RemPlan-2.
- Redesign reports: ReviewConsistency-3, ReviewSafety-3, OriginCodeClosure-3 with its erratum, and OriginStateClosure-3.

**Not read:** any other Prompt-1 or Prompt-2 file, the Handoff, or any current-round review or closure report. None existed at START.

**Source read completely.**
- `lifetime_reference.py` 1–1780, `buffer_reference.py` 1–502, `generation_reference.py` 1–561.
- `worker_authority.py`, `migration_reference.py`, `snapshot_reference.py`, `admission.py`, `authority.py`, `consumers.py`.
- The `values.py` diff and result types, and `lifetime.py` 1–140.
- Tests: `test_worker_exit_contracts.py` 1–841, `test_contract_source_rules.py` 1–187, and the fixture helpers at `test_admission_contracts.py:39-72` and `test_lifetime_contracts.py:36-160`.

**Suites executed.** All runs used `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`.

| CPython | `-B -m unittest discover -s tests/contracts -t .` | `-B -m unittest discover -s tests -t .` | `-B tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | 130 OK | 233 OK | 5 PASS |
| 3.12.12 | 130 OK | 233 OK | 5 PASS |
| 3.13.12 | 130 OK | 233 OK; inherited SQLite ResourceWarnings visible | 5 PASS |
| 3.14.3 | 130 OK | 233 OK; inherited SQLite ResourceWarnings visible | 5 PASS |

**Inline attacks.** I also ran 25 inline attacks against the reference APIs in the form `python3.14 -B - <<'EOF' … EOF` (stdin heredoc, same environment).
- No file in the tree was written.
- I read private fields only to observe state; I never wrote them.
- Representative outputs are quoted in each finding.
- I did not run `tools/check.py`.
- Besides the listed commands, I used `ls`, `awk`, `sort`, `uniq`, `cut`, `tr`, `head` and `date` read-only, only for listing and formatting.

## 1. Findings

### [P2-1] Non-delivery publication and refresh commit terminalize worker-backed operations without checking the worker-exit ledger

**Location** (`lifetime_reference.py`):
- `run_plan_step`, lines 372–390 and 406–413: a non-delivery PUBLICATION terminalizes the lease and releases its permit.
- `commit_refresh`, lines 963–972: no owner or ledger check. It reaches `_commit_refresh_record`, lines 980–1057 (the neutral path terminalizes at 1013–1026; the changed path is 1032–1057).
- `publish_refresh_buffer`, lines 940–961.
- `register_subscription`, lines 851–896.
- By contrast, generic `complete()` already refuses worker-backed operations at lines 746–750.

**Violated invariant:**
- Design §4.1, lines 211–213: "Public publication is legal only after serial M is RESULT_ACCEPTED, no command is active, the exact receiver remains live…"
- Design §6, lines 444–446 and 480–482: no worker fact releases a permit, and "A known commit does not establish worker quiescence."
- W2 overlay §11.1, lines 742–747: the lifetime design "never permits migration cutover while it can resume."
- Brief line 143: "no publication before stop."
- A16 lines 55–57 ("Success remains private until … stop … and exact receiving-task acceptance") and the implementation record overstate what is enacted.

**Reproduction:**
- **(a) Default worker provider.** The default provider captures the dispatching task, so the worker token equals the receiver token. Sequence: acquire EXECUTE → `dispatch_worker` → `dequeue_worker` → `run_plan_step(LOWER)` → `run_plan_step(PUBLICATION)`. Result: `lease=succeeded completion=succeeded cmd=running_idle remaining=[1] count=0 pubs=1`.
- **(b) Publication during an in-flight effect, followed by migration.** Same as (a), but PUBLICATION is called from inside effect 1, then `begin_drain`, barrier, `begin_migration` and `begin_migration_effect` run. Result: `('in-flight cmd','effect_in_flight','count',1)`, then `('publish during effect','OK','lease','succeeded','count',0,'pubs',1)`, then `('begin_migration while effect in flight','OK','state','migrating')`, then `('begin_migration_effect','OK','phase','effect_begun')`. The old-generation effect then returns as a normal RETURNED effect.
- **(c) Distinct worker W.** The caller creates a refresh candidate, then dispatches and dequeues W. `commit_refresh(candidate)` gives `NeutralRefreshReceipt lease succeeded count 0`, and `migration may begin while W's command can still run: OK migrating`.
- **(d) Changed refresh.** `publish_refresh_buffer` returns `BufferedDelivery` with `lease=succeeded` while the command still has `remaining [1]`.
- **(e) Snapshot registration.** `register_subscription` publishes (`pubs_delta 1`) while the command is RUNNING_IDLE. Accept later moves the lease from PUBLISHING back to RUNNING. After that there is no success terminal path: `complete` gives LEASE_OWNER_CONFLICT and `run_plan_step(PUBLICATION)` raises `ValueError`. Only cancel works, and it gives REFUSED: the registration is published but its lease ends REFUSED.

**Impact:**
- The count reaches zero while a command can still resume: quiescence is invented.
- A publication happens that never passed exit, stop or accept.
- A migration drains, begins and starts effects while old-generation work is in flight.
- Through P2-2, the operation can then become permanently unterminalizable.
- Separately, (e) shows that worker-backed registration and refresh cannot succeed after acceptance, because `_live_lease` rejects the continuation owner.

**Required correction (bounded):**
- Add one shared publication precondition and use it in every non-delivery terminal publication: PUBLICATION, neutral and changed refresh commit and publish, registration, and refresh/registration candidate creation.
- If any command was dispatched, the precondition requires: `active_command_serial is None`; ledger length equals M; the last record is RESULT_ACCEPTED; the owner is the exact continuation owner; and the exact receiver is current.
- Otherwise refuse without mutation. For a known refresh candidate, apply the §10 `RefreshContainmentPending` disposition instead.
- Give the `_live_lease`-based registration and refresh entries the same continuation-owner path that `run_plan_step` has.
- Whether a zero-dispatch (in-task) operation may still publish is a manager or design question; design §3 says every slot is required. The mixed case must refuse either way.

**Closure test:**
- Kinds: EXECUTE, CONSISTENT_SNAPSHOT, SNAPSHOT_REGISTRATION, and REFRESH (neutral and changed), each with the default worker and with a distinct worker.
- Attempt publication or commit at QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT (called from inside the effect), SUCCESS_PENDING and QUIESCENT_SUCCESS.
- Each attempt must refuse with these unchanged: lease state, owner and completion; command state and ordinals; publications; cursors; registrations; coordinator count.
- `begin_migration` must keep refusing while the command can run.
- The accepted-continuation path must succeed exactly once.
- Extend `test_contract_source_rules.py` to enumerate the exact set of `_terminalize` callers and require the shared precondition in each. The current rule at lines 161–183 only checks a subset.

### [P2-2] Terminal leases are not absorbing: containment writers revive terminal records

**Location:**
- `_contain_command` (`lifetime_reference.py:1616-1641`) writes `record.state = CONTAINED` and `record.owner = containment_owner` without checking whether the lease is terminal.
- It is reached from `_validate_worker_barriers` (1607–1613), the `run_worker_effect` exception handler (531–533), `run_worker_cleanup` (632–636) and `_cancel_or_remove` (1664–1670).
- The lookup `_command_for` (1547–1566) resolves terminal records.

**Violated invariant:**
- W2 overlay §3.2, line 202: "terminal states | same terminal state only".
- Design §4.1, lines 197–201: there is "no edge back to a worker-owned state".
- One terminal release per operation.

**Reproduction:**
- **(a) Tail of P2-1(a).** The worker calls `run_effect(1)` and gets GENERATION_MISMATCH. Afterwards: `lease=contained completion=succeeded owner=containment cmd=contained count=0 terminal? False`. Then `close_outcome: nonquiescent ops [1] coordinator count 0`. After the exact stop, `complete_contained` returns `OPERATION_OUTCOME_CONFLICT`, and close stays nonquiescent.
- **(b) Independent of P2-1.** The schedule has `cleanup_steps=1`. The receiver dispatches and then cancels the queued command, giving CANCELLED_CONFIRMED with count 0. The receiver (not the worker) then calls `run_worker_cleanup(auth, 1)`. The call is refused, yet afterwards: `lease=contained terminal=False completion=cancelled_confirmed owner=containment cmd=contained exit=failure count=0`. Close is nonquiescent, and after stop `complete_contained` returns `OPERATION_OUTCOME_CONFLICT`.
- **(c) Tail of P2-1(c).** The same happens for REFRESH: `lease now contained terminal False completion succeeded`.

**Impact:**
- An operation that has already been released (count 0) reappears as non-terminal, permanently.
- Runtime close can never reach CLOSED, and membership never finalizes through close.
- The coordinator count disagrees with the lease table.
- No transition can repair this state.

**Required correction (bounded):**
- Every writer of lease state or owner must refuse or no-op on terminal records: `_contain_command`, `_cancel_or_remove`, the barrier handlers, `revoke_generation` and the `start_close` loop.
- A late worker call against a terminal operation may at most record a bounded diagnostic.

**Closure test:**
- A property test: for each terminal outcome (SUCCEEDED, REFUSED, CANCELLED_CONFIRMED, and delivery RETIRED), drive every worker, delivery and refresh entry with the old authorizations, receipts and candidates, from every task.
- Assert that lease state, completion, owner, charges and coordinator count stay unchanged, and that `close_outcome` reports CLOSED.

### [P2-3] `run_worker_cleanup` mutates state before validating state or identity

**Location:** `lifetime_reference.py:615-641`.
- There is no check of command state, active serial or terminal lease.
- The current-worker check runs inside the `try`.
- The `except BaseException` handler (632–636) commits a primary failure and contains the command.
- The `finally` block (640–641) consumes the cleanup step on every path that reaches the `try`.

**Violated invariant:**
- Design §7, row 1 (line 495): a wrong current worker at exit must be refused "before mutation; no … owner transfer or count change".
- Design §5.3, lines 398–423: cleanup follows the body and precedes stop.
- Brief line 156: "Every refusal must assert unchanged owner, lease/command state…"

**Reproduction:**
- **(a) Live command.** After effect 1, a third task calls `run_worker_cleanup(auth, 1)` and is refused. Afterwards: `lease=contained owner=containment cmd=contained exit=failure next_cleanup=2`. The true worker's `worker_exit_success` then returns `OPERATION_OUTCOME_CONFLICT`.
- **(b) Before dequeue.** The assigned worker runs cleanup on a QUEUED command: `OK`, `cmd=queued next_cleanup=2`. Cleanup ran before the body.
- **(c) Queue-removed command:** see P2-2(b).
- **Wrong-identity sweep.** I made 64 wrong-identity calls: 16 worker-exit entry points across 4 phases. This entry and the plan-step path in P2-5(a) are the only ones whose refusals mutate state.

**Impact:**
- Anyone holding the authorization (the dispatcher receives it) can contain another task's running command and destroy its success path.
- Cleanup can run outside the body → cleanup → stop order.
- Combined with P2-2, it revives terminal leases.

**Required correction (bounded):**
- Before entering the `try`, validate: the exact active command; a permitted state (body running, or contained before stop); a non-terminal lease; and the current worker.
- Never consume a step or commit a primary on a refusal.
- Refuse after stop and in QUEUED or QUEUE_REMOVED.

**Closure test:**
- Callers: a wrong (third) task, the issuing task, and the assigned worker.
- States: QUEUED, QUEUE_REMOVED, RUNNING_IDLE, EFFECT_IN_FLIGHT, CONTAINED, QUIESCENT_CONTAINED, RESULT_ACCEPTED, and a terminal lease.
- Every refusal must leave the full state vector equal.
- The §5.3 body/cleanup/cancel winner schedules must remain unchanged.

### [P2-4] Queued removal creates no exit receipt, so a queued delivery cancellation cannot enter §8 retirement

**Location** (`lifetime_reference.py`):
- `_cancel_or_remove`, lines 1653–1663: QUEUE_REMOVED is set with no receipt, and for a handoff it returns None.
- `request_worker_cancel`, lines 643–647.
- `_dispose_refresh`, lines 1092–1095.
- `begin_delivery_non_success`, lines 1248–1264: it accepts only an exit receipt, a lifecycle observation or a mapped failure as its cause.

**Violated invariant:**
- Design §4.1, line 166: `QUEUE_REMOVED(exit_receipt)`.
- Design §5.2, lines 329–332: queued removal creates QUEUE_REMOVED.
- Design §8, lines 580–589: every pre-commit non-success begins with a registry-owned cause record.

**Reproduction:**
- Queue two ranges, dequeue the first, and dispatch its command.
- The receiver calls `request_worker_cancel` while the command is QUEUED. Output: `cancel returns: None | lease contained registration active count 2 | retirement None | active exit None | command exit receipt None`.
- `delivery_retirement(lease)` and settlement both refuse.
- No registry-issued cause exists: `exit receipts [None] observations 0`.

**Impact:**
- An ordinary receiver cancellation wedges the subscription: the head is contained and the successors keep their permits.
- `RefetchRequired` cannot be reached without fabricating a setup fixture fact: a task-done observation or a worker failure that never happened.
- The wedge lasts until an unrelated close, migration or overflow retires the registration.
- The removed command also looks receipt-less to later writers; this is the precondition for P2-2(b).

**Required correction (bounded):**
- Queued removal must atomically create and return its exit receipt (kind cancel, effect knowledge NOT_BEGUN) for every operation kind.
- For a delivery, either apply §8 phase 1 in the same mutation, or make that receipt an accepted phase-1 cause.

**Closure test:**
- Queued cancel and queued task loss, for serial 1 and for a later serial, on EXECUTE and on a delivery with two queued ranges.
- The receipt must be returned, and replay must be idempotent.
- The delivery must reach RETIRING_HANDOFF, then stop, then `RefetchRequired`, with counts 2→1→0, delivered progress unchanged, and the successor never dequeued.

### [P2-5] Barrier-failure containment writes only the outer lease and ignores the command ledger and delivery grammar

**Location** (`lifetime_reference.py`):
- `_validate_barriers`, exception handler at lines 1524–1529.
- `_validate_queue_target`, lines 1746–1751.
- `revoke_generation`, lines 1476–1486.
- `accept_worker_result`, lines 720–724, which writes `record.state = RUNNING` unconditionally.
- `complete_contained`, lines 771–774.

**Violated invariant:**
- Design §4.1, lines 184–201: there is no success edge out of CONTAINED, and a fence moves QUIESCENT_SUCCESS to QUIESCENT_CONTAINED.
- Design §5.1, line 311: expiry closes the result and transfers to containment.
- Design §7, row 1: refusal before mutation.
- Design §8, lines 580–589: a handoff non-success goes through phase 1.

**Reproduction:**
- **(a) Wrong-task refusal mutates; illegal un-containment.** Distinct worker W calls `run_plan_step(LOWER)` and gets CONTEXT_OWNER_MISMATCH, yet afterwards `lease=contained owner=containment cmd=running_idle`. W keeps running effects and exits success: `lease=contained owner=escrow cmd=success_pending`. After stop, the receiver's accept gives `lease=running owner=continuation cmd=result_accepted`. This is an illegal CONTAINED→RUNNING edge, and publication then succeeds.
- **(b) Expiry between stop and accept.** `accept after expiry: context_expired lease=contained owner=containment cmd=quiescent_success count=1`. The containment owner's `complete_contained` then returns LEASE_INVALID ("not quiescent") until the receiver separately cancels.
- **(c) Handoff contained with no cause.** After expiry, `settle_delivery_success` leaves `('contained','active',2)`: the handoff is contained, the registration ACTIVE and the successor permit still counted. `revoke_generation` on a PUBLICATION_READY handoff gives `contained … retirement None registration active count 2 active_exit None`. The only cause the runtime can then present is the command's SUCCESS exit receipt.

**Impact:**
- Identity and presentation refusals mutate live operations.
- Lease×command pairs appear that are outside the closed grammar.
- An illegal un-containment edge exists.
- The containment owner cannot complete a quiescent contained operation on its own.
- Handoffs are contained without a cause record.

**Required correction (bounded):**
- Use one ledger-aware containment routine for every barrier failure.
- Refuse without mutation on presentation or identity refusals (CONTEXT_OWNER_MISMATCH, wrong owner).
- On genuine invalidation, move the active command together with the lease:
  - RUNNING_IDLE or EFFECT_IN_FLIGHT: contain with a receipt.
  - SUCCESS_PENDING: move to CONTAINED.
  - QUIESCENT_SUCCESS: move to QUIESCENT_CONTAINED.
- For a delivery, begin §8 phase 1 with a registry-owned cause.
- `accept_worker_result` must require the exact expected outer state.

**Closure test:**
- Inject each barrier failure (expiry, invalidation, registry epoch, binding, permit, local fence, queue target) at every command state and at PUBLICATION_READY.
- Assert that the lease×command pair stays inside the design grammar and that no CONTAINED→RUNNING edge occurs.
- The containment owner must complete after stop without help from the receiver.
- A delivery must reach retirement with counts conserved.
- A wrong-task presentation must leave the full state unchanged.

### [P2-6] Known refresh candidates made unusable by cursor divergence or an enqueue fence get no §10 disposition

**Location:**
- `_commit_refresh_record` lines 1013–1021 call `buffer_reference.commit_neutral` lines 456–457, which raises.
- Lines 1032–1037 call `create_candidate` lines 170–173, which raises.
- The `add_buffer` failure branch at lines 1045–1049 sets CONTAINED but keeps the caller as owner and keeps the candidate current.

**Violated invariant:**
- Design §10, lines 783–801: a candidate made unusable by cursor divergence, close, fence or migration gets an explicit disposition. If the worker is quiescent: terminal REFUSED, one release, `RefetchRequired`. Otherwise: containment and `RefreshContainmentPending`.
- Design §10, lines 811–813: no `RefetchRequired` is exposed before the refresh lease is terminal.
- W2 overlay §8.2 step 4: a refresh that reaches enqueue during drain discards its candidate and releases its lease.

**Reproduction:**
- **(a) Cursor divergence.** Two neutral candidates target revision 3. I commit the first. The second gives `('Refusal','refetch_required') lease2 running count 1 current candidates 1`, and a retry gives the same. The changed path behaves the same way: `l2 stale after l1 commit: refetch_required running count 2`.
- **(b) Enqueue during drain.** After `begin_drain` and before this participant's barrier, a changed commit raises GENERATION_MISMATCH and leaves `lease contained owner_is_containment False candidate still current True count 1 leaked CANDIDATE envelopes 1`. After the barrier, `begin_migration` returns `deadline_exceeded`. Only a retry disposes of it: `RefetchRequired lease refused count 0`.

**Impact:**
- A REFETCH_REQUIRED refusal is exposed while the refresh lease is still live and charged.
- An uncommittable candidate stays counted as current.
- A caller that treats the refusal as final leaks the charge, which blocks both close and migration.
- Leaked CANDIDATE records accumulate.

**Required correction (bounded):**
- Route every unusable-candidate outcome through `_dispose_refresh`: cursor divergence (neutral and changed), retired registration and fenced enqueue.
- `_dispose_refresh` applies terminal REFUSED, one release and `RefetchRequired` when quiescent, and the containment owner with `RefreshContainmentPending` otherwise.
- Never raise while the candidate is still current.
- Discard a failed CANDIDATE envelope in the same mutation.

**Closure test:**
- Two candidates with the same `previous`, on both the neutral and changed paths.
- Enqueue during DRAINING_OLD, both before and after the barrier.
- Assert exactly one terminal-or-containment owner, one eventual release, zero current candidates after the disposition, no CANDIDATE leak, and that `begin_migration` proceeds once the disposition commits.

### [P2-7] Terminal operation history is never discarded, and lookups scan lifetime history

**Location:**
- `_terminalize` (1704–1713) leaves every record in `_leases`.
- `_LeaseRecord.neutral_receipt` (line 120) is set at line 1024 and never cleared.
- These maps are never pruned: `_observations`, `_consumed_observations`, `_stops`, `_delivery_stops`, `_results` and `_failures` (lines 218–223).
- These lookups scan the full history: `commit_refresh` (969–971), `publish_refresh_buffer` (944–950), `_command_for` (1555–1566), `_command_for_exit` (1573–1577), `_lease_for` (1531–1535) and `_delivery_record` (1589–1592).
- In the buffer registry, `_buffers` (line 192) and `_registrations` are never pruned, yet `queued_for_resources` (305–309) and `replay_neutral` (469–474) scan them.

**Violated invariant:**
- Design §3, lines 127–128: the command ledger is discarded when the operation becomes terminal.
- Design §10, lines 739–750: retained neutral state is at most C spans, C replay entries and A current fields, and "no evicted candidate or receipt tombstone survives elsewhere."
- Design §10, lines 852–853: no single neutral-lineage mutation does work proportional to lifetime history.
- Brief line 146: resource counts and bounded mutation work.

**Reproduction:** one registration, R = 9.
```
history~   50: lease records=   51 terminal=   51 receipt identities retained in lease records=   50 replay ring=9 avg commit_refresh=   7.5 us
history~  249: lease records=  250 terminal=  250 retained=  249 replay ring=9 avg=  12.6 us
history~ 2049: lease records= 2050 terminal= 2050 retained= 2049 replay ring=9 avg=  70.1 us
history~ 6049: lease records= 6050 terminal= 6050 retained= 6049 replay ring=9 avg= 195.3 us
evicted first receipt via interface: RefreshRecordUnavailable | still retained in a terminal lease record: True
```

**Impact:**
- Memory and per-commit work grow without bound. This contradicts the accepted bounds that were the disposition of Consistency-2 P2-2 and Safety-1 P2-2.
- Evicted receipt identities survive outside the replay ring. The interface still answers uniformly, but the retained state does not match the design.

**Required correction (bounded):**
- At terminalization, discard the command ledger, results, failures, observation and stop entries, and candidate and receipt fields. Keep only a minimal, bounded settlement tombstone for exact replay.
- Index current candidates, authorizations and exit receipts in O(1) maps that the same mutations maintain.
- Prune RETIRED registrations and INVALID or CANDIDATE buffer records.

**Closure test:**
- Run at least 10·R neutral and changed commits plus repeated worker-backed operations.
- Assert: retained records ≤ live operations plus a bounded tombstone window; no receipt identity outside the ring; and constant per-commit lookup work, measured with an operation counter rather than wall-clock time.

### [P3-1] Membership is not bound to admission or acquisition, and leave does not reject acquisition

**Location:**
- `_admit` (`lifetime_reference.py:274-288`) only checks that `self._membership is None`.
- `_AdmissionRecord` (lines 64–71) records no membership or join serial.
- `coordinator.request_leave` (`generation_reference.py:130-135`) has no precondition.
- `acquire_shared` (223–236) ignores membership.
- `_runtime_has_obligations` (516–517) counts only generation permits, so `_finish_pending_leaves` (525–528) ignores queued buffer permits.

**Violated:**
- Design §9, lines 661–663: admission records and leases bind the exact membership and join serial.
- Design §9, lines 682–686: `request_leave` requires local drain and rejects new acquisition; final leave requires no queued delivery.

**Reproduction:**
- Call `request_leave` on an open runtime; it becomes LEAVE_PENDING.
- When any migration attempt closes, it becomes LEFT while `runtime resource still local_open`.
- It still admits (`AdmittedReadHandle`), registers and queues a buffer (count 1).
- The next attempt's required set is empty, so its barrier refuses, and the buffer cannot dequeue during drain. Result: `begin_migration: deadline_exceeded`.

**Consequence:** One premature leave creates a ghost participant that blocks every migration while it holds queued deliveries. This is P3 because reaching it requires calling the coordinator directly, bypassing the registry's own drain-then-leave path.

**Fix:** Bind membership and join serial into admission records and check them at admission and acquisition. Refuse `request_leave` without local drain, or make LEAVE_PENDING refuse acquisition. Count buffer permits as obligations.
**Test:** The sequence above must refuse at admission and at acquisition, and a later attempt must proceed.

### [P3-2] The deployment × phase product is not closed

**Location:**
- `begin_migration_effect` (`generation_reference.py:419-427`) has no phase guard.
- No method implements CURRENT→RETIRED.
- No test enumerates the product.

**Violated:**
- Design §11, lines 911–929: the closed product, which includes `CURRENT × NONE → RETIRED × NONE`.
- Design §11, line 942: each phase transition increments the serial exactly once.
- Design §12, lines 1045–1048: enumerate every legal edge and reject every other.
- The brief's Phase-proof row.

**Reproduction:** From `MIGRATING × EFFECT_BEGUN`, a second `begin_migration_effect()` returns OK and changes the phase serial and request (`!! OK changed=True`). Every other illegal pair I tried was refused with state unchanged.

**Consequence:** No pre-effect proof becomes valid again, but the product used as evidence is not the accepted product.

**Fix:** Guard EFFECT_BEGUN. Either implement the CURRENT→RETIRED edge or explicitly refuse it and record that refusal. Add an exhaustive state × operation property test.

### [P3-3] Replay fast paths answer non-matching inputs instead of refusing

**Location:**
- `worker_exit_failure`, lines 599–602: any failure of the same kind returns the existing receipt.
- `begin_delivery_non_success`, lines 1244–1245: returns the existing retirement before validating the cause.
- `accept_worker_result`, lines 714–715: returns the result to any task after acceptance.

**Violated:**
- Design §6, lines 427–434, and §8, lines 607–609: exact replay is idempotent, but a different failure or cause is a conflict and refuses.
- Design §5.1: only the receiver accepts.

**Reproduction:**
- A second, distinct failure returns the same receipt (`True`), and the recorded failure is still the first one.
- On a retiring handoff, a fake or cross-lease cause returns OK.
- Accept replay from the worker task returns `'v1'`.

**Consequence:** No state is mutated, but conflicts are indistinguishable from replays (a diagnosability problem), and closed results are returned to non-receivers.

**Fix:** Compare the presented failure, cause or task with the recorded tombstone before returning.
**Test:** Assert a conflict refusal with state unchanged.

## 2. Invariant analysis

**Attacks that held.** These support the closures in the tables above.
- **Reservation and containment.** A reservation is made before invocation. A nested or reentrant reservation refuses without consuming an ordinal. Both `BaseException` and `Exception` contain the command before the exception escapes. Unused ordinals are revoked, and the charge is retained until the exact stop.
- **Exit, stop and accept.** Accept before stop refuses. A wrong-task accept refuses with state unchanged. C1 and C2 are isolated:
  - dispatch before acceptance refuses;
  - a cross result and a cross stop do not apply to C2;
  - C1 effect, dequeue and failure attacks do not change C2.
  
  Dispatch beyond M refuses.
- **Cancel and task loss.** The suite covers QUEUED, RUNNING, SUCCESS_PENDING, QUIESCENT and ACCEPTED. My probe covered EFFECT_IN_FLIGHT. In every case: `BEGUN_UNCERTAIN` where an effect was in flight, no other effect can begin, a late return is discarded, nothing publishes, and release happens only after stop.
- **Wrong-identity sweep.** Of 64 worker-exit calls, 60 left the full state unchanged. The 4 that mutated are `run_worker_cleanup` in the queued phase (P2-3) and `run_plan_step` called by a non-context task presenting the current owner, in three phases (P2-5(a)). In two of those three phases the owner is the private escrow object, which I could only reach by observation. All 16 delivery wrong-identity calls left state unchanged.
- **FIFO.** All nine non-success causes conserve. Commit-first cannot be relabelled (suite). No count of zero was ever observed with an unsettled head: the count stayed ≥ 1 across 28 neutral commits behind an active head.
- **Neutral refresh.** The terminal transition and release are atomic. Replay returns the same identity. Evicted, fabricated and cross-registry identities all get a uniform `RefreshRecordUnavailable`.
- **Phase proof.** Proofs are exact to phase, serial, request and successor. Illegal pairs refuse with state unchanged, except P3-2.
- **Membership (suite).** An unjoined runtime cannot admit. Join during an attempt refuses. A LEAVE_PENDING member stays in the frozen attempt set.
- **Retained obligations.** The initial 18 and F1–F10 hold as tabled.

**Invariants the findings break.**
- **Fail-closed direction** (P2-1): publication and permit release are invented while work can still resume.
- **Recovery as a closed grammar:** the findings add new stuck states that the accepted semantics does not have. P2-2 is permanent. P2-4 lasts until close. P2-5(b) needs the receiver. P2-6(b) needs a retry.
- **Locks and races:** these are not modeled in the reference (deferred), but every finding above reproduces in a deterministic, single-threaded sequence.

## 3. Risks and next action

**Residual risks below the finding bar:**
- The reference still allows a zero-dispatch (in-task) publication. Design §3 says every slot is required. The manager should decide whether this remains a supported reference mode.
- A hard fence leaves continuation-owned leases RUNNING until their next barrier check. This is safe, because those barriers refuse publication and dispatch.
- Effect and cleanup diagnostics share one list, and excess records are dropped silently instead of refused.
- Unconsumed no-effect proofs and initial snapshot candidates accumulate. This is minor and is covered by P2-7's pruning.
- Production lock order, threads, async execution, durability and crash recovery remain deferred and are not claimed here.

**Next action:** The manager should consolidate P2-1 to P2-7, plus the P3 findings, into one disposition plan and one bounded source correction. That is correction 1 of 2, with no STOP, carrying the closure tests above. Then the originating State reviewer, or an accepted replacement, must re-run all four original sequences and every counterexample above on the new tuple.
