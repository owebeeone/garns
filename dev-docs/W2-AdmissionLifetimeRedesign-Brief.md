# W2 admission lifetime redesign brief

**Status:** operator-authorized replacement design and review only  
**Date:** 2026-10-03  
**Owner:** manager

The operator said “proceed with narrow redesign” after the W2 stop. Authorize
one new additive design object, not a third repair of the stopped W2 object:
dev-docs/W2-AdmissionLifetimeRedesign.md. Its purpose is to replace point-in-time
plan resolution with whole-operation ownership, closing final Safety P2-1.
No source, test, grammar, ADR, accepted W1 contract, dependency, database,
service or Git/GWZ mutation is authorized. No build starts.

## Immutable baseline and precedence

Read workspace/product instructions and CurrentProgramCheckpoint.md first.
Stopped W2-QueryPlanningDesign.md SHA-256
0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e
remains unchanged. Its complete manifest3 SHA-256 is
5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36.

Read full stopped design, W2-Design-STOP.md, final Consistency/Safety reports,
the accepted W1 tuple, A2/A3/A6/A7/A8/A11/A12, protocol/authority/state/operation
types, and relevant scope/support/ownership records. All previous closed
counterexamples remain regression obligations. Source48/control13/W1 26
recursive manifests must match at start/end.

The replacement is a narrowly scoped overlay. Give an exact supersession map
by sections and quoted clauses of the hash-pinned stopped design: verifier
resolution/return, revocation/epoch transitions, pipeline, live reuse, tests,
ownership/protocol prerequisites. Unchanged canonical algebra, result roles
prerequisite, resource profile, function fingerprints, expression reuse,
authored physical mappings and query/question semantics remain intact.
Do not claim acceptance of stopped bytes alone. Acceptance, if achieved,
applies only to the exact base-plus-overlay tuple, not actual W1 implementation.

Preserve the old stop and its exhausted two-remediation history. This operator-
authorized replacement begins its own ordinary bounded review, zero initial
remediations, with fresh independent Consistency/Safety reviewers (5.6 Sol).
No review cap resets automatically. Originating final Safety reviewer must
verify its original lifetime counterexample against the composed design.

## Sole drafter and writable boundary

One 5.6 Sol drafter writes only dev-docs/W2-AdmissionLifetimeRedesign.md, with
apply_patch. Everything else is read-only, including stopped design and all
reports. Manager owns brief/manifests/testimony/prompts/reviews/acceptance/
checkpoint. No helper agents, broad redesign, source changes or self-closure.

Use repository document format. Keep the overlay focused and concrete; a state
table and invariant/closure map are useful. Return COMPLETE concise testimony,
exact design hash, superseded clauses and unchanged input verification.
Stop writes for pinning/review.

## Required closed design

1. Distinguish reusable admitted read handles from per-operation leases.
   Exact-instance issuer/runtime-owned registry records hold plan/provenance/
   binding; no exposed raw plan/claim bag, duck-typed wrapper or copied token.
   Define narrow contract-only verifier/lease interfaces and owner, exact
   operation identities, owner transfer to worker/containment and refusal
   catalog. Backend/compiler imports do not reverse.
2. Acquisition must atomically validate and account for operation ownership.
   Define the linearization points and lock order; a check followed by
   unprotected I/O is insufficient. Cover lowering, queued dispatch, adapter
   start, all fetches/child/total work, snapshot cursor/registration, assembly,
   delivery/cursor advancement and public result publication. No primitive
   returns or caches a reusable raw Plan beyond its guard.
3. Give runtime/binding admission states and lease states as closed enums,
   complete legal transitions, idempotent/conflicting completion rules,
   exception/cancellation handling. Separate “block new work/drain old work”
   from final revocation/publication. Resolve graceful-drain vs suppressed
   late delivery precisely; existing work must not use stale semantics.
4. Close/deadline/force-close cannot assert CLOSED or release resources while
   queued/running/resolved/contained operations can resume. Preserve A3/A8
   nonquiescent and unresolved knowledge, including reads with no write
   transaction identities. Non-killable worker retains lease ownership until
   authoritative quiescence; a caller cancellation/finally is not proof.
   Maintain A7 commit knowledge/commit fence and existing retained identities.
5. Migration cannot change physical/schema semantics or publish next generation
   while any old-generation operation could execute or publish. Specify
   exclusive/shared generation fencing, acquiring/ordering migration locks,
   finite wait/refusal before effects, failure/indeterminate behavior and
   rollback/reopening policy. Scope must cover all participating runtime
   instances/connections for one qualified deployment, not only a local cache.
   No online/mixed-version schema support silently added; governed-write
   migration accounting remains mandatory; external capture stays deferred.
6. Snapshot/subscription/refresh/delivery cannot pair old-plan rows with a new
   cursor/generation. Idle subscriptions should not hold immortal execution
   leases and block shutdown/migration forever. Cover per-unit leases,
   authority revalidation, durable registration/cursor barriers, buffered
   batches and consumer handoff; specify what happens to precomputed stale
   results and what closed exactly guarantees.
7. Frozen W1 remains unchanged. Specify required separately reviewed protocol/
   lease/result-role ownership amendment, handshakes, exact integration paths,
   staged enabling and raw/legacy/mixed-version fail-closed behavior. Names
   remain internal and provisional; W3 public Surface remains future.
8. Design-level traceable closure vectors at every original pause point:
   after acquire, before lowering/dispatch/adapter/fetch/snapshot watermark/
   publication, race close/drain/force timeout/migration/reopen/epoch change.
   Include non-killable worker, no-transaction read, cross-runtime migration,
   stale/copied/released lease, duplicate completion, exception, delayed
   subscription delivery and correctly admitted success.
   Give falsifiable future tests/static checks; do not demand or claim real
   database/async implementation proof in this design gate.

Preserve CPython >=3.11, supported SQLite, PostgreSQL-primary 15+, async-only
future runtime, in-process provider-neutral trust, one convergent product,
unenforced and unchanged grammar. External capture, crypto/providers,
PG execution, public API names/Surface, W1 P3 assigned W3, W2 implementation
and unrelated refactors remain deferred.

## Review and handoff

Manager pins overlay/brief/testimony plus stopped base, stop/final reports
and recursive source/control/W1 inputs. Hash-pinned no-Git review exception
from accepted parent plan §15 applies; no clean commit or landing claimed.
Reports filed verbatim, all P0/P1/P2 block, one consolidated correction per
round, at most two architectural remediations for replacement object.
GO/GO plus originating lifetime closure accepts design only. A subsequent
separately scoped W1 amendment and implementation execution brief still
require authority; no automatic implementation dispatch.
