# W2 admission-lifetime base-plus-overlay design — ORIGINATING SAFETY CLOSURE REVIEW

**Review object:** composed `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus corrected `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`; final replacement remediation round 2 of 2, design only, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from eighteen-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256` at SHA-256 `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`; accepted no-Git filesystem exception, no commit or cleanliness claim  
**Date:** 2026-10-04  
**Axis:** Focused originating Safety closure of the unsupported active-protocol-retirement counterexample, preserving local-close, legacy-activation, operation-lifetime and provenance closures. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — the originating retirement P2 is closed by removal of the unsafe capability; all earlier Safety closures remain intact, with no new P0, P1, P2, P3, or architectural root found.

---

## Prior-finding closure table

| Prior ID | Counterexample retraced | Final disposition verified | Status |
|---|---|---|---|
| Originating replacement Safety P2-1 | With deployment `ACTIVE(E)`, active leases, buffers, a non-killable worker and unresolved A7 knowledge, the former legal `ACTIVE(E) -> ACTIVATION_RETIRED` edge had no quiescence, containment, access-fence or recovery contract. | `ACTIVATION_RETIRED` is absent from the exact state enum and all legal edges. `ACTIVE(E)` has no outgoing activation transition. Retirement/deactivation/reset/erase requests refuse atomically without altering activation or binding state, access fences, owners, permit counts, buffers, A7 knowledge or durable evidence. | **CLOSED** |
| Safety-1 P2-1 | Ordinary connection/pool/runtime close globally entered `DRAINING_OLD`. | Independent local-resource states and immutable ancestry remain; local close leaves the deployment `CURRENT`, peers operational and retained containment globally counted. | **REMAINS CLOSED** |
| Safety-1 P2-2 | An already-open legacy peer remained outside the lifetime coordinator. | Operator-owned stop-the-world activation, authoritative inventory, physical database/file exclusion, durable epoch and fail-closed recovery remain mandatory. | **REMAINS CLOSED** |
| Stopped W2 final Safety P2-1 | Raw-plan resolution lost ownership across close or migration. | Whole-operation leases, generation permits, guarded continuations, publication barriers and authoritative containment remain unchanged. | **REMAINS CLOSED** |

## Changed-range analysis

The 825-line remediation-1 overlay is preserved as `W2-AdmissionLifetimeRedesign-Revision2.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; the final overlay has 853 lines.

The Revision2-to-final diff is confined to remediation M5:

- removes `ACTIVATION_RETIRED` from the state set;
- removes both indeterminate-to-retired and active-to-retired edges;
- makes `ACTIVE(epoch)` persistent across close, restart, migration, recovery and binding non-reuse;
- makes unknown retirement/reset/deactivation requests state-preserving refusals;
- retains physical fencing in `ACTIVATION_INDETERMINATE`;
- adds exact closure vectors and static checks;
- explicitly defers deployment decommissioning to separate future authority/design.

No unrelated plan, lease, migration, authority, subscription, algebra or result semantics changed.

## 0. Evidence base

At START and END:

- manifest SHA was exactly `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`;
- inventory counts were exactly 18/11/13/48/13/26;
- every entry in the current manifest and five recursive manifests passed `shasum -a 256 -c`;
- no tuple movement occurred.

I read the complete final overlay, unchanged base, DRAFT-3, RemPlan-2, preserved Revision2, all manifested prior-round reports, relevant accepted ADRs/contracts, and the complete Revision2-to-final diff. Focused inspection covered final overlay lines 447–535, 773–825 and 827–853. No current-round peer report, prompt or closure was read. No writes, tests, builds, generators, services, databases, dependencies, Git or GWZ operations occurred.

## 2. Invariant analysis

The original attempted-retirement sequence now fails at its first transition: there is no retirement state, edge or capability. With active work or with a quiescent deployment, an attempted retirement request leaves `ACTIVE(E)` and every ownership, count, fence and evidence value unchanged. Restart must re-establish the same durable epoch before database access. Binding retirement or local/full runtime close cannot erase the activation epoch or authorize legacy access.

Indeterminate activation also remains closed: physical exclusion and evidence persist until authoritative no-activation restoration reaches `UNACTIVATED` or authoritative completion reaches `ACTIVE_UNUSED(E)`. There is no shortcut that abandons uncertain fencing.

The earlier local-close and legacy-peer attacks remain closed because M5 does not change resource ancestry, local/deployment state separation, physical activation proof or coordinator membership. The stopped operation-lifetime counterexample remains closed because acquisition, ownership transfer, generation permits, publication barriers and nonquiescent containment are untouched. Raw-plan, authority-expiry, buffered-delivery, snapshot/cursor and A7 knowledge-separation obligations likewise remain preserved.

No new architectural root was found after the final permitted correction.

## 3. Risks and next action

Deployment decommissioning is deliberately unavailable in v9-6; any future capability requires separate authority and a complete lifecycle design rather than reinterpretation of binding retirement. Real enforcement of durable epochs, physical access fencing and state-preserving refusal remains future implementation evidence.

The single next action is same-tuple verdict merge with the fresh full reviews and required originating closures. If all report GO, the manager may accept only this exact composed design tuple; no W1/A11 amendment or implementation is authorized by this closure.

