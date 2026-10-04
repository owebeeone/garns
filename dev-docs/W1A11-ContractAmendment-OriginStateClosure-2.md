# W1A11-ContractAmendment — ORIGINATING STATE CLOSURE 2

**Review object:** Final correction 2, complete 71-file filesystem tuple at MANIFEST-3 SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; controlling amendment SHA-256 `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`; DRAFT-3 SHA-256 `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`; not accepted; 2026-10-04.  
**Remediation authority:** RemPlan-2 SHA-256 `749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c`; RemInputs-2 SHA-256 `b96517c9cfb8e3f35622242b61a135cbb42b784f5c8b8245081d58e30b4280ac`.  
**Comparison archives:** Revision2 MANIFEST-2 SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`, 59/59; initial Revision1 manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`, 47/47.  
**Axis:** Focused originating State closure, independently retracing `State-Closure-P2-1`, the eight initial State IDs, expanded revocation, and `State-Supp-P2-1`. Read-only; no current peer/fresh/origin reports or prompts were read.

**Verdict: NO-GO.** Correction 2 installs the intended proof, attempt, participant, and barrier architecture, and preserves the earlier State closures. However, `State-Closure-P2-1` remains open through a stale same-attempt, cross-phase proof. This is a **bounded residual in the implemented F8 architecture**, not a new architectural root.

---

## 0. Evidence and tuple verification

At both START and END:

- MANIFEST-3 hash was exact and all 71/71 entries verified.
- RemInputs-2 verified 16/16.
- RemInputs-1 verified 13/13.
- Original Inputs verified 9/9.
- Control verified 3/3.
- Baseline verified 120/120.
- ReadOnly verified 111/111.
- ProductGuard verified 614/614.
- Revision2 MANIFEST-2 verified 59/59 from inside Revision2.
- Revision1 manifest verified 47/47 from inside Revision1.
- No `__pycache__` or `.pyc` was present.

I read the complete RemPlan-2 and DRAFT-3, inspected the corrected recovery, generation, migration, lifetime, buffer, consumer, worker, and focused-test paths, and compared the frozen sources with Revision2. Correction 2 changed exactly the reported 14 Revision2 files and added only `snapshot_reference.py` and `migration_reference.py`; all were authorized. Revision1 comparison confirmed that the previously closed permit, close, provenance, publication, activation, recovery, capability, parameter, and owner-transfer structures remain present.

My allowed Python 3.14 focused run passed 97/97. I separately ran inline `-B` state-machine attacks. The manager’s 97/200/5 matrix and AST25 result were treated as corroboration, not closure.

---

## 1. `State-Closure-P2-1` results

The new architecture correctly handles most required vectors:

- `MigrationAttempt`, participant, acknowledgement, and no-effect proof identities are sealed exact issuer identities.
- `begin_drain` freezes the registered participant set.
- Migration and reopen require every exact participant barrier acknowledgement.
- Missing, ordinary-object, and fabricated proofs refuse without mutation.
- Cross-coordinator and cross-attempt proofs refuse.
- Proof replay after successful reopen refuses.
- A new drain on the same binding and protocol epoch rejects the prior proof.
- Exact DRAINING proof advances the admission epoch once.
- Exact proof created in pre-effect `MIGRATING` restores the old binding.
- Queue reopening requires the registry’s exact acknowledged attempt and completed coordinator reopen.
- Old admissions, leases, and invalidated buffers remain invalid.

Representative output:

```text
F8-DRAINING
['TypeError', 'TypeError', 'ContractRefusal']
prebarrier=ContractRefusal
crosscoord=ContractRefusal
replay=ContractRefusal
crossattempt=ContractRefusal
state=current admission_epoch=3

F8-MIGRATING-EXACT
missing=TypeError
state=current binding_generation=1 admission_epoch=2
```

### [State-Closure-P2-1 residual] A DRAINING-phase release proof remains valid after transition to `MIGRATING`

**Priority:** P2  
**Classification:** **Bounded residual of the existing F8 root. No new architecture root.**

`setup_reference_no_effect_proof` at `generation_reference.py:264-283` records attempt, deployment, old binding, protocol epoch, admission epoch, and evidence digests. `MigrationNoEffectRecord` at `migration_reference.py:87-95` does not record the issuance phase or requested binding.

`begin_migration` at `generation_reference.py:314-328` changes the same attempt from `DRAINING_OLD` to `MIGRATING` and installs a requested binding, but it neither invalidates previously issued no-effect proofs nor advances a proof/phase serial.

`reopen_no_effect` at lines 285-312 checks the attempt, old binding, epochs, effect flags, and barriers, but does not establish that the proof’s released-exclusive-request evidence was produced for the current `MIGRATING` phase. Therefore a proof issued before the exclusive migration transition remains accepted afterward.

Exact reproduction:

