# W1A11-WorkerExitImplementation (correction 1 of 2) — CODE-AXIS REVIEW

**Review object:** The corrected worker-exit internal contracts and deterministic reference implementation, after consolidated source correction 1 of 2. It is the approved filesystem tuple `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256`, SHA-256 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` (128 entries). This is a filesystem tuple, not a Git commit.
- Controlling DRAFT: `dev-docs/W1A11-WorkerExitImplementation-DRAFT-2.md` at `cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30`.
- Controlling disposition: `dev-docs/W1A11-WorkerExitImplementation-RemPlan.md` at `a2d625e1c695b231b3e264470cbd61dfef1ed628744ec25255e59d37e366b2a1`.
- Status: unaccepted candidate; the builder has stopped writing. Reviewed 2026-10-05. This report is filed as `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-2.md`.

**Baseline:** The round-1 object is archived under `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns`, as MANIFEST-1 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` (117 entries, verified from inside the archive). The 20-file writable baseline is `dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256` (`d95fab41…8490a`).
- All sources were read directly from the live filesystem at `/Volumes/projects/limbo/garns-wz/garns`, never from Git HEAD. That tree is the byte-exact 2026-10-04 relocation of the datascad path named by historical documents.
- Changed paths were compared with `cmp`/`diff` against the Revision1 archive.
- Historical live manifests were checked only through the rebased Legacy maps.

**Date:** 2026-10-05

**Axis:** Code. The axis covers architecture, interfaces, call graphs, compatibility reality, ownership and visibility, error and hidden-mutation paths, and whether the bytes do what DRAFT-2 claims and nothing the accepted design forbids. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block (P2-1, P2-2). Four P3 findings are filed and do not block. There is no P0 or P1.
- Every mapped round-1 counterexample (IR1–IR19) and the original counterexamples of all five historical stopped roots are closed when re-run on this tuple.
- The two blockers are both roots that already existed on the round-1 object and that neither round-1 axis attacked. Neither is a regression.
  - **P2-1** is a residual of the participant-lifecycle stopped root: a runtime can join after its close has begun.
  - **P2-2** is an unauthenticated route into the single containment routine that the correction itself introduced.
- Both are bounded source repairs inside the accepted design. No accepted-design, architecture, ownership or compatibility change is needed. **No NEW ARCHITECTURAL root cause** was found, and no STOP is triggered.

**I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.**

---

## Prior-finding retrace table

Every row was re-executed by me on this tuple with inline `-B` stdin attacks using real reference transitions and the repository's fixtures. Builder tests and the manager's failing-before classification were not relied on.

