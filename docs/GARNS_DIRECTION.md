# Garns direction

**Status:** proposed north-star for the first post-v9-5 implementation cycle  
**Written:** 2026-10-03  
**Scope:** product and architecture direction, not evidence that the described
runtime already exists

The review draft that turns this direction into work packages and exit gates is
[Garns v9-6 — PostgreSQL and async runtime implementation plan](../../dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md).

Garns has proved its semantic core. The next job is not to expand the grammar;
it is to turn that core into a credible production data runtime. PostgreSQL is
the primary database for that work, and every public API that can perform
database I/O must be asynchronous.

This document separates that direction from choices still requiring an
architecture decision. It should be read before planning the next iteration,
writing backend code, or adding new DSL syntax.

## Direction in one page

| Area | Direction |
|---|---|
| Product | A declarative semantic compiler and runtime: state meaning once, derive storage, reads, live routing, capture, evolution and target surfaces from one resolved IR. |
| Primary database | **PostgreSQL** is the production reference backend. Claims about it require execution against a real PostgreSQL server. |
| Secondary database | **SQLite** remains useful for fast local tests and semantic comparison. It does not define the production API. |
| Public runtime API | **Async-only** for database access, transactions, capture and live subscriptions. No synchronous database call may block an event loop. |
| Compiler API | Parse, resolve, bind, derive and lower remain synchronous and pure unless measurement later demonstrates a reason to change them. |
| Reads | Keep static `query` and dynamic `question`: one shared relational/result plan; only a question derives live products. |
| Physical storage | Keep explicit per-world bindings. No backend may infer table, identity, link, scope or changelog names. |
| Language | Preserve the ratified v9-5 grammar initially. Prefer consuming facts already present in the IR over adding syntax. |
| Live delivery | Commit-ordered async streams with cancellation, bounded buffering, backpressure and explicit recovery semantics. |
| Capture | A durable change source is authoritative. A notification may wake a consumer but is never the durable record. |
| Evidence | Cross-backend claims require real execution. SQL snapshots, mocks and shared expected tables are supporting evidence only. |

## What remains invariant from v9-5

The repaired B2 implementation is the semantic reference, not the runtime
shape to preserve verbatim. The following commitments remain binding:

1. Garns source resolves once into a typed, module-qualified IR.
2. Storage DDL, SQL, footprints, routing, ledger, capture, evolution and
   generated surfaces consume that IR; they do not rediscover source meaning.
3. Every physical name is supplied by a storage binding. There is no implicit
   pluralisation, `id`, `<link>_id`, `scope_id` or changelog convention.
4. Public identities are qualified. Bare-name convenience does not cross a
   module or runtime boundary.
5. A static `query` is fetch-only and produces no live artifacts.
6. A dynamic `question` belongs to the closed, footprintable algebra and states
   a positive `live bounded N`.
7. Query execution and question refresh use the same relational/result plan.
8. A transaction that rolls back produces no revision, ledger row or batch.
9. Listeners observe committed state only. A routed but result-neutral write
   produces no batch.
10. Unsupported behaviour refuses by stable code at the earliest meaningful
    boundary; it is never approximated or silently defaulted.
11. Generated evidence must be reproducible from source and resolved IR.
12. Test fixtures do not become compiler modes, schema branches or expected
    answer inputs.

