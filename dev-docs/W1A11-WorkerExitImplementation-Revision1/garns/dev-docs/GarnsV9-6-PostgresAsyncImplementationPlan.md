# Garns v9-6 — PostgreSQL and async runtime implementation plan

**Status:** remediated draft for round-2 architecture and implementation review  
**Plan owner:** manager synthesis  
**Baseline:** repaired and ratified v9-5 build B2  
**Direction:** [GARNS_DIRECTION.md](../docs-staging/F51/GARNS_DIRECTION.md)  
**Implementation evidence:** [B2 report](../build/B2/REPORT.md),
[repair](../build/B2/REPAIR.md), [R1 review](../reviews/R1/REVIEW.md),
[R2 review](../reviews/R2/REVIEW.md)

## 1. Objective

Turn the ratified v9-5 semantic compiler into a credible production data
runtime with:

- PostgreSQL as the primary production backend;
- an async-only public API for database access, transactions, capture,
  migrations and live subscriptions;
- SQLite retained as a secondary local/test backend behind the same
  async-facing contract;
- the v9-5 language and semantic guarantees preserved unless a separately
  reviewed ADR proves a grammar change necessary;
- real concurrency, cancellation, recovery and backpressure semantics; and
- executable evidence against a real PostgreSQL service.

This is a runtime/backend iteration, not another language exploration.

## 2. Desired outcome

At the end of v9-6, an application can:

```python
runtime = await GarnsRuntime.open(
    program,
    world="SALES",
    deployment="PROD",
    context=trusted_execution_context,
)

result = await runtime.execute(
    "sales.open_orders",
    parameters={"minimum": 100},
)

async with runtime.transaction() as tx:
    await tx.change(
        "sales.Order",
        order_id,
        {"sales.Order.status": "closed"},
    )

async with runtime.subscribe(
    "sales.open_orders",
    parameters={"minimum": 100},
) as subscription:
    async for batch in subscription:
        consume(batch)
```

The final names may change through ADR review. The required properties may not:
qualified selection, explicit storage binding, cancellation-safe transactions,
post-commit notification, bounded subscriptions and stable refusal behaviour.

## 3. Binding constraints

The implementation must preserve these v9-5 laws:

1. Source resolves once into a typed, module-qualified IR.
2. All downstream products consume that IR; none infer source meaning from
   schema names, test cases or generated SQL.
3. Every physical table, identity, scalar, link, scope and changelog name comes
   from an authored storage binding.
4. Static `query` and dynamic `question` share a relational/result plan.
5. Only a question derives footprints, routing, subscription and delta products.
6. A question must state and enforce `live bounded N`.
7. Rollback produces no revision, ledger row or batch.
8. Listeners observe committed state only.
9. Routed but result-neutral changes emit no batch.
10. Unsupported behaviour refuses at the earliest meaningful pre-effect
    boundary.
11. Evidence is generated through production stages and is reproducible.
12. Public runtime identities remain qualified.

Additional v9-6 constraints:

- No synchronous database I/O may execute on the application event-loop thread.
- An `async def` wrapper around synchronous I/O does not satisfy the plan.
- PostgreSQL behaviour is claimed only after execution against PostgreSQL.
- SQLite behaviour is not evidence of PostgreSQL behaviour.
- Transient notifications are never the durable capture record.
- Backend-specific concerns do not leak into Garns semantic source unless a
  reviewed language decision demonstrates that they are semantic.
- Cancellation is not a database outcome. Every transaction ends as known
  aborted, known committed, or indeterminate; only known-aborted work is
  suppressed, and indeterminate work is reconciled by durable transaction
  identity before retry.
- A replay cursor may never advance past an unresolved transaction that can
  still become visible before it. Ordinary sequence allocation order is not
  evidence of commit order.
- Subscription start, reconnect and overflow recovery use one documented,
  database-consistent snapshot/watermark handshake with no gap between the
  initial result and replay.
- PostgreSQL catalog/schema namespace is authored or immutably bound and every
  DDL, DML, inspection, migration and capture reference is fully qualified and
  correctly quoted. Pooled connection state, including `search_path`, cannot
  redirect a bound object.
- Public scope, capability and writer identity come from a provider-neutral
  trusted execution context. Raw caller assertions, if retained for internal
  tooling, are explicitly trusted-host-only and are not the public security
  boundary.
- External capture is complete only for a declared database-role/RLS matrix.
  Unsupported privilege states refuse before a source mutation can commit.
- Pool acquisition, statements, migration locks, shutdown and cleanup have
  documented deadlines and typed terminal outcomes; no correctness path may
  wait forever silently.

## 4. Scope

### In scope

- promotion of repaired B2 into a clean implementation repository;
- packaging and ordinary CI foundations;
- backend-neutral relational plans and backend protocols;
- async runtime, transaction, migration, capture and subscription APIs;
- a non-blocking SQLite adapter;
- PostgreSQL lowering, execution, pooling, ledger, schema inspection,
  migrations, live refresh and external capture;
- connection loss, cancellation, concurrency and replay behaviour;
- consumption of deployment `at`, `pool` and `mode`;
- differential SQLite/PostgreSQL testing for an explicitly declared common
  subset;
- documentation, diagnostics and generated evidence updates.

### Out of scope unless promoted by a reviewed change request

