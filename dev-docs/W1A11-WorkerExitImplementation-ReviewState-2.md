The tuple held at END and I have read every control. Here is my report.

# W1A11-WorkerExitImplementation round 2 (correction 1 of 2) — STATE-AXIS REVIEW

**Review object:** The corrected worker-exit internal contracts and deterministic reference implementation after consolidated source correction 1 of 2.
- Approved filesystem tuple: `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256`, SHA-256 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720`, 128 entries. This is not a Git commit.
- Controlling DRAFT: `dev-docs/W1A11-WorkerExitImplementation-DRAFT-2.md` at `cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30`.
- Controlling disposition: `dev-docs/W1A11-WorkerExitImplementation-RemPlan.md` at `a2d625e1c695b231b3e264470cbd61dfef1ed628744ec25255e59d37e366b2a1`.
- Status: unaccepted candidate; implementation correction count 1 of 2.

**Baseline:**
- Round-1 object: the Revision1 archive `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns`. Its MANIFEST-1 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` verified 117/117 from inside the archive.
- Archived 20-file writable baseline: map `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a`, 20/20.
- All sources were read directly from the filesystem at `/Volumes/projects/limbo/garns-wz/garns`, never from Git HEAD. Changed files were compared with `diff`/`cmp` against the Revision1 archive.
- Comparison probes were run inside the archive with its own `src` (`garns.__file__` confirmed to resolve into the archive).

**Date:** 2026-10-05

**Axis:** State — durable-state semantics and adversity. I attacked state machines and restart legality, write ordering, kill points between writes, races and lock scope, fail-closed direction, and recovery states as a closed grammar (hunting new stuck states). Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block (P2-1, P2-2). Two P3 findings are filed and do not block. There are no P0 or P1 findings.
- No NEW ARCHITECTURAL root cause was found. All four findings are bounded source repairs inside the accepted single-lifetime-owner architecture.
- None needs an accepted-design, ownership or compatibility change, so no STOP is triggered.
- **I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified below**, with their closure tests, on a new frozen tuple.

---

## Prior-finding retrace table

"Re-run" means I executed the original reproduction, or its exact sequence through the corrected API, myself on this tuple, using inline `-B` stdin probes with the repository's fixtures. Statuses are my State-axis retrace. Originating closure remains the originating reviewers' call.

