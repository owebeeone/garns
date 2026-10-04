# W2 admission-lifetime redesign — consolidated remediation 2

**Status:** final manager-authorized design-only correction; not acceptance
**Date:** 2026-10-04
**Count:** replacement architectural remediation 2 of 2; no third architectural correction authorized. Stopped base/history unchanged.

Corrected overlay 28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4 is preserved byte-identically in W2-AdmissionLifetimeRedesign-Revision2.md. Manifest2 (55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea) becomes historical at its mutable overlay entry after this patch.

## Verdict merge

Full fresh Consistency-2 and Safety-2 are GO. Origin Consistency and stopped Safety are GO. Originating replacement Safety closed both original findings but identified a NEW architectural P2: ACTIVE -> ACTIVATION_RETIRED has no quiescence, containment, access or recovery contract. Its NO-GO controls; other GO verdicts cannot override it.

All reports filed verbatim:
- Consistency-2: 2b1ca5c4a1c79d9c9a9d8fea90368e4852a4f3d296d34738b897a7f53f9b5296
- Safety-2: 65856142628d22c93169e663704db8b6d90a9c681d7981f1a6d47120124d5777
- OriginConsistencyClosure-1: bb73fcca64eb05a2706bf0525b5b1480289601a6efb692d5fc53b4ab5245c097
- OriginSafetyClosure-2: 2090cce0bcd2e3176f1df48d7aa18db0485745c550d56b4f43b15e6853fa3ac1
- OriginReplacementSafetyClosure-1: a369932ccba64a2490950242035f0a001528d5e40d917685a18eb4ae71417282

## Disposition M5 — accept the unsafe retirement root; remove unnecessary capability

Rather than introduce deployment decommissioning into a narrow admission design, REMOVE ACTIVATION_RETIRED and every activation-retirement edge from the closed protocol grammar. This is an alternative corrective disposition, not a severity downgrade or waiver.

After first lifetime open, ACTIVE(epoch) has no outgoing activation-state transition in v9-6: the durable protocol epoch remains mandatory across runtime closes, restart, migration, and binding retirement/recovery. Ordinary resource close and A12 binding non-reuse remain separate controls; neither erases the activation epoch or permits legacy access. No protocol retire/deactivate/reset, epoch deletion/reuse or rollback to legacy is offered. Unknown/retired-state requests refuse with no state, permit, ownership or access change.

ACTIVATION_INDETERMINATE retains operator physical fencing and evidence until existing authoritative no-activation restoration or activation-completion paths resolve it; no retirement shortcut is offered. Failed proof stays indeterminate and fails closed. ACTIVE_UNUSED rollback remains exactly the existing finite unused/no-first-open procedure under its physical fence.

Update exact enum/edges/recovery wording, scope/nonclaims, static and closure vectors, and remediation count2. Add vector: attempt protocol retirement while leases/buffers/nonkillable workers/A7 unknown knowledge exist; the transition is NOT available, all evidence/counts/fences persist, and restart still enforces active epoch. Deployment decommissioning requires separate future authority/design and is not part of this release. Do not change any unrelated semantic or previously closed case.

## Execution and review

Same sole drafter writes ONLY W2-AdmissionLifetimeRedesign.md with apply_patch; frozen base/source/tests/W1/A11/ADRs/grammar/Git/GWZ/services remain read-only. Read complete latest five reports, this plan, previous plans and preserved revision. Verify immutable Inputs11/stopped13/source48/control13/W126 START/END. Return complete concise testimony/hash then STOP.

Manager pins overlay/DRAFT-3/RemPlan2/Revision2/all prior reports plus unchanged inputs in manifest3. Because legal architecture state transitions change, fresh full peer-blind numbered Consistency/Safety review is required. Originating replacement Safety must verify this alternative disposition by retracing the retirement counterexample on the actual new tuple; stopped Safety verifies original lifetime closure retained. Fresh substitution of prior closed consistency cases is permitted after the material change; all original vectors remain required.

If a new architectural root is found after this final correction, STOP and request operator direction. No design acceptance, amendment or implementation absent exact same-tuple GO/GO plus required verified origin closures.