The v9-5 evidence and its honest limits are summarised in
[README.md](README.md#status-and-evidence-snapshot) and
[LIMITATIONS.md](LIMITATIONS.md#inventory).

## Product position

Garns is not an ORM, a session abstraction, a string-based query builder or a
database portability layer that hides semantic differences. It is responsible
for a narrower and stronger contract:

```text
Garns source
  → qualified semantic IR
  → explicit physical binding
  → backend-neutral relational/result plan
  → backend SQL and runtime operations
  → one-shot results or committed live deltas
```

Applications should depend on qualified reads, typed parameters, stable result
shapes, transactional writes and live batches. They should not depend on the
driver, connection object, generated SQL spelling or physical schema names.

## Target architecture

### Pure compiler side

The following operations stay synchronous because they are CPU/local-file work
and should remain deterministic:

- parse Garns source;
- resolve names, types, worlds, deployments and evolution;
- load and validate an explicit storage binding;
- derive a backend-neutral relational/result plan;
- derive question footprints and routing descriptors;
- derive migration intent;
- generate artifacts.

This side must not import a database driver or open a connection.

### Async runtime side

Every operation that can wait on a database, pool, notification, lock or
network is asynchronous:

- open and close a runtime/pool;
- ship or inspect a store;
- execute a query or question refresh;
- begin, commit and roll back a transaction;
- mint, change and delete rows;
- append and read ledger revisions;
- acquire externally captured changes;
- subscribe, receive, cancel and close a live stream;
- run migrations.

The conceptual application surface is:

```python
runtime = await GarnsRuntime.open(program, world="SALES", deployment="PROD")

result = await runtime.execute(
    "sales.open_orders",
    parameters={"minimum": 100},
    scope=account_id,
)

async with runtime.transaction(writer="governed") as tx:
    await tx.change(
        "sales.Order",
        order_id,
        {"sales.Order.status": "closed"},
    )

async with runtime.subscribe(
    "sales.open_orders",
    parameters={"minimum": 100},
    scope=account_id,
) as subscription:
    async for batch in subscription:
        consume(batch)
```

Names are illustrative. The next API decision must settle ownership, error and
cancellation details before implementation freezes them.

### Backend boundary

The backend interface should expose capabilities rather than leak a particular
driver. At minimum it must support:

- acquire/release from an async pool;
- execute/fetch with typed parameter encoding and row decoding;
- an async transaction context with cancellation-safe rollback;
- schema inspection and transactional DDL where the backend supports it;
- backend-specific lowering from the shared relational/result plan;
- ledger revision allocation and ordered delta persistence;
- durable capture acquisition;
- an optional wakeup channel for new committed capture rows;
- backend feature/capability reporting used for early refusal.

The interface must not contain SQLite-specific JSON, rowid or trigger syntax,
and must not reduce PostgreSQL to string substitution over SQLite SQL.

## PostgreSQL as the reference backend

PostgreSQL is the first backend for which Garns should claim production runtime
behaviour. That requires separate, explicit implementation of:

- SQL and DDL lowering;
- type mapping and result decoding;
- list parameters and set membership;
- JSON/nested result aggregation;
- identity generation and `RETURNING` behaviour;
- constraints, indexes and referential actions;
- transaction isolation and revision allocation;
- schema inspection and drift detection;
- migration execution;
- ledger tables;
- durable external capture;
- notification/wakeup integration;
- connection pooling and failure recovery.

The compiler should lower both databases from the same plan, but dialect
differences remain visible behind backend implementations. Semantic parity is
claimed construct by construct, not assumed globally.

### Role of SQLite

SQLite remains valuable for:

- fast compiler and semantic tests;
- local development and examples;
- deterministic single-process fixtures;
- differential tests for the subset explicitly supported by both backends.

It implements the same async-facing runtime contract if retained. A serialized
worker or adapter may bridge its synchronous driver, but synchronous SQLite I/O
must not run on the application event-loop thread. SQLite-specific limitations
must not weaken the PostgreSQL API.

## Async transaction contract

The runtime must define these behaviours before its API is called stable:

1. Entering a transaction acquires one connection and establishes its database
   transaction before returning control.
2. All writes, invariant checks, scope resolution, ledger rows and revision
   allocation for that transaction use the same connection and transaction.
3. Cancellation or an exception before commit rolls back and emits nothing.
4. Live matching begins only after the database confirms commit.
5. A committed revision has a deterministic order visible to ledger, capture
   and subscriptions.
6. Retrying a transaction never duplicates a visible revision silently.
7. Nested transaction behaviour is either explicitly supported with savepoints
   or explicitly refused.
8. Connection loss has a documented outcome: known rollback, known commit, or
   indeterminate result requiring reconciliation.

## Async live-subscription contract

A subscription is a resource, not a callback retained forever. It needs:

- an async iterator or equivalent receive operation;
- explicit cancellation/close;
- bounded buffering;
- a documented backpressure policy;
- commit and revision ordering guarantees;
- a recovery cursor/checkpoint;
- reconnection and replay semantics;
- defined behaviour when `live bounded N` is exceeded;
- isolation by scope and qualified identity;
- no notification for rollback or result-neutral refresh;
- metrics measured from real routing and queue operations.

The v9-5 append-only in-memory subscription log is evidence machinery, not the
production design.

## Capture direction

PostgreSQL notification mechanisms are transient wakeups. They must not be the
only record of a change.

The first implementation should preserve the v9-5 durable-changelog law:

1. A database transaction writes application data and a durable changelog row
   atomically.
2. A wakeup may tell Garns that rows are available.
3. Garns acquires unprocessed rows in durable order, validates their declared
   coverage, maps them to typed deltas, and records the resulting revision.
4. Acquisition is retryable and does not lose or duplicate acknowledged work.

Whether the long-term source is trigger-maintained tables or PostgreSQL logical
replication remains an open architecture decision. Both must produce the same
typed delta and ordering contract.

## Existing declarations that should gain meaning

The next runtime cycle should prefer consuming existing IR facts over adding
language surface:

| Existing declaration | Intended next consumer |
|---|---|
| deployment `at` | connection/pool configuration source |
| deployment `pool` | async pool sizing policy |
| deployment `mode` | read-only/read-write transaction policy |
| world `durability` | transaction durability/isolation policy, once semantics are specified |
| deployment `snapshot` | migration/ship checkpoint policy |
| use/link `filter` and `order` | backend index planning, after index ownership is specified |
| world `generated` targets | actual output selection |

Other unconsumed declarations—verbs, `ordered_within`, `history kept`,
`pattern`, and `length`—remain outside the PostgreSQL/async critical path. They
should either gain a specified consumer in a later cycle or be reconsidered;
they should not quietly remain decorative forever.

## Language policy for the next cycle

The v9-5 grammar starts frozen. PostgreSQL and async runtime work should require
little or no DSL syntax because engine, deployment, world and storage-binding
concepts already exist.

Change grammar only when all of the following are true:

- an application-visible semantic fact cannot be represented in the current
  world/deployment/storage model;
- the fact cannot live solely in deployment configuration or a binding;
- every downstream consumer and refusal boundary is identified;
- both PostgreSQL and SQLite behaviour are stated, including explicit refusal
  where one backend does not support it;
- tests demonstrate that the new syntax is not a backend knob leaking into the
  semantic language.

## Delivery plan

### Phase 0 — promote the reference implementation

- Move repaired B2 into a clean Garns repository.
- Carry the F51 documentation, including this direction document.
- Remove lane-only candidate/review machinery from the product tree.
- Establish ordinary packaging, CI and release metadata.
- Re-measure and regenerate diagnostics, counts and evidence rather than
  carrying stale lane snapshots.

### Phase 1 — establish the async seam

- Introduce the backend-neutral plan/dialect/runtime boundaries.
- Convert the public runtime API to async.
- Adapt SQLite behind that API without blocking the event loop.
- Add cancellation, rollback, close and subscription-lifecycle tests.
- Preserve all v9-5 semantic and evidence gates.

This phase is successful only if the async API is real at the boundary; merely
declaring `async def` around synchronous database work does not count.

### Phase 2 — implement PostgreSQL execution

- Add PostgreSQL binding validation, lowering, schema inspection and shipping.
- Execute static queries and dynamic refreshes against a real server.
- Implement async transactions, ledger and migrations.
- Consume deployment `at`, `pool` and `mode`.
- Add differential tests for the explicitly shared SQLite/PostgreSQL subset.

### Phase 3 — implement PostgreSQL live and capture

- Add durable external capture plus wakeups.
- Define revision ordering and replay cursors.
- Implement async subscription cancellation, bounded queues and backpressure.
- Exercise concurrent writers, connection loss and recovery.
- Prove grouped-key moves, recursive composition, rollback suppression and fold
  equivalence under concurrency.

### Phase 4 — close or remove dormant declarations

- Make generated-target selection effective.
- Decide index ownership and consume `filter`/`order` if retained.
- Prioritise a verb runtime separately from the backend conversion.
- Decide the fate of every remaining validated-but-unconsumed declaration.

## Required evidence for the PostgreSQL/async milestone

The milestone is not complete until all of the following are executable:

- a real PostgreSQL service is started from a documented clean environment;
- schema shipping and drift detection run against it;
- static query features execute, including grouping, arithmetic, calls, nested
  results and pagination for every claimed form;
- dynamic questions subscribe and emit ordered async batches;
- relevant, irrelevant, result-neutral, cross-scope and rolled-back writes have
  the correct measured routing and notification results;
- concurrent transactions have a defined and tested revision order;
- cancellation during acquire, query, write, commit wait and subscription wait
  leaves a known state;
- connection loss and restart exercise the documented recovery path;
- capture uses actual PostgreSQL database effects and durable rows;
- migrations run against real PostgreSQL generations;
- storage metamorphism renames all PostgreSQL physical objects without compiler
  changes;
- unsupported constructs refuse before effect;
- SQLite/PostgreSQL parity is reported only for cases executed on both;
- generated artifacts delete/regenerate byte-identically;
- no test uses expected SQL or expected outcome as detector input.

## Architecture decisions still required

Each item should become a short ADR before implementation commits to it:

1. **Python PostgreSQL driver and pool.** Selection criteria: genuine async I/O,
   cancellation behaviour, prepared statements, codecs, pool lifecycle,
   maintained support and testability.
2. **Backend protocols.** Exact ownership of pools, connections, transactions,
   plans, dialects, schema inspection and errors.
3. **Capture source.** Trigger-maintained durable tables first, logical
   replication first, or a staged path supporting both.
4. **Revision allocation and ordering.** Per world, per deployment or global;
   sequence/transaction relationships; recovery cursor.
5. **Subscription buffering.** Queue bound, producer behaviour at capacity,
   replay and slow-consumer policy.
6. **Isolation and retry.** Default isolation level, serialization/deadlock
   retry ownership and idempotency.
7. **SQLite async adaptation.** Worker-thread, dedicated adapter dependency or
   test-only status.
8. **Deployment configuration and secrets.** How `at env NAME` resolves without
   placing credentials in IR or generated artifacts.
9. **Authentication boundary.** Capabilities and writer identities are
   currently caller assertions; define where authenticated principals enter.
10. **Migration locking and rollout.** Advisory locks, compatibility windows,
    online index/constraint operations and mixed-version deployments.

## Explicit non-goals for the next milestone

- redesigning the DSL for PostgreSQL syntax;
- preserving the synchronous runtime API as the primary interface;
- presenting SQLite behaviour as proof of PostgreSQL behaviour;
- implementing every dormant verb or declaration during the backend rewrite;
- building an ORM/session/identity-map layer;
- treating transient notification delivery as durable capture;
- claiming general concurrency safety before it is specified and attacked;
- adding another backend before PostgreSQL is complete and evidenced.

## Immediate planning questions

The next planning session should answer these in order:

1. Are PostgreSQL-primary and async-only runtime API now binding product
   decisions?
2. Is repaired B2 promoted first, or is promotion combined with the async seam?
3. Which driver/pool and test-server strategy satisfy the evidence requirements?
4. What is the minimum backend protocol that permits PostgreSQL without
   weakening explicit storage provenance?
5. What transaction/revision/cancellation guarantees are application-facing?
6. Which durable capture strategy is the first shippable one?
7. What exact subset must remain SQLite/PostgreSQL-equivalent?
8. Which existing deployment fields become binding in the first milestone?
9. What is explicitly deferred so the iteration stays about runtime substrate?

Once those answers are recorded as ADRs, the next iteration can be scoped as a
build-and-review exercise rather than another language exploration.