| Root (RemPlan) | Mapped round-1 IDs | Original counterexample re-run on this tuple | Status |
|---|---|---|---|
| IR1 publication precondition | ReviewCode-1 P2-1; OriginCodeClosure-1 P2-5; OriginStateClosure-1 P2-1 | **P1a** (M=2; publish after C1 only): refused `lease_invalid`, vector unchanged. After C2 it publishes once: `succeeded count 0 pubs 1`.<br>**P1b** (zero dispatch): refused.<br>**OriginState P2-1(a)** (publish while `running_idle`): refused, unchanged.<br>**(b)** publish and `begin_migration` issued from inside effect 1: `lease_invalid` / `deadline_exceeded`; the effect returns; count 1, publications 0.<br>**(c)/(d)** distinct worker W still running, neutral and changed: `commit_refresh` and `publish_refresh_buffer` both return `RefreshCommitRefused`, unchanged.<br>**(e)** `register_subscription` while `running_idle`: refused, unchanged. | CLOSED |
| IR2 atomic registration | ReviewCode-1 P2-6; OriginCodeClosure-1 P2-7 | **R4**: count is 0 in the same call; `begin_drain` + barrier + `begin_migration` succeed.<br>**P2-7**: after publication, cancel and task loss are no-ops (`succeeded`, count 0). `complete(SUCCEEDED)` replays; `complete(REFUSED)` gives `operation_outcome_conflict`. | CLOSED |
| IR3 presentation-only refusals | ReviewCode-1 P2-4; OriginCodeClosure-1 P2-6 (OriginStateClosure-1 P2-5(a) via IR4) | **R1** wrong-task `commit_refresh`, neutral and changed: `RefreshCommitRefused` with (lease facts, count, candidates, cursors) unchanged. The owner's retry commits once.<br>**P2-5(a)**: W calls `run_plan_step(LOWER)` presenting the owner and gets `context_owner_mismatch`, unchanged; the command stays `running_idle`. | CLOSED |
| IR4 one containment routine | ReviewCode-1 P2-2; OriginStateClosure-1 P2-5; ReviewState-1 P3-1 | **P2/P2b** (expiry or invalidation between stop and accept): accept refused; command `quiescent_contained`; `complete_contained` gives REFUSED, count 0, with no receiver cancel.<br>**P6** (expiry at dequeue): serial 1 → `cancelled_confirmed`, serial 2 → `refused`, count 0.<br>**P2-5(c)** (expiry at `settle_delivery_success`; `revoke_generation` at PUBLICATION_READY): `retiring_handoff`, registration `retiring_refetch`, count 1. Settle gives `RefetchRequired`, count 0, delivered 0.<br>**Probe I**: same result as P2.<br>**EFFECT_IN_FLIGHT row** (cancel, task loss, failure, façade revoke): `begun_uncertain`, containment owner, count 1. | CLOSED |
| IR5 queue removal / registry-detected non-success | ReviewCode-1 P2-7; ReviewState-1 P2-4; OriginStateClosure-1 P2-4 | **Probe D / D1** (queued delivery cancel): returns a `WorkerExitReceipt`; lease `retiring_handoff`, command `queue_removed`, count 2→1. Replay returns the same receipt, and `begin_delivery_non_success(receipt)` is the exact replay. Settle gives `RefetchRequired`, count 0, delivered 0. Successor dequeue refused.<br>**D3** (task loss), **G1** (revoke), **G2** (cancel) at PUBLICATION_READY, and **D4** (expiry at settle): each enters retirement with count 1. A success receipt presented as cause is refused. | CLOSED |
| IR6 terminal absorption / retiring survival | OriginStateClosure-1 P2-2; ReviewState-1 P2-1 | **Sweep**: SUCCEEDED / REFUSED / CANCELLED_CONFIRMED / delivery RETIRED, each × (receiver, third task) × 15–17 worker, delivery, close and revocation entries. (Facts, count, publications, cursors) stayed unchanged and close reported `closed`.<br>**Probe B** (failure-caused and receiver-loss-caused): after `revoke_generation` the lease stays `retiring_handoff`. Settle gives `RefetchRequired`, count 0, registration `retired`, cursors (2,0). The subscription closes `closed`, `begin_migration` succeeds, and replay is read-only. | CLOSED (one entry crashes on terminal records: P3-1) |
| IR7 cleanup validate-before-mutate | OriginCodeClosure-1 P2-4; OriginStateClosure-1 P2-3; ReviewState-1 P2-2 | **A1** (receiver cleanup on QUEUED) and **A1b** (on RUNNING_IDLE): refused with the full vector unchanged; the genuine worker then dequeues.<br>**A2** (re-entrant cleanup inside an effect): refused; the effect returns and knowledge is `returned`.<br>**P2-3(a)** (third-task cleanup): refused, unchanged; genuine success OK.<br>**P2-3(b)** (cleanup on QUEUED): refused, step stays 1. | Original counterexamples CLOSED. Root OPEN: **P2-2** (same-step cleanup re-entry, pre-existing, not closed by the rewrite). |
| IR8 later-slot dispatch | OriginCodeClosure-1 P2-1; ReviewCode-1 P3-2 | **N1** (cancel after C1, then dispatch C2): refused `lease_invalid`, unchanged; `complete_contained` gives REFUSED, count 0.<br>**N2** (delivery retired after C1 by migration barrier, close, fence, overflow, or receiver loss): C2 dispatch refused with the vector unchanged; settle brings count to 0; migration proceeds.<br>**P4**: after C2 dispatch the outer lease stays `running` and C2 is `queued`. | CLOSED |
| IR9 registry-witnessed leave / membership binding | OriginCodeClosure-1 P2-2; ReviewCode-1 P2-8, P3-1; ReviewState-1 P2-3, P2-5; OriginStateClosure-1 P3-1 | **C / R5**: direct `request_leave` → `local_resource_draining` and `finalize_leave` → `lease_invalid`, both with a queued buffer; membership stays `joined`.<br>**C2**: refused.<br>**E / M1**: close during an attempt returns `closed` with the member `leave_pending`, then `left` at reopen.<br>**E2**: repeated close is a membership no-op.<br>**O2–O4**: the UNRESOLVED runtime stays `leave_pending` across no-effect reopen, cutover and full-rollback recovery, stays in later attempts, and becomes `left` after a CLOSED outcome.<br>**OriginState P3-1**: a `left` member's acquire, admit and `request_leave` all refuse. | Original counterexamples CLOSED. Root OPEN: **P2-1** (introduced into the witnessed-leave mechanism). |
| IR10 coordinator protocol | OriginCodeClosure-1 P2-3; ReviewCode-1 P3-6 | **R7**: a stub missing members fails `isinstance`; the registry rejects it with `TypeError`; the reference conforms. The source rule enforces that registry call sites are a subset of protocol members. | CLOSED |
| IR11 refresh disposition | ReviewCode-1 P2-5, P3-4; ReviewState-1 P2-6; OriginStateClosure-1 P2-6 | **Probe H** (three refreshes from one cursor): the first neutral commits; the later changed and neutral commits give `RefetchRequired`, `refused`, count 3→2→1→0, candidates 0; replay `RefreshRecordUnavailable`.<br>**Worker-backed variant**: `RefreshContainmentPending`; W's effect refused; `settle_contained_refresh` gives `RefetchRequired`, count 0; replay is idempotent.<br>**R3 / P2-6(b)** (changed commit during DRAINING_OLD, before and after the barrier): `RefetchRequired`, `refused`, count 0, orphan CANDIDATE records 0; `begin_migration` succeeds. | CLOSED |
| IR12 hard fence | ReviewCode-1 P2-3 | **F / P3**: an accepted, continuation-owned lease becomes `contained` under the containment owner. `complete_contained` gives REFUSED, count 0, close `closed`. | CLOSED |
| IR13 bounded retention | OriginStateClosure-1 P2-7 | 6,049 neutral commits on one registration. `commit_refresh` stays at 58 call events and about 8.8 µs at history 50, 249, 2,049 and 6,049. The evicted first candidate and receipt are dead after `gc`. Authorization, exit, result, failure, stop and candidate indexes are all 0; the ring holds 9. | CLOSED for its stated bounds. **P3-1** is new (dangling ledger pointer after discard). |
| IR14 first join activates | ReviewCode-1 P3-5; OriginCodeClosure-1 P3-1 | The handshake leaves `active_unused`; the first join gives `active` + `joined`. | CLOSED |
| IR15 replay exactness | ReviewCode-1 P3-3; OriginCodeClosure-1 P3-2; OriginStateClosure-1 P3-3 | The same failure replays; a different failure and a late success both give `operation_outcome_conflict`; one diagnostic is recorded. Accept replay from a non-receiver is refused. | CLOSED. **P3-2** is new (a non-worker fills the diagnostic slot). |
| IR16 enumerations / source rules | ReviewCode-1 P3-7; OriginCodeClosure-1 P3-3 | The rules pin the exact 10-method terminalizer set and the exact worker-entry signatures, including `run_worker_cleanup`. The command and product enumerations exist. My EFFECT_IN_FLIGHT row (11 operations) and delivery QUEUE_REMOVED row (14 operations), which the suite does not enumerate, both hold. | CLOSED (coverage residual in §3) |
| IR17 phase guard | OriginStateClosure-1 P3-2 | A second `begin_migration_effect` gives `migration_indeterminate` with the product unchanged; `retire_binding` refuses. | CLOSED |
| IR18 handoff schedule validation | ReviewState-1 P3-2 | **Probe G**: `ValueError` before the exchange; count, generation permits, buffer permits, lineage and head unchanged. | CLOSED |
| IR19 serial-1 label | ReviewState-1 P3-3 | **Probe J**: LOWER then queued cancel → `refused`; with no prior work → `cancelled_confirmed`. | CLOSED |
| Historical: worker exit | ReviewState-3 P2-1 | Effect 1 raising while effect 2 is unused is contained before the exception escapes (`begun_uncertain`, containment owner, ordinals revoked, count retained). Nested reservation is refused. | Original CLOSED. Root OPEN via **P2-2**. |
| Historical: failed FIFO | ReviewCode-3 P2-1; ReviewState-3 P2-2; FreshCodeClosure-2 P2-1 (+ ReviewCode-2 P2-2, ReviewState-2 P2-1) | `complete(REFUSED)` on a handoff gives `operation_outcome_conflict`; cursors (2,0); the second dequeue is refused. The nine-cause matrix rows above hold. The last-permit races hold on both sides of the commit. | CLOSED (P3-1 affects a post-settlement fixture only) |
| Historical: participant lifecycle | ReviewCode-3 P2-2 | **Repro A**: preactivation admission and join both refuse; 0 participants.<br>**Repro B**: the closed participant becomes `left`; the later attempt requires only the live member; migration begins. | Original CLOSED. Root OPEN via **P2-1**, which recreates the closed "ghost participant" outcome by another path. |
| Historical: neutral refresh | ReviewState-3 P2-3 | Neutral (0,1] gives a receipt, cursors (1,1), count 0, no buffer; the next changed range works. Forty neutral commits behind a head: (41,0), one span, ring 9, count 1; the head's success folds to (41,41). | CLOSED |
| Historical: phase proof | OriginStateClosure-2 State-Closure-P2-1 | A DRAINING proof presented in MIGRATING_PRE_EFFECT refuses with the vector unchanged. The exact pre-effect proof reopens once (epoch 1→2). Replay and the old proof refuse. EFFECT_BEGUN disables the edge. | CLOSED |