- grammar redesign;
- an ORM, session or identity-map layer;
- a complete verb runtime for `bulk`, `compound`, `restricted` and aliases;
- another database backend;
- every dormant declaration in the same iteration;
- treating PostgreSQL syntax as portable SQL;
- production authentication/identity-provider implementation;
- distributed cross-database transactions;
- using notifications alone as change capture.

## 5. Decisions required before implementation freezes interfaces

Each row becomes a short ADR. Work may prototype behind internal seams before
an ADR closes, but no public interface depending on it is considered stable.

| ADR | Decision | Required evaluation |
|---|---|---|
| A1 | PostgreSQL async driver and pool | Native async I/O, cancellation, codecs, prepared statements, pool lifecycle, maintenance, licensing, testability |
| A2 | Backend interfaces | Ownership of dialect, pool, connection, transaction, schema inspection, migration, ledger, capture and errors |
| A3 | Public async API | Runtime lifetime, transaction API, result type, subscription resource, cancellation and close semantics |
| A4 | Revision identity and order | Per-world/deployment/global scope, transaction identity, commit-order publication, replay cursor, unresolved transactions and ordering across capture relations; ordinary sequence order is insufficient |
| A5 | Capture source and consumption | Trigger-maintained durable table, logical replication, or staged support; durable event identity, claim/lease, idempotent revision creation and acknowledgement |
| A6 | Subscription buffering and snapshot | Queue bound, slow-consumer action, atomic snapshot/watermark handshake, replay, overflow/refetch and duplicate coalescing |
| A7 | Isolation and retry | Default isolation, serialization/deadlock retries, retry ownership, idempotency requirements |
| A8 | SQLite async adapter | Dedicated worker/thread, adapter dependency, or test-only status |
| A9 | Deployment configuration | Resolution of `at env NAME`, secrets, pool limits, read-only mode and configuration precedence |
| A10 | PostgreSQL test service | Reproducible local/CI provisioning, version range, extensions, lifecycle and parallel-test isolation |
| A11 | Authentication seam | Where trusted principal context enters; derivation and propagation of scope, capabilities and writer identity; trusted-host-only escape hatches |
| A12 | Migration locking and generations | Advisory locks, compatibility windows, online operations, mixed-version deployments and interpretation/draining of pending capture from earlier schema generations |
| A13 | PostgreSQL namespace contract | Authored catalog/schema provenance, qualification/quoting, safe `search_path`, function resolution and pooled-connection validation |
| A14 | Capture privilege boundary | Supported external-writer roles, object/function ownership, grants, RLS, trigger control, partitions, `TRUNCATE`, replication roles and tamper resistance |
| A15 | Replay retention | Consumer watermarks, retained floor, compaction ownership, cursor expiry, refetch and any explicitly bounded no-compaction phase |

### Recommended default positions for review

These are proposals, not closed decisions:

- One backend-neutral `Plan`/`ResultShape`; separate SQLite and PostgreSQL
  dialect lowerers.
- One async runtime protocol implemented natively by PostgreSQL.
- SQLite behind a single serialized worker boundary so it cannot block the
  caller's event loop.
- Durable trigger-maintained capture first is the recommended A5 outcome;
  notification is wakeup only. Until A5 closes, W6 retains separate trigger
  and logical-replication branches behind one typed-delta contract.
- Revision order scoped to one bound world/deployment and published through a
  commit-ordered durable mechanism; a sequence allocated before commit is not
  a replay cursor by itself.
- Bounded per-subscription queues with an explicit overflow/refetch outcome,
  never silent dropping, using the same snapshot/watermark handshake as first
  subscription and reconnect.
- Application retry only when the runtime can identify the whole transaction as
  safely retryable; otherwise return a typed retry/indeterminate outcome.
- One opaque trusted execution context enters the public runtime. Authentication
  provider integration remains outside v9-6, but the trust boundary does not.
- Fully qualified PostgreSQL identifiers plus a pinned safe `search_path` are
  mandatory even when a deployment currently uses only one schema.

## 6. Target component boundaries

```text
source + grammar
      │
      ▼
parse → resolve → qualified Program IR
      │
      ▼
explicit storage binding → WorldIR
      │
      ▼
backend-neutral relational/result Plan
      │
      ├──────────────► footprint/routing derivation (questions only)
      │
      ├──► SQLite dialect ──► async-facing SQLite adapter
      │
      └──► PostgreSQL dialect ──► async PostgreSQL backend/pool
                                      │
                                      ├─ transactions + ledger
                                      ├─ queries + refresh
                                      ├─ schema + migration
                                      └─ durable capture + wakeup
                                                    │
                                                    ▼
                                            async subscriptions
```

Dependency direction remains compiler → plan → backend. A backend never imports
the parser/resolver, and the compiler never imports a database driver.

## 7. Work packages

### W0 — promote and rebaseline B2

**Purpose:** start architectural work from a clean, reproducible repository
rather than an experimental review lane.

Deliverables:

- clean Garns repository containing repaired B2 implementation;
- current F51 product documentation plus the direction and this plan;
- lane-only prompts, candidates, reviews, scaffold checker and frozen seed
  archived outside the product tree;
- package metadata and supported Python declaration;
- ordinary unit/integration test entry points;
- regenerated diagnostics/count snapshots rather than copied stale numbers;
- clean baseline evidence bundle.

