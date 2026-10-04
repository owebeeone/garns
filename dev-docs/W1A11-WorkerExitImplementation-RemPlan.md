# W1A11 worker-exit implementation — consolidated remediation 1

**Status:** manager verdict merge and proposed disposition. The consolidated
source correction is **not authorized** until the operator says so; builder
writes remain stopped.  
**Date:** 2026-10-04  
**Object:** candidate worker-exit internal contracts/reference implementation at
the approved filesystem tuple `W1A11-WorkerExitImplementation-MANIFEST-1.sha256`,
SHA-256 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544`
(117 entries); controlling DRAFT SHA-256
`e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`.
Implementation correction count 0 of 2; this plan would spend correction 1.

## Round 1 dispatch and filing

On 2026-10-04 the operator directed this round to Claude reviewers, half Fable
and half Opus 5.5, in place of the handoff's gpt-5.6-sol selection. Each
reviewer was a fresh Claude Code subagent (general-purpose, background, no
forked context). Each was told to verify its Prompt-2 SHA-256, read only its own
prompt and follow it exactly. The dispatch note named the model and the
relocation, and told the two closure reviewers that the original agents'
contexts were lost, so they run as disclosed replacements. Models below are
taken from the subagent transcripts.

| Filed report | Model | Agent | Window (UTC) | Verdict |
|---|---|---|---|---|
| `W1A11-WorkerExitImplementation-ReviewCode-1.md` (full, Code) | claude-fable-5-1 | adb356a0e780f57be | 10:43:58–11:16:37 | NO-GO: 8 P2, 7 P3 |
| `W1A11-WorkerExitImplementation-ReviewState-1.md` (full, State) | claude-fable-5-1 | aa3706a84bd592e4d | 10:44:03–11:24:50 | NO-GO: 6 P2, 3 P3 |
| `W1A11-WorkerExitImplementation-OriginCodeClosure-1.md` | claude-opus-5-5 | a8073836f689bbd2c | 10:44:10–11:13:58 | NO-GO: 7 P2, 3 P3 |
| `W1A11-WorkerExitImplementation-OriginStateClosure-1.md` | claude-opus-5-5 | a91ec0818e1431e95 | 10:44:15–11:19:18 | NO-GO: 7 P2, 3 P3 |

Filed SHA-256:

- ReviewCode-1 `d9047ed6376a8d237e24a9c126a6a48f16a231591c411a70434b86723d65cc55`
- ReviewState-1 `2ab17d09774b4f478ffdd37247cc1747ff12ced424141bf6adf06d73b291bc47`
- OriginCodeClosure-1 `d433a27ef452ad3ac3dbe294649c0c617fa8eae59ca99c2433fe5402c09f457e`
- OriginStateClosure-1 `d1add3b62da7c0e1564bf227878dedb62058292e23f00fd3eece65bbed1888c2`

Each report is its subagent's final message, extracted byte for byte from the
transcript. No manager text was added inside a report; as with the earlier
erratum, manager notes live in a separate document, here. The reports were held
outside the product tree until all four had finished, so no reviewer could see
another's current-round report. Each confirms that none existed in `dev-docs/`
during its run.

Manager notes on the testimony (verified; report text unchanged):

- ReviewCode-1 abbreviates two hashes wrongly. The Baseline map is
  `d95fab41…7318490a`, not `…f1a8c0c8`. The DRAFT is `…657ff2`, not `…57f2`;
  the full DRAFT SHA in its header is correct. It also counts the accepted design
  as 1,122 lines; the file has 1,121.
- ReviewCode-1 and ReviewState-1 each ran `git status --porcelain`. That command
  is read-only but not on the prompts' command list. OriginCodeClosure-1
  redirected one `shasum -c` output into the session scratchpad, outside the
  product tree, and disclosed it. OriginStateClosure-1 disclosed read-only use of
  `ls`, `awk`, `sort`, `uniq`, `cut`, `tr`, `head` and `date`.
- None of this touched the reviewed bytes. After the last report the manager
  re-verified the following:
  - MANIFEST-1 117/117, Inputs 31, Baseline 20 and ReadOnly 741;
  - Legacy 115/71/111/614, AcceptanceEvidence 13 and RelocationEvidence 8;
  - no bytecode or cache files;
  - root `b806c13`, garns `37b8dc8` and garns-rust `7e8e319` all clean.

  HandoffEvidence still differs only on the checkpoint entry, by design since
  the relocation.

## Verdict merge

**NO-GO.** There are no P0 or P1 findings.

- The four reports file 28 P2 and 16 P3 finding IDs.
- They merge into 13 blocking roots (IR1–IR13) and six non-blocking roots
  (IR14–IR19). The manager adds one pre-existing P3 (IR20).
- Every reviewer pre-commits to GO on a revision that resolves its P2s as
  specified.
- No reviewer classifies any root as architectural, and none needs an
  accepted-design, ownership or compatibility change. No STOP is triggered.

Severity rule: a P2 from any reviewer blocks until that reviewer verifies
closure. Where reviewers split on severity, the root takes the higher one, and
the manager downgrades nothing. The splits are:

- IR8: OriginCode P2, Code P3.
- IR9: OriginCode, Code and State P2; OriginState P3.
- IR10: OriginCode P2, Code P3.
- IR11, fence part only: OriginState P2, Code P3.
- IR12: Code P2, State P3; both closure reviewers noted it below the bar.
- IR13: OriginState P2; State and OriginCode noted it below the bar.

Accepted text settles two questions the reviewers left open.

**Zero-dispatch publication.** OriginStateClosure-1 called this a design
question. OriginCodeClosure-1's remedy would allow it, and ReviewCode-1 says it
must refuse. Design §3 (lines 117–121) fixes "an exact finite positive command
sequence" and says "Every slot is required … no caller may append, skip or
replace a slot." The reference therefore has no in-task publication mode, and
zero-dispatch publication must refuse. Retained fixtures that publish without a
command are adapted to drive the default command, not kept by legalizing an
empty schedule.

**Retention bounds.** ReviewState-1 recorded unbounded retention below the bar
as a declared single-process limit. The candidate record's limits section
declares thread and crash safety, not retention. The accepted design states
these bounds:

- §3 lines 127–128 discard the whole command ledger when the operation becomes
  terminal;
- §10 lines 748–750 let no evicted candidate or receipt tombstone survive
  outside the ring;
- §10 lines 852–853 forbid neutral-lineage work proportional to lifetime
  history.

IR13 is therefore P2, scoped to those bounds. The design sets no separate bound
on outer terminal-lease records, so IR13 does not demand one; the originating
State reviewer judges its closure.

**Blind convergence.** The reviewers worked in separate contexts, on two models
and two axes, and could not read each other's reports. These roots were found
independently:

| Found by | Roots |
|---|---|
| All four | IR9 (leave and membership obligations) |
| Three | IR1 (publication bypasses the ledger); IR4 (lease-only barrier containment: two P2, one P3); IR5 (queue removal and §8 retirement); IR7 (cleanup mutates before validating); IR11 (refresh disposition); IR15 (replay accepts a different input; ReviewState-1 also noted it below the bar) |
| Two | IR2 (registration atomicity); IR3 (wrong-task refresh commit; OriginStateClosure-1 P2-5(a) shows the same mechanism in `run_plan_step`); IR8 (later-slot dispatch); IR10 (protocol seam); IR14 (first open and join) |
| Filed once, seen by others | IR12 (filed by ReviewCode-1, seen by the other three); IR13 (filed by OriginStateClosure-1, seen by ReviewState-1 and OriginCodeClosure-1) |
| One reviewer | IR6, whose two facets come from different reviewers; IR16–IR19 |

The five historical stopped roots on MANIFEST-1:

| Root | Original counterexample | Root status |
|---|---|---|
| Worker exit (`ReviewState-3 P2-1`) | Closed by execution (OriginState, State) | OPEN: IR1, IR4, IR6, IR7, IR8 |
| Failed FIFO (`ReviewCode-3 P2-1`, `ReviewState-3 P2-2`, `FreshCodeClosure-2 P2-1`) | Closed for single-command deliveries under every cause (OriginCode, OriginState, State) | OPEN: IR5, IR6, IR8 (multi-command), IR2 (refetch baseline) |
| Participant lifecycle (`ReviewCode-3 P2-2`) | Reproductions A and B closed (OriginCode, State) | OPEN: IR9, IR10 |
| Neutral refresh (`ReviewState-3 P2-3`) | Closed (OriginState, State) | OPEN: IR11, IR13 |
| Stale phase proof (`OriginStateClosure-2 State-Closure-P2-1`) | Closed by OriginStateClosure-1 as the accepted fresh replacement; State concurs | Closed on MANIFEST-1; re-verify on the corrected tuple. IR17 is a separate P3. |

## Finding map

Every filed ID maps to exactly one root.

| Report | ID → root |
|---|---|
| ReviewCode-1 | P2-1→IR1 · P2-2→IR4 · P2-3→IR12 · P2-4→IR3 · P2-5→IR11 · P2-6→IR2 · P2-7→IR5 · P2-8→IR9 · P3-1→IR9 · P3-2→IR8 · P3-3→IR15 · P3-4→IR11 · P3-5→IR14 · P3-6→IR10 · P3-7→IR16 |
| ReviewState-1 | P2-1→IR6 · P2-2→IR7 · P2-3→IR9 · P2-4→IR5 · P2-5→IR9 · P2-6→IR11 · P3-1→IR4 · P3-2→IR18 · P3-3→IR19 |
| OriginCodeClosure-1 | P2-1→IR8 · P2-2→IR9 · P2-3→IR10 · P2-4→IR7 · P2-5→IR1 · P2-6→IR3 · P2-7→IR2 · P3-1→IR14 · P3-2→IR15 · P3-3→IR16 |
| OriginStateClosure-1 | P2-1→IR1 · P2-2→IR6 · P2-3→IR7 · P2-4→IR5 · P2-5→IR4 · P2-6→IR11 · P2-7→IR13 · P3-1→IR9 · P3-2→IR17 · P3-3→IR15 |

## Blocking roots — disposition and closure

All 13 are accepted for correction; none is disputed or waived. Each correction
carries out clauses the accepted design already states. Closure tests must run
real reference transitions and re-run every mapped reviewer counterexample.
Every refusal must assert the full unchanged-state vector the brief requires.

### IR1 — Generic terminal publication bypasses the command ledger (P2)

Mapped: ReviewCode-1 P2-1, OriginCodeClosure-1 P2-5, OriginStateClosure-1 P2-1.

**Defect.** In `lifetime_reference.py`, `run_plan_step` checks the ledger only
for `ITERATOR_HANDOFF`. `register_subscription`, `publish_refresh_buffer` and
`commit_refresh`/`_commit_refresh_record` never check it. Operations therefore
publish and release:

- with required slots skipped;
- with no command dispatched;
- while a command is still running;
- from inside an in-flight effect, after which migration began.

Design: §3; §4.1 (publication only after serial M is `RESULT_ACCEPTED`, with no
active command and a live receiver); §6; overlay §11.1.

**Correction.**

- Add one shared precondition on every non-delivery terminal success:
  EXECUTE/CONSISTENT_SNAPSHOT publication, registration, and neutral or changed
  refresh commit or publish.
- The precondition requires all of the following:
  - ledger length equals M;
  - the last record is `RESULT_ACCEPTED`;
  - no command is active;
  - the owner is the exact continuation owner;
  - the receiver is live and current.
- Otherwise refuse without mutation. For a known refresh candidate whose worker
  may resume, apply §10 `RefreshContainmentPending` instead.
- Zero-dispatch publication refuses (design §3). Adapt the retained fixtures to
  drive the default command.
- Give the `_live_lease`-based registration and refresh entries the
  continuation-owner path that `run_plan_step` has (OriginStateClosure-1
  P2-1(e)).

**Closure.**

- Test every kind (EXECUTE, CONSISTENT_SNAPSHOT, SNAPSHOT_REGISTRATION, REFRESH
  neutral and changed), each with the default worker and a distinct worker.
- Attempt publication or commit at zero dispatch, after C1 of M=2, and in the
  QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT (called from inside the effect),
  SUCCESS_PENDING and QUIESCENT_SUCCESS states.
- Each attempt refuses with lease, command, owner, completion, ordinals,
  publications, cursors, registrations and count unchanged.
- `begin_migration` keeps refusing while a command can run.
- After every slot is accepted, publication or commit succeeds exactly once,
  including registration and refresh.
- A source rule enumerates every `_terminalize` caller and requires the
  precondition (with IR16).

### IR2 — Registration publication is not atomic with terminal success and release (P2)

Mapped: ReviewCode-1 P2-6, OriginCodeClosure-1 P2-7.

**Defect.** `register_subscription` leaves the lease `PUBLISHING` and still
holding its permit, and `complete()` still offers `PUBLISHING → SUCCEEDED`. A
later receiver loss or cancel then ends a published registration `REFUSED`
while the registration keeps delivering.

Design: §2 row 2 (no separately callable releasing completion after
publication); §5.2; §6; §8. Candidate A16 and the DRAFT both claim this step is
atomic.

**Correction.** `register_subscription` records publication, registration,
terminal `SUCCEEDED` and the one release in a single mutation before it returns.
Drop the separate completion from `complete()` and from the `register()`
fixture.

**Closure.**

- After `register_subscription`, the lease is `SUCCEEDED` with count 0 in the
  same call.
- A later receiver loss or cancel is a no-op.
- `complete(SUCCEEDED)` is idempotent and `complete(REFUSED)` conflicts.
- A migration after the call sees a settled lease.
- A failure before the commit leaves no usable registration and exposes no rows.

### IR3 — Presentation-only refusals are treated as invalidation (P2)

Mapped: ReviewCode-1 P2-4, OriginCodeClosure-1 P2-6. OriginStateClosure-1
P2-5(a) shows the same mechanism in `run_plan_step`; it closes under IR4.

**Defect.** `_validate_barriers` contains the operation on every refusal,
including the `CONTEXT_OWNER_MISMATCH` raised when the wrong task calls.
`_commit_refresh_record` then sends every refusal to `_dispose_refresh`. As a
result, a wrong-task `commit_refresh` destroys the owner's live refresh.

Design: §10 says a presentation-only mismatch returns `RefreshCommitRefused`
with candidate, owner, lease and charge unchanged.

**Correction.**

- Establish presentation authority before barrier validation: the exact
  receiving task or context owner, and the exact lease owner.
- On a mismatch, refuse without mutation (`RefreshCommitRefused` for a refresh).
- Keep containment and disposition for genuine invalidation only: expiry,
  invalidation, fence, generation, migration marker, retirement, overflow and
  cursor divergence.

**Closure.**

- A wrong-task `commit_refresh` of changed and neutral candidates returns
  `RefreshCommitRefused`, with state, candidate count, coordinator count and
  cursors unchanged.
- The owner's retry then commits exactly once.
- Expiry and fence still follow §10.

### IR4 — Barrier-failure containment moves only the outer lease (P2)

Mapped: ReviewCode-1 P2-2, OriginStateClosure-1 P2-5, ReviewState-1 P3-1.

**Defect.** The `_validate_barriers` failure path writes only the lease state
and owner. As a result:

- The active command stays `QUIESCENT_SUCCESS`, with its result still held, or
  stays `QUEUED`. `complete_contained` refuses until the receiver also cancels.
- A contained lease can later be accepted back to `RUNNING`, because
  `accept_worker_result` writes `RUNNING` unconditionally.
- A delivery is left `CONTAINED` with no cause.

Design: §4.1 (fence edges into `CONTAINED`, `QUIESCENT_CONTAINED` and
`QUEUE_REMOVED`; no success edge out of `CONTAINED`); §5.1; §5.2; §7; §8.

**Correction.** Use one ledger-aware containment routine for every genuine
barrier failure:

- Move the active command together with the lease:
  - `RUNNING_IDLE` or `EFFECT_IN_FLIGHT` is contained with a receipt;
  - `SUCCESS_PENDING → CONTAINED`;
  - `QUIESCENT_SUCCESS → QUIESCENT_CONTAINED`, closing the result;
  - `QUEUED → QUEUE_REMOVED`, with the serial-sensitive disposition.
- For a delivery, begin §8 phase 1 with a registry-owned cause (shared with
  IR5).
- Transfer the operation to the containment owner.
- Presentation refusals never reach this routine (IR3).
- `accept_worker_result` requires the exact expected outer state.

**Closure.**

- Inject each barrier failure (expiry, invalidation, registry epoch, binding,
  permit, local fence and queue target) at every command state and at
  `PUBLICATION_READY`.
- The lease and command pair stays within the design grammar, and no
  `CONTAINED → RUNNING` edge exists.
- The containment owner completes after stop without the receiver.
- Deliveries reach retirement with counts conserved.
- These sequences pass: ReviewCode-1 P2-2 and P6, OriginStateClosure-1 P2-5
  (a)–(c), and ReviewState-1 probe I.

### IR5 — Queue removal issues no exit receipt, and registry-detected delivery non-success never enters §8 (P2)

Mapped: ReviewCode-1 P2-7, ReviewState-1 P2-4, OriginStateClosure-1 P2-4.

**Defect.**

- `_cancel_or_remove` sets `QUEUE_REMOVED` without a `WorkerExitReceipt`. For a
  handoff it returns `None` and leaves the lease `CONTAINED`. The registration,
  its successors and the active charge then stay frozen until an unrelated
  close, migration or overflow.
- Receiver cancel, revocation or expiry at `PUBLICATION_READY` or at
  `settle_delivery_success` likewise contain the lease without retirement.
- `begin_delivery_non_success` accepts the command's SUCCESS receipt as a
  non-success cause.

Design: §4.1 (`QUEUE_REMOVED(exit_receipt)`); §5.2; §8 (registry-owned cause
record; closed delivery grammar).

**Correction.**

- Queue removal atomically creates and returns a CANCEL exit receipt
  (`NOT_BEGUN`) for every operation kind.
- For `ITERATOR_HANDOFF`, the same mutation enters §8 phase 1, or the receipt
  becomes an accepted phase-1 cause.
- Registry-detected non-success at `PUBLICATION_READY` or at settle begins
  phase 1 with a registry-issued cause.
- `begin_delivery_non_success` refuses SUCCESS receipts and causes that do not
  belong to this lease.

**Closure.**

- Run queued cancel and queued task loss, at serial 1 and at a later serial, on
  EXECUTE and on a two-range delivery. The receipt is returned and replay is
  idempotent.
- The delivery reaches `RETIRING_HANDOFF` and its successors are released
  exactly once. After stop, `settle_delivery_non_success` returns
  `RefetchRequired`. Counts go 2→1→0, delivered progress is unchanged and the
  successor is never dequeued.
- The same holds for expiry, invalidation and `revoke_generation`, both at
  `PUBLICATION_READY` and at settle.
- `begin_delivery_non_success(lease, success_receipt)` refuses without
  mutation.

### IR6 — Containment writers overwrite terminal and retiring states (P2)

Mapped: OriginStateClosure-1 P2-2, ReviewState-1 P2-1.

**Defect.**

- `_contain_command` writes `CONTAINED` over a terminal lease. It is reached
  from worker barriers, the effect handler, cleanup and cancel. The released
  operation is revived permanently: close never completes and no transition
  repairs it.
- `revoke_generation` overwrites `RETIRING_HANDOFF`.
  `settle_delivery_non_success` requires that label, so it becomes unreachable
  for good, and the permit, the registration and migration all stay stuck.

Design: overlay §3.2 (terminal states are absorbing); design §4.1 (no edge back
to a worker-owned state); §8 (phase two must stay reachable).

**Correction.**

- Every writer of lease state or owner treats terminal leases as absorbing.
  That covers `_contain_command`, `_cancel_or_remove`, the barrier handlers,
  `revoke_generation` and the `start_close` loop. A late call may at most record
  a bounded diagnostic.
- A lease with `delivery_retirement` set stays in `RETIRING_HANDOFF`. Phase two
  keys on the retirement record, not on the outer label.

**Closure.**

- Terminal revival (OriginStateClosure-1 P2-2 (a)–(c)):
  - For each terminal outcome (SUCCEEDED, REFUSED, CANCELLED_CONFIRMED, delivery
    RETIRED), drive every worker, delivery and refresh entry with the old
    authorizations, receipts and candidates, from every task.
  - State, completion, owner, charges and count stay unchanged, and
    `close_outcome` reports CLOSED.
- Retiring overwrite (ReviewState-1 probe B):
  - Take a retiring handoff, caused both by failure and by receiver loss. Run
    `revoke_generation`, then worker and delivery stop, then
    `settle_delivery_non_success`.
  - Settlement returns `RefetchRequired`. Count is 0, the registration is
    `RETIRED`, delivered progress is unchanged, the subscription reports
    `CLOSED` and `begin_migration` succeeds. Replay is read-only.

### IR7 — `run_worker_cleanup` validates inside its containment scope (P2)

Mapped: OriginCodeClosure-1 P2-4, OriginStateClosure-1 P2-3, ReviewState-1 P2-2.

**Defect.** The current-worker check sits inside the `try`. Its refusal is
caught by `except BaseException`, which commits a primary FAILURE and contains
the command, and `finally` consumes the step. As a result:

- a wrong-task call kills a queued or running command;
- cleanup runs on a `QUEUED` command;
- re-entrant cleanup during an effect records `NOT_BEGUN` for an effect that
  ran.

Design: §7 row 1 (refusal before mutation); §4.1; §4.2; §5.3.

**Correction.**

- Before the `try`, validate:
  - the exact active serial and authorization;
  - the current assigned worker;
  - the next step;
  - a legal state: the body running with no active reservation, or the §5.3
    contained-before-stop case. Never `QUEUED`, `QUEUE_REMOVED`,
    `EFFECT_IN_FLIGHT`, after stop, or on a terminal lease.
- Refuse without mutation and without consuming the step.
- Only a raised cleanup action becomes a primary.
- Derive effect knowledge from the reservation history: `BEGUN_UNCERTAIN` while
  a reservation is unreturned.

**Closure.**

- Callers: the wrong task, the issuing task and the assigned worker.
- States: QUEUED, QUEUE_REMOVED, RUNNING_IDLE, EFFECT_IN_FLIGHT, CONTAINED,
  QUIESCENT_CONTAINED, RESULT_ACCEPTED and terminal.
- Every refusal leaves lease and command state, owner, ordinals, exit facts,
  `next_cleanup_step` and count unchanged, and the genuine worker then proceeds.
- Re-entrant cleanup inside an effect refuses, and the effect returns
  `RETURNED`.
- A cleanup primary after a reserved, unreturned effect records
  `BEGUN_UNCERTAIN`.
- The §5.3 winner schedules are unchanged.

### IR8 — Later-slot dispatch skips outer-lease validation (P2)

Mapped: OriginCodeClosure-1 P2-1, ReviewCode-1 P3-2.

**Defect.** For serial > 1, `dispatch_worker` checks only that the prior record
is `RESULT_ACCEPTED`. It then sets the owner and sets the outer state to
`QUEUED` unconditionally. As a result:

- a cancelled operation resumes and publishes `SUCCEEDED`;
- a retiring delivery runs effects during drain and its charge is stranded for
  good.

Design: §4.2 (dispatch under the exact continuation owner; a contained command
ends the schedule); §4.1 (a later `QUEUED` is private to the ledger while the
outer lease stays `RUNNING`); §5.2; §8.

**Correction.** For every serial, check before mutating:

- the lease is non-terminal and not `CONTAINED`, `RETIRING_HANDOFF`,
  `PUBLICATION_READY` or `PUBLISHING`;
- no delivery retirement, candidate or settlement exists;
- serial 1 dispatches from `ACQUIRED` or `RUNNING` under the current caller
  owner;
- serial > 1 dispatches from `RUNNING`, under the exact continuation owner, with
  a live receiver.

Later slots keep the outer lease `RUNNING`.

**Closure.**

- M=2 EXECUTE: accept C1, cancel, then dispatch C2. The dispatch refuses with
  state, owner, ledger, count and publications unchanged. `complete_contained`
  then gives REFUSED with count 0.
- M=2 delivery retired after C1, separately by migration barrier, close, fence,
  overflow and receiver loss: C2 dispatch refuses each time. Stop plus
  specialized settlement releases once, and migration proceeds.
- After a legal C2 dispatch the lease is `RUNNING` and C2 is `QUEUED`.

### IR9 — Membership leave is not bound to the runtime's obligations or close outcome (P2)

Mapped: OriginCodeClosure-1 P2-2, ReviewCode-1 P2-8, ReviewCode-1 P3-1,
ReviewState-1 P2-3, ReviewState-1 P2-5, OriginStateClosure-1 P3-1.

**Defect.**

- The coordinator decides `LEFT` from generation permits alone. Buffer
  permits, local drain, `LOCAL_CLOSED` and unresolved A7 identities are all
  invisible to it.
- Admission and acquisition do not bind membership.
- `close_outcome` commits the local close and then calls a finalize step that
  can refuse.
- A repeated `start_close` raises.

This is reachable through the registry alone. A runtime with an unresolved A7
identity became `LEFT` after a no-effect reopen (OriginCodeClosure-1 P2-2(a)).
A `LEFT` runtime keeps acquiring and blocks migration.

Design §9:

- admissions and leases bind membership and join serial;
- `request_leave` requires local drain and rejects new acquisition;
- `finalize_leave` is allowed only at `LOCAL_CLOSED`, with no permit, delivery,
  worker, containment, close work or unresolved obligation;
- a `LEAVE_PENDING` member stays in the frozen attempt.

Overlay §4 and A16 require validate-then-commit.

**Correction.** Make final leave one registry-witnessed transition:

- The registry presents an exact sealed close-quiescent record, only on a
  CLOSED outcome.
- `finalize_leave` and `_finish_pending_leaves` require that record.
- Buffer permits and exchanges are attributed to the member and counted.
- `request_leave` requires the registry's drain or fence and stops new
  acquisition.
- Admissions and leases bind membership and join serial, and refuse after
  `LEFT`.
- `close_outcome` validates before mutating. During an attempt it returns
  CLOSED with membership `LEAVE_PENDING`, and the leave is finalized when the
  attempt closes.
- `start_close` skips `request_leave` when the membership is already pending or
  left, so a repeated close is a no-op.

**Closure.**

- An UNRESOLVED runtime stays `LEAVE_PENDING` across reopen, cutover and
  recovery until CLOSED, and stays in the next attempt.
- Direct finalize of an open runtime holding a queued permit refuses, with
  membership, count and queue unchanged.
- `request_leave` without drain refuses.
- A `LEFT` membership cannot admit, acquire, add buffers or exchange them.
- Close during an attempt returns CLOSED, and the member becomes `LEFT` after
  the attempt.
- A repeated close is a no-op.
- Later attempts require exactly the live members and reach zero.
- These sequences pass: OriginCodeClosure-1 P2-2 (a)–(c); ReviewCode-1 R5 and
  M1; ReviewState-1 C, C2, E and E2; OriginStateClosure-1 P3-1.

### IR10 — The formal coordinator seam lacks the membership and proof members (P2)

Mapped: OriginCodeClosure-1 P2-3, ReviewCode-1 P3-6.

**Defect.** `SharedGenerationCoordinator` in `lifetime.py` is unchanged from the
baseline.

- It omits `join_runtime`, `request_leave`, `finalize_leave` and
  `close_unjoined`, the §11 proof and effect-begun calls, and other members the
  registry calls.
- `begin_migration` still returns `None`.
- The registry is typed to the concrete class.

A future coordinator could therefore omit membership and phase proof and still
conform. This is the protocol half of the correction that `ReviewCode-3 P2-2`
required. Design: §9; §11; §13, where `lifetime.py` holds the provisional
internal seams. `lifetime.py` is one of the twenty writable files.

**Correction.**

- Add the §9 membership set, the §11 proof and effect-begun transitions, and
  every coordinator member the registry calls, with exact identity types.
- Correct the return type of `begin_migration`.
- Type the registry against the protocol, or add a conformance check.

**Closure.**

- `ReferenceGenerationCoordinator` satisfies the protocol.
- A stub missing any membership or proof member fails `isinstance`.
- A source rule asserts that the protocol's members equal the accepted call
  shapes, and that every `self._coordinator.<name>` call site is a protocol
  member.

### IR11 — Unusable refresh candidates get no §10 disposition (P2)

Mapped: ReviewCode-1 P2-5, ReviewState-1 P2-6, OriginStateClosure-1 P2-6,
ReviewCode-1 P3-4.

**Defect.**

- Cursor divergence, with two candidates from one cursor, raises
  `REFETCH_REQUIRED` from `commit_neutral` or `create_candidate`, outside the
  disposition path. The lease stays `RUNNING` and charged, and its candidate
  stays current.
- A changed commit during `DRAINING_OLD`, before this participant's barrier,
  raises after creating a CANDIDATE record. The lease is left `CONTAINED` but
  still owned by the caller.

Design: §10 (an explicit disposition for cursor divergence, close, fence and
migration; no `RefetchRequired` before the refresh lease is terminal); overlay
§8.2 step 4.

**Correction.**

- Inside the guarded validation, before `commit_neutral`, `create_candidate` or
  `add_buffer`, check:
  - lineage (`previous == produced_through`);
  - registration state;
  - coordinator `CURRENT`.
- Route every unusable outcome through `_dispose_refresh`.
- Never raise while the candidate is current.
- Discard a failed CANDIDATE record in the same mutation.

**Closure.**

- Two or three refreshes from one cursor, neutral and changed: each later commit
  returns `RefetchRequired` with the lease `REFUSED` and the count down once,
  and replay returns `RefreshRecordUnavailable`.
- The worker-backed variant returns `RefreshContainmentPending` until
  `settle_contained_refresh` releases once.
- Enqueue during `DRAINING_OLD`, before and after the barrier, returns
  `RefetchRequired` with the lease `REFUSED`, count 0 and no orphan record.
- `begin_migration` proceeds after the disposition.

### IR12 — Hard fence leaves accepted, unpublished leases running (P2)

Mapped: ReviewCode-1 P2-3. ReviewState-1 probe F and the two closure reviewers'
residual notes observe the same state.

**Defect.** When a worker authorization is present, `start_close(hard=True)`
only revokes it. `_revoke_worker_authorization` ignores `RESULT_ACCEPTED`, so a
continuation-owned lease stays `RUNNING`. Neither the containment owner nor the
former owner can terminalize it, and close stays NONQUIESCENT until the
receiving task acts again.

Overlay §6: from its linearization point, a hard fence changes the selected
resource to `LOCAL_FENCED` "and its remaining leases to contained/revoked
ownership". Design §5.2.

**Correction.** After revoking, move every non-terminal lease that is not
already containment-owned and not a retiring delivery to `CONTAINED` under the
containment owner, through the IR4/IR6 routine.

**Closure.**

- With C1 accepted and continuation-owned, a hard fence leaves the lease
  `CONTAINED` and containment-owned.
- `complete_contained` succeeds without the receiver; count is 0 and
  `close_outcome` reports CLOSED.
- ReviewState-1 probe F passes.

### IR13 — Terminal history is kept and scanned without bound (P2)

Mapped: OriginStateClosure-1 P2-7.

**Defect.**

- Terminal leases keep their command ledgers, results, failures, observations,
  stops and neutral receipts.
- `commit_refresh`, `publish_refresh_buffer` and the command, exit and lease
  lookups scan all of them. Per-commit cost rose from 7.5 µs to 195 µs over
  about 6,000 operations.
- An evicted neutral receipt survives in a terminal lease record.

Design: §3 lines 127–128; §10 lines 748–750 and 852–853; the brief's
neutral-refresh row ("resource counts and bounded mutation work").

**Correction.**

- At terminalization, discard the command ledger and its per-command maps.
- Clear candidate and receipt fields, keeping only the tombstone state the
  design names for exact replay.
- Index current candidates, authorizations and exit receipts so that lookups do
  constant work.
- Prune retired registrations and invalid or failed-candidate buffer records.
- Do not add a configurable history limit (design §10 line 746).

**Closure.**

- Run at least 10·R neutral and changed commits plus repeated worker-backed
  operations.
- No ledger or per-command record outlives its operation.
- No receipt identity survives outside the replay ring.
- Per-commit lookup work is constant, measured with an operation counter rather
  than wall-clock time.
- Outer terminal-lease records are not counted, because the design sets no bound
  on them.

## Non-blocking roots

P3s never block and never force a correction round.

- IR14–IR19: fix them inside correction 1 where they sit on paths it already
  rewrites. Any left open is recorded and assigned to W3, like the existing W1
  P3.
- IR16 belongs in correction 1. Design §11–§12 mandate its enumeration tests,
  and those tests would have caught most of the defects above.

| Root | Mapped | Defect | Correction and closure test |
|---|---|---|---|
| IR14 | ReviewCode-1 P3-5, OriginCodeClosure-1 P3-1 | `join_runtime` refuses `ACTIVE_UNUSED`, while `first_lifetime_open` activates with zero members; the right to withdraw an unused activation is lost | The first join in `ACTIVE_UNUSED` activates and joins in one call; withdrawal stays available until then |
| IR15 | ReviewCode-1 P3-3, OriginCodeClosure-1 P3-2, OriginStateClosure-1 P3-3 | Replay fast paths treat a different failure or cause, or a non-receiver, as an exact replay; a late success leaves no diagnostic | Compare the recorded failure, cause and task; a mismatch refuses with `OPERATION_OUTCOME_CONFLICT` and state unchanged; a late return records a bounded diagnostic |
| IR16 | ReviewCode-1 P3-7, OriginCodeClosure-1 P3-3 | Source rules pin two of nine terminalizers and omit `run_worker_cleanup`; nothing enumerates the phase product or command-state edges; several §7 traces are missing | Assert the exact terminalizer and worker-entry sets; enumerate every legal edge and pair and reject the rest; add the named traces; the new tests fail on MANIFEST-1 |
| IR17 | OriginStateClosure-1 P3-2 | A second `begin_migration_effect` from `EFFECT_BEGUN` succeeds and changes serial and request; `CURRENT → RETIRED` is neither implemented nor refused | Guard `EFFECT_BEGUN`; implement or explicitly refuse the edge; add an exhaustive state × operation test |
| IR18 | ReviewState-1 P3-2 | `dequeue_buffer` validates the handoff schedule after the permit exchange and dequeue; a bad trusted schedule orphans a permit and lets close report CLOSED | Validate before the exchange, or roll it back; an invalid schedule leaves count, permits, head and registration unchanged |
| IR19 | ReviewState-1 P3-3 | Serial-1 queue removal after plan work is labelled `CANCELLED_CONFIRMED` | Condition the label on no prior plan work; test both labels |

### IR20 — `tools/check.py` G10 fails on the frozen object (manager, P3, pre-existing)

**Defect.** The corpus-vocabulary regex at `tools/check.py:589` matches "author"
in `src/garns/backends/contracts/semantic.py:98` ("reserved key aliases cannot
be visible author fields").

- The line came from the stopped ContractAmendment.
- No reviewer could see it: the prompts forbid running `tools/check.py`, and
  `check_product.py` omits G10.
- It does not affect this object's contract behavior or its acceptance gates.
- However, the product gate fails on the current tree, and the committed
  `gate-report.json` predates the line.

**Disposition.** `semantic.py` and `tools/check.py` are both inside the ReadOnly
741 guard; the brief keeps result-role semantics read-only. Correction 1
therefore cannot touch them.

Recommended: reword the message (for example "…visible fields") rather than
weaken the regex. Make the change in the first package authorized to write
`semantic.py`, before the next `tools/check.py` gate run. Folding it into
correction 1 instead would need an explicit operator extension of the write
allowlist.

## Correction shape and boundary

This is one consolidated patch, never a series. The thirteen roots reduce to
seven shared mechanisms; building each once keeps the patch cohesive:

1. One publication precondition for every non-delivery terminal success (IR1,
   IR2).
2. One containment routine (IR3–IR6, IR12) that:
   - separates presentation refusals from invalidation;
   - leaves terminal and retiring leases alone;
   - moves lease, command and result together;
   - routes deliveries into §8 phase 1;
   - transfers the operation to the containment owner.
3. Validate-before-mutate checks on worker entries (IR7, IR8).
4. Refresh disposition routing (IR11).
5. Registry-witnessed leave and membership binding (IR9).
6. A complete coordinator protocol (IR10).
7. Bounded retention with indexed lookups (IR13).

The boundary is unchanged:

- Writes are limited to the brief's twenty writable paths and its three new
  ones.
- `lifetime_reference.py` stays the sole mutable lease and worker owner. Buffer
  state remains its subledger and the coordinator remains the deployment domain.
- The file's 1,780-line cohesion exception covers growth from these
  corrections. Record the new size and reasoning in the implementation record.
  Do not add a second owner or split the file by line count.
- ReadOnly 741, Inputs 31 and the Legacy maps stay byte-identical.
- Retained tests are adapted, never deleted, when entry points change. IR1
  changes every fixture that publishes without a command.
- No helpers, dependencies, network, services, Git/GWZ or `tools/check.py` in
  the live tree, and no self-closure.

## Next steps

1. Operator decisions:
   - authorize correction 1 under this plan;
   - choose the builder's model;
   - decide where IR20 is fixed.
2. Before any write, the manager:
   - preserves MANIFEST-1's exact files plus the manifest under
     `W1A11-WorkerExitImplementation-Revision1/`, so MANIFEST-1 still verifies
     from inside that directory after live edits (lane precedent);
   - pins this plan, the four reports and the controls in a RemInputs map.
3. One builder writes the single patch, stops writing and returns complete
   testimony, filed verbatim as DRAFT-2.
4. The manager:
   - reproduces the focused, full and product runs on Python 3.11–3.14, with
     bytecode disabled and warnings visible;
   - AST-parses the changed sources;
   - verifies every guard;
   - pins MANIFEST-2.
5. Round 2:
   - Fresh peer-blind full Code and State reviews, because the correction
     changes call graphs and the formal coordinator protocol.
   - Originating closure of every round-1 finding by the reviewer who filed it.
     The four round-1 agents can be continued with their context intact while
     this session lasts; otherwise use disclosed replacements.
6. Correction 2 is the last one allowed. An architectural root, or any
   accepted-design, ownership or compatibility change, stops the lane for the
   operator.
