# W1A11-ContractAmendment — STATE-AXIS REVIEW

**Review object:** `W1A11-ContractAmendment`, builder-complete candidate at 47-file filesystem-manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`; controlling `dev-docs/W1A11-ContractAmendment.md` SHA-256 `e5293ebeb777a31f07203bcba6860e5875fb0d1e643ea98f3a49efc92438db48`; not accepted; 2026-10-04.  
**Baseline:** Approved no-Git exact-tuple exception. Accepted sources were read from the immutable 120-file `dev-docs/W1A11-ContractAmendment-Baseline/` archive, manifest SHA-256 `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf`; current source was read directly from the verified filesystem tuple.  
**Date:** 2026-10-04  
**Axis:** Durable-state semantics and adversity: transitions, ownership, barriers, crash direction, restart legality, and closed recovery grammar. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — eight P2 findings block. I pre-commit to GO on a revision that resolves P2-1 through P2-8 as specified.

---

## 0. Evidence base

I read the complete review prompt; `AGENTS_GWZ.md`, `AGENTS.md`, review-loop skill/template, plan §§15–16, checkpoint, execution brief, ownership extension, amendment/DRAFT, `PRODUCT_LAYOUT`, A1–A16, W1/W2 acceptances, and the full accepted W2 base and lifetime overlay. I inspected and diffed all amended contract/reference files against the archive, concentrating on `admission.py`, `lifetime.py`, `lifetime_reference.py`, `generation_reference.py`, `worker_authority.py`, `protocols.py`, `state.py`, and all contract tests.

The allowed Python 3.14 focused suite passed 76/76 and `tools/check_product.py` passed 5/5. Inline read-only probes reproduced every dynamic counterexample below. Start and end verification both produced: manifest 47/47, Inputs 9/9, Control 3/3, Baseline 120/120, ReadOnly 111/111, ProductGuard 614/614; all had zero failures. The manifest, controlling-document, and prompt hashes remained exact.

## 1. Findings

### [P2-1] Forgeable value permits can make live operations disappear from the generation count

`lifetime.py:83-93` exposes `GenerationPermit` as a constructible value, and `generation_reference.py:111-114` releases by value equality rather than exact issued identity. A probe acquired a live lease, constructed `GenerationPermit(operation, coordinator.admission_epoch)`, released it, and reached `MIGRATING` with that lease still live. This violates W2 §§4/8.2: callers cannot release permits, and migration effects require authoritative global zero. Impact is cutover overtaking resumable old work. Make permits sealed exact-instance identities, keep epoch private, and accept release only from the owning registry record. Regression: every fabricated/equal/cross-coordinator permit must refuse without changing count; migration must remain blocked.

### [P2-2] Local close reports `CLOSED` while a valid buffered-delivery permit remains globally charged

`lifetime_reference.py:346-372` considers leases and resource charges but never `_buffers`; buffer permits live separately at lines 374-440. After enqueueing one envelope, hard-closing its subscription returned `CloseKnowledge.CLOSED` while coordinator count remained 1 and `_BufferRecord.permit_live` remained true. This violates W2 §§7/9: `CLOSED` guarantees no queued valid buffer or future delivery. Impact is a false terminal state and a permanently blocked migration. Finalization must atomically invalidate/release selected buffers exactly once, or return nonterminal knowledge until that happens. Regression: close every resource level with queued buffers and assert no `CLOSED` until buffer ownership is gone. This is a bounded model correction.

### [P2-3] Buffer exchanges do not bind envelope provenance to the producing lease or consuming admission

`publish_refresh_buffer` and `dequeue_buffer` (`lifetime_reference.py:385-422`) check kind/queue/generation but never compare the envelope’s admission identity, plan digest, cursors, or advancement with the refresh lease and subscription registration; dequeue never compares the supplied handle with `envelope.admission_identity`. A probe enqueued an envelope for `sales.live`, dequeued it using a separately admitted `sales.other` handle, and obtained a handoff lease whose guarded plan was `sales.other`. This violates W2 §9’s exact-envelope validation and permits cross-plan rows to be relabeled. Store authoritative provenance in the private buffer record and compare it at both exchanges. Regression: cross-handle, stale-plan, copied, cursor-mismatched, and already-delivered envelopes must refuse without count mutation.

### [P2-4] Publication is neither a single-use state transition nor mandatory for refresh handoff

`run_plan_step` (`lifetime_reference.py:218-245`) permits `PUBLICATION` from `ACQUIRED` or already `PUBLISHING` and increments the public count each time. One lease published twice in a probe. Separately, `publish_refresh_buffer` bypasses `run_plan_step` entirely; after the context expired, it still enqueued a buffer and completed `SUCCEEDED`. This violates W2 §§4–5 and A11’s zero-staleness publication barrier. Impact is duplicate public handoff or delivery after authority/fence expiry. Introduce one guarded `RUNNING -> PUBLISHING` linearization point, reject repetition, and route refresh enqueue through it atomically. Test duplicate publication plus expiry/invalidation/local-fence races before enqueue.

### [P2-5] Activation recovery treats absence of evidence as authoritative no-activation proof

`generation_reference.py:64-78` accepts `recover_activation(None)` and resets `ACTIVATION_INDETERMINATE` to `UNACTIVATED`; `withdraw_unused` at lines 87-91 accepts only an epoch and erases it. The existing test endorses this transition. W2 §8.1 requires authoritative no-activation/restored-access proof, and unused withdrawal requires the same physical fence plus no-ever-open proof. Absence is not evidence; this may restore legacy access after an uncertain activation. Require typed, binding/epoch-bound negative recovery and withdrawal evidence, retain the last epoch/evidence against reuse, and test that `None`, stale, and mismatched proof leave state indeterminate/unused unchanged. This is an architectural proof-shape correction.

### [P2-6] `MIGRATION_INDETERMINATE` is an implemented entry-only stuck state

`generation_reference.py:166-172` can enter `MIGRATION_INDETERMINATE` but exposes no authoritative-success, authoritative-full-rollback/new-epoch, or non-reuse recovery transition. The accepted overlay §3.1 explicitly defines those exits. This violates the required closed recovery grammar and makes any post-effect uncertainty permanent in the reference contract. Add proof-bearing recovery operations with exact requested/old binding and epoch rules; ordinary work must remain refused until one succeeds. Regression: enumerate all three legal resolutions and reject every unsupported exit without mutation. Architectural.

### [P2-7] Operation capability is not derived from operation kind, allowing query authority to authorize mutation effects

`lifetime_reference.py:187-191` maps only subscription kinds to `LIVE` and every other kind—including `GOVERNED_MUTATION` and `MIGRATION`—to `QUERY`. `WorkerAuthorizationIssuer.issue_for_dispatch` (`worker_authority.py:86-117`) accepts the capability from its caller rather than deriving/checking it against the operation. A query-only context acquired `GOVERNED_MUTATION`, issued `Capability.QUERY` worker authority, and ran the effect callback. This violates A11/A14 and the exact effect-boundary contract. Define a closed operation-kind/capability mapping and make worker issuance use the registry-owned requirement. Regression: query-only contexts must create neither mutation/migration leases nor effect ordinals.

### [P2-8] Parameters are mutable across acquisition because executable protocols accept an unbound second copy

The private lease records parameters at `lifetime_reference.py:77,154-213`, but `run_plan_step` supplies only the plan. `protocols.py:37-41,78-80` then accepts caller-provided `ParameterValues` again for execute/snapshot/subscribe, with no verifier method capable of comparing them. Thus a lease may be acquired under one parameter set and executed under another, contrary to W2 §§4–5’s immutable whole-operation binding. Remove the duplicate parameter argument or expose only registry-bound, immutable parameters to guarded consumers. Regression: post-acquisition substitution must refuse before lowering/effect/publication. Architectural interface correction.

## 2. Invariant analysis

Attacks that held: handles and leases were sealed/noncopyable; normal acquisition charged all ancestors and isolated peer close; owner transfer did not recharge; identical terminal completion was idempotent and conflicting completion preserved counts; hard fencing retained operation identity and suppressed the ordinary guarded publication path; ordinary two-participant drains waited for both permits; worker tuple/ordinal reuse checks refused; first activation made reset/withdrawal refuse; and close retained transaction and read-operation identities independently.

Those successes do not close the alternate permit-release, buffer, publication, activation-recovery, capability, or parameter paths above. Passing deterministic tests proves only tested schedules, not production threading, persistence, databases, physical fencing, or crash recovery.

## 3. Risks and next action

Deferred production coordination and restart evidence remain legitimate residual risks, but the findings are internal contract/reference defects, not demands for deferred production proof. P2-1, P2-5, P2-6, P2-7, and P2-8 alter ownership or interface shape and require a consolidated architectural correction followed by fresh peer-blind review; P2-2 through P2-4 require exhaustive exchange/finalization regressions in that same patch. The next action is one builder-owned remediation mapping all eight IDs to the stated closure tests, then a new exact tuple and independent re-review.