Exit criteria:

- 103+ inherited tests pass or every count change is explained;
- G0–G11 behaviours have replacement CI checks independent of lane numbering;
- generated artifacts reproduce byte-for-byte;
- no absolute lane path remains in product documentation or artifacts;
- the promoted repository contains no candidate-selection runtime code.

Dependencies: none. All later work depends on W0.

### W1 — freeze ADRs and backend contracts

**Purpose:** prevent driver details or the current synchronous engine from
becoming the accidental architecture.

Deliverables:

- ADRs A1–A15;
- backend capability model;
- backend-neutral `Plan`, parameter and result-shape boundary;
- async runtime/connection/transaction/subscription protocols;
- typed backend error/refusal translation policy;
- transaction and subscription state diagrams;
- known-abort/known-commit/indeterminate-commit state and reconciliation
  diagram, including durable transaction identity;
- transaction-handle ownership, nested/concurrent-use and connection
  reset/discard contract;
- deadline, cleanup shielding, graceful-drain and forced-close contract;
- trusted execution-context contract;
- compatibility matrix identifying the claimed SQLite/PostgreSQL subset.

Exit criteria:

- both SQLite and PostgreSQL can be described without optional methods whose
  absence silently changes semantics;
- every I/O-bearing method is async;
- cancellation points and ownership are explicit;
- no public type mentions a selected driver;
- unsupported backend capabilities map to pre-effect refusals;
- every A1–A15 decision has an accepted ADR before W1 hands its protocol tuple
  to W2; packages repeat the relevant ADRs as explicit dependencies rather than
  relying on that handoff implicitly; and
- the contract tests can represent every terminal state without treating task
  cancellation as proof of database rollback.

Dependencies: W0.

### W2 — extract plan and dialect seams

**Purpose:** separate shared semantic planning from SQLite SQL and execution
without changing user-visible semantics.

Deliverables:

- backend-neutral relational/result plan nodes;
- exhaustive plan visitor/validation;
- SQLite lowerer consuming the plan rather than resolved read syntax directly;
- backend capability validation before lowering/effects;
- preserved query/question SQL and result parity on the inherited SQLite suite;
- architecture tests preventing compiler ↔ backend dependency reversal.

Exit criteria:

- static query and dynamic refresh use the same plan object;
- adding a plan node fails exhaustive consumers until implemented;
- SQLite inherited results, footprints, deltas and refusals remain equivalent;
- no PostgreSQL implementation is faked by rewriting SQLite SQL;
- no physical name is synthesized.

Dependencies: W1.

### W3 — async runtime with SQLite reference adapter

**Purpose:** stabilise the public async contract before adding PostgreSQL
complexity.

Deliverables:

- async runtime open/close lifecycle;
- async execute and result retrieval;
- async transaction context and write methods;
- async migration/ship boundary;
- async subscription resource and iterator;
- cancellation-safe rollback and close;
- durable client transaction identity and reconciliation for indeterminate
  commit acknowledgement;
- one-owner transaction handles with explicit nested/concurrent refusal or
  savepoint semantics;
- bounded acquire, statement and shutdown deadlines with idempotent close;
- provider-neutral trusted execution context propagated through execute,
  transaction, capture and subscription boundaries;
- SQLite adapter isolated from the event-loop thread;
- removal or explicit internal-only marking of the synchronous runtime API.

Exit criteria:

- event-loop responsiveness test detects deliberate blocking and passes the
  adapter;
- cancellation before commit rolls back with no ledger/batch;
- known commit reports or durably schedules the committed revision exactly
  once, including when cancellation arrives after the commit request;
- indeterminate commit returns a typed reconciliation outcome and is never
  automatically retried until transaction identity is resolved;
- identical client transaction identifiers in two world/deployment scopes
  reconcile only against the A4-qualified durable identity, including after
  lost commit acknowledgement;
- subscription close releases registry, queue and backend resources;
- a connection returns to the pool only after protocol quiescence and session
  sanitation, otherwise it is destroyed;
- neutral, irrelevant, cross-scope and rollback behaviour remains correct;
- conflicting caller-supplied scope, capability or writer claims at execute,
  transaction, capture and subscription entry points refuse before effect or
  are ignored in favor of A11 context-derived values; any trusted-host escape
  hatch is separately named and unreachable through the ordinary API;
- sync database access is unreachable from the public API.

Dependencies: W2 and accepted ADRs A1–A4, A6–A8 and A11.

### W4 — PostgreSQL schema, lowering and execution

**Purpose:** make PostgreSQL a real, executable backend for one-shot reads and
governed writes.

Deliverables:

- PostgreSQL dialect lowerer;
- PostgreSQL type/parameter/result codecs;
- async pool and connection lifecycle;
- schema DDL, inspection and drift detection;
- authored PostgreSQL namespace resolution, full qualification/quoting and
  borrow-time `search_path`/session validation;
- explicit storage binding validation;
- query/question refresh execution;
- governed transactions, invariants, ledger and revision allocation;
- migration execution for the supported evolution subset;
- connection, statement and migration-lock deadline enforcement;
- deployment privilege inspection sufficient to reject unsupported runtime and
  migration roles before effect;