## Changed-range analysis

**What changed.** MANIFEST-1 and MANIFEST-2 differ in exactly the 13 paths DRAFT-2 declares. MANIFEST-2 additionally pins only 11 manager records (BuilderPrompt-2, DRAFT-2, MANIFEST-1, the four round-1 reports, RemInputs, RemPlan, Verification-2, VerificationLogs-2).

Changed source:

| File | Lines added / removed | Lines before → after |
|---|---|---|
| `lifetime_reference.py` | +558 / −329 | 1,780 → 2,009 |
| `generation_reference.py` | +141 / −13 | 561 → 689 |
| `lifetime.py` | +52 / −7 | 299 → 344 |
| `buffer_reference.py` | +34 / −28 | 502 → 508 |
| `snapshot_reference.py` | +3 / −3 | 181 → 181 |

- Tests: `test_worker_exit_contracts.py` (841 → 2,682), `test_contract_source_rules.py` (187 → 340), plus small adaptations in four retained test modules.
- Documents: A16 and the implementation record.
- Byte-identical (`cmp`): `admission.py`, `authority.py`, `consumers.py`, `worker_authority.py`, `migration_reference.py`, `protocols.py`, `values.py`, `__init__.py`; `test_worker_authority.py` and the ADR README are unchanged per the manifests.
- No file outside the allowlist changed. No C-style or Rust file changed (the inherited `src/garns_rust/sqlite.rs` is identical in both manifests).

