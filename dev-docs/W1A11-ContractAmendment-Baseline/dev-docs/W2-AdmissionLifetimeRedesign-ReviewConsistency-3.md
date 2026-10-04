# W2 ADMISSION-LIFETIME BASE-PLUS-OVERLAY DESIGN — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`; final corrected composed replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the 18-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256` at SHA-256 `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`; accepted no-Git exception, no commit or clean-tree claim  
**Date:** 2026-10-04  
**Axis:** Consistency — internal coherence, controlling-contract agreement, exact supersession, and satisfiable lifecycle/evidence obligations. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — no P0, P1, P2, or P3 findings. All prior consistency findings remain closed, final correction M5 closes the unsupported-retirement contradiction, and no new architectural root was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Consistency-1 P2-1 — no A11-compatible worker authority | Add exact-command/effect issuer-private authorization behind a separately reviewed A11/W1 prerequisite. | §§2 and 5.1 preserve task-bound public context, bind authorization to exact lease/command/worker/generation/ordinal, and disable worker execution until amendment acceptance. | **CLOSED** |
| Consistency-1 P2-2 / Safety-1 P2-1 — local close globally drained deployment | Separate local-resource lifecycle from deployment-generation lifecycle. | §§3–7 scope close to immutable descendants, leave peers under `CURRENT`, and retain nonquiescent permits for later migration. | **CLOSED** |
| Consistency-1 P2-3 — contradictory queued-buffer migration ordering | Use one pre-zero queue barrier with single permit release. | §8.2 step 4 installs `MIGRATION_INVALIDATING`, resolves enqueue/dequeue races, and reserves cutover cleanup from releasing permits again. | **CLOSED** |
| Safety-1 P2-2 — already-open legacy peer escaped coordination | Require operator-owned stop-the-world activation and physical access exclusion. | §8.1 requires authoritative inventory plus PostgreSQL/SQLite access fencing; marker-only activation refuses. | **CLOSED** |
| Stopped Safety P2-1 — verifier result outlived admission validity | Replace point verification with whole-operation lease ownership. | §§4–7 retain lease, owner, ancestry and generation permit through every continuation, publication, or containment outcome. | **REMAINS CLOSED** |
| OriginReplacementSafety P2-1 / M5 — `ACTIVE -> ACTIVATION_RETIRED` lacked quiescence and recovery semantics | Remove activation retirement rather than design decommissioning here. | §8.1’s enum and edge set omit retirement; `ACTIVE(epoch)` has no outgoing activation transition, survives close/restart/migration/binding retirement, and unknown reset/deactivation requests preserve all fences, ownership and evidence. | **CLOSED** |

## Changed-range analysis

The Revision2-to-current diff is confined to M5 and dependent evidence: removal of `ACTIVATION_RETIRED` and both retirement edges; explicit persistence of `ACTIVE(epoch)` across resource close, restart, migration, recovery and binding non-reuse; fail-closed retention of `ACTIVATION_INDETERMINATE`; retirement/reset refusal vectors; static checks; nonclaim language; and remediation-count testimony.

The attempted retirement trace now has one legal result whether active leases, buffers, non-killable workers, or unresolved A7 knowledge exist: the request is outside the closed grammar and refuses atomically, leaving the active epoch, physical access exclusion, binding/resource states, owners, counts, buffers and durable evidence unchanged. Binding `RETIRED` remains a distinct A12/non-reuse condition and does not erase activation. Deployment decommissioning is explicitly deferred. No changed range alters the base algebra, encoding, resource profile, result-role prerequisite, function fingerprints, authored mappings, query/question semantics, or previously corrected lifetime protocols. No new architectural root is introduced.

## 0. Evidence base

At START and END, the current manifest SHA remained exactly `86be2201…6b2e2`; the base, overlay and DRAFT hashes remained exactly `0b8b77a0…af44e`, `01257e07…6bb26`, and `161c9005…a377`. Recursive verification passed every entry at exact counts 18/11/13/48/13/26. No tuple movement occurred.

I read the complete 711-line base and 853-line overlay; brief, DRAFT-3, STOP, RemPlan-1, RemPlan-2, Initial and Revision2 snapshots; all manifested prior replacement reports and closures; checkpoint, W2 execution brief, parent-plan §§15–16, W1 acceptance, complete relevant A2/A3/A6/A7/A8/A11/A12 ADRs and authority/state/protocol/operation/semantic contracts. I compared both snapshots to current with `diff -u` and checked the supersession quotations against the base. No current peer or closure report was read. No writes, tests, builds, generators, services, Git, or GWZ operations occurred.

## 1. Findings

None.

## 2. Invariant analysis

Adversarial traces found coherent ownership from atomic acquisition through dispatch, worker containment, fetches, snapshot/registration, assembly and publication. Graceful drain, hard fence, final quiescence and independent A7 knowledge remain distinct. Raw-plan escape, copied leases, no-transaction reads, idle subscriptions, buffer permits, cross-runtime/process migration fencing, authority expiry and mixed peers retain explicit fail-closed paths.

The final activation grammar is closed and monotonic: unused activation alone may withdraw under the original physical fence; first open makes the epoch permanently active for this release; indeterminate activation can resolve only through authoritative restoration or completion. This is consistent with A3 close, A8 containment and A12 generation/binding changes because none claims protocol deactivation.

## 3. Risks and next action

Real worker, database, crash, advisory-lock, credential-fencing and cross-process behavior remain implementation-gate evidence. W1/A11 amendment wording and activation implementation still require separate review.

The next action is same-tuple verdict merge with the independent Safety review and required originating closures. If all report GO, acceptance may cover only this exact composed design; it does not authorize amendment or implementation.