- consumption of deployment `at`, `pool` and `mode`;
- CLI/config path suitable for local and CI PostgreSQL services.

Exit criteria:

- real server tests cover every claimed static query shape;
- shared query/question plans produce equal initial rows;
- arbitrary metamorphic physical names execute without code changes;
- duplicate names in multiple schemas remain bound correctly under poisoned
  or changed pooled `search_path` state;
- qualified-name collisions remain isolated;
- constraint, transaction and drift failures map to stable Garns outcomes;
- unsupported PostgreSQL forms refuse before effect;
- PostgreSQL tests do not use SQLite expected SQL/results as their detector.

Dependencies: W2–W3 and accepted ADRs A1, A2, A4, A7, A9, A10 and A12–A14.

### W5 — PostgreSQL live routing and governed concurrency

**Purpose:** preserve Garns live semantics under real asynchronous concurrency.

Deliverables:

- PostgreSQL transaction-to-ledger-to-router integration;
- commit-ordered revision delivery;
- database-consistent snapshot/watermark handshake for first subscription,
  reconnect and overflow refetch;
- bounded async subscription queues;
- cancellation and unsubscribe;
- replay cursor/checkpoint;
- retention floor, cursor-expiry and typed refetch-required path;
- concurrent writer and isolation tests;
- retry/indeterminate-commit handling;
- metrics for routing, refresh, queue depth, overflow and replay.

Exit criteria:

- listeners are notified only after commit confirmation;
- known rollback emits nothing; known commit is eventually visible exactly
  once; indeterminate commit remains reconcilable and is not silently
  suppressed or retried;
- grouped-key moves update old and new groups;
- composed-question dependencies route recursively;
- folded batches equal one-shot PostgreSQL recomputation after every revision;
- slow consumers follow the documented backpressure/overflow policy;
- connection loss and restart follow the documented replay path;
- forced out-of-order allocation/commit interleavings cannot be skipped by a
  checkpoint cursor;
- commits at every snapshot/register/refetch boundary preserve a continuous
  result history;
- valid retained cursors replay completely and expired cursors terminate with a
  typed refetch-required outcome;
- metrics are measured, never constants.

Dependencies: W4 and accepted ADRs A3, A4, A6, A7 and A15.

### W6 — PostgreSQL external capture

**Purpose:** bring external writers into the same typed revision/delta stream
without treating notifications as durable state or conflating two different
capture strategies.

Deliverables:

- one strategy-neutral typed event, order, replay and acknowledgement contract;
- exactly one A5-selected implementation branch:
  - trigger-table branch: durable capture schema, database-side trigger/function
    mechanism and application-row/changelog-row atomicity;
  - logical-replication branch: durable slot/WAL position, relation/type mapping,
    slot lifecycle and retention/lag controls;
- optional wakeup channel;
- durable source-event identity, exclusive/CAS claim or equivalent, claim
  recovery, async acquisition, atomic/idempotent revision creation,
  acknowledgement and replay;
- typed coverage validation against the storage binding;
- supported writer-role/RLS matrix and fail-closed privilege inspection;
- scope-before/scope-after derivation;
- ordering across captured carriers;
- schema-generation interpretation or migration drain/fence for pending events;
- restart, duplicate-delivery and partial-failure tests;
- explicit future seam for logical replication if not selected initially.

Exit criteria:

- the selected branch proves its own durable-source atomicity; trigger-table
  evidence is never used to prove logical-replication behavior or vice versa;
- missed wakeups lose no data;
- concurrent acquisition, worker death and lost acknowledgement create exactly
  one Garns revision per source event and no permanent claim;
- renamed capture objects/fields work through binding provenance when the
  selected branch has such objects; logical replication proves relation/type
  mapping metamorphism instead;
- incomplete coverage refuses before acquisition is acknowledged;
- unsupported roles, RLS, trigger/replication settings, partition paths,
  `TRUNCATE` behavior or capture visibility refuse before a supported external
  mutation can commit;
- pending events across a supported migration remain interpretable exactly
  once or migration refuses before effect;
- external and governed deltas feed the same live contract.

Dependencies: W4–W5 and accepted ADRs A4–A5 and A12–A15. A5 must be closed to
one branch before W6 implementation is assigned.

### W7 — parity, hardening and release

**Purpose:** turn the new runtime into an honest release rather than a backend
prototype.

Deliverables:

- declared SQLite/PostgreSQL semantic compatibility matrix;
- differential execution suite for the shared subset;
- PostgreSQL-only capability tests;
- load/concurrency/cancellation/recovery suite;
- diagnostics catalogue and coverage report;
- async integration and deployment documentation;
- updated limitations and non-claims;
- generated target and packaging verification;
- release evidence manifest.

Exit criteria:

- all hard gates in §9 pass;
- no P0/P1/P2 review finding remains;
- documentation examples execute from a clean environment;
- every backend claim names real executable evidence;
- every unimplemented capability is refused or documented without ambiguity.

Dependencies: W0–W6.

### W8 — consume selected existing declarations

This work follows the PostgreSQL/async milestone unless a declaration is needed
by W4:

- make `generated <targets>` control emission;
- decide index ownership, then consume `filter`/`order` if retained;
- define whether `durability` and `snapshot` gain concrete backend semantics;
- separately plan a verb runtime;
- decide the fate of `ordered_within`, `history kept`, `pattern` and `length`.

