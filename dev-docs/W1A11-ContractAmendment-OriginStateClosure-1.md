# W1A11-ContractAmendment — ORIGINATING STATE CLOSURE 1

**Review object:** Remediation 1, complete 59-file filesystem tuple at `W1A11-ContractAmendment-MANIFEST-2.sha256` SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`; controlling amendment SHA-256 `21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b`; DRAFT-2 SHA-256 `d5c45f54f4fb1ed6105dd227050229b6a2c35b7517208df7156f36a041d4e58c`; not accepted; 2026-10-04.  
**Remediation authority:** RemPlan SHA-256 `7a8d145e29f5a1c2de01d91a205bf2689b974763795a73046d0c4db39712aa53`; RemInputs SHA-256 `6abcd861c58160bec0c2124a0dda680456ff6dcf0e06eff05110d234cb5bae63`.  
**Baseline for comparison:** Preserved Revision1 archive, manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`, verified from inside the archive at 47/47.  
**Axis:** Focused originating State closure: transitions, ownership, permit conservation, barriers, recovery grammar, and exact counterexample retrace. Read-only; no current-round peer/fresh/origin reports or prompts were read.

**Verdict: NO-GO.** The eight original State P2 findings, the expanded P2-4 revocation vector, and `State-Supp-P2-1` are closed on their original counterexamples and adjacent tested paths. One new architectural P2 blocks acceptance: proof-free pre-effect migration reopen contradicts the accepted recovery grammar and RemPlan R12.

---

## 0. Evidence and tuple verification

I read the complete RemPlan and DRAFT-2, inspected the complete current amended contract/reference implementation, compared its changed ranges with the exact Revision1 archive, and retraced every originating State finding with current tests and direct inline state-machine probes. Green builder claims were not treated as closure.

At both START and END:

- MANIFEST-2 hash was exact and all 59/59 entries verified.
- RemInputs verified 13/13.
- Original Inputs verified 9/9.
- Control verified 3/3.
- Baseline verified 120/120.
- ReadOnly verified 111/111.
- ProductGuard verified 614/614.
- Revision1 manifest hash remained exact and verified 47/47 from inside `dev-docs/W1A11-ContractAmendment-Revision1/`.
- The amendment, DRAFT-2, RemPlan, and RemInputs retained the hashes stated above.

The allowed Python 3.14 focused suite passed 85/85. I also ran one inline `-B` adversarial probe covering all eight prior State findings, the expanded revocation vector, the owner-transfer supplement, and the new reopen counterexample. No files were written; the final inventory contained no `__pycache__` or `.pyc`.

The manager’s 85-focused/188-full/5-product matrix was treated only as corroborating execution evidence, not as finding closure.

---

## 1. Changed-range analysis

Relative to preserved Revision1, the implementation changed exactly the RemPlan-authorized surface:

- Modified contract/design files: A16, the amendment, `admission.py`, `generation_reference.py`, `lifetime.py`, `lifetime_reference.py`, `model.py`, `protocols.py`, and `worker_authority.py`.
- Modified focused tests: admission, core contracts, generation, lifetime, and worker authority.
- Added: `consumers.py` (129 lines), `buffer_reference.py` (284 lines), and `recovery.py` (104 lines).

The archive-to-current diff contained 14 modified files and three new files, all in the remediation allowlist. Hunk inspection showed the intended concentration: closed consumers and products; operation grammar; sealed permit identity; activation/migration recovery; registry epochs and barriers; exact buffer provenance; close finalization; worker tuple authority; and their tests. No unrelated production, grammar, generator, or accepted-source range was changed.

The new blocker lies inside the authorized R12 recovery range, not in an unowned edit: `generation_reference.py:189-205` introduced drain/reopen behavior, while `recovery.py` added post-effect and activation proof shapes but no proof shape or attempt identity for pre-effect reopen.

---

## 2. Prior-finding closure table