| Root (RemPlan) | Mapped round-1 IDs | Original counterexample re-run on this tuple | Status |
|---|---|---|---|
| IR1 publication precondition | ReviewCode-1 P2-1 (P1a/P1b); OriginCodeClosure-1 P2-5(a)–(c); OriginStateClosure-1 P2-1(a)–(e) | **P1a** (M=2 EXECUTE, publish after C1): `REFUSED lease_invalid`, vector unchanged. After C2 is accepted it publishes once (`SUCCEEDED`, count 0); a replay refuses.<br>**P1b** (zero dispatch, EXECUTE and CONSISTENT_SNAPSHOT): refused, unchanged.<br>**P2-1(a)** (default worker, publish while `running_idle`): refused, unchanged.<br>**P2-1(b)** (publish from inside effect 1): refused. `begin_migration` while the command can run gives `deadline_exceeded`.<br>**P2-1(c)/(d)** (distinct worker running; neutral or changed `commit_refresh`, and `publish_refresh_buffer`): `RefreshCommitRefused`, vector unchanged; migration refuses.<br>**P2-1(e)** (registration while the command is running, then while quiescent-success): refused. After accept it publishes atomically: `SUCCEEDED`, count 0. | CLOSED |
| IR2 atomic registration | ReviewCode-1 P2-6 (R4); OriginCodeClosure-1 P2-7 | `register_subscription` reaches `SUCCEEDED` with count 0 in the same call.<br>A later receiver loss or receiver cancel is a no-op (`SUCCEEDED`, registration live).<br>`complete(SUCCEEDED)` is idempotent; `complete(REFUSED)` gives `operation_outcome_conflict`.<br>`begin_migration` afterwards succeeds.<br>Expiry before the commit: refused, lease contained, 0 publications, 0 registrations. | CLOSED |
| IR3 presentation-only refusals | ReviewCode-1 P2-4 (R1); OriginCodeClosure-1 P2-6; OriginStateClosure-1 P2-5(a) | Wrong-task `commit_refresh` (neutral and changed) and wrong-task `publish_refresh_buffer` return `RefreshCommitRefused` with the vector unchanged. The owner's retry commits once; replay is read-only.<br>A distinct worker presenting the owner on `run_plan_step(LOWER)` gets `context_owner_mismatch` with the vector unchanged. The later accept gives `RUNNING`, so there is no CONTAINED→RUNNING edge. | CLOSED on the mapped counterexamples. The same class of bypass exists on another entry: **P2-2** |
| IR4 one containment routine | ReviewCode-1 P2-2 (P2, P2b, P6); OriginStateClosure-1 P2-5(b),(c); ReviewState-1 P3-1 (probes F, I) | Matrix: 5 causes (expiry, invalidation, authority epoch, `revoke_generation`, hard fence) × 5 stages (queued, running_idle, success_pending, quiescent_success, accepted), plus a prior-work variant at queued: 30 cells.<br>Results by stage:<br>• QUEUED → QUEUE_REMOVED and terminal: `CANCELLED_CONFIRMED` with no prior work, `REFUSED` after LOWER;<br>• RUNNING_IDLE → CONTAINED;<br>• SUCCESS_PENDING → CONTAINED;<br>• QUIESCENT_SUCCESS → QUIESCENT_CONTAINED;<br>• accepted → outer CONTAINED.<br>In every cell `complete_contained` succeeds with the receiver absent, count reaches 0, and 0 publications occur. | CLOSED |
| IR5 queue-removal receipt; registry-detected delivery non-success | ReviewCode-1 P2-7 (D1–D4, G1, G2); ReviewState-1 P2-4 (probe D); OriginStateClosure-1 P2-4 | Delivery matrix: 7 stages (dequeued, queued, running_idle, success_pending, quiescent_success, accepted, publication_ready) × 8 causes (receiver cancel, task loss, expiry, invalidation, `revoke_generation`, hard fence, graceful close, migration): 56 cells. Every cell:<br>• reaches `RETIRING_HANDOFF`;<br>• count goes 2→1→0;<br>• the successor dequeue refuses;<br>• settlement before stop refuses (`lease_invalid`);<br>• one `RefetchRequired` is returned and replay is read-only;<br>• delivered stays at 0;<br>• a late success refuses.<br>Queue removal returns a CANCEL `NOT_BEGUN` receipt. `begin_delivery_non_success(success receipt)` refuses. | CLOSED |
| IR6 terminal leases absorb; retiring survives | OriginStateClosure-1 P2-2(a)–(c); ReviewState-1 P2-1 (probe B) | On `SUCCEEDED`, `CANCELLED_CONFIRMED` and `REFUSED` leases, every worker, delivery and refresh entry was driven from the receiver and from a third task. This includes the receiver's cleanup after a queued cancel. State, completion, owner, count and publications stay unchanged; only no-op observations return; close reports `CLOSED`.<br>Probe B, failure-caused and receiver-loss-caused: `revoke_generation` plus a hard fence, then stops and settlement, gives `RefetchRequired`, count 0, registration `RETIRED`, delivered 0, subscription `CLOSED`, read-only replay, and the next `begin_drain` succeeds. | CLOSED |
| IR7 cleanup validates before mutating | OriginCodeClosure-1 P2-4(a),(b); OriginStateClosure-1 P2-3(a)–(c); ReviewState-1 P2-2 (A1, A2) | Receiver and third-task cleanup in queued, queue_removed, running_idle, contained, quiescent_contained and accepted states gives `worker_authority_invalid` with the full vector unchanged. The genuine worker then runs its effects, cleanups and success exit.<br>Reentrant cleanup inside an effect refuses, and the effect returns `RETURNED`. | CLOSED on the mapped entry. The same impact through the façade is **P2-2** |
| IR8 later-slot dispatch | OriginCodeClosure-1 P2-1 (N1, N2); ReviewCode-1 P3-2 (P4) | **N1**: C2 dispatch after a cancel gives `lease_invalid` with the vector unchanged; `complete_contained` gives `REFUSED`, count 0.<br>A legal C2 dispatch leaves the outer lease `RUNNING` and C2 `QUEUED`.<br>**N2**: after delivery retirement by migration, close, fence, overflow or receiver loss, C2 dispatch refuses with the vector unchanged. Settlement releases once, and migration proceeds. | CLOSED |
| IR9 registry-witnessed leave | OriginCodeClosure-1 P2-2(a)–(c); ReviewCode-1 P2-8/P3-1 (R5, M1); ReviewState-1 P2-3/P2-5 (C, C2, E, E2); OriginStateClosure-1 P3-1 | **R5/C**: direct `request_leave` or `finalize_leave` with a queued buffer refuses; the member stays `joined`, count 1.<br>**C2/P3-1**: `request_leave` on an open runtime refuses.<br>**M1/E**: close during an attempt gives `CLOSED` with `leave_pending`. A repeated `start_close` (graceful or hard) is a no-op. The member is `left` after reopen and is absent from the later attempt (required set 1; barrier refuses).<br>**P2-2(a)**: an UNRESOLVED runtime stays `leave_pending` across reopen and remains in the next attempt. | Mapped counterexamples CLOSED. The misordered join path is a residual: **P2-1** |
| IR10 coordinator seam | OriginCodeClosure-1 P2-3 (R7); ReviewCode-1 P3-6 | The reference coordinator conforms. Stubs missing `join_runtime`, `witness_local_close`, `observe_request_released` or `begin_migration_effect` are refused at registry construction. `begin_migration` returns `MigrationRequestIdentity`. Every changed-signature call site passes the membership. There is no retained reader outside `contracts/`. | CLOSED (shape residual **P3-4**) |
| IR11 refresh disposition | ReviewCode-1 P2-5/P3-4 (R2, R3); ReviewState-1 P2-6 (H); OriginStateClosure-1 P2-6(a),(b) | **H**: three refreshes from cursor 0. The first commits neutral. The diverged changed and neutral commits each return `RefetchRequired` with the lease `REFUSED`; count goes 3→2→1→0, 0 current candidates, 0 orphan buffer records.<br>Worker-backed divergence returns `RefreshContainmentPending` until `settle_contained_refresh` releases once; replay is read-only.<br>An enqueue during `DRAINING_OLD`, before or after the barrier, gives `RefetchRequired` with count 0 and no orphan record, and `begin_migration` then succeeds. | CLOSED |
| IR12 hard fence | ReviewCode-1 P2-3 (P3); ReviewState-1 probe F | A hard fence on an accepted, continuation-owned EXECUTE gives `CONTAINED` under the containment owner. `complete_contained` succeeds without the receiver; count 0. This is also covered by the IR4 matrix. | CLOSED |
| IR13 bounded retention | OriginStateClosure-1 P2-7 | 900 neutral commits on one registration:<br>• a constant 58 Python call events per commit at histories 20, 100, 450 and 900;<br>• 9 live receipt and 9 live candidate identities (R = 9);<br>• the authorization, exit, result, failure, stop and refresh-candidate indexes are all 0;<br>• every terminal ledger has length 0. | CLOSED as the RemPlan scopes it. Outside that scope: **P3-3**, plus a recorded residual on close scans |
| IR14 first open joins | ReviewCode-1 P3-5 (R6); OriginCodeClosure-1 P3-1 | A join before the handshake refuses. After the handshake the coordinator is still `active_unused` with 0 participants. The first join gives `active` plus a membership. Withdrawal then refuses. | CLOSED |
| IR15 replay exactness | ReviewCode-1 P3-3 (P5); OriginCodeClosure-1 P3-2; OriginStateClosure-1 P3-3 | A different failure gives `operation_outcome_conflict`. A late success records one diagnostic. An accept replay from the worker task gives `context_owner_mismatch`. A `begin_delivery_non_success` replay requires the exact cause; a different cause or the failure object conflicts. | CLOSED (adjacent ordering defect **P3-1**) |
| IR16 enumeration and source rules | ReviewCode-1 P3-7; OriginCodeClosure-1 P3-3 | Source rules read in full. The enumeration suites `CommandGrammarEnumerationTests` (7×8) and `MigrationProductTests` (6×11) drive real transitions. | CLOSED. Coverage gaps: the façade `revoke` path and the wrong-task late return are not enumerated (P2-2, P3-1) |
| IR17 phase guard | OriginStateClosure-1 P3-2 | A second `begin_migration_effect` gives `migration_indeterminate` with the product unchanged. `retire_binding` gives `lifetime_protocol_required`. | CLOSED |
| IR18 dequeue validation | ReviewState-1 P3-2 (probe G) | An empty handoff schedule raises `ValueError` before the exchange. Count, permits, buffer permits, lineage, cursors and lease records are unchanged. A later close reports `CLOSED` with count 0. | CLOSED |
| IR19 serial-1 label | ReviewState-1 P3-3 (probe J) | LOWER, then dispatch, then a queued cancel gives `REFUSED`. | CLOSED |
| IR20 (manager P3, `tools/check.py` G10) | — | Not run. It is deferred by the prompt, and `tools/check.py` is prohibited. | DEFERRED, not retraced |
| Historical: worker exit | ReviewState-3 P2-1 | Effect 1 raises (`RuntimeError`, and separately a `BaseException` subclass) while effect 2 is unused. Before the exception escapes:<br>• the lease is `CONTAINED` under the containment owner;<br>• the ordinals are (∅,∅);<br>• effect knowledge is `BEGUN_UNCERTAIN`;<br>• count is 1.<br>Effect 2, success exit, publish and `complete` all refuse. `complete_contained` refuses before the stop and releases once after it. | Original CLOSED. Root still touched by P2-2 and P3-1 |
| Historical: failed FIFO | ReviewCode-3 P2-1; ReviewState-3 P2-2; FreshCodeClosure-2 P2-1 (retaining ReviewCode-2 P2-2, ReviewState-2 P2-1) | Generic `complete(handoff, REFUSED)` and `complete_contained` refuse; count 2, cursors (2,0).<br>Expiry before publication gives `RETIRING_HANDOFF`, count 1. A renewed-context successor dequeue gives `refetch_required` with cursors still (2,0).<br>Settlement returns `RefetchRequired` with count 0. A refresh on the retired registration refuses; a new registration succeeds.<br>The 56-cell matrix above also applies. | CLOSED |
| Historical: participant lifecycle | ReviewCode-3 P2-2 | **Repro A**: preactivation admission and join refuse; 0 participants.<br>**Repro B**: a closed peer reaches `left`; the later attempt requires 1 member and migration proceeds. | Original repros CLOSED. **OPEN via P2-1** (join after close began) |
| Historical: neutral refresh | ReviewState-3 P2-3 | A neutral commit returns a receipt: `SUCCEEDED`, count 0, no added publication, cursors (1,1), ring 1. The next changed range from cursor 1 gives `BufferedDelivery` with cursors (2,1).<br>**K1**: 20 neutrals behind an active head give 1 span, ring 9, count 1. Evicted, cross-registry and counterfeit handles are uniformly unavailable. The span folds on head success to (21,21). | CLOSED |
| Historical: phase proof | OriginStateClosure-2 State-Closure-P2-1 (retaining OriginStateClosure-1 State-Closure-P2-1) | A stale `DRAINING_OLD` proof after `begin_migration` refuses with product, epoch, binding, count and queues unchanged. A fresh pre-effect proof reopens once (epoch 2), and its replay refuses. After `EFFECT_BEGUN`, both the proof and `observe_request_released` refuse. | CLOSED |