These are not allowed to expand W3–W6 opportunistically.

## 8. Dependency and merge strategy

The critical path is:

```text
W0 → W1 → W2 → W3 → W4 → W5 → W6 → W7
```

Safe parallel work after W1:

- PostgreSQL test-service tooling can proceed alongside W2.
- Documentation/API examples can track W3 behind non-binding prototypes.
- PostgreSQL codec/type research can proceed alongside W3.
- Capture prototypes may explore A5, but do not merge before W4's transaction
  and revision contracts are stable.

### Product layout and write boundaries

W0 must freeze this path map in `docs/PRODUCT_LAYOUT.md` before W1. It may
translate names while promoting B2, but any later boundary change requires a
reviewed plan amendment; builders do not infer ownership from nearby files.

| Surface | Required product path |
|---|---|
| pure parser/resolver/compiler | `src/garns/compiler/**` |
| backend-neutral plans | `src/garns/plan/**` |
| backend protocols and errors | `src/garns/backends/contracts/**` |
| public async lifecycle | `src/garns/runtime/**` |
| SQLite backend | `src/garns/backends/sqlite/**` |
| PostgreSQL execution backend | `src/garns/backends/postgres/**`, excluding owned `live/` and `capture/` subtrees |
| shared live semantics | `src/garns/live/**` |
| PostgreSQL live adapter | `src/garns/backends/postgres/live/**` |
| PostgreSQL capture adapter | `src/garns/backends/postgres/capture/**` |
| PostgreSQL service tooling | `tools/postgres/**`, `tests/support/postgres/**` |
| non-product API documentation research | `research/api-docs/**` |
| non-product PostgreSQL codec/type research | `research/postgres-codecs/**` |
| non-product capture research | `research/capture/**` |
| tests | matching subtree under `tests/**` |
| ADRs/product docs/evidence | `docs/adr/**`, `docs/**`, `evidence/**` |

Package ownership is single-writer per phase:

| Package | Writable paths | Read-only inputs | Product and handoff |
|---|---|---|---|
| W0 | entire new promoted product root | repaired B2, F51 docs, this plan and reviews | clean layout, stable `evidence/v9-5-b2/**`, `docs/PRODUCT_LAYOUT.md`; manager accepts baseline before W1 |
| W1 | `docs/adr/**`, `src/garns/backends/contracts/**`, matching contract tests | compiler, plan inputs and promoted evidence | accepted A1–A15 and frozen protocol tuple; manager is integration owner |
| W2 | `src/garns/plan/**`, `src/garns/compiler/plan_bridge/**`, `src/garns/backends/sqlite/lower/**`, matching tests | W1 protocols and compiler IR | exhaustive plan/dialect seam reviewed before W3/W4 |
| W3 | `src/garns/runtime/**`, SQLite runtime files outside `lower/**`, matching tests, and `docs/api/**` only after the interface freeze | W1 protocols, including A4/A11, and W2 plan tuple | frozen public async/trust/lifecycle surface reviewed before W4/W5; W3 owner alone integrates API research |
| W4 | PostgreSQL execution subtree excluding `live/**` and `capture/**`, matching execution tests | W1–W3 tuples | real-server execution/migration baseline reviewed before W5/W6 |
| W5 | `src/garns/live/**`, PostgreSQL `live/**`, matching live/concurrency tests | W3 public surface and W4 backend | accepted revision/replay/subscription implementation before W6 |
| W6 | PostgreSQL `capture/**`, selected-branch tests and capture operations docs | accepted A5 branch and W4–W5 tuples | one evidenced external-capture branch before W7 |
| W7 | release, packaging, evidence and documentation paths; source corrections only through a finding-linked repair list | accepted W0–W6 outputs | one integrated release candidate and implementation-review tuple |
| W8 | paths named by a separately reviewed declaration change request | accepted v9-6 release | later independent package; never opportunistic W3–W6 work |

Every admitted parallel sub-lane has an isolated boundary:

| Sub-lane | Writable path | Read-only inputs | Product, handoff and integration owner |
|---|---|---|---|
| PostgreSQL service tooling alongside W2 | `tools/postgres/**`, `tests/support/postgres/**` | W1 A10 and promoted test conventions | reviewed service contract handed to the W4 owner; no other package writes these paths concurrently |
| API documentation/examples alongside W3 | `research/api-docs/**` | accepted A3/A11 and W3 interface drafts | non-mergeable review notes/examples handed to the W3 owner, who alone rewrites accepted material into `docs/api/**` after the interface freeze |
| PostgreSQL codec/type research alongside W3 | `research/postgres-codecs/**` | accepted A1/A2 and backend-neutral plan/result contracts | non-mergeable experiment report and fixtures handed to the W4 owner, who alone implements product code/tests |
| capture research | `research/capture/**` | accepted A4/A5/A12–A15 and W4/W5 contracts available at the research point | non-mergeable experiment report handed to the W6 owner; no prototype source enters runtime paths |

W0 materializes and verifies these already allocated relative roots. Under a
multiple-whole-build D8 outcome, the pre-W0 allocation prefixes every product
and research root with its isolated build root. Research paths are never part
of a release artifact.