**Traceability.** Every source change maps to a RemPlan mechanism:
- the publication precondition (`_publication_ready`, `_require_publication_ready`, the continuation path in `_owner_matches`);
- the single containment routine (`_contain_lease`, `_contain_command`, `_begin_retirement`), with `_cancel_or_remove` deleted;
- the presentation pre-check in `_validate_barriers`;
- worker-entry validation (`dispatch_worker`, `run_worker_cleanup`, `accept_worker_result`);
- refresh disposition routing plus `discard_candidate`;
- witnessed leave (`witness_local_drain`, `witness_local_close`) with member-bound permits;
- the protocol expansion;
- indexes plus `_discard_operation_history`, the buffer replay index and record pruning, and `consume_initial` deletion;
- the IR14/IR15/IR17/IR19 edits.

The only additions not named by a root are the declared observers `lease_facts` and `worker_cleanup_step`, and deletion of the dead `buffer_reference.invalidate`. Both are inside IR13/IR16 scope.

**New root-cause candidates.**
- **P2-1** is introduced by the IR9 witnessed-leave mechanism. Revision1 returned `CLOSED` on the same sequence (leaving the member JOINED); the corrected `close_outcome` now raises after committing local close.
- **P3-1** is introduced by the IR13 history discard.
- **P3-2** is introduced by the IR15 late-return diagnostic.
- **P2-2** is pre-existing: it reproduces identically on Revision1. The IR7 rewrite moved validation ahead of the action but still claims the step only in `finally`.

None is a NEW ARCHITECTURAL root: each is repaired inside the existing owner and seams.

## 0. Evidence base

**Tuple verification.** Run at START (before reading any source or running any probe) and at END (15:41:38Z, after the last probe).

| Check | Expected | START | END |
|---|---|---:|---:|
| `shasum -a 256 …MANIFEST-2.sha256` | `ee441c18…200720` | exact | exact |
| `shasum -a 256 -c …MANIFEST-2.sha256` | 128 OK | 128 OK | 128 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | 31 / 20 / 741 | 31 / 20 / 741 |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 | all OK | all OK |
| WorkerExitRedesign-AcceptanceEvidence / RemInputs | 13 / 18 | 13 / 18 | 13 / 18 |
| Revision1 MANIFEST-1, verified from inside the archive | 117 OK | 117 OK | 117 OK |
| This prompt / DRAFT-2 / RemPlan SHA-256 | `8a9b8bbd…0119` / `cf10c9f6…cd30` / `a2d625e1…66b2a1` | exact | exact |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 | 0 |

No current-round report for this object (`W1A11-WorkerExitImplementation-ReviewCode-2`, `-ReviewState-2`, any `*-Reverdict.md`) existed in `dev-docs/` at END. I read none, and no peer prompt.

**Documents read completely:**
- Process: the review-loop `SKILL.md` and `references/review-prompt-template.md`; `../AGENTS_GWZ.md`; product `AGENTS.md`; program plan §§15–18 (lines 767–859); the ExecutionBrief; `docs/PRODUCT_LAYOUT.md`.
- Controls: the accepted design `W1A11-WorkerExitRedesign.md` (all 1,121 lines) and its ACCEPTANCE; `W2-AdmissionLifetimeRedesign.md` (all 853 lines); `W2-QueryPlanningDesign.md` (all 711 lines); `W2-AdmissionLifetimeRedesign-ACCEPTANCE.md`; `W1-ACCEPTANCE.md`; RemPlan; DRAFT-2; BuilderPrompt-2; Verification-2; VerificationLogs-2; the implementation record; A16 (by diff against Revision1).
- Stopped-source and design reports named by Inputs: ContractAmendment STOP, ReviewCode-3, ReviewState-3, FreshCodeClosure-2, OriginStateClosure-2, RemPlan, RemPlan-2; WorkerExitRedesign ReviewConsistency-3, ReviewSafety-3, OriginCodeClosure-3 with its Erratum, OriginStateClosure-3.
- Prior-round inputs: ReviewCode-1, ReviewState-1, OriginCodeClosure-1, OriginStateClosure-1.
- Not read, by rule: any other round-2 prompt (including the similarly named `…ReviewState-Prompt-2.md`) and any current-round report.

**Source read completely:**
- `lifetime_reference.py` 1–2009; `generation_reference.py` 1–689; `buffer_reference.py` 1–508.
- `lifetime.py` (diff plus protocol, 255–344); `snapshot_reference.py` registry section (60–181); `worker_authority.py`; `authority.py`; the `consumers.consume` path; `recovery.MigrationRecoveryProof`.
- Unified diffs against Revision1 of every changed source and test file.
- Tests: fixture helpers in `test_admission_contracts.py` and `test_lifetime_contracts.py`; the `test_worker_exit_contracts.py` header and fixtures (1–140), `vector`, `counted`, `full_command`, RetentionBoundTests, the membership tests (714–790) and CommandGrammarEnumerationTests (2529–2682); `test_contract_source_rules.py` 90–340.
- `rg` found no private-attribute writes in the contract tests. The only setattr-style writes in `test_contracts.py` are expected-refusal attacks or the fixtures' trusted provider seams.

**Gates.** Every listed interpreter, with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B`, and no warning filter:

| CPython | Focused contracts | Full tests (ResourceWarning lines) | `tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | Ran 173 OK | Ran 276 OK (0) | 5 PASS |
| 3.12.12 | Ran 173 OK | Ran 276 OK (0) | 5 PASS |
| 3.13.12 | Ran 173 OK | Ran 276 OK (116) | 5 PASS |
| 3.14.3 | Ran 173 OK | Ran 276 OK (84) | 5 PASS |

