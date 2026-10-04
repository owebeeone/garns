# W2 admission-lifetime replacement overlay — SAFETY-AXIS REVIEW

**Review object:** composed design-only tuple: `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`; operator-authorized replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, filesystem tuple pinned by the four-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` at SHA-256 `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`. Files were read directly under the accepted no-Git exception; no commit or clean-tree claim was made.  
**Date:** 2026-10-04  
**Axis:** Safety — focused originating closure of the stopped design’s operation-lifetime race, plus adversarial inspection for degraded lifecycle, migration, cancellation, delivery, and mixed-version paths. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — the originating final Safety P2-1 is closed, but one new architectural P2 finding blocks the replacement design. I pre-commit to GO on a revision that resolves P2-1 as specified while preserving the verified lifetime closure.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on composed tuple | Status |
|---|---|---|---|
| Final W2 Safety P2-1 — verifier resolution was not retained as an operation lease across revocation | Replace point-in-time raw-plan resolution with an exact-instance per-operation lease spanning lowering, dispatch, adapter work, fetches, snapshot/cursor work, assembly, publication, or retained containment. Close must drain or report nonquiescence; migration must drain deployment-wide generation permits before effects or cutover. | The overlay eliminates raw-plan return, atomically acquires and charges a unique operation lease while holding a shared generation permit, retains ownership across awaits and worker transfers, checks every scheduled step and publication barrier, distinguishes graceful drain from hard and final fencing, retains non-killable/no-transaction operations, and prevents generation cutover while any old permit can resume. Every original pause/race point was retraced below. | **CLOSED.** |
| Earlier raw-plan admission bypass and semantic-provenance findings retained by the stopped base | Keep handle-only executable seams, complete trusted rebuild-and-compare, mixed-version refusal, and raw/extracted/copied/cross-runtime refusal. | Overlay §§1.1, 2, 10, and 11 retain and strengthen these obligations; `plan_admission_lifetime_v1` rejects point-verifier, raw-plan, legacy, and mixed peers. No raw plan or plan-bearing wrapper may escape the registry’s lexical invocation. | **REMAINS CLOSED.** |

## Changed-range analysis

This is a new additive replacement object, not a third edit to the stopped design. The overlay’s exact supersession map changes only admission lifetime and its protocol prerequisites:

- point-in-time verifier resolution is replaced by atomic `ReadOperationLease` acquisition;
- registry-owned lexical plan consumption replaces returning a private raw `Plan`;
- unique operation identity, owner transfer, closed lease states, terminal completion, and retained containment are added;
- a coordinator-issued shared generation permit spans the complete operation;
- graceful drain, hard fence, and final fence become distinct transitions;
- close outcomes can retain nontransaction read operations independently of A7 transaction identities;
- migration acquires a deployment-wide exclusive generation fence only after all execution and delivery permits drain;
- snapshots, refreshes, buffered deliveries, and iterator handoffs receive finite unit ownership;
- staged enablement requires a separately reviewed W1 result/lifetime amendment and the `plan_admission_lifetime_v1` handshake.

The stopped base’s algebra, encoding, resource profile, result-role prerequisite, function fingerprints, query/question semantics, lowering rules, authored mappings, and existing counterexamples remain unchanged.

The replacement directly closes the originating lifetime race. However, overlay lines 129–163, 275–280, and 302–304 also couple ordinary runtime, pool, and connection close to the deployment binding’s global `DRAINING_OLD` state. That is outside the necessary disposition and creates the new architectural root reported below.

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` returned exactly `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`.
- The object hashes remained:
  - stopped base: `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`;
  - overlay: `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`;
  - DRAFT testimony: `c12dadeb1f86715e520a702d6daf1ee6e719ba4676b98b0e419840222927505f`.
- Inventory counts were exactly 4/11/13/48/13/26 for:
  - replacement manifest;
  - replacement inputs;
  - stopped design manifest;
  - source inputs;
  - control inputs;
  - accepted W1 manifest.
- `shasum -a 256 -c` passed for every entry in all six manifests. No tuple movement occurred.

I read:

- workspace and product instructions;
- the complete review-loop skill and canonical template;
- complete replacement brief, overlay, DRAFT testimony, stopped base, STOP record, permitted prior final reports, and originating closure records;
- all recursively pinned replacement inputs, stopped-design entries, controls, source inventory, and accepted W1 tuple relevant to this review;
- full accepted A2, A3, A6, A7, A8, A11, and A12;
- complete relevant W1 protocol, authority, state, operation, semantic, and value contracts.

I did not read any current peer prompt, report, or closure. No file, test, build, generator, service, dependency, database, Git, or GWZ state was modified.

### Original-counterexample retrace

The stopped finding paused an admitted operation after verification and before every later boundary, then raced close, migration, reopen, or epoch change. The composed design now gives each case a closed result:

- **Immediately after acquisition:** the registry has already inserted and charged an `ACQUIRED` lease while holding the deployment’s shared generation permit. Close or migration cannot overlook it.
- **Before lowering:** `run_plan_step` requires the exact live lease and owner; no reusable raw plan has escaped. Graceful drain permits pinned old semantics; hard fencing prevents the step.
- **Before queue dispatch:** dispatch atomically transfers ownership under the queue lock. Cancellation either proves authoritative dequeue or transfers ownership to containment.
- **Before adapter start:** the step rechecks lease ownership, authority, binding, and fence state. A hard-fenced operation cannot start the adapter.
- **During an uninterruptible adapter call:** hard fencing does not pretend termination. Ownership becomes `CONTAINED`, the generation permit remains charged, private results are discarded, and no later command or publication is allowed.
- **Before first or later fetch, child, nested, or total work:** every independently scheduled continuation repeats the lease check and remains within the parent operation. No derived command can outlive or cache the plan.
- **Before snapshot watermark or registration:** rows, cursor, and registration remain under one lease and generation. A mismatch or fence discards the entire candidate and returns refusal/refetch.
- **Before assembly or cursor advancement:** ownership and generation remain charged; neutral refresh advancement occurs within its lease.
- **Before public result or delivery publication:** the atomic publication barrier revalidates owner, lease, authority, binding, generation, and cursor before caller visibility.
- **Buffered delivery delay:** enqueue exchanges the refresh charge for a finite generation-bound permit. Migration either completes the old handoff before cutover or invalidates it and drains its permit; it cannot relabel it.
- **Graceful close:** blocks new local acquisitions while existing owned operations may complete and publish under pinned old semantics before the deadline. Neither `CLOSED` nor a next generation is visible while ownership remains.
- **Hard or force close:** suppresses future commands and publication but preserves containment, worker ownership, and generation permits. It returns `NONQUIESCENT` while work can resume.
- **Final close:** requires terminal leases, authoritative worker quiescence, terminal delivery handoffs, and independently valid A7 knowledge before `CLOSED`.
- **Migration:** the deployment-wide exclusive fence cannot enter `MIGRATING`, perform effects, or publish the next generation until all old execution and delivery permits across participants reach zero.
- **Reopen or epoch change:** creates a new runtime identity and epoch; old handles and leases remain invalid, while retained old permits still block unsafe cutover.
- **No-transaction read:** its `OperationIdentity` independently prevents false closure or cutover even with no A7 transaction identity.
- **Authority expiry:** authority is revalidated before database effects and at final publication/handoff; expiry cannot ride an existing lease through those barriers.
- **Correct uncontended success:** an exact current handle can acquire one lease, complete all steps, publish exactly once, and release its permit. The safety machinery does not make legal work permanently impossible.

This satisfies the original closure test and correctly distinguishes:

- **graceful drain:** new work stops, but preexisting pinned work may finish before the deadline;
- **hard fence:** further steps and publication stop, but resumable work remains owned;
- **final fence:** only authoritative quiescence permits closure, retirement, or generation cutover.

## 1. Findings

### [P2-1] Ordinary resource close globally drains the deployment binding

**Classification:** new architectural root cause.

**Location:** `W2-AdmissionLifetimeRedesign.md:129-163`, especially the deployment binding state and acquisition requirement; lines 275–280, where graceful drain changes “the binding” to `DRAINING_OLD`; and lines 300–304, where runtime, pool, and connection close all install that graceful-drain barrier. Migration’s intentional deployment-wide use of `DRAINING_OLD` appears separately at lines 334–373.

**Violated invariant:** closing one connection, pool, or runtime must drain only work owned by that resource. It must not stop unrelated healthy runtimes and connections for the same qualified deployment. Deployment-wide `DRAINING_OLD` is the migration cutover fence and must be entered only by the serialized migration protocol.

**Reproduction/state sequence:**

1. Runtimes `R1` and `R2` are independently open for the same qualified deployment and generation `G`; both participate in the deployment coordinator.
2. `R2` is healthy and ready to acquire work.
3. An application closes one connection in `R1`, or closes `R1`’s pool/runtime.
4. Section 7 says that close installs the graceful-drain barrier. Section 6 defines that barrier as changing runtime/records to `DRAINING` **and the binding to `DRAINING_OLD`**.
5. Acquisition at lines 199–204 requires the binding to be `CURRENT`. Consequently, `R2` and every unrelated connection for the deployment now refuse new leases despite no migration, generation change, incompatibility, or failure.
6. The closed binding grammar provides no ordinary-resource-close transition restoring the deployment to `CURRENT`. `DRAINING_OLD -> CURRENT` is described only as migration pre-effect refusal/reopen, requiring authoritative proof that no migration effect began and a new admission epoch.
7. A routine connection close can therefore wedge the whole deployment, or an implementation must invent an unreviewed distinction between local drain and deployment drain.