Avoid parallel implementations of the same shared plan, public API,
transaction, revision or replay protocol. Those are convergence points with one
writer and one manager/integration owner. If the operator selects multiple
independent whole builds, W0 must instead allocate isolated product roots and a
separate comparison/selection/repair gate before any output enters these paths.

## 9. Hard exit gates

| Gate | Requirement |
|---|---|
| P0 Baseline | Clean promoted repository; inherited semantic/evidence suite green; no lane runtime dependencies. |
| P1 Architecture | A1–A15 closed before their dependants; compiler/backend dependency direction enforced; backend-neutral plan exhaustive; write ownership unambiguous. |
| P2 Async honesty and trust | Public I/O API async; no event-loop-blocking database calls; known-abort/known-commit/indeterminate outcomes, A4-qualified transaction identity, deadlines, cleanup and idempotent close executable; public scope/capability/writer claims are constrained by A11 context under hostile-input tests. |
| P3 PostgreSQL execution | Real server ships schema and executes every claimed query/write/migration shape through explicit bindings. |
| P4 Transactions | Concurrent commit, rollback, cancellation, retry and connection-loss outcomes match the documented three-way terminal contract; transaction-handle and pool sanitation tests pass. |
| P5 Live | Commit-safe ordering, snapshot/watermark continuity, recursive composition, grouped movement, neutral suppression, fold equivalence, bounded queues, retention and expired-cursor recovery pass on PostgreSQL. |
| P6 Capture | The selected PostgreSQL capture branch survives missed wakeups/restart/concurrent consumers, atomically and idempotently couples source event to revision/ack, preserves schema-generation meaning, and passes its privilege/RLS matrix without loss or silent duplication. |
| P7 Provenance | Full semantic/physical/catalog/schema metamorphic rename passes under poisoned `search_path`; no naming defaults, schema dispatch, fallback SQL or fixture modes. |
| P8 Cross-backend | Every parity claim is executed on both SQLite and PostgreSQL; differences are capability-gated or refused. |
| P9 Evidence | Regeneration deterministic; later-stage mutants execute real states; detector independence preserved. |
| P10 Operations | Pool lifecycle, bounded acquire/query/lock/shutdown, resource cleanup, slow consumer, reconnect, retention/compaction, observability and deployment/privilege configuration verified. |
| P11 Documentation | API, deployment, failure semantics, diagnostics, limitations and examples match the shipped bytes. |
| P12 Review closure | Independent Code and State reviewers report GO on the same final implementation bytes with no unresolved P0/P1/P2. |

A gate cannot pass from a mock, SQL snapshot or self-reported checklist when the
claim concerns database effects or concurrency.

## 10. Verification matrix

Each semantic shape is tested at the appropriate layers:

| Capability | Pure compiler | SQLite async | PostgreSQL | Concurrent PostgreSQL |
|---|---:|---:|---:|---:|
| Parse/resolve/qualification | required | — | — | — |
| Plan and result shape | required | required | required | — |
| Static query execution | — | required | required | selected load cases |
| Dynamic initial result | required footprint | required | required | required |
| Governed transaction | — | required | required | required |
| Ledger/revision | typed derivation | required | required | required |
| Rollback suppression | — | required | required | required |
| Group/composition routing | footprint required | required | required | required |
| Subscription cancellation | — | required | required | required |
| Backpressure/replay | — | contract tests | required | required |
| External capture | binding derivation | optional parity | required | required |
| Evolution/migration | classify required | required subset | required subset | lock/rollout cases |
| Metamorphic names | required | required | required | selected cases |
| Commit ambiguity/reconciliation | — | adapter contract | required | forced fault cuts |
| Snapshot/watermark continuity | footprint required | contract tests | required | forced boundary interleavings |
| Replay retention/cursor expiry | — | capability-gated | required | fast/slow consumer and compaction crash |
| Pool sanitation/deadlines | — | required | required | blocked child, reborrow and shutdown races |
| PostgreSQL namespace isolation | binding required | — | required | duplicate schemas and poisoned `search_path` |
| Capture role/RLS safety | binding coverage | — | required | role, RLS, partition, trigger/slot and tamper cases |
| Capture claim/idempotency | typed identity | optional parity | required | multi-worker kill/ack-loss barriers |
| Capture schema generations | classify required | optional parity | required | pending old-generation event across migration |
| Trusted-context enforcement | contract/refusal derivation | execute/transaction/subscribe | execute/transaction/capture/subscribe | conflicting scope/capability/writer claims across concurrent scopes |

The plan must name the exact supported subset before differential parity numbers
are published.

## 11. API migration strategy

The synchronous v9-5 engine is evidence and a migration source, not the future
public API.

1. Introduce the async API in a new namespace/module while the plan is under
   review.
2. Port all internal call sites and examples.
3. Route every public call through the A11 trusted execution context; raw
   scope/capability/writer assertion APIs, if needed, live in a visibly separate
   trusted-host-only internal surface.
4. Mark synchronous runtime entry points internal or deprecated; do not build
   new features on them.
5. Remove the public synchronous surface before v9-6 is declared stable unless
   a reviewed compatibility requirement says otherwise.
6. Keep pure compiler operations synchronous.

No compatibility wrapper may call synchronous database work directly from an
event-loop thread.

## 12. Failure and cancellation cases that must be designed explicitly

