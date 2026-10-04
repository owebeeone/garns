# W2 admission-lifetime replacement overlay — SAFETY-AXIS REVIEW

**Review object:** composed design-only tuple: `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`; corrected replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, filesystem tuple pinned by the nine-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256` at SHA-256 `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`. Files were read directly under the accepted no-Git exception.  
**Date:** 2026-10-04  
**Axis:** Safety — focused originating verification of whole-operation lifetime ownership and local-close isolation. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both originating Safety P2 counterexamples are closed; no new P0/P1/P2/P3 or architectural root was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tuple | Status |
|---|---|---|---|
| Stopped W2 Safety P2-1 — admission lifetime ended after verifier resolution | Exact-instance lease and generation permit span acquisition through terminal publication or authoritative containment. | Lines 224–267 atomically validate, insert, attribute, and retain the lease; lines 270–358 cover every effect and authority boundary; lines 360–442 distinguish graceful drain, hard fence, final quiescence, non-killable containment, and A7 knowledge. | **CLOSED.** |
| Origin Safety P2-1 — ordinary close globally entered deployment `DRAINING_OLD` | Separate local resource lifecycle from deployment generation lifecycle; ordinary close drains only immutable descendants, while only migration enters `DRAINING_OLD`. | Lines 137–187 define independent closed state machines; lines 224–246 give immutable ancestry and counts; lines 360–435 scope local drain/fence/finalization; lines 521–597 retain locally contained permits in deployment-wide migration accounting. | **CLOSED.** |

## Changed-range analysis

The preserved initial overlay differs materially in four accepted areas. Relevant to originating closure, the correction introduces exact local runtime/pool/connection/subscription states, immutable resource ancestry, per-ancestor lease charging, and local-only close transitions. It reserves deployment `DRAINING_OLD` for the serialized migration path.

The correction also adds issuer-private worker authorization, a unique pre-zero migration queue barrier, and stop-the-world legacy activation. These preserve the lifetime proof: worker authority cannot outlive its exact command/effect ordinal; queued buffers cannot be double-released or enqueued behind migration invalidation; and already-open legacy peers cannot bypass lifetime fencing. No changed range reopens the original counterexamples, and no new architectural root was identified.

## 0. Evidence base

At START and END:

- Manifest SHA-256 was exactly `55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea`.
- Object and DRAFT hashes were exactly `28f7ca80…943a4` and `c7e511f8…edaa2`.
- Counts were exactly 9/11/13/48/13/26.
- Every entry in all six required manifests verified. No tuple movement occurred.

I read the complete prompt, corrected 825-line overlay, unchanged 711-line base, brief, DRAFT-2, STOP, remediation plan, preserved initial overlay, legitimate initial reports and originating report, relevant accepted ADRs/contracts, and the Initial-to-current diff. I read no current peer report, prompt, or closure. No writes, tests, builds, services, or Git/GWZ operations occurred.

## 2. Invariant analysis

The original lifetime race remains closed at every pause after acquisition and before lowering, dispatch, adapter start, first/later fetch, child/total work, snapshot watermark, registration, assembly, cursor advancement, and public result/delivery:

- The lease and shared generation permit remain charged across every await and owner transfer.
- Graceful local drain blocks new descendant work but permits already-owned pinned work before final fencing.
- Hard fencing prevents another command or publication while retaining resumable work as `CONTAINED`.
- `CLOSED` requires terminal attributed leases, buffers, handoffs, workers, and independently valid A7 knowledge.
- Migration cannot cut over while a local nonquiescent participant retains a deployment permit.
- Reopen creates new exact identities and cannot adopt or bypass old contained work.
- Nontransaction reads remain visible through `OperationIdentity`.
- Snapshot rows, watermark, and registration remain one-generation products.
- Delayed buffers are either handed off before cutover or invalidated exactly once by the pre-zero barrier.
- Worker effects require immediate issuer-private validation; the public task-bound context is never transferred.

The local-close sequence is also closed. Closing one connection selects only leases dispatched to it; pool, subscription, and runtime close select precisely their immutable descendants. Other participants remain `LOCAL_OPEN`, their handles and epochs remain valid, and the deployment remains `CURRENT`. Retained local containment stays registered and globally counted, so isolation does not weaken migration fencing. Only migration, while holding its mutex, changes the deployment to `DRAINING_OLD`.

Raw-plan escape, copied or cross-runtime handles and leases, mixed peers, authority expiry, idle subscriptions, duplicate completion, and A7 commit-knowledge confusion all retain explicit fail-closed paths.

## 3. Risks and next action

Real worker, database, advisory-lock, crash, and deployment activation evidence remains appropriately deferred to implementation gates. Current W1/A11 bytes remain unchanged; their separately reviewed amendment is still a prerequisite.

The next action is to combine this originating GO with the fresh full-review verdicts on the same manifest. Acceptance, if authorized, applies only to the exact base-plus-overlay design tuple and does not launch W1 amendments or implementation.

