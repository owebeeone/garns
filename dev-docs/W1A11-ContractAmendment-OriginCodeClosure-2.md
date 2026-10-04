# W1A11-ContractAmendment — ORIGINATING CODE CLOSURE REVIEW 2

**Intended file:** `dev-docs/W1A11-ContractAmendment-OriginCodeClosure-2.md`  
**Review object:** final correction 2, complete 71-file manifest SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; amendment SHA-256 `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`; DRAFT-3 SHA-256 `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`; RemPlan-2 SHA-256 `749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c`; RemInputs-2 SHA-256 `b96517c9cfb8e3f35622242b61a135cbb42b784f5c8b8245081d58e30b4280ac`, 16 entries.  
**Comparison objects:** preserved Revision2 complete 59-file manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`, then initial Revision1 complete 47-file manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`.  
**Date:** 2026-10-04  
**Axis:** originating Code reviewer, final focused closure of the nine original Code P2 findings, especially the three correction-1 residuals. Independent, adversarial and read-only.

**Focused verdict: GO.** All nine original Code findings are closed on the frozen MANIFEST-3 tuple. The three previously open residuals—raw-Plan frame/traceback escape, assigned-worker impersonation and publication to a closed destination queue—refused under direct probes with conserved state and counts. No new architectural or bounded Code root was found in the authorized correction range.

This is focused originating closure, not overall amendment acceptance. Fresh full Code/State review and the manager’s final gate remain independently required.

## Prior-finding closure table

| Original finding | Final direct evidence | Status |
|---|---|---|
| Code P2-1 — arbitrary Plan-taking continuation | Consumer issuance no longer accepts a callback. A direct raising callable passed to `run_plan_step` refused before invocation; its effect count stayed zero and its traceback contained no direct `Plan` local. A valid fixed consumer returned only `ClosedStepProduct`. | **CLOSED** |
| Code P2-2 — split parameter sets | `execute`, `consistent_snapshot` and `subscribe` still have no second `parameters` argument. A lease acquired with `tenant=A` returned only the pinned detached `{"tenant": "A"}` value. | **CLOSED, preserved** |
| Code P2-3 — unordered/repeated publication | Direct publication from `ACQUIRED`, duplicate publication and backward work all refused. One valid publication committed exactly once. A committed `PUBLISHING` lease could not be relabeled `REFUSED` and completed only as `SUCCEEDED`. | **CLOSED** |
| Code P2-4 — old authority after no-effect reopen | Exact attempt/barrier/proof reopen invalidated both the old handle and old lease; a newly admitted handle acquired successfully. | **CLOSED, preserved** |
| Code P2-5 — unlinked buffer provenance | Copied, wrong-admission and replayed envelopes refused. Exact dequeue exchanged buffer ownership for one handoff lease; terminal handoff completion returned the global count to zero. | **CLOSED, preserved** |
| Code P2-6 — command/worker absent from ownership | Wrong tuples remain rejected. The issuing task’s otherwise exact dequeue attempt refused without changing `QUEUED` state or count. After genuine worker dequeue, switching back to the issuer made `run_effect` refuse without consuming the ordinal; the assigned worker then consumed it once. | **CLOSED** |
| Code P2-7 — privileged kinds default to QUERY | `GOVERNED_MUTATION`, `MIGRATION`, `NESTED_FETCH` and `TOTAL_FETCH` are absent as independently acquirable operation kinds. Derived child/total commands remain parent-owned and share one permit. | **CLOSED, preserved** |
| Code P2-8 — close finalization from OPEN | Direct finalization from `LOCAL_OPEN` refused without mutation. After close start, selected-ancestry acquisition refused while an unrelated peer acquired normally. | **CLOSED, preserved** |
| Code P2-9 — proofless activation recovery | `None` and stale proof inputs refused without state change; exact proof returned to `UNACTIVATED`; the used activation epoch remained unavailable. | **CLOSED, preserved** |

## Correction-1 residual closure

### Raw-Plan frame and traceback escape

`consumers.py` now stores only a fixed label for `ClosedPlanConsumer`. `ReferenceConsumerIssuer.issue` has no effect/callback argument, and `consume` constructs and returns closed data without invoking caller code.

The original and adjacent probes established:

- passing an ordinary callable to `run_plan_step` refuses at issuer ownership validation;
- a callable that would raise and retain its argument was never invoked;
- callback registration through `issue_consumer("x", callback)` raises `TypeError`;
- the refusal traceback exposed no direct `Plan` local;
- a valid call returned only `ClosedStepProduct`;
- publication commitment and counters are complete before the product becomes outwardly observable.

