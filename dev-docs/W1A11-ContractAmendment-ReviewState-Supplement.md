# W1A11-ContractAmendment — STATE-AXIS SUPPLEMENTAL REVIEW

**Review object:** Same initial 47-file filesystem tuple, manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`; no remediation or source changes.  
**Supplemental evidence:** `dev-docs/W1A11-ContractAmendment-ManagerCounterexamples.md`, SHA-256 `73be6bc196915682c17cc28cbc860ef4ec1ddaf954d78d8454907e61dcf1d76d`.  
**Date:** 2026-10-04  
**Axis:** State-machine mutation and publication-barrier adversity. Read-only originating review; no current peer report was read.

**Verdict: NO-GO** — one manager counterexample extends initial State P2-4; the other is one additional independent bounded P2, `State-Supp-P2-1`. The initial pre-commit to GO now also requires closure of `State-Supp-P2-1`.

---

## 0. Evidence and tuple verification

At both start and end, the manifest hash remained exact with 47/47 entries. Inputs 9/9, Control 3/3, Baseline 120/120, ReadOnly 111/111, and ProductGuard 614/614 verified with zero failures. The controlling amendment, execution brief, ownership extension, and accepted W2 documents retained their pinned hashes.

I reproduced both sequences using the allowed Python 3.14 `-B` environment with bytecode disabled. No files were written.

## 1. Counterexample classification

### Revoked lease still publishes — covered by initial State P2-4, not a new root

**Location:** `src/garns/backends/contracts/lifetime_reference.py:218-245,448-451`.

Exact manager reproduction:

1. Acquire an `EXECUTE` lease.
2. Call `revoke_generation()`.
3. Call `run_plan_step(..., PlanStep.PUBLICATION, ...)`.

Observed:

```text
REVOKED_ACQUIRED_PUBLICATION ['published'] 1 publishing
```

I also isolated generation revalidation from the already-reported illegal direct `ACQUIRED -> PUBLISHING` edge by first running `LOWER`, producing legal `RUNNING`, then revoking and publishing:

```text
REVOKED_RUNNING_PUBLICATION ['published'] 1 publishing
```

The callback ran and `publications` advanced despite the admission being `REVOKED` and the registry epoch changing.

This is the same root as initial State P2-4: publication is not implemented as one authoritative linearization point revalidating every barrier. That finding already covered incomplete publication-state validation and alternate publication bypasses; this sequence adds the missing admission-state, registry-epoch, and pinned binding/generation checks. It is a **bounded extension of the existing P2-4 correction**, not an independent architecture root.

**Required correction:** The unique publication transition must validate `RUNNING`, exact owner/live lease, current authority, admission state/epoch, pinned binding/generation, coordinator state, and local fences before invoking the callback or recording visibility. `revoke_generation()` must either refuse while live leases exist or atomically contain/fence every affected lease; it cannot create a revoked-but-publishable state.

**Expanded P2-4 closure test:** Pause a legal `RUNNING` lease, then independently revoke its admission, advance registry epoch, change coordinator binding/generation, or hard-fence its ancestry. Every publication attempt must produce zero callback calls, zero publication-count change, and retained/refused containment as appropriate. Graceful-drain cases must separately prove only the explicitly pinned old-generation path remains legal before final fencing.

### [State-Supp-P2-1] Rejected queued transfer mutates ownership before validating the state

**Location:** `src/garns/backends/contracts/lifetime_reference.py:247-257`.

**Classification:** Independent **bounded P2**; no interface or architectural redesign is required.

`transfer_owner` assigns `record.owner = new_owner` before checking that `queued=True` is legal only from `ACQUIRED`. Reproduction:

1. Acquire a lease and run `LOWER`, producing `RUNNING`.
2. Call `transfer_owner(lease, old, new, queued=True)`.
3. The method raises `ValueError`.
4. Retry a guarded step with each owner.

Observed:

```text
REJECTED_TRANSFER ValueError running
OWNER_AFTER_REJECTION old refused ContractRefusal
OWNER_AFTER_REJECTION new accepted new
```

The rejected transition preserved the visible lease state as `RUNNING` but silently transferred authority to `new`. This is independent of initial P2-1 through P2-8: none covered mutation-before-validation in compare-and-transfer.

The violated invariant is that wrong owner or illegal transition refuses without changing owner, state, charges, or counts. Impact is involuntary loss of the authoritative owner, acceptance of an owner from a failed operation, and potential permanent retention if the caller trusts the exception and discards `new`.

**Required correction:** Validate exact expected owner, non-null new owner, current lease state, and the complete requested transition before mutating either owner or state. Commit both fields together only after all checks pass.

**Closure test:** Enumerate lease states against `queued=True/False`. For every illegal transition, snapshot owner, state, completion, resource charges, and coordinator count; assert the exception leaves all unchanged, the prior owner remains usable, and the proposed owner remains rejected. Legal `ACQUIRED -> QUEUED` and `QUEUED -> RUNNING` transfers must still change owner/state exactly once without recharging ancestry.

## 2. Next action

Add the expanded P2-4 publication/revocation vectors and `State-Supp-P2-1` to the single consolidated remediation plan. The originating State re-review must rerun these exact counterexamples on the corrected tuple; green aggregate tests alone are not closure.
