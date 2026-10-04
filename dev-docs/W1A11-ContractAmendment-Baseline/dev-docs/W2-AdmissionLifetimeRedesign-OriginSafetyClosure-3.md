# W2 admission-lifetime replacement overlay — SAFETY-AXIS REVIEW

**Review object:** composed design-only tuple: `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`; final corrected replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, filesystem tuple pinned by the eighteen-entry `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256` at SHA-256 `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`. Files were read directly under the accepted no-Git exception.  
**Date:** 2026-10-04  
**Axis:** Safety — focused originating verification of whole-operation lifetime ownership and local-close isolation after the final retirement-state correction. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — the original stopped lifetime and replacement local-close counterexamples remain closed; the narrow correction introduces no new P0/P1/P2/P3 or architectural root.

---

## Prior-finding closure table

| ID | Verified on final tuple | Status |
|---|---|---|
| Stopped W2 Safety P2-1 — admission lifetime ended after verifier resolution | Exact-instance operation leases and generation permits still span lowering, dispatch, adapter/fetch work, snapshot and assembly through publication or authoritative containment. Graceful drain, hard fence, final quiescence, and A7 knowledge remain distinct. | **CLOSED.** |
| Origin Safety P2-1 — local close globally entered deployment `DRAINING_OLD` | Independent local-resource states and immutable ancestry remain unchanged. Connection/pool/subscription/runtime close affects only attributed descendants; unrelated peers remain open under deployment `CURRENT`; retained containment remains globally counted. Only migration enters `DRAINING_OLD`. | **CLOSED.** |

## Changed-range analysis

The Revision-2-to-final diff is confined to removing `ACTIVATION_RETIRED`, its two incoming edges, and the implied retirement capability. `ACTIVE(epoch)` now has no outgoing activation transition and persists across resource close, full shutdown, restart, migration, migration recovery, and binding non-reuse. Retirement, deactivation, reset, or epoch-erasure requests refuse atomically without changing access fences, ownership, counts, buffers, A7 knowledge, or durable evidence.

`ACTIVATION_INDETERMINATE` retains its physical fence until authoritative restoration to `UNACTIVATED` or completion to `ACTIVE_UNUSED(epoch)`. Deployment decommissioning is explicitly outside this release. The narrow change does not touch the lease, local-close, migration-permit, worker-authority, queue-barrier, or publication rules. No new architectural root was found.

## 0. Evidence base

At START and END:

- manifest SHA-256 was exactly `86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2`;
- object and DRAFT hashes were exactly `01257e07…d6bb26` and `161c9005…54a377`;
- inventory counts were exactly 18/11/13/48/13/26;
- every entry in all six required manifests verified, with no tuple movement.

I read the complete prompt, final 853-line overlay, unchanged base, Revision 2, both remediation plans, permitted prior reports and DRAFTs, and the complete narrow diff. I read no current peer prompt, report, or closure. No writes, tests, builds, services, or Git/GWZ operations occurred.

## 2. Invariant analysis

Every original lifetime pause remains owned after acquisition and before lowering, queue dispatch, adapter start, first or later fetch, child/total work, snapshot watermark, registration, assembly, cursor advancement, and public result or delivery. Graceful drain may finish pinned work before final fencing; hard fence prevents another command or publication while retaining containment; `CLOSED` and migration cutover remain impossible while work can resume. Nontransaction reads retain operation identities, non-killable workers retain permits, and reopen cannot adopt old ownership.

The local-close trace also remains closed: immutable ancestry selects only the closing resource’s descendants, surviving runtimes continue acquiring under deployment `CURRENT`, and retained local containment remains visible to a later migration.

The removed-retirement counterexample now fails safely. With active leases, queued buffers, a non-killable worker, or unresolved A7 knowledge, a retirement request has no legal transition or capability. It cannot release a permit, alter ownership, remove evidence, weaken physical fencing, or enable legacy access. Restart still requires the same `ACTIVE(epoch)`. With no active work, the request remains unsupported rather than creating an underspecified decommissioning path. Indeterminate activation cannot escape through retirement and remains fail-closed when neither authoritative recovery proof exists.

Raw-plan escape, copied/cross-runtime leases, authority expiry, delayed buffers, mixed peers, snapshot-generation mixing, and premature migration publication retain their specified refusal or containment paths.

## 3. Risks and next action

Real database, worker, advisory-lock, crash, and activation evidence remains appropriately deferred. Current W1/A11 bytes remain unchanged and require separate amendment authority.

The next action is to combine this originating GO with the fresh same-manifest full reviews. Any newly discovered architectural blocker would stop the lane because both replacement remediation allowances are exhausted; otherwise acceptance may cover only this exact composed design tuple.

