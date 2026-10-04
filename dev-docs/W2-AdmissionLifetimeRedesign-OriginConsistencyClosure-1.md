# W2 admission-lifetime base-plus-overlay design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus corrected `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; composed design-only replacement after remediation 1, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the nine-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256` at SHA-256 `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`; accepted no-Git exception, with no commit or cleanliness claim  
**Date:** 2026-10-04  
**Axis:** Focused originating Consistency closure — retrace the initial worker-authority, local-close, and queued-buffer counterexamples while preserving the stopped-base lifetime and provenance closures. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — all three originating Consistency P2 findings are closed at design level; no new P0, P1, P2, P3, or architectural root was found. This focused GO is not a substitute for the required fresh full reviews.

---

## Prior-finding closure table

| ID | Original counterexample | Corrected design | Status |
|---|---|---|---|
| Initial Consistency P2-1 | After lease ownership transferred from task `T` to worker `W`, validating task-bound `TrustedContext C` in `W` necessarily failed owner identity; validating only before enqueue allowed expiry/invalidation before the effect. | Lines 129–133 and 314–358 keep public `TrustedContext` task-bound and disable worker-backed W2 until a separately reviewed A11/W1 extension exists. The issuer-private authorization is bound to exact runtime, lease, operation, command, worker, generation, capability, and effect ordinals. The worker performs a trusted-time/epoch/live-record check immediately before each effect without impersonating `T`; cancellation, invalidation, fencing, or terminal completion revokes unused ordinals. | **CLOSED** |
| Initial Consistency P2-2 | Closing runtime `R1` changed the deployment binding to `DRAINING_OLD`, blocking healthy peer `R2` and leaving no ordinary-close transition back to `CURRENT`. | Lines 137–187 define independent record, local-resource, and deployment state machines. Lines 364–398 reserve `DRAINING_OLD` for migration and make local drain affect only selected ancestry. Lines 400–435 retain nonquiescent descendant counts globally while unrelated peers continue under deployment `CURRENT`. | **CLOSED** |
| Initial Consistency P2-3 | A queued buffer retained permit `P`; exact migration step 4 waited for zero permits, while invalidation releasing `P` occurred only after cutover, making the sequence contradictory or permanently refusing. | Lines 544–581 place one authoritative queue barrier before the zero-permit wait. It marks `MIGRATION_INVALIDATING`, releases every queued permit once, rejects late enqueue under the same lock, and keeps dequeue winners counted as active delivery leases. Lines 623–645 make this the sole invalidation path and prohibit a second release during cutover cleanup. | **CLOSED** |

## Changed-range analysis

The initial-to-corrected diff is one consolidated architectural remediation implementing the accepted plan:

- it introduces explicit local resource ancestry, attribution, and lifecycle states separate from deployment generation state;
- it adds the issuer-private worker-effect authorization shape and names a separately reviewed A11/W1 amendment as a prerequisite;
- it replaces the conflicting buffer rules with a single pre-zero-permit invalidation barrier;
- it additionally defines stop-the-world activation for already-open legacy peers, including physical access fencing, durable activation states, finite refusal, indeterminate recovery, and irreversible post-first-open behavior.

The last item addresses the prior Safety lane’s merged activation root. I attacked it for interaction with my three counterexamples and found no new architectural root: activation precedes lifetime execution, local close does not mutate activation or generation state, and normal migration runs only after `ACTIVE(epoch)` is established.

## 0. Evidence base

At START and END:

- manifest 2 remained exactly `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`;
- base, overlay, and DRAFT-2 remained exactly `0b8b77a0…af44e`, `28f7ca80…943a4`, and `c7e511f8…edaa2`;
- recursive verification passed at exact counts 9/11/13/48/13/26 for manifest 2, replacement inputs, stopped manifest, source inputs, control inputs, and accepted W1 tuple;
- no tuple movement occurred. Historical manifest 1 was not treated as a current check.

I read the complete corrected 825-line overlay, unchanged 711-line base, brief, DRAFT-2, STOP, prior final stopped-object reports, initial replacement reports, preserved initial overlay, remediation plan, relevant complete A2/A3/A6/A7/A8/A11/A12 ADRs, and W1 authority/protocol/state/operation contracts. I compared the preserved initial overlay to the corrected overlay with `diff -u`.

No file write, test, build, generator, database, service, dependency, Git, or GWZ operation occurred.

## 2. Invariant analysis

The corrected worker handshake closes both branches of the original authority attack. The public context never crosses task ownership, while the private authorization remains exact-command/effect scoped and rechecks current issuer state at the worker boundary. It neither claims current A11 already supports this nor enables execution before the amendment.

The two-runtime close trace now leaves `R2` and deployment `CURRENT` untouched. `R1` rejects new descendant work, retains nonquiescent permits and containment in the deployment coordinator, and reaches `LOCAL_CLOSED` only after its own descendants become terminal. A later migration still observes those retained permits.

The idle-buffer trace now has one total order: migration stops new permits, installs the queue marker, invalidates queued envelopes once, resolves refresh/enqueue and dequeue races under the queue lock, then waits for active permits. Cutover retires registrations and clears already-invalid entries without releasing permits twice.

The correction preserves the original whole-operation lease, raw-plan non-escape, snapshot-generation coupling, nontransaction operation identities, non-killable-worker containment, A7 knowledge separation, mixed-peer refusal, provenance rebuilding, and retained stopped-base attacks.

## 3. Risks and next action

Implementation must still prove the private issuer handshake, resource ancestry accounting, queue barrier, physical activation fencing, and restart recovery. Those are explicitly deferred implementation gates, not missing design shape.

The next action is to combine this originating closure with the fresh peer-blind full Consistency and Safety verdicts on manifest 2. Acceptance remains blocked unless those reviews both report GO on this exact tuple; implementation additionally remains blocked on the separately reviewed W1/A11 amendment, activation ownership package, and execution brief.

