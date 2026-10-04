# Architecture

How Garns is put together, what owns what, and where each guarantee is actually
enforced. Every claim below is traceable to a file in this repository; syntax and
per-construct semantics belong to [DSL_REFERENCE.md](DSL_REFERENCE.md), refusal
codes to [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue), phase mechanics to
[COMPILER_PIPELINE.md](COMPILER_PIPELINE.md), and the honest list of what is not
implemented to [LIMITATIONS.md](LIMITATIONS.md#inventory).

## Overview

Garns is a declarative DSL compiled once into a typed, module-qualified IR, and
then consumed — never re-derived — by every downstream product: SQL, DDL,
footprints, live routing, ledger validation, migrations, and generated Python and
Rust surfaces.

Three structural commitments shape everything else.

| Commitment | Consequence | Enforced at |
|---|---|---|
| **One IR, many consumers** | Storage, lowering, footprints, live routing, capture, evolution and generation all read `ir.Program` / `WorldIR`. No consumer re-parses source or re-derives a source fact. | `src/garns/ir.py::Program`, exhaustive visitors in `src/garns/visit.py` |
| **Every physical name is an input** | Table, identity column, scalar column, link column, family discriminator, engine table and changelog field come from a per-world JSON binding. A missing or ambiguous mapping refuses; nothing is guessed or pluralised. | `src/garns/storage.py:170` (`bind_world`) |
| **Refusal is the only failure channel** | A refusal carries a stable code, one of seven ordered stages, and a source position. The first refusal wins. | `src/garns/refuse.py:11` (`STAGES`), `refuse.py::Refusal` |

The seven stages, in order, are `decode, validate, lower, generate, ship, load,
runtime` (`src/garns/refuse.py:11`). "Pre-effect" throughout this document means
*at or before `validate`*, i.e. before any store, schema, ledger, generated
artifact or migration exists.

Scale of the implementation (measured with `wc -l`): 22 modules and 8,008 lines
under `src/garns/`, plus 105 lines of `src/garns_rust/sqlite.rs`. The largest
modules are `resolve.py` (1,382), `parse.py` (813), `ast.py` (810),
`resolve_read.py` (789), `ir.py` (781), `lower_sqlite.py` (700), `engine.py`
(564).

## Data flow

```
grammar/garns.lark ──► parse.parser()  (Lark LALR, propagate_positions)
                          │
  *.garns text ───────────┴──► ast.SourceFile        located nodes + every Name occurrence
                                   │
                          resolve.Resolver.run()      ordered phases, one pass
                                   │
                                   ▼
                            ir.Program                qualified identities + Reference map
                                   │
        storage-<WORLD>.json ──────┴──► storage.bind_world()
                                   │
                                   ▼
                             storage.WorldIR          one world + its physical binding + scope paths
                                   │
             ┌─────────────────────┼──────────────────────────────┐
             ▼                     ▼                              ▼
   lower_sqlite.lower_ddl   lower_sqlite.lower_read      footprint.derive_footprint
        (schema DDL)          (Plan / ChildPlan)          (questions only)
             │                     │                              │
             ▼                     ▼                              ▼
      engine.Store.ship     engine.Engine.execute            live.LiveEngine
             │                     ▲                              │
             ▼                     │                        (index, match,
      engine.Transaction ──────────┘                         Instance.refresh, fold)
      capture.CaptureAdapter ──────┘
             │
             ▼
      evolution.classify / migrate / open_store        generate.generate → surfaces
```

Read the chain as: **located AST → qualified Program IR → WorldIR (storage
binding) → shared Plan/ChildPlan → execution / live / capture / evolution /
generation.** There is exactly one lowering entry point, `lower_read`
(`src/garns/lower_sqlite.py:526`); both `Engine.execute` (`engine.py:282`) and
live refresh (`live.py::Instance._fetch`, which calls `engine.execute`) obtain
their SQL from it. There is no second query engine.

Verified: the static query `sales_static.open_orders_once` and the live question
`sales.open_orders` — different nouns, different modules — lower to byte-identical
SQL over the SALES world's binding.

```
### sales.open_orders  noun=question shape=windowed live_bound=20
SELECT s0."id_76d3517dac" AS "$k0", s0."id_76d3517dac" AS "identity",
       j1."co_1e32478f5c" AS "customer", s0."co_26bff25d88" AS "total"
  FROM "ta_8d09f00415" AS s0
  LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7"
 WHERE (s0."co_7cbde43f56" = 'open')
 ORDER BY s0."co_66617ed9a4" DESC, s0."id_76d3517dac" ASC LIMIT 20
### sales_static.open_orders_once  noun=query shape=windowed live_bound=None
   (identical SQL text)
```

## Components and dependency direction

Dependencies point strictly downward; no module below imports one above it.

| Layer | Modules | Depends on | Never depends on |
|---|---|---|---|
| Foundations | `refuse.py`, `types.py`, `calls.py`, `visit.py` | stdlib only (`visit.py` on `ir`) | anything else |
| Front end | `ast.py`, `parse.py` | `ast`, `refuse`, `lark` | `ir`, `resolve` |
| Semantics | `resolve.py`, `resolve_read.py`, `ir.py` | `ast`, `types`, `calls`, `refuse` | storage, SQL, engine |
| Physical binding | `storage.py` | `ir`, `refuse` | SQL text, engine |
| Lowering | `lower_sqlite.py` | `ir`, `storage`, `types`, `visit`, `refuse` | engine, live |
| Runtime | `engine.py`, `live.py`, `capture.py` | lowering, storage, ir, footprint | resolve, parse |
| Derivation | `footprint.py` | `ir`, `storage`, `visit`, `refuse` | SQL text |
| Lifecycle | `evolution.py` | `ir`, `storage`, `lower_sqlite`, `refuse` | live, capture |
| Products | `generate.py`, `surfaces.py` | lowering, footprint, storage | engine, live |
| Harnesses | `metamorphic.py`, `mutants.py` | everything above | — |
| Entry | `cli.py` | parse, resolve, storage, lowering, engine, generate | — |

Two structural facts to preserve when changing code:

* `lower_sqlite.py` imports `storage.WorldIR` but **never** the engine — SQL text
  generation is independent of execution. `engine.py` imports `lower_read`, not
  the other way round.
* `live.py` never issues SQL itself; it re-runs the shared plan through
  `engine.execute` (`src/garns/live.py:120`). This is what makes query/question
  parity structural rather than tested.

`metamorphic.py` and `mutants.py` are **conformance harnesses**, not part of the
compiler. `binding_document` (`src/garns/storage.py:305`) and
`tools/storage_template.py` are authoring aids; the compiler never calls them —
`bind_world` only ever reads a document from disk.

## Identity and qualification

Every identity in the IR is module-qualified. Bare names exist only inside
`Resolver.lookup` (`src/garns/resolve.py:119`), which resolves a local name
against the module's own declarations and its named imports, and refuses
`NAME_AMBIGUOUS` when both exist.

| Thing | Qualified form | Built by |
|---|---|---|
| module | `module` | `resolve.py::Resolver.collect` |
| intent, newtype, carrier, read, verb, tombstone | `module.Name` | `resolve.py:95` (`Resolver.qid`) |
| use | `module.Carrier.intent_local_name` | `ir.py::Use.qid` |
| link | `module.Carrier.link_name` | `ir.py::Link.qid` |
| capability | `WORLD#capability:name` | `resolve.py::resolve_world` |
| writer source | `WORLD#writer_source:name` | `resolve.py::resolve_world` |
| given | `module.read#given_name` | `resolve_read.py::resolve_read` |

Every runtime boundary takes a qualified identity and refuses otherwise:
`Engine.execute(read_qid)` → `READ_UNKNOWN` with the message "reads are selected
by qualified name" (`src/garns/engine.py:207`); `tx.mint(carrier_qid,
{field_qid: value})` → `LEDGER_CARRIER_UNKNOWN` / `LEDGER_FIELD_UNKNOWN`
(`engine.py::LedgerValidator`); `LiveEngine.subscribe(read_qid)`
(`src/garns/live.py:184`).

Alongside the IR the resolver records a **reference map** — one
`ir.Reference(file, line, column, text, identity, role)` per bound identifier
occurrence (`resolve.py:92`). This is what lets `metamorphic.py` rename every
identifier in the *sources* and re-resolve, without touching compiler code. It
exists because `parse.py::_Builder.name` makes each identifier occurrence its own
located `ast.Name`.

## Scope model

There is **no scope column anywhere**. Scope is a resolved *link path*.

* A world declares `scope <module>.<Trait>.<link>`, resolved to
  `ir.ScopeRoot(trait, link, root)` (`resolve.py::resolve_world`), or
  `scope deployment`, which leaves `World.scope is None` and makes
  `World.deployment_scoped` true (`src/garns/ir.py:663`).
* `Resolver.compute_scope_paths` (`src/garns/resolve.py:1160`) derives, per world,
  a map `carrier qid → tuple of link qids` reaching the scope root. Carriers that
  carry the scope trait get a one-hop path; others take an explicit `scope_via`
  link or the unique link into an already-scoped carrier, iterated to a fixpoint.
  Ambiguity refuses `SCOPE_PATH_AMBIGUOUS`; an unreachable carrier refuses
  `TRAIT_REQUIRED`; a `scope_via` into an exempt carrier refuses
  `SCOPE_PATH_TO_EXEMPT`.
* `lower_sqlite.scope_predicate` (`src/garns/lower_sqlite.py:370`) walks that path
  recursively against the reserved parameter `:_scope`, nesting
  `IN (SELECT identity FROM parent WHERE …)` for multi-hop paths.
* At write time `Engine.scope_key_of` (`engine.py:246`) follows the same path
  through the store, reading intermediate rows for multi-hop paths, and each
  `Delta` carries `scope_before` / `scope_after`.

Verified on the LEDGERHOUSE conformance world (a private captured schema with a
two-hop path `Jar → Shelf → Household`):

```
scope_paths[LEDGERHOUSE] =
  pantry.Jar:        ('pantry.Jar.shelf', 'pantry.Shelf.keeper')
  pantry.Shelf:      ('pantry.Shelf.keeper',)
  tenancy.Household: ()