## Changed-range analysis

**Changed set.**
- Comparing the live tree with the Revision1 archive over all 117 MANIFEST-1 paths gives exactly 13 changed paths. They equal DRAFT-2's list, and all are inside the brief's 23-path allowlist:

  | Path | Lines +/− | Size |
  |---|---|---|
  | `lifetime_reference.py` | +558/−329 | 1,780→2,009 |
  | `generation_reference.py` | +141/−13 | 561→689 |
  | `lifetime.py` | +52/−7 | 299→344 |
  | `buffer_reference.py` | +34/−28 | 502→508 |
  | `snapshot_reference.py` | +3/−3 | 181 |
  | `test_worker_exit_contracts.py` | +1853/−12 | 841→2,682 |
  | `test_contract_source_rules.py` | +154/−1 | 187→340 |
  | `test_admission_contracts.py` | +33/−3 | 371→401 |
  | `test_lifetime_contracts.py` | +18/−4 | 671→685 |
  | `test_generation_contracts.py` | +19/−7 | 307→319 |
  | `test_contracts.py` | +15/−0 | 903→918 |
  | A16 | +47/−14 | 159→192 |
  | implementation record | +144/−77 | 155→222 |

- The other 10 allowlisted paths are byte-identical.
- No file under `src/` or `tests/` is outside MANIFEST-2 (64 of 64 pinned). No new source or test file exists.

