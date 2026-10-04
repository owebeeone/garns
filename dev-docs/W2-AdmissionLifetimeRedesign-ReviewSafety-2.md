# W2 admission-lifetime base-plus-overlay design — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; corrected composed replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the nine-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256` at SHA-256 `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`, under the accepted no-Git exception. No commit or clean-tree claim was used.  
**Date:** 2026-10-04  
**Axis:** Safety — degraded and mixed-version paths, irreversible transitions and preconditions, disclosure scale, reachable stuck states, quiescence claims, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both prior Safety P2 findings and the stopped design’s original lifetime counterexample are closed; no new P0, P1, P2, or P3 finding was identified.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Stopped final Safety P2-1 — verifier resolution was not retained across revocation | Replace point-in-time resolution with an exact operation lease spanning all work, publication, or retained containment. | Retraced every §11.1 pause: acquisition charges immutable ancestry and a shared generation permit; owner transfer survives dispatch/awaits; every scheduled step and publication remains lease-guarded; close cannot publish `LOCAL_CLOSED`, and migration cannot cut over, while resumable ownership remains. | **CLOSED** |
| Safety-1 P2-1 — ordinary local close entered deployment-wide `DRAINING_OLD` | Separate local lifecycle state and immutable resource ancestry from deployment generation state; reserve `DRAINING_OLD` for migration. | Overlay §§3.1, 4, 6–7 now make connection/pool/subscription/runtime close affect only selected descendants. Unrelated participants remain `LOCAL_OPEN` under deployment `CURRENT`; retained containment remains registered and globally counted for later migration. | **CLOSED** |
| Safety-1 P2-2 — an already-open legacy peer could remain outside the lifetime coordinator | Add operator-owned finite stop-the-world activation with authoritative inventory, physical access fencing, durable epoch state, and closed recovery transitions. | Overlay §8.1 requires termination/absence proof plus PostgreSQL session/credential fencing or SQLite exclusive physical exclusion before `ACTIVE_UNUSED`; failure before access change restores `UNACTIVATED`, post-fence uncertainty stops both paths, first lifetime open irreversibly enters `ACTIVE`, and unsupported environments refuse activation. | **CLOSED** |

## Changed-range analysis

`diff -u W2-AdmissionLifetimeRedesign-Initial.md W2-AdmissionLifetimeRedesign.md` showed one consolidated remediation matching M1–M4:

- §§2, 5 and 5.1 add issuer-private exact-command/effect worker authority while preserving task-bound public `TrustedContext`; this is explicitly a future separately reviewed A11/W1 prerequisite.
- §§3–7 add closed local-resource states, immutable ancestry/accounting and locally scoped drain/fence/finalization, separating ordinary close from deployment migration.
- §§8.2 and 9 add one pre-zero `MIGRATION_INVALIDATING` queue barrier that handles queued buffers, late enqueue and active dequeue without duplicate permit release.
- §8.1 adds the one-time activation state machine, operator ownership, physical legacy-access fence, finite refusal, indeterminate recovery, unused withdrawal and irreversible first-open boundary.
- §§10–12 update staged enabling, vectors, static checks and nonclaims consistently.

No changed range falls outside the remediation dispositions. These are material architectural corrections and consume replacement remediation round 1. No new architectural root was found.

## 0. Evidence base

At START and END, the manifest SHA remained exactly `55271fb…353eea`; all entries verified with counts exactly 9/11/13/48/13/26 across the current tuple, overlay inputs, stopped manifest, source inputs, control inputs and accepted W1 manifest. Object, DRAFT and preserved-initial hashes remained exact; no tuple movement occurred.

I read the complete 711-line base and 825-line overlay; initial overlay and complete diff; brief, DRAFT-2, RemPlan-1, initial Consistency/Safety reports and originating closure; stopped W2 record and final reports; checkpoint, execution brief and process authority; accepted A2/A3/A6/A7/A8/A11/A12; and the relevant complete authority, state, protocol, migration and semantic contracts. I did not read any current-round peer, closure, or reviewer prompt. No tests, builds, generators, services, writes, Git, or GWZ operations were used.

## 1. Findings

None.

## 2. Invariant analysis

The original lifetime attack now fails at every named boundary. Once acquired, a lease cannot become unowned through cancellation, `finally`, dispatch, worker transfer, fetch, child/total work, snapshot registration, assembly, or publication. Graceful drain permits pinned work only before the applicable final fence; hard fence suppresses later steps and publication; non-killable work remains `CONTAINED`/`NONQUIESCENT` with its permit and operation identity. A7 transaction knowledge remains independent, so neither lease completion nor commit reconciliation invents the other proof.

Local close no longer widens into a deployment outage. Exact ancestry determines which leases, buffers, handoffs and workers are drained; a parent cannot close over a retained descendant; a reopened resource is a new identity. Meanwhile the deployment coordinator still sees retained local permits, so isolation does not weaken later migration safety.

Migration now closes the idle-buffer gap: global acquisition stops, each queue is marked, queued permits are released once, a late refresh cannot enqueue behind the marker, and a dequeue winner becomes an active delivery lease that delays cutover. Effects start only after zero old-generation permits and exclusive ownership; failures after effects remain indeterminate.

Mixed-version activation no longer relies on cooperation by legacy binaries. The durable marker records a completed physical fence rather than pretending to create one. Old credentials, sessions and processes cannot continue or reopen; lack of authoritative inventory or exclusion fails closed.

The worker-authority attack also failed at design level: public context never crosses tasks; authorization is bound to exact runtime/lease/command/worker/generation and finite effect ordinals; immediate validation checks current issuer record and fence state; cancellation/fencing revokes unused ordinals; enabled execution is forbidden until the separate A11/W1 amendment is accepted.

Raw-plan escape, stale/copied leases, authority expiry, snapshot/cursor generation mixing, nontransaction-read invisibility, premature generation publication and disclosure-scale attacks likewise remain closed.

## 3. Risks and next action

Real lock, thread, database, crash and credential-fencing behavior remains future implementation evidence. In particular, the A11 amendment must preserve the specified atomic ordinal consumption/pre-effect boundary; implementation must not insert an await or reusable authorization gap there.

The single next action is manager merge with the same-tuple independent reports and required originating closures. If all are GO, acceptance may cover only this exact composed design; W1/A11 amendment, activation ownership and implementation still require separate authority and review.

