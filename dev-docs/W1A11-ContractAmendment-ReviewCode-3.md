# W1A11-ContractAmendment — CODE-AXIS REVIEW

**Review object:** W1A11-ContractAmendment final architecture correction2 of2, approved no-Git filesystem object at `dev-docs/W1A11-ContractAmendment-MANIFEST-3.sha256` SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` (71 files); controlling amendment `dev-docs/W1A11-ContractAmendment.md` SHA-256 `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`; unaccepted candidate, builder writes stopped, reviewed 2026-10-04.  
**Baseline:** Approved no-Git exception. Sources were read directly from the current filesystem and compared with the preserved Revision2 complete59 archive, Revision1 complete47 archive, and accepted Baseline archive. Current and historical manifests were verified within their respective archive boundaries; superseded live-source hashes were not misclassified as unowned changes.  
**Date:** 2026-10-04  
**Axis:** Code — architecture, interfaces, call graphs, compatibility reality, ownership, visibility, failure paths, and correspondence between the amendment and executable reference behavior. Independent, adversarial, read-only. The State axis ran in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — no P0 or P1 findings; two P2 findings block. P2-1 is the still-open correction1 F2 delivery-accounting defect. P2-2 is a newly demonstrated but bounded omission in the already-selected participant lifecycle contract. Neither requires a new architectural decision or operator STOP. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## 0. Evidence base

### Authority and controlling inputs

I read completely:

- `../AGENTS_GWZ.md` and workspace `AGENTS.md`.
- `/Users/owebeeone/.claude/skills/review-loop/SKILL.md` and its complete canonical review template.
- `GarnsV9-6-PostgresAsyncImplementationPlan.md` §§15–16.
- `W1A11-ContractAmendment-ExecutionBrief.md`, `OwnershipExtension.md`, the controlling amendment, and `W1A11-ContractAmendment-DRAFT-3.md`.
- Full accepted `W2-QueryPlanningDesign.md`, `W2-AdmissionLifetimeRedesign.md`, their acceptances, W1 acceptance, `PRODUCT_LAYOUT.md`, ADRs A1–A16, and the ADR index.
- Both remediation plans and both remediation-input manifests.
- The legitimate prior `ReviewCode`, `ReviewState`, supplement, `ReviewCode-2`, `ReviewState-2`, `OriginCodeClosure-1`, and `OriginStateClosure-1` reports.
- The current contract implementation and contract tests, including the new `snapshot_reference.py` and `migration_reference.py`.

I did not read any current `ReviewCode-3`, `ReviewState-3`, `Origin*Closure-2`, or `Fresh*Closure-2` report or prompt, nor manager checkpoint/restart material for current findings.

### Tuple and archive verification

At both the start and end of review:

- `W1A11-ContractAmendment-MANIFEST-3.sha256` had exact SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
- All 71 current-manifest entries passed.
- `Inputs.sha256` had exact SHA-256 `032508b3b5ba210be4b53d939c1301e85a06083b787727a2fd9bf78270b9da24`; 9/9 entries passed.
- `Control.sha256` had exact SHA-256 `3d614336ae2a944fe40fbefa79ca48be662d839ddb1d163abeb7353bccf84951`; 3/3 entries passed.
- `Baseline.sha256` had exact SHA-256 `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf`; 120/120 entries passed.
- `ReadOnly.sha256` had exact SHA-256 `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 entries passed.
- `ProductGuard.sha256` had exact SHA-256 `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 entries passed.

Additional controls:

- `W1A11-ContractAmendment-DRAFT-3.md` matched `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`.
- `W1A11-ContractAmendment-RemPlan-2.md` matched `749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c`.
- RemInputs correction1 passed 13/13; RemInputs correction2 matched `b96517c9cfb8e3f35622242b61a135cbb42b784f5c8b8245081d58e30b4280ac` and passed 16/16.
- Revision1’s internal manifest passed 47/47 inside Revision1.
- Revision2’s internal MANIFEST-2 passed 59/59 inside Revision2.
- The seven historical nested manifests passed with counts 26, 11, 18, 5, 13, 13, and 48.
- No `.pyc`, `.pyo`, or `__pycache__` artifact existed after the review.

### Changed-range inspection

The current object was diffed against Revision2. Fourteen Revision2 paths changed and two source paths were added, consistent with the builder declaration.

Changed implementation paths:

- `admission.py`
- `buffer_reference.py`
- `consumers.py`
- `generation_reference.py`
- `lifetime.py`
- `lifetime_reference.py`
- `recovery.py`
- `worker_authority.py`

Added implementation paths:

- `snapshot_reference.py`
- `migration_reference.py`

Changed tests:

- `test_admission.py`
- `test_generation.py`
- `test_lifetime.py`
- `test_worker_authority.py`

The remaining changed paths were A16 and the amendment document. All changed ranges were inspected against Revision2, and their callers, protocols, state/value types, exports, and neighboring unchanged implementation were traced.

### Executed gates and attacks

Using Python 3.14 with bytecode disabled:

- Focused contract discovery: **97/97 passed**.
- `tools/check_product.py`: **5/5 passed**.

I also retraced the prior counterexample classes rather than treating passing tests or prior closure reports as proof. Two inline reference-state attacks produced current failures:

1. Refused first handoff followed by a second dequeue:

   `HANDOFF1_PUBLISHED 0 HANDOFF1_STATE refused SECOND_DEQUEUE_STATE acquired COUNT 1`

2. Participant lifecycle attacks:

   - Pre-activation participant and handle surviving activation:

     `PREACTIVATION_PARTICIPANT_AND_HANDLE_SURVIVE active acquired 1`

   - A fully closed participant blocking a later drain/migration:

     `CLOSED_PARTICIPANT_STILL_BLOCKS closed deadline_exceeded draining_old 0`

## 1. Findings

### [P2-1] Refusing an unpublished handoff advances the delivered cursor and removes the FIFO head

**Location:** `src/garns/backends/contracts/lifetime_reference.py:360-388`, especially the unconditional handoff completion at lines 379–385; `src/garns/backends/contracts/buffer_reference.py:266-276`.

**Root cause:** `ReferenceLifetimeRegistry.complete()` invokes `complete_handoff()` whenever the lease record has a handoff envelope, irrespective of whether the terminal result represents successful caller-visible publication. `complete_handoff()` then removes the FIFO head and advances `delivered_through` and `last_delivered_advancement`. It has no outcome or publication proof with which to distinguish delivery from refusal, cancellation, or failure.

**Violated invariant:** Produced and delivered progress are separate. Only successful publication of the exact current FIFO head may advance delivered progress. Refusal before publication must not make the range appear delivered or permit a later range to overtake it.

**Reproduction:**

1. Register a buffer and enqueue two contiguous envelopes `(0,1]` and `(1,2]`.
2. Dequeue the first envelope into a handoff lease.
3. Complete that lease as `REFUSED` before any validate/publication operation.
4. `complete()` nevertheless calls `complete_handoff()`.
5. The first head is popped, delivered progress advances to 1, and the second envelope can be acquired.

The observed state was:

`HANDOFF1_PUBLISHED 0 HANDOFF1_STATE refused SECOND_DEQUEUE_STATE acquired COUNT 1`

Thus the implementation records delivery despite zero publication and exposes the successor range.

**Impact:** A refused or failed range can be skipped permanently while accounting reports it as delivered. Later work can proceed across the resulting gap, defeating FIFO delivery, recovery accounting, and the amendment’s conservation claim.

**Classification:** This is not a new architectural root. It is the residual of correction1 F2 and keeps `ReviewCode-2 P2-2` and `ReviewState-2 P2-1` open. The accepted design already requires separate produced/delivered cursors and exact head ownership.

**Required correction:** Make handoff settlement outcome- and publication-aware. Only a proven caller-visible successful publication may remove the exact current head and advance delivered progress. Refusal, cancellation, or pre-publication failure must either retain/requeue the exact head or retire the registration into an explicit refetch/recovery state that prevents subsequent dequeue until continuity is restored. Duplicate terminal calls must remain idempotent.

**Closure test:**

- Enqueue two contiguous envelopes.
- Acquire the first and fail/refuse it before publication.
- Assert delivered progress does not advance and the second envelope cannot dequeue as contiguous delivered work.
- Retry or recover the first, publish it successfully, and assert progress advances exactly once.
- Repeat completion and prove no duplicate advancement.
- Exercise close and migration while the failed head is retained, proving conservation and explicit recovery behavior.

### [P2-2] Participant membership is constructor-only rather than an activation-bracketed join/leave lifecycle

**Location:** `src/garns/backends/contracts/lifetime_reference.py:104-125`, `162-174`, and `654-678`; `src/garns/backends/contracts/generation_reference.py:223-228`; `src/garns/backends/contracts/lifetime.py:262-281`.

**Root cause:** `ReferenceLifetimeRegistry.__init__()` registers a generation participant unconditionally, including while the coordinator is unactivated. Admission checks coordinator binding/current generation but do not reject authority created before the activation fence. At the opposite end of the lifecycle, final runtime close never unregisters the participant. The reference coordinator exposes `register_participant()` but no matching unregister operation, and the formal `SharedGenerationCoordinator` protocol cannot require a complete join/leave pair.

**Violated invariant:** Under the accepted W2 overlay §§7 and 8.2, a participant joins only through the valid ACTIVE/ACTIVE_UNUSED first-open handshake. Once locally closed, it remains registered only while retained work exists, then final close unregisters it. Membership used for a frozen migration attempt must reflect live, valid participants without permitting topology mutation inside the attempt.

**Reproduction A — authority crosses activation:**

1. Construct an unactivated coordinator.
2. Construct a lifetime registry; its constructor immediately registers a participant.
3. Create an admission handle before activation.
4. Activate the coordinator and perform the first open.
5. Use the pre-activation handle.

The handle acquired successfully:

`PREACTIVATION_PARTICIPANT_AND_HANDLE_SURVIVE active acquired 1`

The activation boundary did not invalidate the pre-activation participant or admission authority.

**Reproduction B — closed participant becomes a permanent migration obligation:**

1. Activate a coordinator with two participant registries.
2. Fully close one registry’s runtime until its local state is `CLOSED`.
3. Begin drain/migration.
4. Have the remaining live participant acknowledge the attempt.
5. Attempt migration with no remaining retained work in the closed registry.

The attempt still waited for the closed participant and expired:

`CLOSED_PARTICIPANT_STILL_BLOCKS closed deadline_exceeded draining_old 0`

**Impact:** Authority can be minted on the wrong side of activation, and a participant that has completed its local lifecycle can remain forever in future frozen acknowledgement sets. The former weakens the one-time activation fence; the latter can make all later drains/migrations fail despite no retained work.

**Classification:** This is a new concrete root relative to the prior report IDs, but it is bounded, not a new architectural blocker. The accepted architecture already specifies when participants join, how long they remain, and when they leave. The code and protocol omitted that lifecycle bracketing.

**Required correction:** Add an exact participant join/leave contract to the formal protocol and reference coordinator. Reject participant registration and admission before a valid activation/first-open fence, or make first-open and join one atomic operation. Final `CLOSED` transition must unregister the exact participant only after all retained permits, handoffs, and close work are terminal. Joining or leaving during a frozen drain attempt must be rejected or assigned prospectively without mutating that attempt’s required set. Stale, duplicate, copied, and cross-participant unregister tokens must refuse without effect.

**Closure test:**

- Attempt registry construction/admission before activation and prove no reusable authority crosses activation.
- Activate with two participants; fully close one after retained work reaches zero; prove it unregisters and no longer blocks a later drain/migration.
- Attempt unregister while retained work exists and prove refusal without membership loss.
- Exercise duplicate, stale-generation, copied, and cross-participant unregister attempts.
- Begin a drain, then attempt participant join and leave; prove the frozen attempt topology is unchanged.
- Complete a valid close/unregister and prove later attempts include exactly the remaining live participants.

## 2. Invariant analysis

### Initial-review closure table — all 18 IDs

| Prior report ID | Prior subject | Current result |
|---|---|---|
| ReviewCode P2-1 | F1 callback-bearing product path | **CLOSED.** Ordinary effect callbacks are absent; fixed products and explicit steps are used. |
| ReviewCode P2-2 | R2 unpinned parameter input | **CLOSED.** Consumption uses one pinned parameter input. |
| ReviewCode P2-3 | F1/R3 ordering and publication | **CLOSED for the original counterexample.** Reservation/commit ordering is explicit; P2-1 above is the separate F2 handoff-settlement residual. |
| ReviewCode P2-4 | F8/R4 stale authority after epoch change | **CLOSED.** Epoch changes invalidate prior authority. |
| ReviewCode P2-5 | R5/F2 provenance and cross-owner completion | **CLOSED for the original shortest counterexample.** Exact owner/token checks reject cross, stale, and copied provenance. P2-1 concerns the outcome of a correctly owned handoff. |
| ReviewCode P2-6 | F9 caller-supplied worker identity | **CLOSED.** Dequeue and effect execution consult the trusted current-worker hook. |
| ReviewCode P2-7 | R7 privileged nested/total kinds | **CLOSED.** Independent privileged kinds were removed. |
| ReviewCode P2-8 | R8 close without prior drain | **CLOSED.** Drain is required before final close. |
| ReviewCode P2-9 | F3/R9 split activation fences | **CLOSED.** Admission and generation use the same activation fence. |
| ReviewState P2-1 | R10 unsealed permit lifecycle | **CLOSED.** Exact sealed permit provenance controls terminal operations. |
| ReviewState P2-2 | R11 local close with queued buffers | **CLOSED for the prior sequence.** Queued work participates in close/drain state. |
| ReviewState P2-3 | R5 cross-provenance mutation | **CLOSED.** Cross-owner and stale tokens refuse before mutation. |
| ReviewState P2-4 | F1/R3 expanded revocation/publication ordering | **CLOSED.** Committed state precedes outward product visibility and revocation barriers are explicit. |
| ReviewState P2-5 | F3/R9 activation-fence divergence | **CLOSED.** One activation proof is retained across the path. |
| ReviewState P2-6 | R12 unproved indeterminate exit | **CLOSED.** Indeterminate/no-effect exits carry proof. |
| ReviewState P2-7 | R7 privileged child command | **CLOSED.** Child actions are derived from parent authority. |
| ReviewState P2-8 | R2 parameter repinning | **CLOSED.** Parameters remain pinned through the operation. |
| ReviewState-Supplement P2-1 | R13 owner transfer mutates before validation | **CLOSED.** Transfer validates before mutation. |

### Correction1 closure table — all 13 IDs across all four namespaces

| Prior report ID | F-map | Current result |
|---|---:|---|
| ReviewCode-2 P2-1 | F1 | **CLOSED.** Callback-free fixed products and commit-before-return remain enforced. |
| ReviewCode-2 P2-2 | F2 | **OPEN as P2-1.** Refusal still completes the FIFO head as delivered. |
| ReviewCode-2 P2-3 | F3 | **CLOSED.** The same activation fence is retained. |
| ReviewState-2 P2-1 | F2 | **OPEN as P2-1.** Produced/delivered accounting still conflates failed completion with delivery. |
| ReviewState-2 P2-2 | F4 | **CLOSED.** Attempt identity, frozen participant set, and acknowledgements are explicit. |
| ReviewState-2 P2-3 | F5 | **CLOSED.** Snapshot candidates are sealed from candidate rows and watermark evidence. |
| ReviewState-2 P2-4 | F6 | **CLOSED.** Nested commands are derived from parent authority. |
| ReviewState-2 P2-5 | F7 | **CLOSED.** Successor generation is exactly current generation plus one. |
| ReviewState-2 P2-6 | F1 | **CLOSED.** Fixed products cannot run ordinary callbacks after return. |
| OriginCodeClosure-1 P2-1 residual | F1 | **CLOSED.** Commit and outward product construction are correctly ordered. |
| OriginCodeClosure-1 P2-6 residual | F9 | **CLOSED.** Actual trusted-current-worker state, not caller identity, gates execution. |
| OriginCodeClosure-1 P2-3 bounded route | F10 | **CLOSED.** Final target-queue barrier is explicit. |
| OriginStateClosure-1 State-Closure-P2-1 | F8 | **CLOSED.** Attempt-bound no-effect proof covers both DRAINING and pre-effect MIGRATING. |

### F1–F10 attack summary

| Invariant | Attack result |
|---|---|
| F1 — callback-free products, reservation/commit, publication order | Held. Fixed `ClosedStepProduct`-style values contain no executable callback; state commits before outward visibility. |
| F2 — FIFO produced/delivered/head accounting | **Failed.** P2-1 reproduces advancement after refusal with zero publication. |
| F3 — same activation fence | Held for normal admitted operations; P2-2 separately shows participant membership itself is not correctly bracketed by that fence. |
| F4 — exact migration attempt and frozen participant acknowledgements | Held once membership exists. P2-2 shows stale membership can enter later attempts. |
| F5 — candidate production/consumption from sealed rows and cursors | Held. Arbitrary replacement rows/cursors were rejected by provenance and seal checks. |
| F6 — parent-derived commands | Held. No independent nested/total privileged command path remained. |
| F7 — successor generation | Held. Migration accepts only exact generation `g + 1`. |
| F8 — proof-bearing no-effect | Held from DRAINING and pre-effect MIGRATING; retries remain attempt-bound. |
| F9 — trusted current worker | Held. Caller identity could not substitute for the runtime current-worker check. |
| F10 — final target-queue barrier | Held. Target validation requires the final queue barrier before effect. |

### Additional attacks that held

- Reserved structural keys, result-field roles, nested-owner markers, and normative vectors remained lossless through current model/value construction.
- Trusted lexical plans did not expose a raw plan, root, closure, or legacy handshake fallback through the executable protocols inspected.
- Admission and lease handles remained issuer-owned and provenance-bound; copied, stale, and cross-owner terminal operations refused before mutation.
- Effect ordinal replay was refused.
- Snapshot consumption required sealed candidate evidence rather than arbitrary rows or a caller-selected cursor.
- Migration required exact attempt identity, exact successor generation, frozen acknowledgements, proof-bearing no-effect exits, and final target-queue validation.
- Close operations retained permits/work through terminalization; the defect is the missing participant leave after that terminal point, not premature loss of retained work.
- Current tests exercise actual reference transitions rather than only fixtures, but their passing status did not cover the two failing sequences above.

## 3. Risks and next action

The two blockers are bounded code/interface corrections inside the accepted architecture:

- P2-1 needs terminal-outcome-aware handoff settlement and continuity tests.
- P2-2 needs the already-specified activation-bracketed participant join/leave pair in both protocol and reference behavior.

Neither finding asks for a production backend, database, deployment activation, public API freeze, credentials, external-write capture, cross-process locking, or other explicitly deferred work. The reference implementation remains the evidence surface, so passing focused/product gates is useful but cannot substitute for the missing state sequences.

The single next action is to produce a bounded revision resolving P2-1 and P2-2 exactly as specified, add the closure tests, regenerate the controlled manifest tuple, and rerun the two final read-only axes.