**Retained tests.**
- AST inventory of class test methods: 122 → 165. No retained test was removed.
- The adaptations I read preserve or strengthen coverage:
  - `run_command` / `run_default_command` drive the required slot;
  - unpublished generic completions move from `SUCCEEDED` to `REFUSED`, keeping the idempotency and conflict assertions;
  - new `SUCCEEDED`/`CONTAINED` assertions were added;
  - `assertIsNotNone` was strengthened to `assertIsInstance(BufferedDelivery)`;
  - generation tests now join a participant before activation-dependent steps.

**Coordinator seam.** All changed coordinator signatures have updated call sites: `acquire_shared`, `add_buffer` and `exchange_buffer_for_shared` take the membership, and `begin_migration` returns the request identity. Each call site is one of three in `lifetime_reference.py` or in tests. No module outside `contracts/` reads the seam. The exported `PlanAdmissionVerifier` protocol still matches the registry.

**Size exception.** `lifetime_reference.py` grows by 229 lines. The growth is the containment routine, the publication precondition, the indexes with their discard, and the observers. It stays the single mutable owner, so the recorded cohesion exception holds.

**New-root candidates.**
- **P2-1 and P2-2** reproduce identically on the Revision1 archive (`cwd` = archive, its own `src`):
  - Revision1, misordered join: `close_outcome` returned `CloseOutcome` while the membership stayed `joined`, and `begin_migration` refused.
  - Revision1, façade revoke by a third task: the running command was contained.

  Both are therefore retained roots that round-1 did not attack, not regressions. Correction 1 changed P2-1's symptom from a silent `CLOSED` with a JOINED ghost to a commit-then-raise. It also removed `revoke`'s last internal caller while asserting that only genuine invalidation reaches the containment routine.
- **P3-1 and P3-2** are introduced by the correction: the IR15 diagnostic and the IR13 ledger discard.
- **P3-3** is pre-existing retention that the corrected record now describes as discarded.
- **P3-4** is an omission inherited from the accepted W1 protocol that a new source rule now pins.
- None of the six is a NEW ARCHITECTURAL root cause. All are bounded source repairs.

## 0. Evidence base

**Reviewer provenance:** I am a fresh Claude subagent dispatched with model parameter `opus`, with no prior agent context. The prompt's SHA-256 `d0e3ea5d2b26ca8dcb1cb3e8f74fe49ba5ed0017093dd00c379c8766fa7b83b9` was verified before reading and was unchanged at END.

**Tuple verification (START and END identical):**

| Check | START | END |
|---|---|---|
| `shasum -a 256` MANIFEST-2 | `ee441c18…0720` | `ee441c18…0720` |
| `shasum -a 256 -c` MANIFEST-2 | 128 OK | 128 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK | 31 / 20 / 741 OK |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 OK | same |
| AcceptanceEvidence / RemInputs | 13 / 18 OK | 13 / 18 OK |
| MANIFEST-1, verified from inside the Revision1 archive | 117 OK (`7e80ca67…a544`) | 117 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 |
| DRAFT-2 / RemPlan SHA-256 | `cf10c9f6…acd30` / `a2d625e1…b2a1` | unchanged |

No `W1A11-WorkerExitImplementation-ReviewCode-2.md`, `-ReviewState-2.md` or `*-Reverdict.md` existed during the review.

**Documents read in full:**
- `/Users/owebeeone/.claude/skills/review-loop/SKILL.md` and `references/review-prompt-template.md`; `../AGENTS_GWZ.md`; product `AGENTS.md`.
- Plan `GarnsV9-6-PostgresAsyncImplementationPlan.md` §§15–18 (lines 767–859).
- The ExecutionBrief.
- The accepted design `W1A11-WorkerExitRedesign.md` (1,121 lines) and its ACCEPTANCE; the W2 overlay `W2-AdmissionLifetimeRedesign.md` (853 lines) and the W2 composition ACCEPTANCE; `W1-ACCEPTANCE.md`.
- `docs/PRODUCT_LAYOUT.md`, `docs/adr/A16-admission-lifetime.md`, `docs/adr/README.md`.
- The RemPlan (777 lines), DRAFT-2, BuilderPrompt-2 and Verification-2.
- VerificationLogs-2: the commands and the result lines for every run.
- The implementation record `W1A11-WorkerExitImplementation.md`.
- The four round-1 reports: ReviewCode-1, ReviewState-1, OriginCodeClosure-1, OriginStateClosure-1.
- The stopped-source reports: `W1A11-ContractAmendment-{STOP,ReviewCode-3,ReviewState-3,FreshCodeClosure-2,OriginStateClosure-2,RemPlan,RemPlan-2}.md`.
- The redesign reports `W1A11-WorkerExitRedesign-{ReviewConsistency-3,ReviewSafety-3,OriginCodeClosure-3,OriginCodeClosure-3-Erratum}.md`.

**Read in part:**
- `W2-QueryPlanningDesign.md`: section map and §5.3. The overlay supersedes its lifetime clauses.
- `W1A11-WorkerExitRedesign-OriginStateClosure-3.md`: header, closure table and section map.

**Not read:** any round-2 prompt other than my own (ReviewCode-Prompt-2, ReviewState-2-Prompt, ReviewState-Prompt-2, OriginCode/OriginStateClosure-Prompt-2, Reverdict-Prompt), the Handoff, the checkpoint and other lanes' reports.

**Source read in full (live bytes):**
- `lifetime_reference.py` 1–2009, `generation_reference.py` 1–689, `lifetime.py` 1–344, `buffer_reference.py` 1–508.
- `snapshot_reference.py` 1–181 together with its Revision1 diff.
- `worker_authority.py`, `migration_reference.py`, `authority.py`, `consumers.py` and `admission.py`.
- Revision1 `open_lifetime`, `request_worker_cancel`, `_cancel_or_remove` and `close_outcome`, for comparison.

