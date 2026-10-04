# W2 admission-lifetime base-plus-overlay design — ORIGINATING SAFETY CLOSURE REVIEW

**Review object:** composed `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus corrected `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; replacement remediation round 1, design only, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from nine-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256` at SHA-256 `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`; accepted no-Git filesystem exception, no commit or cleanliness claim  
**Date:** 2026-10-04  
**Axis:** Focused originating Safety closure of local-close/global-drain and already-open-legacy activation counterexamples, with preservation of stopped lifetime/provenance closure. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — both originating P2 findings are closed, but one new architectural P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified while preserving the verified closures.

---

## Prior-finding closure table

| Prior ID | Original counterexample retraced | Corrected design | Status |
|---|---|---|---|
| Safety-1 P2-1 | Closing one connection, pool or runtime changed the deployment binding to `DRAINING_OLD`, blocking unrelated runtimes and leaving no ordinary-close return to `CURRENT`. | Sections 3.1, 4, 6 and 7 now define independent local-resource and deployment state machines, immutable ancestry/count attribution, local-only drain/fence/finalization, and migration-only `DRAINING_OLD`. Unrelated participants remain `LOCAL_OPEN` under deployment `CURRENT`; retained local containment remains globally counted. | **CLOSED** |
| Safety-1 P2-2 | A legacy process already open before `plan_admission_lifetime_v1` could remain invisible to the new coordinator and execute generation-`G` work after new peers activated or migrated. | Section 8.1 now requires finite stop-the-world activation owned by the deployment operator, authoritative process/session inventory, physical database/file access exclusion, durable activation epoch, fail-closed indeterminate recovery, and no rollback after first lifetime open. Cooperative handshake or marker-only evidence is expressly insufficient. | **CLOSED** |
| Stopped W2 final Safety P2-1 | Revocation after raw-plan resolution could race lowering, adapter work, fetch or publication. | Whole-operation leases, immutable ownership, generation permits, guarded steps, publication barriers and nonquiescent containment remain intact. | **REMAINS CLOSED** |

## Changed-range analysis

The initial 578-line overlay is preserved at SHA-256 `ee7c62ae…d3c638`; the corrected overlay has 825 lines. The diff implements remediation M1–M4: local-resource hierarchy, issuer-private worker authorization prerequisite, one migration queue invalidation barrier, and lifetime-protocol activation. The two originating counterexamples are corrected directly rather than waived. The activation addition introduces the distinct retirement root below.

## 0. Evidence base

At START and END, manifest SHA was exactly `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`; all entries verified, with counts exactly 9/11/13/48/13/26. No tuple movement occurred.

I read the complete corrected overlay, unchanged base, brief, DRAFT-2, STOP, remediation plan, preserved initial overlay, initial reports, prior stopped reports, relevant accepted ADRs/contracts, and the Initial-to-current unified diff. Focused traces covered corrected overlay lines 137–268, 360–442, 446–597 and 660–801. No files, tests, builds, services, dependencies, Git or GWZ state were changed.

## 1. Findings

### [P2-1] Active protocol retirement has no quiescence or recovery contract

**Classification:** new architectural root cause.

**Location:** `W2-AdmissionLifetimeRedesign.md:448-450` introduces `ACTIVATION_RETIRED`; lines 480–493 make `ACTIVE(epoch) -> ACTIVATION_RETIRED` legal. Unlike activation and migration, the document defines no retirement owner, preconditions, acquisition/publication behavior, retained-work handling, physical-access fence, or terminal/recovery rule.

**Violated invariant:** a deployment protocol cannot retire while active runtimes, leases, workers, buffers or A7 identities may still execute or publish, nor may retirement discard the durable epoch needed to refuse legacy access and reconcile retained work.

**Reproduction:** activate epoch `E`, open runtime `R`, acquire a lease and pause a non-killable worker. Take the explicitly legal `ACTIVE(E) -> ACTIVATION_RETIRED` edge. The text does not say whether new acquisitions refuse, whether the worker’s generation permit remains authoritative, whether publication is suppressed, whether `R` must close, or whether restart may recreate `ACTIVE(E)`. An implementation may therefore retire immediately and lose the activation fence while work can resume, or retain an unrecoverable state with no defined completion path.

**Impact:** false quiescence, stale publication, legacy-access reopening, or permanent deployment refusal are all permitted by the closed state machine.

**Required correction:** define retirement as an operator-owned, finite-wait, physically fenced drain with explicit acquisition, publication, containment, A7 and restart semantics. `ACTIVATION_RETIRED` must be terminal and preserve enough durable evidence to prevent epoch/legacy reuse; timeout or uncertainty must retain a named nonterminal/indeterminate state.

**Closure test:** retire with active leases, queued buffers, a non-killable worker and unresolved A7 identity. Retirement must not become terminal or release access until all are authoritatively resolved; timeout must preserve containment. After terminal retirement, old and lifetime peers must both refuse open/work across restart.

## 2. Invariant analysis

The local-close sequence now holds at every resource level: acquisition charges exact immutable ancestry; local drain rejects only selected descendants; sibling and peer acquisition continues under `CURRENT`; force-close containment remains registered and visible to later migration.

The legacy activation sequence also holds: new binaries cannot self-certify absence of old peers; activation requires operator inventory plus physical exclusion, publishes `ACTIVE_UNUSED` only while fenced, makes the first open atomically `ACTIVE`, and fails closed after uncertain fencing. Pre-fence refusal may safely restore legacy access; post-first-open rollback is forbidden.

Raw-plan escape, authority expiry, nontransaction reads, non-killable workers, buffer permits, migration publication and A7 knowledge separation remain closed at design level.

## 3. Risks and next action

Real process, database, lock and credential evidence remains deferred to implementation gates. The next action is one bounded correction defining active-protocol retirement, followed by focused re-verdict of P2-1 on a newly pinned tuple.