`tools/check.py`, `compileall` and `py_compile` were not run. A passing suite is corroboration only.

**Inline attacks.** About 40 stdin `-B` probes on 3.14.3; the four findings were re-run on 3.11.14 and the comparison probes on the Revision1 archive. They drove real reference transitions through the repository fixtures. Private fields (`_leases`, `_buffers`, `_permits`, `_attempts`, `_participants`, `_admissions`, `_queues`) were read only to observe and never assigned. Clock, task and invalidation changes used only the fixtures' trusted provider seams and `authority.invalidate`, exactly as the builder's tests do. Representative outputs:

```text
A1 refused worker_authority_invalid ... A1 unchanged: True      A2 reentrant cleanup -> refused | knowledge returned
B[failure] after revoke_generation: retiring_handoff count 1 ... settle -> RefetchRequired lease refused count 0 cursors (2, 0) retired ... begin_migration OK
D cancel returns WorkerExitReceipt | lease retiring_handoff | cmd queue_removed | count 1 ... D settle -> RefetchRequired count 0 delivered 0
H c2 -> RefetchRequired refused count 1 candidates 1 ; H c3 -> RefetchRequired refused count 0 candidates 0
H-w diverged c2 -> RefreshContainmentPending ... settle -> RefetchRequired refused count 0 | replay RefetchRequired 0
history~ 6049: commit call-events=58 avg commit_refresh=   8.8us leases=6050 ring=9 count=0 ; evicted first receipt alive: False
BEFORE[migration] count=1 lease=retiring_handoff cursors=(1, 0) pubs+=0 late success=refused ... AFTER [migration] (0,'succeeded',(1,1),3) -> unchanged
stale DRAINING proof in MIGRATING_PRE_EFFECT: refused | unchanged: True ; exact pre-effect proof: OK -> current gen 1 epoch 2
```

**Randomized state walks.** Fresh fixture per seed; refusals ignored; any unexpected exception type and any invariant break reported. Invariants checked after every step:
- the lease × command pair and owner label lie inside the closed grammar;
- the coordinator permit set equals the live leases, and the buffer-permit set equals the QUEUED buffer records;
- a retiring handoff implies a retiring registration;
- terminal records hold no ledger, candidate or envelope;
- delivered ≤ produced, and lineage stays within its bounds;
- an active head implies a live handoff lease;
- the candidate index matches live refresh candidates.

| Walk | Seeds × steps | Coverage | Problems |
|---|---|---|---|
| Unguided | 150 × 400 | reached no publication (weak; reported for completeness) | 0 |
| Goal-directed | 200 × 500 | 112 publications, 1 handoff | 0 |
| Retuned | 200 × 600 | 891 publications; 155 handoffs (22 succeeded, 123 retired); 13,040 leases | 0 |
| Distinct worker, cleanup steps, wrong-task presentations, hard fences | 150 × 500 | 212 publications; 304 succeeded; 983 leases | 0 |

**Procedural disclosures.**
- One early command wrote three temporary path/hash listing files (`m2.txt`, `m1h.txt`, `m2h.txt`) into the session scratchpad (`/private/tmp/claude-501/…/scratchpad/`) to compare the two manifests' entry sets. That is outside the product tree, but the prompt asks for no file writes, so I disclose it. Nothing in the tree or the archives was written, and the tuple verified unchanged at END.
- Read-only utilities beyond the listed set were used for listing and formatting only: `cat`, `grep`, `awk`, `sort`, `uniq`, `join`, `cut`, `tr`, `head`, `tail`, `ls`, `date`, `basename`, `printf`.
- No helpers, Git/GWZ, network, installs or services.

## 1. Findings

### [P2-1] Membership join is not bound to the registry's local open state; after a join that follows the start of local close, `close_outcome` commits LOCAL_CLOSED and then raises from the witnessed-leave transition, leaving a closed runtime JOINED in every later frozen attempt

**Location:**
- `src/garns/backends/contracts/lifetime_reference.py`:
  - 247–252 `open_lifetime`: no check that local close has not begun.
  - 1502–1512 `start_close(runtime)`: witnesses drain only when the membership is already JOINED.
  - 1520–1551 `close_outcome`: local commit at 1540 and 1543, then `witness_local_close` at 1550.
- `src/garns/backends/contracts/generation_reference.py`:
  - 108–136 `join_runtime`: no validation of the local open resource.
  - 157–175 `witness_local_close`: raises `LOCAL_RESOURCE_DRAINING` at 166–167 when drain was not witnessed.

**Violated invariant:**
- Design §9: `join_runtime` "validates … the exact binding, protocol epoch, runtime identity and local open resource".
- Design §9: "Closing before activation performs only `UNJOINED -> LEFT` … later open/join on that registry refuses."
- Design §9: an idle closed runtime "can never become a permanent acknowledgement obligation".
- Overlay §4 and A16: validate-then-commit.
- RemPlan IR9: "`close_outcome` validates before mutating."
- A16 and DRAFT-2 IR9 claim close "witnesses close instead of calling a refusable finalize"; `witness_local_close` is refusable and runs after the commit.