| Finding | Status | Originating counterexample retrace |
|---|---|---|
| State P2-1 — forgeable generation permit | **CLOSED** | `GenerationPermit` is sealed and exact-instance keyed. A fabricated instance and a wrong owner both raised `ValueError`; count remained 1 and `begin_migration` remained refused in `DRAINING_OLD`. |
| State P2-2 — `CLOSED` with a live buffered permit | **CLOSED** | Hard close of a subscription with one queued envelope invalidated and released the buffer exactly once. `close_outcome` returned `CLOSED`, coordinator count was 0, and subsequent dequeue refused. Queue/subscription/runtime and peer cases are exercised by focused tests. |
| State P2-3 — cross-plan/provenance buffer exchange | **CLOSED** | Private candidate/queued/dequeued records bind exact envelope, admission, registration, digest, parameters, binding, queue, cursor lineage, producer operation, and permit. Copied-envelope and cross-admission dequeues both refused without count change; only the exact exchange succeeded. |
| State P2-4 — repeated/bypassed publication | **CLOSED** | Direct `ACQUIRED -> PUBLICATION` refused; steps advance strictly; duplicate publication is rejected; refresh visibility uses its exact buffer barrier; barrier failures contain the lease before visibility. |
| Expanded State P2-4 — publication after revocation | **CLOSED** | After legal `LOWER`, `revoke_generation()` revoked admissions, advanced the registry epoch, and contained the lease. Publication raised `ContractRefusal`, invoked no callback, and left `publications == 0`. Refresh candidate publication after revocation is likewise fenced by the common barrier. |
| State P2-5 — absence accepted as activation/withdrawal proof | **CLOSED** | Recovery and withdrawal require exact typed, binding/epoch-bound proof inputs. `None`, wrong type, and stale epoch left state unchanged; exact recovery worked; stale unused-withdrawal proof left `ACTIVE_UNUSED`. Used epochs remain unavailable and `ACTIVE` has no reset edge. |
| State P2-6 — entry-only `MIGRATION_INDETERMINATE` | **CLOSED on the original post-effect counterexample** | Missing proof left the coordinator indeterminate. Exact proof exercised all three exits: requested-next success to `CURRENT` generation 2, full rollback/no-effect to `CURRENT` generation 1 with a new admission epoch, and binding non-reuse to `RETIRED`. |
| State P2-7 — caller-selected QUERY authority for privileged effect | **CLOSED** | Non-read mutation/migration kinds were removed from this read-admission grammar. The remaining operation set has an exhaustive registry-owned capability mapping; worker issuance derives it. Static-query/live-question grammars are disjoint, and a query admission acquiring `REFRESH` refused before a permit was created. |
| State P2-8 — unbound second parameter copy | **CLOSED** | `execute`, `consistent_snapshot`, and `subscribe` no longer accept duplicate parameters. Parameters are pinned at acquisition and reach only issuer-owned `ClosedStepProduct`; the probe observed the original `{"tenant": "pinned"}` value. |
| State-Supp-P2-1 — rejected queued transfer mutates owner | **CLOSED** | Illegal `queued=True` generic transfer from `RUNNING` raised `ContractRefusal` before mutation. State and count were unchanged, the proposed owner remained rejected, and the old owner completed the lease successfully. |

Representative direct-probe output was:

```text
P2-1 1 draining_old
P2-2 closed 0
P2-3 ContractRefusal ContractRefusal 1 1
P2-4 ContractRefusal ContractRefusal 0 0 contained
P2-5 TypeError ContractRefusal ContractRefusal active_unused
P2-6 [
  ('requested_next_succeeded', 'TypeError', 'current', 2),
  ('full_rollback_no_effect', 'TypeError', 'current', 1),
  ('binding_non_reuse', 'TypeError', 'retired', 1)
]
SUP-P2-1 ContractRefusal running 1 old-completed
```

These closures apply to the executable reference contract. They do not claim production synchronization, durable coordination, physical fencing, or crash/restart proof.

---

## 3. New finding

