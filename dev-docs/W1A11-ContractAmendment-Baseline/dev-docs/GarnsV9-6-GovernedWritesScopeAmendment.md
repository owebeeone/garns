# Garns v9-6 governed write scope amendment

**Operator decision:** binding, external-write capture deferred  
**Architecture status:** draft for review with W1, not independently reviewed  
**Decision date:** 2026-10-03  
**Recorded by:** manager

The operator has directed that v9-6 finish the PostgreSQL-first, async runtime
with supported SQLite, without waiting for external-write capture. Supported
application mutations go through Garns. External capture becomes a separately
authorized future project described in
[its project brief](GarnsExternalWriteCapture-ProjectBrief.md).

## Governing documents and precedence

This is an additive scope amendment. Do not alter the reviewed historical
documents or their acceptance records.

| Historical document | SHA-256 |
|---|---|
| `GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |

The earlier D6a/D7/D8 and D4/D6b operator records remain controlling for
Python, identity, delivery shape and backend support. This amendment supersedes
only their open D5 status and the historical plan/amendment requirements for
external capture in this release. Unmentioned requirements remain binding.

## D5 closed as deferred

D5 is **binding/closed: no external-capture branch in v9-6**. Neither triggers
nor logical decoding is selected. Selecting or implementing either mechanism
is not a W1 or release prerequisite. No capture prototype is assigned by this
decision, and the future project is not on the release critical path.

## Supported write contract

- Governed mutations are the supported Garns write operations executed under
  the trusted in-process context and the runtime transaction contract.
- Live correctness, ledger history and replay guarantees require that bound
  data is modified only through supported governed paths and supported Garns
  schema-management operations.
- Application deployment must restrict unmanaged write access through its
  trusted host, credential custody and database privileges. A database role
  cannot distinguish Garns from arbitrary SQL using the same credentials;
  no protection against a trusted administrator or compromised host is claimed.
- Raw SQL, other services or administrative edits outside those paths are
  outside live/history guarantees. They can invalidate those guarantees even
  when a subsequent governed write refreshes some results. A static query
  reads committed state under its transaction isolation; that is not proof
  that subscriptions or replay noticed an external change.
- Automatic detection or repair of out-of-band writes is not promised.
  Operational documentation must warn against them while the runtime is in
  use; any supported resynchronization procedure needs separate evidence.
- All bound-data effects of every supported Garns operation, including
  schema management, migration DML/backfills, DDL conversions and induced
  cascades or triggers, must be atomically represented in its governed
  ledger/footprint/revision contract or the operation must refuse before
  effect. Deferral is not permission to lose effects caused by Garns itself.
- A metadata-only generation transition is admissible only under an A12
  contract proving that it changes neither bound rows nor the observable
  values/result shapes of retained queries. Any incompatible reader or cursor
  must instead receive a typed generation/refetch-required outcome, ordered
  with the generation publication, before it can continue with stale state.

W1 must classify and test three cases explicitly: a metadata-only generation
change uses that evidenced generation transition or refuses; migration
DML/backfill atomically records every data effect or refuses before effect;
and a DDL conversion/cascade changing bound rows has the same atomic accounting
or refusal requirement. Real database proof belongs to later implementation
gates, not this document review.

## Requirements retained

Keep the async-only API, non-blocking SQLite, real PostgreSQL evidence,
authored storage bindings and provider-neutral in-process identity seam.
Keep durable transaction identity, atomic governed mutation/ledger recording,
known-abort/known-commit/indeterminate reconciliation, commit-safe revision
publication, multi-instance coordination, snapshot/watermark continuity,
bounded queues, replay, retention and schema-generation safety.

No external trigger installer, WAL consumer, claim/ack worker or capture
service is required. Internal mechanisms used to make governed writes safe
are not forbidden, but they cannot create an external-write support claim.

## W1 contract and ADR changes

W1 still produces and reviews A1–A15. Use explicit scope records rather than
omit ADR identifiers and leave dependencies ambiguous:

| ADR | Revised obligation |
|---|---|
| A2/A3 | Freeze governed backend and async API contracts; no mandatory external-capture method or public working capture endpoint. If a compatibility surface remains, it must refuse as unsupported before effect. |
| A4 | Keep durable governed transaction identity and commit-safe revision/replay ordering; external-source ordering is deferred. |
| A5 | Record external capture as deferred, with non-claims; do not require a source mechanism, worker protocol or speculative adapter interface. |
| A11 | Keep all governed execution, transaction, subscription, provenance, expiry, counterfeit and disclosure requirements. External-capture processor/admin/source-actor requirements are deferred. |
| A12 | Keep migration locks, mixed-version safety and interpretation/retention of governed ledger generations. Classify metadata-only generation transitions, migration DML/backfills and DDL conversions/cascades under the effect-accounting/refusal and no-stale-continuation rules above; pending external capture is deferred. |
| A14 | Freeze governed deployment privilege/RLS and effect-coverage boundaries for writes and schema-management operations, including induced data effects. External-writer role matrices and capture-source tamper controls are deferred. |
| A15 | Keep governed consumer watermarks, compaction, retained floors, cursor expiry and refetch semantics. |

A1/A6–A10/A13 remain required, subject to the existing support decisions.
Preserve explicit per-package ADR dependencies for these revised scopes.
Future extensibility does not justify an additional capture implementation
or delaying W1 to design the future project.

## Execution and release gate changes

- The critical path becomes W0 → W1 → W2 → W3 → W4 → W5 → W7.
- W6 is deferred and has no builder assignment or merge obligation.
- W7 consumes accepted W0–W5 output tuples, accepted scoped A1–A15 and this
  scope amendment. It does not wait for a W6 output tuple.
- P6 is reported **deferred/out of release scope**, never PASS. P0–P5 and
  P7–P12 remain required for their governed-write claims, including independent
  final implementation review and Surface review at the public API freeze.
- The provider-neutral amendment's W6 extensions, capture-only verification
  matrix cells, external-actor checks and W7 requirement to consume W6
  counterfeit/claim/ack evidence are deferred. Its governed W3/W7 trust,
  lifecycle, secret-disclosure and named-provider-absence checks still apply.
- P7/P9/P10 and the parent verification/observability requirements apply fully
  to governed provenance, evidence and operations; their external-source-only
  cases are deferred, not silently counted as passing.
- W8 still follows the core release and uses explicit ADR dependencies. It
  cannot implicitly reintroduce external capture.

Ownership paths in `docs/PRODUCT_LAYOUT.md` are unchanged. The allocated W6
and capture-research paths are dormant; the historical W7 dependency row is
superseded by this amendment. No package is relocated or reassigned.

## Review and evidence discipline

Include this amendment in W1's independent architecture reviews. Operator
approval of the reduced scope is recorded; architecture acceptance and
implementation evidence are not claimed by writing this document.

Preserve inherited W0 grammar, capture code, tests and baseline evidence.
Their presence does not establish shipped PostgreSQL capture support. W1/W7
must classify legacy capture surfaces and documentation so the public release
does not advertise or enable unverified external capture. Any later source or
test retirement must be explicit and preserve the historical evidence.

The release evidence manifest must identify deferred gates and the applicable
scope tuple. Ship documentation describing the governed-write restriction,
supported privilege model and external-write non-claims, without implying
that administrators are prevented from bypassing them.
