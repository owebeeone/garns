# W2 ADMISSION-LIFETIME BASE-PLUS-OVERLAY DESIGN — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`; final corrected composed design after replacement remediation 2 of 2, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the 18-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256` at SHA-256 `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`, under the accepted no-Git exception; no commit or cleanliness claim  
**Date:** 2026-10-04  
**Axis:** Safety — degraded and mixed-version paths, irreversible transitions, disclosure, stuck states, quiescence, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — the round-2 architectural P2 is closed by removal of the unsafe capability; no P0, P1, P2, P3, or new architectural root was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| OriginReplacementSafetyClosure-1 P2-1 — `ACTIVE(epoch) -> ACTIVATION_RETIRED` lacked quiescence, containment, physical-access, and recovery semantics | Remove `ACTIVATION_RETIRED`, every transition to it, and every protocol retirement/deactivation/reset capability; retain the active epoch permanently after first lifetime open. | Overlay §§8.1, 11.2, 11.3 and 12 now give `ACTIVE(epoch)` no outgoing activation transition, preserve it across close/restart/migration/recovery/binding retirement, make retirement-like requests atomic refusals with no state or evidence change, and retain `ACTIVATION_INDETERMINATE` behind its physical fence until authoritative restoration or completion. Retracing retirement with active leases, buffers, a non-killable worker, and unresolved A7 knowledge leaves all ownership, permits, fences, and evidence intact. | **CLOSED** |

## Changed-range analysis

`diff -u W2-AdmissionLifetimeRedesign-Revision2.md W2-AdmissionLifetimeRedesign.md` is confined to remediation M5 and dependent testimony/vectors. It removes `ACTIVATION_RETIRED` from the enum and legal edges, replaces “roll forward or retire” with exact epoch preservation, defines atomic refusal of retire/deactivate/reset/erase requests, closes `ACTIVATION_INDETERMINATE` to its two authoritative recovery edges, adds persistence and hostile-request vectors/static checks, and states that deployment decommissioning is outside this release.

No unrelated algebra, admission, worker authority, local lifecycle, migration, buffer, result, or query/question rule changed. The correction is the authorized second architectural remediation. I found no new architectural root; therefore the cap does not require a STOP.

## 0. Evidence base

At START and END, manifest SHA remained exactly `86be2201…06b2e2`; counts remained exactly 18/11/13/48/13/26; and every entry in the current manifest plus replacement-input, stopped-design, source, control, and W1 manifests passed `shasum -a 256 -c`. The object and DRAFT hashes remained exact. No tuple movement occurred.

I read the complete 711-line base, 853-line overlay, brief, DRAFT-3, STOP, both remediation plans, Initial and Revision2 snapshots, manifested prior replacement reports and originating closures, parent-plan §§15–16, accepted A2/A3/A6/A7/A8/A11/A12, and relevant authority/protocol/state/operation contracts. I checked the supersession map and compared Revision2 with the current overlay. No current-round peer, closure, or report was read. No writes, tests, builds, generators, services, databases, dependencies, Git, or GWZ operations occurred.

## 1. Findings

None.

## 2. Invariant analysis

The attempted-retirement attack now fails structurally: there is no callable protocol state transition from `ACTIVE(epoch)`. Whether work is active or quiescent, an unsupported retirement request changes no activation or binding state, physical-access fence, lease/permit ownership, buffered delivery, A7 knowledge, or durable evidence. Restart must read the same active epoch, so refusal cannot reopen a legacy path.

The safe pre-activation recovery distinction remains intact. `ACTIVATING` may return to `UNACTIVATED` only with authoritative pre-change/no-effect evidence. `ACTIVATION_INDETERMINATE` preserves physical exclusion until authoritative no-activation restoration or activation completion. `ACTIVE_UNUSED` withdrawal remains limited to proof that no lifetime runtime ever opened.

The broader composed safety attacks also continued to fail. Whole-operation leases retain ownership across lowering, dispatch, awaits, worker execution, fetch, snapshot, assembly, and publication. Hard fences suppress later effects/publication without manufacturing quiescence. Non-killable and nontransaction work remains named and globally counted. Local close does not drain healthy peers. Migration cannot begin effects or publish a generation until old execution, delivery, and buffer permits are resolved. Mixed peers and already-open legacy processes fail closed through operator inventory and physical access fencing. A7 commit knowledge remains independent of worker and lease quiescence.

## 3. Risks and next action

Real worker, database, crash, advisory-lock, credential, and physical-fence evidence remains appropriately deferred. Permanent activation intentionally makes protocol decommissioning a separate future design rather than an implicit escape hatch.

The next action is same-tuple verdict merge and required originating closure. If all required reports are GO, acceptance may cover only this exact composed design; it does not authorize the W1/A11 amendment, activation implementation, decommissioning, or W2 implementation.