**Tests read:**
- `test_contract_source_rules.py` in full.
- `test_worker_exit_contracts.py`: the class and method inventory plus lines 1–75, 743–766, 870–1045, 1182–1230, 1416–1540, 1914–2080 and 2360–2682.
- The fixtures in `test_admission_contracts.py` (1–140) and `test_lifetime_contracts.py` (1–200).
- The full Revision1 diffs of every changed test file.

**Allowed gates** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B`, no warning filters). These are corroboration only:

| Interpreter | Focused `discover -s tests/contracts` | Full `discover -s tests` | `tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | Ran 173 OK | Ran 276 OK (0 ResourceWarning lines) | 5 PASS |
| 3.12.12 | Ran 173 OK | Ran 276 OK (0) | 5 PASS |
| 3.13.12 | Ran 173 OK | Ran 276 OK (116 inherited SQLite ResourceWarning lines, visible) | 5 PASS |
| 3.14.3 | Ran 173 OK | Ran 276 OK (84, visible) | 5 PASS |

**Inline read-only attacks** (`python3.14 -B -` on stdin, real reference transitions):
- Batches: IR1 (×2), IR2, IR3, IR4 (30-cell matrix), IR5/IR6 delivery (56-cell matrix), post-acceptance cancel return value, IR6, IR7 (18 caller × state cells plus reentrancy), IR8 (×2), IR9 plus the misordered-join attack, the stranded-member migration block, IR10, IR11, IR13 (900-commit scaling with `sys.setprofile` call counts and weakrefs), IR14/15/17/18/19, the five historical roots, non-worker exit diagnostics, the post-terminal active serial, initial-snapshot retention, façade `revoke`, C1/C2 isolation with counterfeits and S1, K1 neutral lineage, `PlanAdmissionVerifier` conformance.
- The two blocking attacks were also run with `cwd` set to the Revision1 archive (its own `src` resolved, as `garns.__file__` showed).
- Private fields were read only to observe state (`_leases`, `_attempts[...]`, `_participants`, `_buffers._registrations`, `_snapshots._initial`, `_queues`) and were never assigned. Expiry, invalidation and task switching used only the fixtures' trusted provider controls (`now`, `epoch`, `task`, `authority.invalidate`), exactly as the suites do.

**Procedural disclosure:**
- Besides the listed commands I used `ls`, `grep`, `awk`, `sort`, `uniq`, `comm`, `tr`, `head`, `cat`, `basename` and `echo`, read-only. I used a one-time `find / -maxdepth 6 -name review-loop` to locate the skill. I used an AST inventory script, stdlib only.
- One malformed attack script failed with `SyntaxError` before executing anything; it was corrected and re-run.
- No file was written. No helper agent, Git/GWZ operation, network, install, service, `tools/check.py`, `compileall` or `py_compile` was used.

## 1. Findings

### [P2-1] A runtime can join the coordinator after its local close has begun; its close then commits and raises, and the stranded JOINED member blocks later migration attempts

**Location:**
- `src/garns/backends/contracts/lifetime_reference.py:247-252`: `open_lifetime` calls `join_runtime` with no check of the registry's runtime resource state.
- `src/garns/backends/contracts/generation_reference.py:108-136`: `join_runtime` validates only the open record, activation, deployment `CURRENT` and that no attempt is open.
- `lifetime_reference.py:1502-1512`: `start_close` witnesses the drain and requests leave only if a JOINED membership exists at that moment.
- `lifetime_reference.py:1535-1551`: `close_outcome` moves resources to `LOCAL_CLOSED` (1535–1540) and retires admissions (1542–1543) before calling `witness_local_close` (1550).
- `generation_reference.py:157-168`: `witness_local_close` raises `LOCAL_RESOURCE_DRAINING` when the drain was never witnessed.
- `_admit` (292–307) also admits after such a join, because it never checks local resource state.

**Violated invariant:**
- Design §9 lines 657–660: `join_runtime` "validates … runtime identity and local open resource".
- Design §9 lines 677–680: closing before activation performs only `UNJOINED -> LEFT`, "and later open/join on that registry refuses".
- Design §9 lines 697–699: an idle runtime that has reached `LEFT` "can never become a permanent acknowledgement obligation".
- RemPlan IR9 (lines 514–516): "`close_outcome` validates before mutating".
- The ReviewCode-3 P2-2 required correction: "closed idle runtime leaves later migration topology".

**Reproduction** (ACTIVE coordinator from `make_lifetime_fixture`; a second registry `ghost` with its own runtime resource):

```text
ghost.start_close(rt)                     # membership None: nothing witnessed
join after start_close:                   ('OK', 'ParticipantMembership')
admission after join on draining runtime: ('OK', 'AdmittedReadHandle')
close_outcome:                            ('REF', 'local_resource_draining') | runtime now: local_closed | admissions: ['retired'] | membership: joined
retry close_outcome:                      ('REF', 'local_resource_draining')
attempt = begin_drain(); live registry acknowledges only
begin_migration:                          ('REF', 'deadline_exceeded')
no-effect reopen:                         ('REF', 'migration_indeterminate')
count: 0 state: draining_old required: 2 acked: 1
second start_close (undocumented recovery): ('OK', 'NoneType') leave_pending   # still in the frozen required set
```

On Revision1 the same sequence returned `CloseOutcome` (CLOSED) with the membership still `joined`, and `begin_migration` gave `deadline_exceeded`.