- task cancelled while waiting for a pool connection;
- task cancelled during a query fetch;
- task cancelled after writes but before commit;
- task cancelled while commit acknowledgement is in flight;
- task cancelled after PostgreSQL commits but before acknowledgement reaches
  the caller;
- connection lost before commit request;
- connection lost after commit may have succeeded;
- reconciliation sees no transaction identity, an aborted identity, or an
  already-committed identity;
- PostgreSQL serialization/deadlock failure;
- two transactions allocate/publish in one order and commit in the opposite
  order, including rollback gaps;
- transaction handle is used concurrently, nested without an accepted
  savepoint contract, or retained by a child task after owner cancellation;
- rollback/cancel does not quiesce the driver before the connection would
  return to the pool;
- pooled connection returns with altered `search_path`, role, transaction,
  prepared state or other session settings;
- subscription consumer stops reading;
- subscription queue fills;
- a commit lands between listener registration, snapshot, watermark capture,
  overflow marking, refetch and replay resumption;
- replay cursor is behind the retained floor or compaction crashes;
- listener closes during refresh;
- capture wakeup is missed or duplicated;
- capture consumer crashes after reading but before acknowledgement;
- two capture consumers claim the same source event or one loses commit
  acknowledgement after producing its revision;
- capture row/record remains pending while a migration changes its binding or
  schema generation;
- supported external writer encounters trigger disable, partition routing,
  `TRUNCATE`, replication-role behavior, RLS denial or capture tampering;
- pooled `search_path` resolves an identically named object in another schema;
- migration process dies while holding or waiting for a lock;
- pool acquisition, statement, migration-lock wait, shutdown or cleanup exceeds
  its configured deadline;
- application restarts with unconsumed committed revisions;
- backend reports schema drift after deployment.

Each case needs a documented state/outcome and an executable test. Catching an
exception is not itself a specified outcome.

## 13. Observability requirements

Expose measurements sufficient to distinguish correctness from apparent calm:

- pool wait/acquire/release and saturation;
- acquire/query/statement/lock/shutdown deadline and forced-discard outcomes;
- transaction begins, commits, rollbacks, retries and indeterminate outcomes;
- transaction-identity reconciliation results and pool sanitation/discard;
- revision allocation and delivery lag;
- unresolved revision publications, commit-order watermark and retained floor;
- routing probes, candidates, listener scans and refreshes;
- result-neutral refreshes and emitted batches;
- subscription queue depth, overflow, cancellation and replay;
- subscription snapshot/watermark transitions and expired-cursor/refetch paths;
- capture events available/claimed/lease-expired/revision-created/acknowledged/
  retried by strategy and schema generation;
- privilege/RLS/namespace validation and refusal counts;
- reconnect and recovery progress;
- migration lock wait and operation duration.

Counters must be driven by the actual operation. A permanently-zero field does
not prove that an operation did not occur.

## 14. Documentation deliverables

Update or add:

- architecture: plan/dialect/backend dependency direction;
- compiler pipeline: backend capability refusal boundary;
- integration: async Python API and lifecycle;
- DSL reference whenever its factual runtime/backend/API statements change,
  even when grammar semantics do not;
- diagnostics: new backend/runtime outcomes and positions;
- testing: PostgreSQL service, concurrency and destructive commands;
- limitations: backend matrix and deliberately deferred behaviour;
- operations: deployment configuration, pooling, migration and recovery;
- ADR index.

W0 copies repaired-B2 reports, repair notes, both ratifying reviews and their
manifest into stable `evidence/v9-5-b2/**`, rewrites this plan's evidence links
to that location, and runs a relative-link check. W7 assigns factual updates to
the product `README.md`, `DSL_REFERENCE.md`, `AI_DEVELOPER_GUIDE.md`,
`EXTENDING_GARNS.md`, architecture, integration, testing, diagnostics and
limitations documents. Versioned historical evidence is preserved, but shipped
guidance may not retain obsolete SQLite-only, synchronous-runtime,
PostgreSQL-refusal or trigger-only statements.

All examples claiming PostgreSQL or async behaviour must be executable in the
document test harness.

## 15. Review loop for this plan

The plan is a document/interface gate and must pass before any dependent
builder prompt is issued.

1. Freeze one exact commit tuple. While this pre-initial-commit scaffold remains
   under its no-git rule, use the plan's SHA-256 as the exact tuple and name all
   other working-tree content as out of scope.
2. Launch two fresh peer-blind read-only reviewers concurrently against that
   tuple: Axis Consistency and Axis Safety.
3. Each files one standalone report with P0/P1/P2/P3 findings and exactly one
   verdict, `GO` or `NO-GO`. Any P0, P1 or P2 makes that verdict `NO-GO`; P3-only
   findings do not block unless this gate is explicitly tightened.
4. The manager files both reports verbatim. Acceptance requires `GO`/`GO` on
   the same exact tuple.
5. After any `NO-GO`, the manager maps every finding to one disposition and
   closure test in one remediation plan, applies one consolidated amendment,
   and obtains focused re-verdicts. A dispute requires evidence and reviewer
   verification; an operator waiver is not a `GO` verdict.
6. Continue the same reviewers only for bounded corrections that leave the
   reviewed architecture and compatibility surface intact. Use fresh reviewers
   for a new numbered round when remediation changes an interface,
   architecture, mutation boundary, compatibility rule or platform assumption.