pantry.open_jars  scoped=True
SELECT s0."jar_no" AS "$k0", s0."lbl" AS "jar_label", s0."mass_g" AS "grams",
       j2."label_txt" AS "shelf"
  FROM "jar" AS s0 LEFT JOIN "shelf" AS j2 ON j2."shelf_no" = s0."on_shelf"
 WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1
                          WHERE p1."kept_by" = :_scope)
   AND (s0."cond" = 'open')
 ORDER BY s0."mass_g" DESC, s0."jar_no" ASC
```

Reserved parameter names are `_scope`, `_clock`, `_parents`
(`lower_sqlite.py:22-24`); a given whose name starts with `_` refuses
`GIVEN_NAME_RESERVED` in both the resolver and `lower_read`.

## Routing and live semantics

`LiveEngine` (`src/garns/live.py:156`) registers itself as an engine listener at
construction and is driven only by committed deltas.

| Concept | Definition | Location |
|---|---|---|
| Footprint atom | `(carrier, field)` where field is a use qid, a link qid, or `"*"` for structural change | `footprint.py::Atom` |
| Index key | `(partition, carrier, field)`; `partition` is `scope:<identity>` for a scoped carrier, else `global` | `live.py:176` (`routing_keys`) |
| Probe | one dictionary lookup; increments `Stats.probes`, and `Stats.candidates` per id returned | `live.py:205` (`_probe`) |
| Listener scan | one instance visited by iterating the registry; increments `Stats.listener_scans` | `live.py:81-84` (`Registry.__iter__`) |
| Batch | `Batch(instance, base_seq, seq, revision, changes)` of `upsert`/`delete`, or `None` when nothing changed | `live.py:135` (`Instance.refresh`) |

`match(deltas)` (`live.py:212`) probes only the keys a delta can touch: its
partitions (`scope_before`, `scope_after`, plus `*`), its carrier and that
carrier's family, and its changed fields plus `*` for inserts and deletes. The
routing path never iterates the registry, so `listener_scans` is zero **by
construction** — and the counter is genuinely live because `Registry.__iter__` is
the only way to visit all instances and it increments the same counter.

A refresh whose row count exceeds the question's `live bounded N` refuses
`LIVE_BOUND_EXCEEDED` at stage `runtime` (`src/garns/live.py:121-122`).
`fold(initial, keys, batches)` (`live.py:244`) replays batches onto an initial
keyed state; fold-equivalence against one-shot recomputation is what the live
correctness gate compares.

Verified end to end on SALES (ship → seed → subscribe → close one order):

```
initial rows:            [{'identity': 1, 'customer': 'Acme', 'total': 150.0}]
one-shot query rows:     [{'identity': 1, 'customer': 'Acme', 'total': 150.0}]
after tx-close, batch:   {'instance': 'inst1', 'base_seq': 0, 'seq': 1,
                          'revision': 2, 'changes': [{'op': 'delete', 'key': [1]}]}