1. Begin drain.
2. Install the participant barrier.
3. While still `DRAINING_OLD`, issue a no-effect proof containing `released-before-exclusive-migration`.
4. Call `begin_migration(attempt, requested_generation_2)`, entering pre-effect `MIGRATING`.
5. Present the earlier DRAINING proof to `reopen_no_effect`.

Observed:

```text
F8-STALE-PHASE
ACCEPTED
before=('migrating', 1, 1)
after=('current', 1, 2)
```

The stale proof reopened generation 1 and incremented its admission epoch after the transition that established the exact requested migration. Its “exclusive request released” evidence necessarily predates that later migration-phase request and cannot prove the current request was released.

This violates RemPlan-2 F8’s requirement that stale proof cannot reopen and that the proof carry released-exclusive-request evidence for the current recovery transition. The existing test creates its MIGRATING proof only after `begin_migration`, so it does not attack this cross-phase reuse.

**Required bounded correction:**

- Bind each no-effect proof to the exact attempt phase in which it was issued.
- On `begin_migration`, invalidate all DRAINING-phase proofs for that attempt or advance a private attempt-phase serial.
- A MIGRATING proof must additionally bind the exact requested successor binding and the post-transition exclusive-request release/no-effect outcome.
- `reopen_no_effect` must compare the proof phase/serial and requested binding with current attempt state before any mutation.

No new public architecture or third architecture correction is required; the sealed attempt/proof model already provides the needed ownership boundary.

**Required regression:**

1. Issue a proof in `DRAINING_OLD`.
2. Complete barriers and transition the same attempt to `MIGRATING`.
3. Assert the earlier proof refuses with state, binding, admission epoch, queues, and counts unchanged.
4. Issue a new proof for that exact MIGRATING phase and requested binding.
5. Assert it reopens once; replay, wrong requested binding, and any prior phase proof refuse.

---

## 2. Originating closure table

| Finding | Result on MANIFEST-3 |
|---|---|
| State P2-1 — forgeable generation permit | **CLOSED.** Fabricated and wrong-owner release raised `ValueError`; count remained 1 and migration remained blocked. |
| State P2-2 — `CLOSED` with live buffered permit | **CLOSED.** Subscription close invalidated the queued permit, returned `CLOSED` at count 0, and later dequeue refused. |
| State P2-3 — cross-plan/provenance buffer exchange | **CLOSED.** Copied and cross-admission envelopes refused without count mutation. FIFO and active-handoff ownership are now additional protections. |
| State P2-4 — repeated/bypassed publication | **CLOSED.** Direct publication refused, publication remains single-use, live visibility uses exact candidate barriers, and no external callback runs inside the private Plan/step transition. |
| Expanded State P2-4 — publication after revocation | **CLOSED.** Revocation contained the lease; publication refused and `publications` remained 0. |
| State P2-5 — absence accepted as activation/withdrawal proof | **CLOSED.** Missing/stale recovery and wrong physical-fence withdrawal refused without state change. |
| State P2-6 — entry-only migration indeterminate | **CLOSED.** All three exact attempt-bound post-effect outcomes succeeded; missing proof left state indeterminate. |
| State P2-7 — query authority authorizes privileged effect | **CLOSED.** Read operations are an exhaustive QUERY/LIVE set; independent nested/total operation kinds were removed; static/live cross-acquisition refused. |
| State P2-8 — duplicate unbound parameters | **CLOSED.** Protocols remain lease/handle based with no second parameter argument. |
| State-Supp-P2-1 — rejected transfer mutates owner | **CLOSED.** Illegal queued transfer preserved state/count; proposed owner remained rejected and old owner remained usable. |
| State-Closure-P2-1 — proof-free reopen | **NOT CLOSED.** Missing/cross/replay vectors close, but a DRAINING proof is accepted after the same attempt advances to pre-effect `MIGRATING`. |

Representative preservation output:

```text
P2-1 ValueError ValueError 1 ContractRefusal
P2-2 closed 0 ContractRefusal
P2-3 ContractRefusal ContractRefusal 1 1
P2-4 ContractRefusal ContractRefusal 0 contained
P2-5 TypeError ContractRefusal ContractRefusal active_unused
P2-6 [
  ('requested_next_succeeded', 'TypeError', 'current', 2),
  ('full_rollback_no_effect', 'TypeError', 'current', 1),
  ('binding_non_reuse', 'TypeError', 'retired', 1)
]
P2-7 operation-map-exact ContractRefusal
P2-8 no-duplicate-parameters
SUP ContractRefusal ContractRefusal running 1
```

---

## 3. Final classification and next action

There is **no new architectural blocker** in this originating State closure. Correction 2’s migration attempt, frozen participants, exact barriers, sealed proofs, and queue-reopen boundary are sufficient architecture.

There is one blocking **bounded residual**: proof freshness is attempt-exact but not phase-exact. Acceptance remains NO-GO until that residual and its cross-phase regression are corrected under explicit review-loop authorization. Because correction 2 is the final authorized architecture correction, writes should remain stopped; no automatic third architecture patch or replacement object is authorized.