**Impact:**
- The close linearization point reports a refusal after it has already committed local close and admission retirement, and every retry raises again. This is the validate-then-commit defect IR9 was meant to remove, on a path it did not cover.
- The runtime's resources are `LOCAL_CLOSED`, yet it stays a JOINED participant. Every later `begin_drain` freezes it as a required participant.
- Until that closed runtime acknowledges a barrier, migration and no-effect reopen refuse with count 0, and the deployment is stuck in `DRAINING_OLD`. That is the ReviewCode-3 P2-2 Reproduction B consequence.
- The only recovery is an undocumented second `start_close` on an already-closed runtime, and it still leaves the member owing a barrier acknowledgement.

**Classification:** bounded source repair, residual of the historical participant-lifecycle root. It needs no design or ownership change and is not architectural.

**Required correction:**
1. Make join refuse once the registry's runtime has left `LOCAL_OPEN`. Either:
   - `open_lifetime` refuses before calling `join_runtime` when any of the registry's RUNTIME resources is not `LOCAL_OPEN`; or
   - `start_close(runtime)` on an UNJOINED registry presents its open record so the coordinator marks it closing, and `join_runtime` refuses it.
2. Make `close_outcome` validate the leave-witness precondition before any resource or admission mutation, so that no refusal follows a commit.

**Closure test:**
- ACTIVE coordinator. Construct a registry, add its runtime, then call `start_close(runtime)` in both the graceful and the hard variant.
- `open_lifetime` must refuse with membership `None` and the coordinator's participants and activation unchanged.
- `close_outcome` must return `CLOSED` through `close_unjoined` (`LEFT`), and a later join must refuse.
- A later attempt must exclude the runtime, and `begin_migration` must proceed on the live members' acknowledgements.
- Assert that no `close_outcome` refusal leaves resource or admission state changed.

### [P2-2] The public executor façade's `revoke(authorization)` reaches the single containment routine with no presentation authority

**Location:**
- `src/garns/backends/contracts/worker_authority.py:121-143`: the façade `revoke` delegates without any check.
- `lifetime_reference.py:242-244`: the façade is bound to `_revoke_worker_authorization`.
- `lifetime_reference.py:799-801`: the façade is exposed through the public `worker_issuer` property.
- `lifetime_reference.py:1899-1911`: `_revoke_worker_authorization` calls `_contain_lease` for QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT, SUCCESS_PENDING and QUIESCENT_SUCCESS commands, with no current-task, current-worker or receiver check.
- Nothing in the registry calls `revoke` any more. `self._workers` is used only at line 1610 for `context_owner`. Revision1's `start_close(hard)` used it; correction 1 replaced that with `_contain_lease`.

**Violated invariant:**
- Design §5.2 lines 325–329: cancellations have exactly "three trusted sources … The task and source are obtained from trusted providers; no caller supplies an owner or claims proof."
- Design §7 row 1: refusal happens before mutation for a wrong identity.
- RemPlan IR4 line 295: "Presentation refusals never reach this routine (IR3)".
- IR7's closure standard (line 426): refusal for "the wrong task, the issuing task and the assigned worker".
- A16 lines 66–71: a presentation-only mismatch refuses without mutation; only genuine invalidation moves the lease through the containment routine.

**Reproduction** (distinct assigned worker `W`; a task `THIRD` that is neither receiver nor worker calls `registry.worker_issuer.revoke(authorization)`):

```text
queued:            (RUNNING, None, 'command') queued       -> (REFUSED, REFUSED, 'containment') discarded   count 0
running_idle:      (RUNNING, None, 'worker') running_idle  -> (CONTAINED, None, 'containment') contained     count 1
quiescent_success: (RUNNING, None, 'escrow') quiescent_success -> (CONTAINED, None, 'containment') quiescent_contained count 1
running delivery:  -> (RETIRING_HANDOFF, None, 'containment') count 1, registration retiring_refetch
Revision1 (same third-task revoke on a running command): contained contained
```

**Impact:** Any task holding the command authorization, which `dispatch_worker` returns to the receiver, can destroy another task's live operation without being a trusted cancellation source. It can:
- terminalize a queued operation as `REFUSED`;
- kill a running command's success path;
- close a quiescent private result;
- retire a delivery's registration, invalidating its successors and forcing a refetch.

This is the same impact that three round-1 reports rated P2 for `run_worker_cleanup` (IR7). It also directly contradicts the corrected mechanism's claim that presentation errors never reach containment. ReviewCode-1 §3 recorded this route below the bar (D6), and DRAFT-2's limits call it "unchanged in kind". After correction 1 it is the one remaining unauthenticated route into `_contain_lease`.

**Classification:** bounded source repair; not architectural.

**Required correction:** Remove `revoke` from the public façade, together with `_revoke_worker_authorization`, which has no internal caller. Otherwise, validate through the trusted providers that the current task is the exact assigned worker or the live receiver before any mutation, and refuse mutation-free otherwise. Cancellation must stay limited to the design's three trusted sources.

**Closure test:**
- A third-task `revoke` at QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT (from inside the effect), SUCCESS_PENDING and QUIESCENT_SUCCESS refuses with the full `vector(...)` unchanged. Run it on EXECUTE and on a running two-range delivery.
- Add a source rule that enumerates every public method reaching `_contain_lease` and requires each to validate the receiver, the assigned worker, or a trusted observation or barrier first.

### [P3-1] A non-worker's refused `worker_exit_success` fills the late-return diagnostic

**Location:** `lifetime_reference.py:608-622`. `command.late_return_diagnostic = True` is set before any current-worker check; `_validate_worker_barriers` is reached only at line 629.

**Violated invariant:**
- Design §4.1 lines 197–201: a late *worker* return after containment is recorded as a closed diagnostic.
- Design §7 row 1.
- The brief: "Every refusal must assert unchanged … result/failure … facts".

**Reproduction:** Contain the command by a receiver cancel. A third task then presents (authorization, closed result) and gets `operation_outcome_conflict`. The `worker_exit_facts` diagnostic count moves 0 → 1, and only vector element 5 changes.