**Reproduction.** Peer registry joined; a second registry constructed UNJOINED with a runtime resource.

```text
start_close(runtime)                 -> runtime local_draining | membership None   (no drain witness)
open_lifetime()                      -> joined | participants: 2                   (join accepted on a draining runtime)
close_outcome(runtime)               -> refused local_resource_draining 'local close requires the witnessed drain fence'
after failed close                   -> runtime local_closed | admissions retired | membership joined
begin_drain                          -> attempt requires the closed runtime: True
begin_migration (only peer acked)    -> refused deadline_exceeded            (3.11.14 and 3.14.3)
repeat close_outcome                 -> refused again; membership joined
recovery only via a second start_close(runtime) -> leave_pending; close_outcome -> closed; membership left
Revision1, same sequence             -> close_outcome: closed | membership joined   (no raise; member also never left)
```

**Impact:**
- The close linearization point reports failure for a close that already committed: resources are `LOCAL_CLOSED` and admissions `RETIRED`. This is the ReviewState-1 P2-5 defect class that IR9 was meant to remove.
- An idle, obligation-free, `LOCAL_CLOSED` runtime stays a JOINED participant. Every later frozen attempt requires its barrier acknowledgement, so migration and no-effect reopen succeed only while that closed runtime keeps acknowledging. Once its process is gone, this is the permanent acknowledgement obligation design §9 excludes: the ghost-participant outcome of the historical ReviewCode-3 P2-2, reached by a new path.
- The only recovery is an undocumented repeated `start_close`. That repeat is not a no-op: it also relabels RETIRED admissions to DRAINING (see §3).

**Classification:** bounded source repair; new failure mode introduced by correction 1's witnessed-leave mechanism; not architectural.

**Required correction:**
1. `open_lifetime` (the registry-mediated join) must refuse once local close has begun, for example when a registered RUNTIME resource is not `LOCAL_OPEN`. An unjoined registry whose close has begun proceeds only `UNJOINED -> LEFT` through `close_unjoined`, as design §9 states.
2. `close_outcome` must establish every coordinator precondition before its first local mutation: either witness drain and request leave first, or refuse with resource and admission states unchanged. It must never invoke a refusable coordinator transition after committing.

**Closure test:**
- `start_close(runtime)` on an unjoined registry: `open_lifetime` refuses, membership stays `None`, and `close_outcome` returns CLOSED via `close_unjoined`. A later join refuses.
- Every path on which a coordinator witness could refuse makes `close_outcome` refuse with resource states and admissions byte-identical.
- After any CLOSED outcome the member is `LEFT` (or `LEAVE_PENDING` during an attempt, then `LEFT` at attempt close) and absent from the next attempt's required set; `begin_migration` proceeds on the live members' acknowledgements alone.

### [P2-2] `run_worker_cleanup` claims the cleanup step only after the action returns, so a same-step re-entry runs one step twice, skips the next, and success exit plus publication proceed with an incomplete cleanup schedule

**Location:** `src/garns/backends/contracts/lifetime_reference.py:660-701`. The step is validated at 670–675 (`step != command.next_cleanup_step`), the trusted action runs at 690, and `next_cleanup_step` advances only in `finally` at 700–701. The success gate at 627–628 trusts that counter.

**Violated invariant:**
- Design §5.1: "The outermost trusted worker wrapper performs every trusted cleanup before it requests success exit."
- Design §5.3: the finite ordered K-step cleanup schedule; "Success exit is requested only after cleanup returns."
- Design §4.2: callback-induced re-entry must observe the in-progress state and refuse without consuming anything.
- RemPlan IR7: validate "the next step" before the containment scope; refuse without consuming the step.
- Brief: "ordered finite cleanup".
- Fail-closed direction: this invents cleanup completion.

**Reproduction.** Schedule `WorkerCommandSpec("c", (1,), cleanup_steps=2)`. A fixed hostile cleanup action for step 1 re-enters `run_worker_cleanup(authorization, 1)` once. This uses the brief's sanctioned "fixed hostile … cleanup actions", and re-entry is a mandated attack.

```text
nested step-1 cleanup ACCEPTED | actions run: [1, 1] | next step now 3
step 2 refused: worker_authority_invalid cleanup step is unavailable
SUCCESS EXIT ACCEPTED with cleanup steps run = [1, 1]
published: succeeded publications 1 count 0            (3.14.3; identical on 3.11.14)
Revision1 archive: nested ACCEPTED | ran [1, 1] | success exit ACCEPTED   (pre-existing)
```

**Impact:**
- The registry's only enforcement of "every trusted cleanup ran before success" is defeated.
- One trusted cleanup step executes twice (a non-idempotent cleanup double-acts) and another never executes.
- The command still exits success, the operation publishes SUCCEEDED, and its permit is released.

**Classification:** bounded source repair; pre-existing in Revision1 and not closed by the IR7 rewrite; not architectural.

**Required correction:** Claim the step atomically with validation, before invoking the action: advance or mark the step in progress first, and treat a claimed step as consumed whether the action returns or raises. Refuse any cleanup call for a command whose cleanup action is already on its stack. The same marker can refuse effect reservation after cleanup began.

