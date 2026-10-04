# W2 ADMISSION-LIFETIME BASE-PLUS-OVERLAY DESIGN — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; corrected composed design after replacement remediation 1, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the nine-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256` at SHA-256 `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`, under the accepted no-Git exception; no commit or cleanliness claim  
**Date:** 2026-10-04  
**Axis:** Consistency — internal coherence, controlling-contract agreement, exact supersession, and satisfiable lifecycle/evidence obligations. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — no P0, P1, P2, or P3 findings. All prior consistency counterexamples close on the corrected tuple, the originating lifetime closure remains intact, and no new architectural root was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Consistency-1 P2-1 — worker ownership had no A11-compatible authority path | Add an issuer-private, exact-command/effect authorization and require a separately reviewed A11/W1 amendment. | Overlay lines 129–133 and 314–358 keep public `TrustedContext` task-bound, bind authorization to exact runtime/lease/operation/command/worker/generation/effect ordinals, check immediately before effect, revoke unused ordinals, and prohibit worker-backed W2 until amendment acceptance. The original delayed-worker/expiry sequence now makes zero adapter calls without pretending the worker owns the public context. | **CLOSED.** |
| Consistency-1 P2-2 / Safety-1 P2-1 / Origin P2-1 — local close globally drained the deployment | Separate local resource lifecycle from deployment generation state. | Lines 137–187 define independent record, local-resource, and deployment machines; lines 236–246 give immutable ancestry/counting; lines 360–442 restrict ordinary close to selected descendants while peers remain `CURRENT`, and retained containment remains globally visible. The two-runtime counterexample now has a legal trace. | **CLOSED.** |
| Consistency-1 P2-3 — buffer invalidation appeared both before and after the zero-permit barrier | Establish one authoritative pre-zero queue barrier and nonduplicative cutover cleanup. | Lines 544–581 place invalidation at migration step 4, serialize refresh/dequeue races under the queue lock, retain the marker through the wait, release each permit once, and reserve step 10 for registration/handle retirement and cleanup without another release. Lines 623–647 and vectors 754–756 agree. | **CLOSED.** |
| Safety-1 P2-2 — already-open legacy peers escaped the lifetime handshake | Add finite stop-the-world activation with operator inventory, physical access fencing, durable state, and closed recovery. | Lines 446–519 define owner, states, legal transitions, timeout/refusal, indeterminate recovery, unused rollback, first-open irreversibility, restart enforcement, and PostgreSQL/SQLite physical exclusion. A marker or cooperative census alone is explicitly insufficient. | **CLOSED.** |
| Stopped-design final Safety P2-1 — point verification did not retain operation ownership | Replace raw-plan resolution with whole-operation leases and quiescence fences. | Lines 214–312 retain ownership from atomic acquisition through every lowering, dispatch, fetch, snapshot, assembly, and publication boundary; lines 400–442 preserve non-killable and no-transaction identities; lines 715–732 retain the complete original pause/race closure. | **REMAINS CLOSED.** |

## Changed-range analysis

The `diff -u` from preserved `W2-AdmissionLifetimeRedesign-Initial.md` to the corrected 825-line overlay is confined to the four remediation dispositions and their dependent vectors:

- issuer-private worker authority plus the explicit A11/W1 prerequisite;
- local resource ancestry/state separated from deployment migration state;
- a one-time activation state machine and physical legacy-access fence;
- a unique pre-zero subscription queue barrier with single-release accounting.

Dependent edits update acquisition lock order, close outcomes, staged enablement, test vectors, static checks, and remediation-count testimony. They do not alter the base algebra, canonical encoding, result-role prerequisite, resource profile, function fingerprints, authored mappings, or query/question semantics. No change falls outside the remediation plan’s declared roots. The activation protocol is the planned correction for Safety P2-2, not an unclassified new architectural root.

## 0. Evidence base

At both START and END, the manifest SHA was exactly `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`; manifest counts were exactly 9/11/13/48/13/26; and `shasum -a 256 -c` passed every entry in the current manifest plus the five recursive manifests.

I read the complete workspace/product instructions, review-loop skill and template, brief, DRAFT-2, remediation plan, preserved initial overlay, prior reports and originating closure, stopped base and STOP record, parent-plan §§15–16, W1 acceptance/layout, and complete relevant A2/A3/A6/A7/A8/A11/A12 and authority/protocol/state/operation/semantic contracts. I compared Initial to current with `diff -u` and checked every supersession quotation against the 711-line base. No current-round peer, closure, or reviewer prompt was read. No file, test, build, generator, service, database, dependency, Git, or GWZ state was modified.

## 2. Invariant analysis

Attacks on raw-plan escape, lease forgery/reuse, ownership after awaits, no-transaction reads, non-killable workers, A7 commit knowledge, local versus global close, cross-process generation fencing, migration failure recovery, idle subscriptions, delayed delivery, snapshot/cursor consistency, authority expiry, activation restart/rollback, and mixed peers produced no additional defect.

The composed protocol has one coherent acquisition-to-publication trace: acquisition atomically charges immutable local ancestry and a deployment permit; owner transfers are compare-and-transfer; hard fencing suppresses future steps without inventing quiescence; final closure requires terminal operations and independent A7 knowledge. Migration alone enters `DRAINING_OLD`, performs the unique queue barrier, proves zero old permits, and only then begins effects or publishes the requested generation. The future W1/A11 amendments and activation package are explicit prerequisites, so the frozen W1 bytes are neither silently reinterpreted nor claimed already sufficient.

## 3. Risks and next action

Real database, thread, async, crash, advisory-lock, credential-rotation, and supported-version evidence remains deferred to implementation gates. The exact amended W1/A11 contract wording and activation implementation still require separate independent review.

The single next action implied by this verdict is same-tuple verdict merge with the independent Safety review and required originating closure. If those also report GO, the manager may accept only this exact composed design tuple; no amendment or implementation is thereby authorized.