stats:                   {'probes': 20, 'candidates': 1, 'refreshes': 1,
                          'listener_scans': 0, 'batches': 1}
```

Known conservatism, not a bug to "fix" silently: unscoped instances additionally
register under `global` and a `*` partition (`live.py:196-200`), so they are
probed for writes in every scope. See [LIMITATIONS.md](LIMITATIONS.md#inventory).

## Transactions and ledger

`Engine.transaction(writer, transaction_id)` (`engine.py:214`) yields a
`Transaction` that, on `__enter__`, validates the writer against the world
(`governed`, or the declared `writer_source`) and the transaction id against
`^[A-Za-z0-9_-]{1,64}$` (`engine.py:22`), then opens `BEGIN`.

`mint` / `change` / `delete` each run **typed pre-effect ledger validation**
through `LedgerValidator` (`engine.py:72`) before any statement is issued:

1. carrier known and not an abstract family — `LEDGER_CARRIER_UNKNOWN`,
   `LEDGER_CARRIER_ABSTRACT`;
2. field a real use or link of that carrier (a member name may denote a family
   field) — `LEDGER_FIELD_UNKNOWN`;
3. value of the right type class and closed-set member — `LEDGER_VALUE_TYPE`;
4. scope identity resolvable in the scope root's table — `LEDGER_SCOPE_UNKNOWN`
   (`engine.py:150`, `check_scope`);
5. engine-stamped uses rejected as inputs — `VERB_INPUT_ENGINE_OWNED`.

Invariants are re-evaluated as SQL against the written row by reusing the same
`_Lowerer` that lowers reads (`engine.py:544`, `_check_invariants`), refusing
`INVARIANT_VIOLATED`.

On normal exit the transaction inserts one revision row and one ledger row per
delta, commits, **and only then** notifies listeners (`engine.py:217`,
`_commit`). On an exception it rolls back, so a rolled-back transaction produces
no revision, no ledger row and no batch. The three engine tables — generations,
revisions, ledger — are themselves named by the binding
(`storage.py::EngineTables`) and emitted by `lower_ddl`
(`src/garns/lower_sqlite.py:605`).

## Worlds, deployments and engines

A **world** selects modules and fixes durability, writer class, generated
targets, the required scope trait and its exemptions, the scope root,
capabilities and the quarantine retention (`resolve.py::resolve_world`). Each
module belongs to at most one world (`WORLD_MODULE_COLLISION`), and a world must
list every module its members import (`MODULE_NOT_LISTED`).

A **deployment** names a world, an engine, a location, a ship mode, a mode and a
snapshot policy, optionally extending another deployment
(`resolve.py:1229`, `resolve_deployment`).

| Set | Value | Location |
|---|---|---|
| `TARGETS` | `{python, rust}` | `resolve.py:26` |
| `ENGINES` (recognised) | `{sqlite, postgres}` | `resolve.py:27` |
| `LOWERED_ENGINES` | `{sqlite}` | `resolve.py:28` |
| `SHIP_MODES` | `{on_open, explicit}` | `resolve.py:29` |
| `MODES` | `{readwrite, readonly}` | `resolve.py:30` |
| `SNAPSHOTS` | `{none, before_ship}` | `resolve.py:31` |

**PostgreSQL is recognised but not implemented.** The grammar and resolver accept
`engine postgres`, but there is no PostgreSQL lowering — `lower_sqlite.py` and the
SQLite `Store` are the only backend. A deployment using it refuses
`ENGINE_LOWERING_ABSENT` at stage `validate`, positioned at the `engine` item
(or the deployment name when the engine is inherited through `extends`), before
any `ir.Deployment` is constructed and therefore before any schema, store,
ledger, generation or migration effect (`src/garns/resolve.py:1292-1299`). An
unknown engine still refuses `ENGINE_UNKNOWN` (`resolve.py:1258-1259`), which is
what keeps "recognised" and "lowerable" observably distinct. Verified:

```
ENGINES         = ['postgres', 'sqlite']
LOWERED_ENGINES = ['sqlite']
corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns
  → refused: ENGINE_LOWERING_ABSENT  validate  24:10