**Impact:** Any holder of the authorization and the result identity can fabricate the bounded "late worker return" diagnostic. `CommandGrammarEnumerationTests.LATE_RETURN` masks this counter but drives only the worker task, so the gap is untested.

**Remedy:** Require the exact current assigned worker before recording, and refuse mutation-free otherwise.

**Closure test:** Third-task and receiver presentations leave `worker_exit_facts` unchanged. The genuine worker's late return still records exactly one diagnostic.

### [P3-2] Terminal history discard leaves a dangling active command serial

**Location:**
- `lifetime_reference.py:1925-1951`: `_discard_operation_history` empties `command_ledger` but not `active_command_serial`.
- `lifetime_reference.py:899-923`: the `lease_facts` observer.
- `lifetime_reference.py:1412-1423`: `setup_reference_delivery_stop` indexes `command_ledger[active_command_serial - 1]`, reached through `_delivery_record` (1725–1733) over the never-pruned `_retirements` index.

**Violated invariant:**
- Design §3 lines 125–128: at most one nonterminal record, and the whole ledger is discarded at terminalization.
- Typed refusal instead of an uncaught exception.

**Reproduction:**
- Retire a running delivery through cancel, stop it, and settle: `lease_facts` gives `(REFUSED, REFUSED, 'containment', 1, 0)`, and `setup_reference_delivery_stop(retirement)` raises `IndexError: list index out of range`.
- EXECUTE after `complete_contained`: `(REFUSED, REFUSED, 'containment', 1, 0)`.

**Impact:** The correction-1 observer, which the refusal-testimony `vector` helper uses, reports an active command for a terminal operation with an empty ledger. A trusted fixture path crashes with a non-`ContractRefusal` exception. Any future access keyed by the stale serial will crash too.

**Remedy:** Clear `active_command_serial` in `_discard_operation_history`, and refuse delivery-stop issuance on terminal records.

**Closure test:** After every terminal route, `lease_facts` reports active serial `None`, and post-terminal delivery-stop issuance raises `ContractRefusal`. The routes are publication, complete, `complete_contained`, queue removal, settle success, settle non-success and both refresh dispositions.

### [P3-3] Unconsumed initial-snapshot candidates, with their frozen rows, outlive their terminal registration leases

**Location:**
- `snapshot_reference.py:110-136`: records are deleted only by `consume_initial`.
- `lifetime_reference.py:925-955` creates them; `1925-1951` never purges them.
- The `_discard_operation_history` docstring and the implementation record's "Bounded retention" row claim that every current candidate field is discarded at terminalization.

**Violated invariant:**
- RemPlan IR13 correction: "Clear candidate and receipt fields, keeping only the tombstone state the design names for exact replay".
- OriginStateClosure-1 P2-7 closure intent: retained records ≤ live operations plus a bounded tombstone window.
- The record's own claim.

**Reproduction:** 50 registrations each produce an initial candidate and are then cancelled. That leaves 50 terminal (`refused`) registration leases and 50 `_InitialRecord`s still holding frozen rows (e.g. `FrozenMap((('secret_row', 0),))`) and lease references.

**Impact:** Memory and unpublished row data are retained in proportion to abandoned registrations, and the documented discard is inaccurate. This is P3 because it is outside the design's §10 neutral-lineage bounds, which are the scope of IR13's blocking closure.

**Remedy:** Index the initial candidate by lease, discard it at terminalization, and correct the record.

**Closure test:** Abandoned registrations leave the initial-candidate store empty, with weakref proof that the rows and the candidate die. Successful registration is unchanged.

### [P3-4] The formal coordinator seam declares `mark_indeterminate` but not its only exit, and the source rule pins the omission

**Location:**
- `lifetime.py:266-326`: the seam declares `begin_migration_effect`, `publish_generation` and `mark_indeterminate`, but not `recover_migration`. The reference coordinator implements `recover_migration` at `generation_reference.py:550-580`.
- `tests/contracts/test_contract_source_rules.py:31-46,229`: `set(COORDINATOR_METHODS) == methods` freezes the member set.

**Violated invariant:**
- Design §11 lines 920–926: `MIGRATION_INDETERMINATE × EFFECT_BEGUN` has three authoritative exits.
- Overlay §8.2: ordinary work refuses "until authoritative recovery establishes the exact outcome".
- The review contract: a missing half of a lifecycle pair is a finding.

**Reproduction:** `hasattr(SharedGenerationCoordinator, "recover_migration")` is `False`. A full stub of the declared members conforms. Adding the member would fail the source rule.

**Impact:** A future coordinator written to the formal seam conforms while offering no exit from the absorbing indeterminate state it declares an entry into. The registry calls neither member today, so there is no current failure.

**Remedy:** Declare `recover_migration(proof) -> None` and add it to `COORDINATOR_METHODS`. Alternatively, move both members to a separately declared operator-recovery seam.

**Closure test:** A stub lacking `recover_migration` fails `isinstance`, and the source rule includes the member.

## 2. Invariant analysis

The following attacks failed against this tuple. They are what a future GO rests on.

- **One publication precondition** guards every generic terminal success: `run_plan_step(PUBLICATION)` for every kind, `register_subscription`, `_commit_refresh_record` and `prepare_delivery_publication`. The IR1 vectors covered every kind × default or distinct worker × each prepublication stage, including calls from inside an effect, the two-slot case and zero dispatch.
- **Registration** publishes, registers, terminalizes and releases in one call. Generic `complete(SUCCEEDED)` is replay-only.
- **Presentation refusals** are mutation-free on refresh commit, `publish_refresh_buffer`, plan steps, dispatch, cancel, accept, settle and registration. The consumer-failure containment in `run_plan_step` cannot be triggered by presentation errors, because `consume` never fails for an owned consumer.
- **The containment routine** moves lease and command together in every cell of the 30-cell matrix. Terminal leases absorb every entry from every task. A retiring handoff keeps its label through revocation and fence.
- **Delivery conservation** held in all 56 cells:
  - exactly one queued release and one active release;
  - no successor dequeue;
  - no settlement before stop;
  - read-only replay;
  - delivered progress never invented;
  - a late success conflicts.

  Generic `complete` and `complete_contained` refuse handoffs. My trace of every `_terminalize` call site confirms that only the two specialized settlements terminalize a handoff.