**Closure test:**
- A hostile cleanup action re-entering for the same step, and separately for the next step, gets a refusal with the full vector unchanged (cleanup step, exit facts, diagnostics, lease facts).
- Actions run exactly `[1, 2]`.
- `worker_exit_success` refuses until both steps have run, and publications stay 0 until then.

### [P3-1] Terminalization discards the command ledger but keeps `active_command_serial`, leaving a dangling index that crashes the delivery-stop seam after settlement

**Location:** `lifetime_reference.py:1925-1951` (`_discard_operation_history` clears `command_ledger` at 1944 but not `active_command_serial`); `:1412-1428` (`setup_reference_delivery_stop` dereferences it at 1417); `:899-923` (`lease_facts` reports the dangling pair).

**Violated invariant:**
- Review mandate: no index outlives the record it points to.
- Design §3: "the whole bounded ledger is discarded".
- Design §8: post-settlement stop observation is replayable, not a crash.

**Reproduction:** A worker failure on a delivery, then stop, retirement, delivery stop and `settle_delivery_non_success`. Afterwards `lease_facts` shows `(REFUSED, REFUSED, 'containment', 1, 0)`: active serial 1 with ledger length 0. A late `setup_reference_delivery_stop(retirement)` raises `IndexError: list index out of range` at line 1417. `complete_contained` on a non-delivery leaves the same `(…, 1, 0)` pair.

**Impact:** A late executor stop issued after settlement produces an untyped crash instead of a refusal or idempotent replay. The closed observer reports an impossible (serial, ledger) pair. No count or ownership change.

**Correction:** Reset `active_command_serial` (and any per-ledger pointer) inside `_discard_operation_history`. Make retirement-keyed fixtures and lookups refuse or replay on terminal records.

**Closure test:** After every terminal route, `lease_facts` reports `(…, None, 0)`. A late delivery stop after settlement returns a typed refusal or replay.

### [P3-2] The IR15 late-return diagnostic is written before the current-worker check, so any task holding the authorization and a result fills the worker's diagnostic slot

**Location:** `lifetime_reference.py:608-640`. `late_return_diagnostic = True` at 621 precedes `_validate_worker_barriers` at 629.

**Violated invariant:**
- Design §7 row 1: a wrong current worker at exit gets "refusal before mutation".
- Design §4.1: only "a late worker return" is recorded as the closed diagnostic.
- IR15: a mismatch refuses with state unchanged.

**Reproduction:** With distinct worker W, W's failure contains the command. Then the receiver, and separately a third task, call `worker_exit_success(authorization, result)`. Each is refused with `operation_outcome_conflict`, but the diagnostic count moves `0 -> 1`. W's genuine late return then finds the slot already filled.

**Impact:** A wrong-identity refusal mutates the diagnostic grammar and misattributes a non-worker call as the worker's late return. No owner, state, ordinal or count change.

**Correction:** Validate the exact active command and current assigned worker before recording the diagnostic.

**Closure test:** Receiver and third-task late success refuse with the vector, including the diagnostic count, unchanged. The assigned worker's late success fills the slot once and is idempotent.

## 2. Invariant analysis

These attacks failed (the invariants held). They are what the pre-commitment rests on.

- **Closed command grammar and lease × command product.**
  - EFFECT_IN_FLIGHT row: dequeue, nested effect, exit success, stop, accept, cleanup and next dispatch refuse unchanged. Exit failure, cancel, task loss and façade revoke contain with `begun_uncertain`, the containment owner and the charge retained; the late effect return then refuses.
  - Delivery QUEUE_REMOVED row: all 14 operations refuse or no-op. The only movement is P3-2's diagnostic.
  - Across the four walks (700 seeds), no pair or owner outside the grammar was observed, and the permit and buffer-permit sets always matched live state.
- **Reservation before invoke, containment before the next effect, no caller impersonation.** Effect 1 raising is contained before escape and effect 2 is revoked. A nested reservation refuses without consuming. Wrong-task cleanup, plan steps and refresh commits refuse unchanged. P2-2 is the one re-entry gap.
- **Exact executor quiescence.** `complete_contained` refuses before stop. Delivery settlement requires a delivery stop, which needs a quiescent or QUEUE_REMOVED command. Every terminalizing route required quiescence, acceptance or QUEUE_REMOVED, so count zero never concealed resumable work.
- **Shared containment routine.**
  - Terminal absorption held across the sweep.
  - Retiring survival held under revocation and fence.
  - Lease, command and result moved together (`quiescent_success -> quiescent_contained` with the result closed).
  - §8 phase one began with a registry-owned cause for queue removal, task loss, barrier failure, revocation, receiver cancel and settle-time expiry.
- **Last-permit iterator settlement.** Before the commit, migration, close, fence and receiver loss all retire the handoff with count 1 and a late success refused. After the commit, those races leave `(0, 'succeeded', (1,1))` unchanged; replay returns the same receipt; a late non-success is refused.
- **Neutral lineage.** Forty commits behind a delayed head: cursors (41,0), one span, ring 9, count 1, then fold to (41,41).
  - Evicted, cross-registry, counterfeit and unhashable identities all return `RefreshRecordUnavailable`.
  - In-window replay is exact.
  - Neutral versus close or migration holds on both sides.
  - delivered ≤ produced held across all walks.