### [State-Closure-P2-1] Pre-effect migration drain can reopen with no authoritative no-effect proof

**Priority:** P2  
**Classification:** New independent **architectural** recovery-interface root. It is adjacent to State P2-6 but is not the original post-effect indeterminate-exit defect.

`ReferenceGenerationCoordinator.reopen_no_effect()` at `generation_reference.py:199-205` has no proof argument. From `DRAINING_OLD`, provided only that `_migration_effect_begun` is false, any caller reaching the coordinator can:

1. advance `admission_epoch`;
2. restore `CURRENT`;
3. clear `_old_binding`;
4. then permit registries to reopen migration-invalidated queues.

There is no exact drain-attempt identity, no binding/epoch-bound pre-effect proof record, and no evidence that the exclusive migration request was released or that the attempted path was authoritatively established as effect-free. `recovery.py` defines activation proofs and post-effect `MigrationRecoveryProof`, but nothing usable by this transition.

The direct reproduction was:

```text
NEW-REOPEN () -> 'None' current 1 2
```

That is: after `begin_drain(binding)`, calling the zero-argument method succeeded, changed state from `DRAINING_OLD` to `CURRENT`, and advanced the admission epoch from 1 to 2.

The focused test at `tests/contracts/test_lifetime_contracts.py:400-431` currently endorses this proof-free transition by calling `coordinator.reopen_no_effect()` directly. It verifies old-handle invalidation, which correctly closes R4, but does not establish the proof required by R12.

This contradicts two controlling requirements:

- Accepted W2 lifetime ordering says the same old generation may reopen after pre-effect refusal **only with authoritative no-effect proof** and a new admission epoch.
- RemPlan R12 says mismatched or absent proof cannot publish, reopen, or retire.

Impact is a false return to admitting old-generation work while the authoritative migration request/release outcome has not been represented. A registry may subsequently clear `MIGRATION_INVALIDATING` and resume queue activity based solely on this local state change. The new epoch prevents stale leases from executing, but it does not prove that reopening itself is legal.

**Required correction:** Add a typed pre-effect migration no-effect proof and bind it to one exact drain attempt, qualified deployment, old binding, active protocol epoch, and pre-effect/no-effect outcome. The coordinator must retain an unforgeable or authoritative attempt identity sufficient to reject stale, cross-attempt, replayed, mismatched, or absent evidence. Change `reopen_no_effect` to require and validate that proof before mutating state or admission epoch. Queue reopening must remain impossible until that exact coordinator transition succeeds.

**Required closure tests:**

1. Begin drain and install the queue barrier; snapshot state, admission epoch, old binding, queue states, and count.
2. Try `None`, ordinary objects, wrong deployment/binding/epoch, stale prior-attempt proof, cross-coordinator proof, and replayed proof.
3. Assert every refusal leaves the entire snapshot unchanged and queues remain `MIGRATION_INVALIDATING`.
4. Supply the exact current-attempt authoritative no-effect proof; assert one transition to `CURRENT`, one admission-epoch advance, old handles and leases remain invalid, invalid buffers are not resurrected, and queues reopen only afterward.
5. Start another drain on the same binding/protocol epoch and prove the prior proof cannot reopen it.
6. Preserve all three existing post-effect `MIGRATION_INDETERMINATE` resolutions and their exact proof requirements.

---

## 4. Closure judgment

Remediation 1 materially and correctly closes the originating eight State findings, the expanded publication/revocation path, and the supplemental owner-transfer mutation. Permit conservation, close truth, buffer provenance, publication barriers, activation recovery, post-effect migration recovery, capability derivation, parameter pinning, and transfer atomicity all held under direct attack.

Acceptance nevertheless remains blocked by `State-Closure-P2-1`. The correction is architectural because it changes the coordinator’s recovery contract and requires a new exact proof/attempt identity rather than another local assertion. After that narrow correction, originating State closure must rerun this counterexample plus all prior counterexamples on the next frozen tuple.