```

This was the single bounded wave-3 repair of reviewer finding R1 P2.4; see
`../evidence/v9-5-b2/REPAIR.md` and
[LIMITATIONS.md](LIMITATIONS.md#inventory).

## Where schema independence is enforced

"Schema independence" means: the compiler contains no knowledge of any particular
schema's vocabulary, and renaming everything changes nothing but names.

| Guarantee | Mechanism | Location |
|---|---|---|
| No pluralisation, no `<link>_id`, no `id`, no `scope_id` | every physical name is a required key in the binding document | `storage.py:170` (`bind_world`), 17 `STORAGE_*` codes |
| No entity-pair or vocabulary branch in lowering | forward steps become `LEFT JOIN target AS jN ON jN.<identity> = prev.<link column>`; inverse steps become generic correlated subqueries | `lower_sqlite.py::_Frame.alias_for`, `::many_subquery_from_prefix` |
| No schema-name dispatch in derivation | footprint and SQL lowering are exhaustive `visit.Visitor` subclasses; an unhandled node raises `TypeError` | `visit.py:34`, `visit.py:44` (`check_exhaustive`) |
| Renaming is total | resolver reference map replayed over sources by the metamorphic harness; binding re-keyed with fresh physical names | `resolve.py:92`, `metamorphic.py::transform` |
| Decode classification uses parser state only | LALR value stack, expected-terminal set, failing token — no text pattern, filename, comment or marker | `parse.py:69` (`classify_decode`), `parse.py:51-58` |

Verified: both consumer visitors are exhaustive over the current IR unions.

```
footprint missing: []      lowerer missing: []      showlowerer missing: []
EXPR_NODES:    And Or Not Compare Contains In Is Presence Within Quantified Truth
OPERAND_NODES: PathRef Literal GivenRef ClockRef AggRef Arith Negate StaticAggregate Call
SHOW_NODES:    ShowPath ShowIdentity ShowCount ShowRank ShowScalar ShowNested
```

## Static queries versus dynamic questions

Two nouns, one algebra core, one lowering, different obligations.

| | `query` (static) | `question` (dynamic) |
|---|---|---|
| Algebra | closed subset **plus** arithmetic, aggregates, `distinct`, `having`, `call` | closed subset only |
| `live bounded N` | not admitted by the grammar | required — `QUESTION_LIVE_BOUND_REQUIRED` |
| Footprint | refuses `QUERY_NOT_LIVE` at `validate` (`footprint.py:219`) | derived (`footprint.py::derive_footprint`) |
| Subscribe | refuses `QUERY_NOT_LIVE` at `runtime` (`live.py:187`) | registers an `Instance` |
| Generated products | `queries/<qid>.sql` only | `questions/<qid>.sql` **plus** `.footprint.json`, `.binding.json`, `.routing.json` |
| Composition (`within`) | — | inner must be a question, unwindowed, parameterless (`resolve_read.py:758`) |

Static-only IR nodes are *refused*, never approximated, when a question would
need them: `ClockRef`, `Arith`, `Negate`, `StaticAggregate`, `Call`, `Truth`,
`ShowScalar`, `having` and `distinct` all raise `QUESTION_NOT_FOOTPRINTABLE`
(`footprint.py:49`, `_static_only`).

Verified: generating the SALES world yields exactly three `queries/*.sql` and
four `questions/sales.open_orders.*` files, and no query produces a footprint,
binding or routing descriptor.

## Capture

For a world declaring `writers external_captured`, rows are written by an outside
writer and observed through declared changelog tables.

* `lower_capture_ddl` (`src/garns/lower_sqlite.py:666`) emits one changelog table
  per relation plus three triggers (`AFTER INSERT`, `AFTER UPDATE`,
  `AFTER DELETE`) using the mapped names. The update trigger writes a `before`
  row from `OLD` and then an `update` row from `NEW`, so every update carries its
  before-image.
* Coverage is checked twice. At **bind** time the binding must map every field of
  every relation — `WRITER_CAPTURE_INCOMPLETE`, stage `validate`
  (`storage.py:250-298`). At **load** time `CaptureAdapter.check_coverage`
  (`src/garns/capture.py:31`) reads `PRAGMA table_info` on the real changelog
  tables and refuses the same code at stage `load`, before any effect; those
  `PRAGMA` counts are also the measured coverage denominators.
* `acquire(transaction_id)` (`src/garns/capture.py:47`) reads rows whose revision
  column is still null, orders each relation by its own `seq`, merges, builds
  typed deltas validated by the same `LedgerValidator`, writes one revision plus
  its ledger rows, stamps the consumed changelog rows, and notifies live
  listeners. An `update` without its buffered before-image refuses
  `CAPTURE_SEQUENCE_INVALID`.

Limitation: each relation's changelog has its own `AUTOINCREMENT` sequence, so
ordering within one acquisition is `(seq, carrier)`, not a true global order
(`capture.py:66`).

## Generated targets

`generate(world, out_dir)` (`src/garns/generate.py:55`) deletes and rewrites the
tree and returns `path → sha256`.

| Product | Per | Contents |
|---|---|---|
| `schema.sql` | world | `lower_ddl` output |
| `ir.json` | world | canonical IR + world + storage + scope paths |
| `queries/<qid>.sql` / `questions/<qid>.sql` | read | plan SQL, child SQL as comments, total SQL when paged |
| `questions/<qid>.{footprint,binding,routing}.json` | question only | derived descriptors |
| `python/<qid with . → __>.py` | read | constants + a `rows(connection, params)` helper |
| `rust/<qid with . → __>.rs` | read | `pub const READ/NOUN/SQL/PARAMS/COLUMNS/SCOPED/USES_CLOCK` |
| `rust/main.rs` | world | matches a qualified read name to its SQL, calls `sqlite::run` |
| `rust/sqlite.rs` | world | copied verbatim from `src/garns_rust/sqlite.rs` |
| `manifest.json` | world | schema, `ir_digest`, `storage_digest`, file digests |

**How the Rust runner relates to the engine: it does not reimplement it.** Each
generated `rust/<read>.rs` is a constants module holding the lowered SQL
unchanged (`surfaces.py:30`), and `rust/sqlite.rs` is a 105-line raw
`#[link(name = "sqlite3")]` FFI shim with no crates that prints one JSON array
per row of `[type_code, text]` cells using SQLite's own text conversion
(`src/garns_rust/sqlite.rs:8`, `:82-97`). Python and Rust therefore encode
identically, and parity is **row-shape parity over the same SQL text against the
same SQLite file** — not a claim that Rust has an engine. Nothing in the Rust
tree binds parameters from Garns types, writes, or routes. See
[INTEGRATION.md](INTEGRATION.md#generated-rust-surface).

## Seams for a future Rust/Glade adapter

No Rust runtime and no "Glade" adapter exist in this repository — `rg -i glade`
returns nothing, and `TARGETS` is `{python, rust}` (`resolve.py:26`). This
section names the **existing interfaces** such an adapter would attach to, so
that a future one is an addition rather than a rewrite. Everything below is a
description of current code, not a promise.

| Seam | Interface as it exists today | What an adapter would supply |
|---|---|---|
| Target admission | `TARGETS` in `resolve.py:26`, checked in `resolve_world` (`TARGET_UNKNOWN`) | a new target name and its refusal-free path |
| Surface emission | `surfaces.py::python_surface` / `rust_surface` / `rust_main`, called from `generate.py:83-85`; each takes a `Plan` and returns text | a third emitter over the same `Plan` |
| Plan contract | `lower_sqlite.Plan` — `sql`, `params`, `key_columns`, `columns`, `children`, `total_sql`, `scoped`, `uses_clock`, `shape`, `live_bound` | consume, never re-derive |
| Hidden key columns | `$k0…$kN` (subject identity, or one per group key; `distinct` uses the shown columns), `$parent` and `$k0` for children (`lower_sqlite.py:25`, `:474`) | reproduce the same key discipline |
| Engine-owned parameters | `:_scope`, `:_clock`, `:_parents` (`lower_sqlite.py:22-24`) | bind these outside the declared givens |
| Row encoding | `[type_code, text]` cells with SQLite's own conversion (`src/garns_rust/sqlite.rs`) | reuse, so parity stays checkable |
| Delta/batch shapes | `engine.Delta`, `live.Change`, `live.Batch`, each with `as_dict()` | a wire form, not a new semantics |
| Descriptors | `questions/<qid>.binding.json` and `.routing.json` (`generate.py:29,46`) | drive client-side subscription from these, not from source |

The hard constraint any adapter inherits: a generated artifact counts only if
deleting and regenerating it from Garns source through the resolved IR produces
it byte-for-byte. See [EXTENDING_GARNS.md](EXTENDING_GARNS.md) for the actual
playbook.

## Sustainability assessment

Which parts are designed to be extended, and which exist to satisfy the v9-5
exit matrix and would be re-scoped in a production repository.

| Component | Verdict | Why |
|---|---|---|
| `refuse.py`, `types.py`, `visit.py` | **Stable extension point** | Tiny, total, no downstream coupling. New stages/type classes/nodes plug in here first. |
| `ast.py`, `parse.py` | **Stable**, grammar-bound | `_Builder` is mechanical over the frozen grammar. `classify_decode` is a fixed 6-code taxonomy derived from parser state; adding a decode code means adding a parser-state rule, not a text rule. |
| `resolve.py`, `resolve_read.py` | **Stable but heavy** | 2,171 lines and ~176 distinct refusal codes between them. It is the right place for new validation, but it is the single largest change-impact surface in the repo. |
| `ir.py` | **Stable extension point** | Frozen dataclasses plus canonical encoding. Adding a node requires updating every exhaustive visitor — by design, `visit.check_exhaustive` makes the omission loud. |
| `storage.py` | **Stable extension point** | The binding schema (`garns-v9-5/storage-binding/1`) is versioned and the validation is exhaustive. `binding_document` is an authoring aid only. |
| `lower_sqlite.py` | **Stable core, SQLite-shaped** | One entry point, generic joins. But the module *is* the dialect: a second engine needs a sibling module plus a dialect seam that does not exist yet (`LOWERED_ENGINES` currently makes that absence explicit rather than latent). |
| `engine.py` | **Stable for reads; partial for writes** | `mint`/`change`/`delete` are complete and validated; declared verbs (`alias`, `bulk`, `restricted`, `compound`) resolve and validate fully but have **no runtime and no generated surface**. |
| `live.py` | **Stable** | Small, measured, no schema coupling. The `*`-partition conservatism for unscoped instances is a known coarseness. |
| `footprint.py` | **Stable** | Exhaustive; refuses rather than approximates. |
| `capture.py` | **Stable, SQLite-trigger-shaped** | The trigger-based changelog is SQLite DDL emitted by `lower_capture_ddl`; a different engine needs a different acquisition mechanism. |
| `evolution.py` | **Partial** | 18 event kinds and real `ALTER TABLE` migration, but column- and table-level only; an unclassified column disappearance refuses `MIGRATION_UNSUPPORTED`. |
| `generate.py`, `surfaces.py` | **Stable extension point** | Deterministic, digest-verified, and the natural place to add a target. |
| `src/garns_rust/sqlite.rs` | **Conformance machinery** | 105 lines of FFI whose only job is to make Python/Rust row encoding comparable. It is evidence for a parity gate, not a client runtime. |
| `metamorphic.py`, `mutants.py` | **Conformance machinery** | They exist to prove generalisation and detector independence. They import the production pipeline and must never be imported by it. |
| `tools/check.py`, `tools/make_mutants.py`, `tools/migrate_seed_corpus.py` | **Prototype/lane machinery** | `check.py` is the v9-5 exit-matrix runner (12 gates, 128 checks); the other two rewrite `corpus/worlds/` and `corpus/mutants/` destructively and are part of no gate. |
| `tools/storage_template.py`, `tools/generate_all.py` | **Keep** | Authoring aid and the committed-artifact producer, respectively. |
| `tests/` | **Stable** | 103 stdlib `unittest` cases over the production pipeline that compute their own oracles. Note `tools/check.py` does not invoke them; see [TESTING.md](TESTING.md#commands). |

Declared-but-unconsumed facts, present in the IR and carried through
qualification but read by no DDL, index, query or runtime check:
`ordered_within`, `history kept`, the `filter` flag on uses and links, and the
`pattern` / `length` intent refinements; `dimension` is only checked for
positivity on a `Vector` intent. These are inventoried in
[LIMITATIONS.md](LIMITATIONS.md#inventory).