- **Refresh disposition routing.** Every unusable candidate (cursor divergence, retirement, DRAINING_OLD before and after the barrier, queue target) is disposed without raising: REFUSED plus `RefetchRequired` when quiescent, `RefreshContainmentPending` otherwise. Presentation mismatches return `RefreshCommitRefused` unchanged.
- **History discard and indexes.** Commit work is constant (58 call events from 50 to 6,049 history). Evicted identities are dead. Per-command indexes empty at terminalization. Replays after terminalization are idempotent where the design retains the record (task loss, settlements, refresh settle, neutral ring) and refuse where it discards it (ledger). The single exception is P3-1.
- **Membership.**
  - The A7 UNRESOLVED runtime stays `leave_pending` through no-effect reopen, cutover and full-rollback recovery, and leaves only after CLOSED.
  - A `left` member admits, acquires and leaves nothing more.
  - Attempt required sets are frozen and join during an attempt refuses.
  - Close during an attempt reports CLOSED, then `left`.
  - P2-1 is the one gap.
- **Phase product.** The stale DRAINING proof refuses with state, generation, epoch, phase, serial, count, membership and queues unchanged. The exact pre-effect proof reopens once. EFFECT_BEGUN disables the edge. A second effect and `retire_binding` refuse.
- **DRAFT-2 interpretations checked against the design.**
  - Cause identity: consistent with §8 ("conflicting … cause refuses").
  - A premature but usable refresh returns `RefreshCommitRefused`: consistent with §10's presentation-only rule and §4.1. The RemPlan's Pending wording would destroy a live refresh, and the design controls per BuilderPrompt-2.
  - `complete(SUCCEEDED)` refuses before publication: consistent with §2 row 2 and §6.
  - The retired-registration tombstone: consistent with §8's typed `RefetchRequired` for known retired registrations, though the RemPlan said "prune retired registrations" (see §3).
  - Retained observations, retirements and outer records: within the RemPlan's IR13 scope.
  - Handshake then first-join activation: consistent with §9 and overlay §8.1.
- **Retained-test adaptations.** The diffs keep each attack, for example idempotent completion and refused conflicting completion. No test overwrites private state.

## 3. Risks and next action

Residual risks below the finding bar (recorded, not filed):

- **Close and barrier scans over retained outer records.** Close, migration barrier, `close_outcome` and `revoke_generation` scan all retained terminal-lease records and retired-registration tombstones. With no live state, 10 / 100 / 1,000 tombstones cost 72 / 612 / 6,012 barrier call events, 88 / 718 / 7,018 close call events and 34 / 124 / 1,024 `close_outcome` call events. The RemPlan excluded outer terminal-lease records, which dominate this cost. Retired registrations are kept as tombstones, contrary to the RemPlan bullet but justified by §8.
- **Spurious diagnostic from double containment.** One genuine invalidation inside a refresh disposition runs `_contain_lease` twice and sets a spurious cancellation-race diagnostic (`cancel` primary plus `cancel_diagnostic=True` after a single expiry).
- **Admission relabel on repeated close** (pre-existing). A repeated `start_close(runtime)` relabels RETIRED or REVOKED admissions to DRAINING, a backward admission edge. Acquisition still refuses. It matters for P2-1's recovery path.
- **Queue relabel by the migration barrier** (pre-existing). The barrier relabels CLOSED queues to MIGRATION_INVALIDATING, and a no-effect reopen relabels them OPEN. Local resource state still guards every use.
- **Refused legal edge.** Design §11 lists `CURRENT × NONE -> RETIRED × NONE` as legal, but the reference explicitly refuses it. RemPlan IR17 allowed that, citing decommissioning authority. A decision is needed before W3/W4 rely on binding non-reuse from CURRENT.
- **Accumulation.** Unconsumed initial-snapshot candidates and unconsumed no-effect proofs accumulate, with no behavioral effect.
- **Unauthenticated cancel source.** The façade `revoke()` is callable by any authorization holder. It is a fail-closed cancel source, carried over from ReviewCode-1's D6 residual.
- **Test coverage gaps.**
  - The command enumeration omits the EFFECT_IN_FLIGHT and delivery QUEUE_REMOVED rows (both hold under my probes).
  - The first RetentionBoundTests method has a vacuous changed-work assertion (`assertEqual(1, len(changed_calls) or 1)`); the second method covers changed-commit constancy.
- **Wrapper-trusted ordering.** Body-then-cleanup ordering is not registry-enforced: a cleanup action can still reserve an effect. This is related to P2-2's remedy.
- **Deferred, not reported:** production async/thread/process execution, locks, durability and crash recovery, provenance, PostgreSQL, activation, credentials, W3 names, and IR20 (`semantic.py` and `tools/check.py` are verified unchanged inside the 741-entry ReadOnly map).

**Single next action:** The lane owner merges this NO-GO with the Code axis. One consolidated bounded source correction (correction 2 of 2) should resolve P2-1 and P2-2 with the closure tests above; P3-1 and P3-2 are recommended on the same paths. Then freeze a new exact tuple and obtain re-verdicts with changed-range attacks. Neither blocker needs an accepted-design, ownership or compatibility change, and no NEW ARCHITECTURAL root was found, so no operator STOP is implied by this report.