If a connection close were to perform that global reopening transition, it would also invalidate old handles and epochs deployment-wide for unrelated runtimes. If it does not, acquisition remains blocked. Either interpretation gives ordinary close migration-scale blast radius.

**Impact:** routine lifecycle cleanup can cause a cross-runtime deployment outage and a stuck `DRAINING_OLD` state. Pool churn, connection sanitation failure, subscription shutdown, or one tenant/runtime closing can deny unrelated reads and governed work. It also conflates local resource ownership with the exclusive migration fence, making the intended migration serialization and no-effect reopening rules ambiguous.

**Required correction:** separate local lifecycle draining from deployment-generation draining:

- connection close drains only leases owned by or dispatched to that connection;
- pool/runtime close marks only its local registry/records `DRAINING`, blocks new local acquisitions, and drains or contains its local operations;
- the deployment binding and coordinator remain `CURRENT` for other participants during ordinary close;
- only the serialized migration protocol may enter deployment `DRAINING_OLD`;
- acquisition must validate both the local resource state and the deployment state independently;
- local final close removes that participant only after its leases, workers, buffers, and handoffs are terminal, without changing other participants’ epochs or handles;
- migration must still see every registered participant and its retained permits, including a locally nonquiescent closing participant.

**Closure/regression test:** open two runtimes with multiple pools/connections for one deployment. Close, force-close, timeout, and reopen each connection, pool, subscription, and runtime in one participant while the other acquires and completes operations. Verify unrelated acquisitions remain legal while the deployment is `CURRENT`; local closing resources reject new work; retained nonquiescent permits still block migration; no ordinary close enters `DRAINING_OLD`, changes another runtime’s epoch, or invalidates its handles. Then initiate migration and verify that only the migration mutex transition globally blocks old-generation acquisition across both participants.

## 2. Invariant analysis

Attacks that did not produce further findings:

- **Raw-plan escape:** the registry invokes closed consumers lexically; continuations cannot return or retain a plan, root, plan-bearing wrapper, lowerer closure, or reusable claim bag.
- **Lease forgery and reuse:** handles and leases are exact-instance, noncopyable, nonserializable, issuer-owned identities. Copied, fabricated, released, wrong-owner, cross-runtime, cross-binding, and cross-generation values refuse.
- **Ownership after awaits:** caller, worker, runtime, and containment transfers are compare-and-transfer operations. Caller cancellation or `finally` cannot release worker-owned work.
- **Non-killable workers:** missed deadlines retain `CONTAINED` ownership and generation permits and return `NONQUIESCENT`; private late results cannot publish or start another command.
- **Transaction knowledge:** lease state does not invent commit knowledge, and A7 reconciliation does not prove worker quiescence. The A8 late-commit fence remains independent.
- **Migration effects:** no DDL, backfill, generation publication, or next-generation admission occurs before zero old-generation execution and delivery permits plus the exclusive generation permit.
- **Cross-process participation:** PostgreSQL and file-backed SQLite require deployment-level coordination; unsupported SQLite multiprocess identity refuses rather than falling back to local counts.
- **Migration failure:** pre-effect failure may reopen only with authoritative no-effect proof; failure during or after effects becomes `MIGRATION_INDETERMINATE` and refuses ordinary work until authoritative recovery.
- **Idle subscriptions:** they retain no execution lease. Queued buffers have finite permits that can be invalidated so an idle consumer cannot block shutdown or migration forever.
- **Delayed delivery:** dequeue exchanges the buffer permit for a delivery lease, and the post-await barrier revalidates authority and generation. Old envelopes cannot survive cutover.
- **Snapshot consistency:** rows, watermark, and durable registration share one lease and generation or the complete candidate is discarded.
- **Mixed peers:** missing or old lifetime handshake, legacy bare-plan routes, point-verifier paths, and peers unable to join the deployment fence refuse before lowering or I/O.
- **Scope preservation:** current W1 bytes remain frozen. Structural result roles and lifetime protocols are explicit separately reviewed prerequisites; no implementation, external capture, provider integration, public Surface, or database proof is silently claimed.

## 3. Risks and next action

Real thread, process, advisory-lock, crash, database, and async behavior remains future implementation evidence and is not required for this design verdict. The composed object also remains non-executable under current W1 bytes; that is an explicit prerequisite rather than a defect.

The single next action is one consolidated replacement-design correction separating local resource drain from deployment migration drain while preserving the verified whole-operation lease closure. Because P2-1 is a new architectural root in the replacement object’s initial review, it consumes that object’s first architectural remediation allowance. The revised composed tuple requires focused originating Safety re-verification of this new close sequence and renewed confirmation that every original lifetime pause/race remains closed.