7. At most two architectural remediation rounds are allowed. A third new
   architectural root cause stops the lane for an operator redesign-or-accept
   decision; it does not silently produce another patch.

## 16. Later implementation review

Plan acceptance authorizes builder prompts; it does not accept implementation.
Each interface freeze and the final implementation tuple uses the same bounded
process with the axes appropriate for code:

- Axis Code attacks architecture, interfaces, call graphs, compatibility and
  whether shipped bytes implement this plan.
- Axis State attacks transaction/capture durability, crash and restart states,
  concurrency, recovery and fail-closed behavior.
- Any user-facing API freeze adds a Surface review of API docs/examples and a
  first-day open/execute/transaction/subscribe/close walkthrough, including
  stated defaults and lifecycle symmetry.

P12 passes only when Code and State both report `GO` on the same final bytes,
all P0/P1/P2 findings are closed by their originating reviewer or an accepted
fresh-review replacement after material change, and the filed evidence names
the exact tuple. Surface review must also be `GO` for a frozen public API.

## 17. Operator decision register

`Binding/closed` records direction already stated by the operator and captured
in the direction/plan documents. `Open` never satisfies its due-before gate.
Only the **decision artifact** authorizes a package; implementation and
verification artifacts are later outputs and cannot be prerequisites for their
own package.

| ID | Decision and permitted outcomes | Status / owner | Pre-launch decision artifact | Dependants and due-before boundary | Later implementation / verification artifact |
|---|---|---|---|---|---|
| D1 | PostgreSQL is primary production backend: yes/no | Binding/closed: yes; operator | `GARNS_DIRECTION.md` and this plan §§1, 4 | W1, W4–W7 | A1/A2/A10/A13 and real-server gates P3–P10 |
| D2 | Public database runtime is async-only; sync facade supported/internal/removed | Binding/closed: async-only, no supported sync facade; operator | `GARNS_DIRECTION.md` and this plan §§1, 3, 11 | W1 A3 and W3–W7 | A3, W3 API tests and P2 |
| D3 | Promote repaired B2 before architecture work: yes/combine | Binding/closed: promote first; operator | manager-approved W0 input brief naming B2 source, F51 docs, archive policy and expected evidence | W0 and every later package; before W0 | W0 promoted baseline and `evidence/v9-5-b2/**` manifest |
| D4 | SQLite tier: supported secondary runtime or test/development only | Open; operator | signed decision record naming one tier | W1 A8; before A8 is accepted and W1 hands off | A8, compatibility matrix, W3/W7 evidence/docs |
| D5 | First capture branch: trigger table, logical replication, or staged both | Open; operator advised by disposable research | signed decision record naming exactly one first W6 branch and non-claims | W1 A5; before A5 is accepted and W1 hands off | A5 branch contract, W6 evidence and P6 |
| D6a | Supported Python version range | Open; operator advised by packaging constraints | signed Python support-range record | W0 package metadata; before W0 | package metadata and clean-environment W0/W7 evidence |
| D6b | Supported PostgreSQL version range | Open; operator advised by driver/service research | signed PostgreSQL support-range record | W1 A1/A10 and W4; before A1/A10 are accepted and W1 hands off | A1/A10, service matrix and W4–W7 real-server evidence |
| D7 | Authentication scope: provider-neutral seam only or named provider integration | Open; operator; provider integration may remain deferred | signed decision record naming seam-only or provider integration | W1 A11; before A11 is accepted and W1 hands off | A11, W3 hostile-claim tests and P2; seam-only keeps provider integration a non-goal |
| D8 | Delivery shape: one convergent implementation or multiple isolated whole builds | Open; operator | signed delivery-shape record plus concrete product/research root allocation; multiple builds name every isolated root and selection gate | every builder prompt; before W0 or any builder | W0 materializes/verifies `PRODUCT_LAYOUT.md`; manager records selection/repair evidence if multiple |

The manager's launch-state check rejects a package whenever a required decision
is `Open`, `Provisional`, lacks its pre-launch decision artifact or contradicts
an accepted ADR. It does not require a later implementation/verification
artifact to start the package that produces that artifact. The decision/ADR/
package graph must topologically sort before the first builder prompt.

## 18. Definition of plan acceptance

This plan is ready to launch implementation only when:

- every decision required by the first proposed builder package is closed with
  its named artifact; provisional status never authorizes dependent work;
- the D1–D8/A1–A15/W0–W8 graph topologically sorts, with no package output used
  to authorize itself or a predecessor;
- W1 accepts all A1–A15 before handing its protocol tuple to W2, and each later
  package repeats its relevant ADRs as explicit dependencies;
- peer-blind Consistency and Safety reviewers report `GO` on the same exact
  plan tuple;
- no P0/P1/P2 finding remains open; a P3 has a recorded disposition but does
  not block unless the gate is explicitly tightened;
- work packages have unambiguous write boundaries and deliverables;
- the PostgreSQL test-service strategy is executable in the target environment;
- hard gates can falsify the claims they protect;
- no milestone requires changing the frozen language accidentally; and
- the manager publishes final builder prompts from the ratified plan, with each
  prompt naming its write boundary, read-only inputs, accepted dependency tuple
  and still-deferred outcomes.