Derived child/total work uses sealed `ClosedDerivedCommand` identities with issuer-owned records and one-shot ordinals; it introduces no callback into the Plan-holding path.

### Actual assigned-worker authentication

`ReferenceLifetimeRegistry.dequeue_worker` now requires `RuntimeAuthority.is_current_task(worker)` before changing queued ownership. `WorkerAuthorizationIssuer.run_effect` repeats the trusted current-task check immediately before liveness validation, ordinal consumption and effect.

The exact former counterexample now behaves correctly:

1. dispatching caller creates the exact command/worker/authorization tuple;
2. while the caller remains current, dequeue refuses;
3. lease state remains `QUEUED` and the coordinator count is unchanged;
4. the assigned worker dequeues successfully;
5. switching back to the caller makes effect execution refuse with zero effects;
6. switching to the assigned worker allows one effect;
7. the previously refused attempt did not consume its ordinal.

Original public-context validity remains tied to the issuing task; worker identity is checked separately and does not impersonate that context.

### Closed destination queue

Initial and refresh candidate records now bind their exact subscription and queue. `_validate_queue_target` requires:

- the lease’s exact subscription ancestry;
- exact subscription and delivery-queue kinds;
- the queue to descend from that subscription;
- both local resources to remain `LOCAL_OPEN`;
- the destination’s `QueueState` to remain `OPEN`.

The focused race created a valid initial snapshot candidate, then hard-closed the destination queue before registration publication. `register_subscription` refused, publication and coordinator counts were unchanged, and the lease moved to `CONTAINED`. Thus candidate production cannot preserve authority to publish after the target fence changes.

## Changed-range analysis

Compared with Revision2, MANIFEST-3 contains:

- 14 changed common paths;
- 12 added paths;
- zero removed paths.

The changed implementation surface is the authorized amendment/A16 plus:

- `admission.py`
- `buffer_reference.py`
- `consumers.py`
- `generation_reference.py`
- `lifetime.py`
- `lifetime_reference.py`
- `recovery.py`
- `worker_authority.py`
- four focused contract-test modules

The two added source modules are cohesive:

- `snapshot_reference.py` owns sealed initial/refresh candidate records;
- `migration_reference.py` owns sealed attempt, participant, acknowledgement and no-effect identities.

The remaining additions are remediation evidence and controls. The 611-line Revision2 registry grew because it coordinates the same admission/lease/resource/publication/buffer/close state graph; the amendment records the exception and a concrete revisit point. I found no additional Code blocker arising from that retained ownership boundary.

## Independent execution evidence

Using Python 3.14 with bytecode disabled and the pinned cached Lark 1.3.1:

- focused contract suite: **97/97 passed**;
- full suite: **200/200 passed**;
- product checks: **5/5 passed**;
- `ast.parse`: **25/25 manifest Python files passed**.

The inherited SQLite `ResourceWarning`s remained visible in the full suite; no warning filter was used. Green tests were not treated as closure—the nine explicit inline probes above supplied the closure evidence.

## Tuple and guard verification

At both start and end:

- MANIFEST-3 matched SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`;
- all 71 MANIFEST-3 entries verified;
- amendment, DRAFT-3, RemPlan-2 and RemInputs-2 matched their exact hashes;
- RemInputs-2 verified 16/16;
- RemInputs-1 verified 13/13;
- original Inputs verified 9/9;
- Control verified 3/3;
- Baseline verified 120/120;
- ReadOnly verified 111/111;
- ProductGuard verified 614/614;
- Revision2 MANIFEST-2 verified 59/59 from inside Revision2;
- Revision1 manifest verified 47/47 from inside Revision1;
- bytecode/cache inventory remained zero.

No source, test, documentation, manifest or workspace file was written. No helper agent, Git/GWZ operation, service, network access, dependency change or bytecode-producing command was used.

## New-root classification and disposition

No new architectural root was found. No new bounded root was found. The final architecture-correction limit is therefore not triggered by this focused closure.

All nine originating Code P2 findings are closed on MANIFEST-3. The amendment remains a deterministic single-process reference contract only: it does not prove real worker authentication, database snapshot provenance, durable recovery, physical fencing, locks, cross-process coordination, crash behavior or production backend/runtime integration.