- **Worker entries** validate before mutating: cleanup across 18 caller × state cells, and later-slot dispatch for every serial and retirement cause.
- **Membership** in the normal open-then-close order:
  - leave is registry-witnessed;
  - generation and buffer permits carry the runtime identity and join serial, and LEFT members admit, acquire, enqueue and exchange nothing;
  - frozen attempts keep LEAVE_PENDING members, which become LEFT after attempt close;
  - repeated close is a no-op;
  - the first join performs `ACTIVE_UNUSED -> ACTIVE`.
- **Neutral refresh:** Q = 8, C = R = 9. Spans coalesce per gap; the ring stays at 9; evicted, cross-registry and counterfeit handles get the uniform `RefreshRecordUnavailable`; a current candidate exists only on a charged lease. Diverged, retired or fenced candidates take the quiescent-or-containment disposition with exactly one release, and changed-neutral-changed keeps two gaps. Per-commit work is constant (58 call events) and per-command indexes drain at terminalization.
- **Phase product** is closed: a stale same-attempt DRAINING proof refuses unchanged; a fresh pre-effect proof reopens once; `EFFECT_BEGUN` removes the edge; a second effect and `CURRENT -> RETIRED` refuse.
- **Identities:**
  - C1/C2 isolation holds: C1 success and stop replays are idempotent, and C1 conflict, effect, dequeue, cleanup and worker-task accept attacks leave C2's vector unchanged.
  - Seal-minted counterfeits of every new identity refuse.
  - Copy, deepcopy and pickle raise `TypeError`.
  - A child-task accept refuses.
- **Ownership:**
  - `WorkerAuthorizationIssuer` holds callables only;
  - `release_shared` occurs only in `_terminalize`;
  - cursor stores live only in `buffer_reference.py`, and participant stores and proof issuance only in `generation_reference.py`;
  - the protocols carry no raw `Plan` (source rules re-read).
- **Retained initial-18, F1–F10 and expanded revocation** were spot-checked by execution:
  - pinned parameters (via the step products);
  - expanded revocation (`revoke_generation` contains, 0 publications);
  - F2 fold on head success;
  - F8;
  - F9 (worker impersonation through IR3-style presentation);
  - generic-completion refusals.

  The remainder are corroborated only by the passing suites.
- **Interpretations declared in DRAFT-2's limits**, checked against the design:
  - the triggering registry record is the cause (§8);
  - premature candidate presentation is a retryable `RefreshCommitRefused`, while an unusable one is disposed (§10 distinguishes presentation from invalidation, and the design overrides the RemPlan's literal text as BuilderPrompt-2 requires);
  - generic `complete(SUCCEEDED)` refuses (§6);
  - a retired registration keeps a tombstone (§8 requires typed `RefetchRequired`);
  - operation-level records are retained (outside the §3 and §10 bounds);
  - the handshake is followed by first-join activation (§9 and overlay §8.1).

  All are consistent, apart from the retention scope noted in P3-3 and below.

## 3. Risks and next action

**Residual risks below the finding bar** (recorded, not filed):
- After acceptance, `request_worker_cancel` and `observe_receiving_task_done` return the finished command's SUCCESS receipt as their disposition; Revision1 returned `None`. For a delivery that receipt is not the recorded phase-1 cause, so a canceller's `begin_delivery_non_success` replay with it conflicts.
- Close, barrier and revocation scan every retained terminal lease record. On an untouched peer subscription, `close_outcome` work grew from 25 to 925 call events after 900 refreshes. Per-commit work is constant as IR13 requires, and the RemPlan excludes outer records.
- Several maps are kept indefinitely: `_observations` (which hold receiving-task references), `_consumed_observations`, `_retirements` and `_delivery_stops`, plus the coordinator's `_no_effect_proofs`. Retired-registration tombstones are also scanned by `retire_for_resources`.
- A7 unresolved identities are supplied by the caller to `close_outcome(resource, unresolved)`. The registry-witnessed `CLOSED` cannot itself verify A7 truth.
- The trusted fixture `setup_reference_initial_snapshot` contains the lease when given a non-matching subscription or queue argument.
- Effect and cleanup diagnostics share one list, and excess entries are dropped rather than refused (§5.3).
- `begin_delivery_non_success` accepts a fixture-issued, never-committed `ClosedWorkerFailure` and records the command exit as CANCEL.
- `publish_refresh_buffer` is a commit entry beyond §10's sole entries. For an absent candidate presented with a live lease it raises `REFETCH_REQUIRED` instead of returning the uniform `RefreshRecordUnavailable`.
- Protocol conformance is checked by name only (`runtime_checkable`). Signature drift goes undetected, except for the `begin_migration` return annotation the source rule checks.
- Production async, thread and process execution, locks, durability, crash recovery, provenance, PostgreSQL, activation and W3 names are deferred by mandate and are not reported.

**Single next action:** Apply one consolidated bounded source correction, implementation correction 2 of 2, resolving P2-1 and P2-2 with their closure tests. Fix the P3s where they sit on the paths it touches. Freeze a new tuple and obtain this axis's focused re-verdict plus originating closure.

None of the findings needs an accepted-design, architecture, ownership or compatibility change, so no operator STOP is implied. The five historical stopped roots remain OPEN until that closure; the participant-lifecycle root stays open through P2-1. Nothing in this report accepts source or alters the historical two-correction records.
