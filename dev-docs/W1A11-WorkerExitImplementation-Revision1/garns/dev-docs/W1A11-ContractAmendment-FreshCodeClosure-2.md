# W1A11-ContractAmendment — FOCUSED CODE ORIGINATING CLOSURE 2

**Review object:** Corrected 71-file filesystem tuple at `dev-docs/W1A11-ContractAmendment-MANIFEST-3.sha256`, SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; controlling amendment SHA-256 `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`; DRAFT-3 SHA-256 `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`; remediation 2 candidate, not accepted.  
**Comparison object:** Preserved Revision2 59-file manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`, verified from inside `W1A11-ContractAmendment-Revision2/`.  
**Date:** 2026-10-04  
**Scope:** Focused originating closure of correction-1 Code P2-1 through P2-3. Independent, adversarial, read-only. No current peer, Review-3, Origin-2 report, or current review prompt was read.

**Verdict: NO-GO** — Code P2-1 and P2-3 are closed, but Code P2-2 remains open through one bounded P2 failure path. I pre-commit to GO on a bounded revision that resolves the finding below as specified.

---

## 0. Evidence base

I read the complete RemPlan-2, SHA-256 `749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c`, its complete 16-entry RemInputs-2 manifest, the current amendment and DRAFT-3, and the closure-relevant current source and tests. I compared every changed Revision2 path and both authorized additions by hunk inventory, then inspected the complete consumer, buffer, recovery, generation, and relevant lifetime-registry/test transitions.

The authorized Python 3.14 focused suite passed 97/97 and `tools/check_product.py` passed 5/5. The manager’s reported full 200 and multi-interpreter results are corroboration only, not closure evidence used for this verdict.

Direct probes established:

```text
CALLBACK_REFUSED True True
CALLBACK_REFUSED True True
CALLBACK_FREE_SIGNATURE (label: 'str') -> 'ClosedPlanConsumer'
DUPLICATE_STEP_REFUSED True
FIFO_START_COUNT 2
LATER_FIRST_REFUSED True 2
FIFO_SUCCESS_COUNT 0
MISMATCHED_FENCE_REFUSED True True
SAME_FENCE_WITHDRAWAL unactivated None
```

The adverse handoff sequence instead produced:

```text
REFUSED_HEAD_COUNT 1
SECOND_AFTER_REFUSED_HEAD accepted acquired 1
REFUSED_FIRST_SECOND_PUBLISHED 4 0 refused succeeded
```

At both review boundaries, the current manifest retained its exact hash and verified 71/71. Inputs verified 9/9, Control 3/3, Baseline 120/120, ReadOnly 111/111, ProductGuard 614/614, RemInputs-1 13/13, and RemInputs-2 16/16. Revision2 verified 59/59 and Revision1 47/47 from inside their archives. The seven historical nested baseline manifests verified 26/26, 11/11, 18/18, 5/5, 13/13, 13/13, and 48/48. No file, bytecode, generated evidence, dependency, service, database, Git, or GWZ state was modified.

## 1. Finding

### [P2-1] A refused head handoff is recorded as delivered, allowing the next FIFO range to publish across a delivery gap

**Location:** `src/garns/backends/contracts/lifetime_reference.py:360-387`; `src/garns/backends/contracts/buffer_reference.py:219-276`.

`ReferenceLifetimeRegistry.complete` calls `complete_handoff` for every terminal handoff outcome, including `REFUSED` and `CANCELLED_CONFIRMED`. `complete_handoff` unconditionally removes the active head and advances `delivered_through` to that envelope’s `observed_through`.

Reproduction:

1. Publish sequential envelopes `(0,1]` and `(1,2]`.
2. Dequeue the first envelope, producing the sole active head.
3. Complete that handoff directly as `REFUSED`, without `VALIDATE`, `PUBLICATION`, or caller-visible delivery.
4. Dequeue the second envelope.

The second dequeue succeeds because the refused first handoff advanced `delivered_through` to 1. It can then publish and complete successfully, returning the coordinator count to zero even though range 1 was never delivered.

This violates RemPlan-2 F2’s selected ordered-delivery semantics. `delivered_through` cannot advance on a refused, cancelled, fenced, expired, or otherwise unpublished handoff. The impact is a silent delivery gap represented as complete FIFO progress, allowing later state to become caller-visible without the required preceding delivery or a typed refetch transition.

Advance `delivered_through` and remove the active FIFO head only when the exact handoff has committed publication and completes `SUCCEEDED`. A non-successful active handoff must conservatively choose a closed outcome, such as retiring the registration and invalidating/releasing all queued successors exactly once with refetch required. It must not make the next envelope dequeueable merely by recording failure as delivery.

Closure tests must cover an active head completing as:

- `REFUSED` before any step;
- `CANCELLED_CONFIRMED` where legally reachable;
- `REFUSED`/contained after authority expiry, hard fence, or failed publication barrier;
- `SUCCEEDED` only after exact publication.

For every non-success path, assert unchanged `delivered_through`, no later-envelope handoff/publication, explicit registration refetch/retirement, and exact permit/count conservation.

## 2. Prior three-ID closure table

| Prior Code ID | Status | Independent closure result |
|---|---|---|
| Code P2-1 — callback plan escape and reentrant step rollback | **Closed** | `issue_consumer` accepts only `label`; frame/traceback callback arguments raise `TypeError` before state/count mutation. `consume` invokes no external code while holding the plan. The former reentrant route is absent, and duplicate sequential steps refuse. |
| Code P2-2 — scalar cursor wedges multiple accepted buffers | **Open via current P2-1** | The success path is repaired: separate produced/delivered frontiers, later-before-earlier refusal, one active head, two FIFO successes, and count `2 → 0` all hold. The failure path falsely treats a refused head as delivered and admits the second range. |
| Code P2-3 — unused withdrawal accepts a different activation fence | **Closed** | Successful activation retains its physical-fence digest. A different-fence withdrawal refuses without changing activation or epoch; an exact same-fence withdrawal succeeds once. |

## 3. Changed-range and architecture classification

Revision2 comparison found exactly fourteen modified prior paths plus the two authorized new modules.

For the originating three findings:

- `consumers.py`, `admission.py`, `lifetime_reference.py`, and admission tests remove the caller callback and independent child/total lease routes. The architectural Code P2-1 correction holds.
- `buffer_reference.py`, `lifetime_reference.py`, generation permit exchange, and lifetime tests implement produced/delivered frontiers and ordered head ownership. The chosen architecture is coherent, but its non-success terminal branch is incomplete.
- `generation_reference.py`, `recovery.py`, and generation tests retain and compare the activation fence. Code P2-3 holds.
- A16 and the amendment accurately describe the intended callback-free, FIFO, and same-fence corrections, except that the current implementation overstates successful FIFO completion for refused handoffs.

The remaining RemPlan-2 F4–F10 changes are outside this focused originating three-ID closure and receive no acceptance verdict here.

The remaining blocker is **bounded**, not architectural: it requires outcome-sensitive handoff finalization inside the existing FIFO design. No new architectural root was found, so the correction-2 architectural ceiling does not itself force an operator STOP. Any proposed interface or architecture redesign would exceed this report’s bounded pre-commit and would require the mandated operator decision.

## 4. Limits and next action

This remains deterministic single-process reference evidence. It proves no production database provenance, async/thread behavior, durable recovery, cross-process coordination, physical fencing, worker authentication, activation operation, or public API surface. Those deferrals are unchanged and are not findings.

Apply one bounded correction to distinguish successful delivered completion from refused/cancelled/contained handoff termination, add the specified two-envelope failure-path tests, freeze a new exact tuple, and rerun focused originating and independent review.

