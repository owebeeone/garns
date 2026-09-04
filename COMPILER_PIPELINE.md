# Compiler pipeline

Phase-by-phase mechanics of the Garns compiler and runtime: what each phase
consumes, what it produces, what it guarantees, and which refusals it owns.
Structural context is in [ARCHITECTURE.md](ARCHITECTURE.md); construct syntax and
semantics in [DSL_REFERENCE.md](DSL_REFERENCE.md); the refusal catalogue in
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue); commands in
[TESTING.md](TESTING.md#commands); the public API and CLI in
[INTEGRATION.md](INTEGRATION.md#python-api).

## Phases

Twelve phases. Phases 1–3 are the compiler proper; 4 is shared lowering; 5–9 are
runtime and lifecycle; 10–12 are products and entry points. `Stage` names are the
`refuse.py` stages (`decode, validate, lower, generate, ship, load, runtime`).

| # | Phase | Entry symbol | Input | Output | Invariants | Diagnostics owned (stage) |
|---|---|---|---|---|---|---|
| 1 | Parse | `parse.py::parse_text` | `.garns` text + `grammar/garns.lark` | `ast.SourceFile` | LALR only; every identifier occurrence is its own located `ast.Name`; classification reads parser state, never text | 6 codes (`decode`) |
| 2 | Resolve | `resolve.py::resolve_files` | `list[ast.SourceFile]` | `ir.Program` + reference map | one pass, fixed sub-phase order; every identity qualified; a refusal means no `Program` is ever returned | ~176 codes (`validate`) |
| 3 | Storage binding | `storage.py::bind_world` | `ir.Program`, world name, binding path | `storage.WorldIR` | world selected explicitly; every relation/use/link/kind/changelog field mapped; no name collides; nothing derived | 17 `STORAGE_*` + `WORLD_UNKNOWN`, `WRITER_CAPTURE_INCOMPLETE` (`validate`) |
| 4 | Lowering | `lower_sqlite.py::lower_read`, `::lower_ddl` | `WorldIR` (+ one `ir.Read`) | `Plan` / `ChildPlan`; DDL text | one entry point for both nouns; joins come only from resolved edges; deterministic tiebreak | `NESTED_SHOW_PATH`, `QUANTIFIER_MULTIPLE_MANY`, `GIVEN_NAME_RESERVED` (`validate`); 2 internal guards (`lower`) |
| 5 | Engine | `engine.py::Store.ship`, `::Engine.execute`, `::Engine.transaction` | `WorldIR`, SQLite connection | shipped store; `Result`; committed revisions + ledger rows | typed pre-effect ledger validation before any statement; listeners notified only after commit | 25 codes (`runtime`) |
| 6 | Footprint | `footprint.py::derive_footprint` | `WorldIR`, question `ir.Read` | `Footprint` | exhaustive visitor; static-only nodes refuse rather than approximate | `QUERY_NOT_LIVE`, `QUESTION_NOT_FOOTPRINTABLE`, `QUESTION_COMPOSE_CYCLE` (`validate`) |
| 7 | Live | `live.py::LiveEngine.subscribe`, `::on_commit` | committed deltas + footprints | `Batch` per affected instance | routing never iterates the registry; registration only after a successful initial fetch | `QUERY_NOT_LIVE`, `LIVE_BOUND_EXCEEDED` (`runtime`) |
| 8 | Capture | `capture.py::CaptureAdapter.acquire` | changelog rows in the store | one revision + typed deltas | coverage re-checked against the real store before any effect | `CAPTURE_*` (`runtime`), `WRITER_CAPTURE_INCOMPLETE` (`load`) |
| 9 | Evolution | `evolution.py::classify`, `::migrate`, `::open_store` | two `ir.Program`s / two `WorldIR`s / a store | `Classification`; executed DDL; generation record | continuity by qualified identity; migration is transactional | 12 codes (`ship`), 5 codes (`load`) |
| 10 | Generation | `generate.py::generate` | `WorldIR`, output directory | artifact tree + `manifest.json` | delete-and-rewrite; deterministic; no filesystem path leaks into products | — (consumes upstream refusals) |
| 11 | Surfaces | `surfaces.py::python_surface`, `::rust_surface`, `::rust_main` | a `Plan` | Python / Rust text | SQL embedded unchanged | — |
| 12 | CLI | `cli.py::main` | argv | stdout / exit code | `--world`, `--binding`, `--read` required; nothing selected by position | exits `2` on any `Refusal` |

Counts: 241 distinct refusal codes appear as string literals at 347 raise sites
across `src/**/*.py`; **21 further codes are selected through a variable**
(a ternary, a required-item loop, or a `missing_code`/`code` parameter passed to
a helper that raises it), giving **262** distinct implemented codes — the total
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) catalogues in 266 code/stage rows.
Distinct literal codes by module: `resolve.py` 120, `resolve_read.py` 56,
`engine.py` 19, `storage.py` 19, `evolution.py` 16, `parse.py` 6,
`lower_sqlite.py` 5, `capture.py` 4, `footprint.py` 3, `live.py` 2.

## Phase 1: Parse

`parse.py::parser()` builds one `Lark(grammar_text(), parser="lalr",
propagate_positions=True, maybe_placeholders=False, keep_all_tokens=True)` over
`grammar/garns.lark` (`src/garns/parse.py:30-40`), memoised in a module global.
The grammar start symbol is `start: toplevel*`.

**AST build.** `parse.py::_Builder` walks the Lark tree into `ast.py` nodes.
`_Builder.name` (`parse.py:135`) turns *every* identifier token into its own
`ast.Name` with a `Loc`, appending it to `SourceFile.names`. That list is what
makes the resolver's reference map — and therefore the metamorphic rename —
possible. Dispatch is explicit: `_Builder.decl` (`parse.py:717`) and
`_Builder.toplevel` (`parse.py:768`) raise `AssertionError` on an unknown tree
name rather than silently ignoring it.

**Decode classification.** `parse.py::classify_decode` (`parse.py:69`) turns a
Lark `UnexpectedInput` into a `Refusal`, using only three parser facts: the value
stack read by `_stack_of` from `ip.parser_state.value_stack` (`parse.py:51-58`),
the expected-terminal set from `_expected_of` (`parse.py:61`), and the failing
token. No text pattern, filename, comment or marker participates.

| Order | Code | Condition |
|---|---|---|
| 1 | `SOURCE_TRUNCATED` | `UnexpectedEOF`, or the offending token is `$END` |
| 2 | `MEANS_REQUIRED` | only `STRING` expected and the preceding tail token is not one that takes a non-meaning string (`PATTERN`, `BREAKING`, `PATH`, `DEFAULT`) |
| 3 | `TYPE_SHAPE_INVALID` | the last tail token opens a type position (`COLON`, `OPTIONAL`, `LIST_OF`, `OF`) and expected ⊆ `{NAME, OPTIONAL, LIST_OF}` |
| 4 | `EXPR_NOT_ADMITTED` | inside an open body (`LBRACE` depth > 0), an expression keyword (`WHERE`, `HAVING`, `INVARIANT`) opened the current item and no later item tree closed |
| 5 | `DECL_SHAPE_INVALID` | inside an open body otherwise, or a malformed top-level declaration |
| 6 | `SOURCE_NOT_GARNS` | failure at top level with nothing but completed trees on the stack |

Public entry points: `parse_text(text, file)`, `parse_path(path)`,
`parse_paths(paths)`, and `garns_files(directory)` which returns the sorted
`*.garns` files of one directory (`parse.py:795-813`).

## Phase 2: Resolve

`resolve.py::resolve_files` is `Resolver(files).run()` (`resolve.py:1375`).
`Resolver.run` (`resolve.py:1335`) executes a fixed sub-phase order; each
sub-phase may only depend on state the earlier ones established.

| Order | Sub-phase | Symbol | Establishes |
|---|---|---|---|
| 1 | collect | `Resolver.collect` (`:154`) | module scopes; one `DeclEntry` per declaration; `MODULE_DUPLICATED`, `ID_DUPLICATED`, `TERM_RESERVED` |
| 2 | imports and cycles | `Resolver.resolve_imports` (`:197`) | named imports bound to owner declarations; module import graph acyclic (`MODULE_CYCLE`) |
| 3 | types, newtypes, intents | `resolve_intents` (`:303`) → `resolve_newtype`, `resolve_intent` | closed-set intents resolved first so other intents may reference the nominal type; `resolve_type` (`:249`) |
| 4 | carriers | `resolve_carriers` (`:394`) | traits in composition order via `_trait_order` (`:412`, `TRAIT_CYCLE`), then other carriers, then `resolve_member` (`:722`) |
| 5 | inverses and link targets | `compute_inverses` (`:765`), `validate_link_targets` (`:798`) | reverse edges (`INVERSE_DUPLICATED`); link targets and mint cycles (`LINK_TO_TRAIT`, `LINK_CYCLE_UNMINTABLE`) |
| 6 | reads and invariants | `resolve_reads_and_invariants` (`:828`) → `resolve_read.py::ReadResolver` | typed expressions, paths, shapes, givens; then `check_compositions` (`resolve_read.py:758`) |
| 7 | verbs and evolution statements | `resolve_verbs` (`:847`) | `alias`/`bulk`/`restricted`/`compound`; tombstones; `tighten`/`retype`/`restore`/`move_home`; `EVOLUTION_STATEMENT_HOMELESS` |
| 8 | tombstone reservation | `check_tombstones` (`:1320`) | `ID_RESERVED` for a redeclared tombstoned identity |
| 9 | worlds, scope paths, capabilities | `resolve_worlds` (`:1023`) → `resolve_world` (`:1037`), `compute_scope_paths` (`:1160`), `check_capabilities` (`:1219`) | `ir.World`; `Program.scope_paths[world][carrier]` |
| 10 | deployments | `resolve_deployment` (`:1229`) | `ir.Deployment`; `extends` resolved recursively with cycle detection |
| 11 | closure checks | `check_homeless_intents` (`:1309`), `check_unused_imports` (`:242`) | `INTENT_HOMELESS`, `IMPORT_UNUSED` |

**Path resolution** (`resolve_read.py::ReadResolver.resolve_path`, `:57`) walks
resolved edges only. A link becomes a forward `ir.LinkStep`; an inverse name a
reverse `LinkStep` (`many` unless the source link is the carrier's sole key);
the path ends in a `UseTerminal`, `LinkTerminal`, `IdentityTerminal` or
`KindTerminal`. Walking into a scalar refuses `PATH_THROUGH_SCALAR`; an
unquantified to-many terminal refuses `TERM_TO_MANY_UNQUANTIFIED`.

**Two algebras, one resolver.** `ReadResolver.dyn` (`:237`) resolves the closed
dynamic algebra; `ReadResolver.static` (`:358`) adds arithmetic
(`arith`, `:424`), aggregates (`static_aggregate`, `:443`), `distinct`,
`having`, and registry calls (`call`, `:469`). Both produce nodes of the same
`ir.Expr` / `ir.Operand` unions.

**Reference map.** `Resolver.ref` (`:92`) appends an
`ir.Reference(file, line, column, text, identity, role)` for each bound
identifier occurrence. `Program.references` carries them, and
`metamorphic.py::transform` replays them to rename sources without touching
compiler code.

## Phase 3: Storage binding

`storage.py::bind_world(program, world_name, binding_path)` (`:170`) is the only
producer of a `WorldIR`. It refuses `WORLD_UNKNOWN` when the named world is not
declared, loads the JSON through `load_binding` (`:140`, refusing
`STORAGE_BINDING_UNREADABLE` / `STORAGE_SCHEMA_UNKNOWN` for schema
`garns-v9-5/storage-binding/1`), and then checks the document exhaustively
**before anything is lowered**:

| Requirement | Refusal |
|---|---|
| every storable carrier of the world has a relation mapping; no mapping names a non-carrier | `STORAGE_RELATION_MISSING`, `STORAGE_RELATION_UNKNOWN` |
| every use and link key of that carrier — including the member-qualified keys a family member adds, from `expected_relation_keys` (`:150`) — has a column | `STORAGE_COLUMN_MISSING`, `STORAGE_LINK_MISSING`, `STORAGE_COLUMN_UNKNOWN`, `STORAGE_LINK_UNKNOWN` |
| every physical name is a plain identifier `^[A-Za-z_][A-Za-z0-9_]*$` | `STORAGE_NAME_INVALID` |
| tables and columns collide with nothing, including the three engine tables | `STORAGE_TABLE_COLLISION`, `STORAGE_COLUMN_COLLISION` |
| `kind` is admitted only for families | `STORAGE_KIND_NOT_ADMITTED` |
| `capture` present exactly when the world declares `writers external_captured` | `WRITER_CAPTURE_INCOMPLETE`, `STORAGE_CAPTURE_NOT_ADMITTED` |

`StorageMapping.source` records only the binding file's *name*, not its path
(`storage.py:300-301`), so regeneration from a relocated checkout is
byte-identical. `WorldIR` (`storage.py:63`) then exposes the world's carriers,
storable relations, reads, and the physical accessors `column_of`,
`link_column_of`, `relation_of`, `scope_path`, plus `digest()`.

## Phase 4: Lowering

**Reads.** `lower_sqlite.py::lower_read(world, read)` (`:526`) is the single
entry point for both nouns and returns one `Plan`:

```
Plan(read, noun, sql, params, key_columns, columns, children,
     total_sql, scoped, uses_clock, shape, live_bound)
```

| Mechanism | Behaviour | Location |
|---|---|---|
| Hidden key columns | `$k0` = subject identity for collections and windows; one `$k0…$kN` per group key when grouped; for `distinct` the shown columns *are* the key. Absent from `Plan.columns`. | `:526` (`lower_read`), prefix at `:25` |
| Reserved parameters | `:_scope`, `:_clock`, `:_parents` are engine-owned; a given starting with `_` refuses `GIVEN_NAME_RESERVED` | `:22-24`, `:527-529` |
| Forward join | `LEFT JOIN target AS jN ON jN.<identity> = prev.<link column>` | `_Frame.alias_for` (`:90`) |
| Inverse step | correlated subquery: `EXISTS` / `NOT EXISTS` for `some`/`every`, scalar subquery for `count(…)`/`max(…)`/`min(…)` | `many_subquery_from_prefix` (`:261`) |
| Scope weaving | recursive `scope_predicate` over the resolved link path against `:_scope` | `:370`, called from `base_predicates` (`:384`) |
| Base predicates | family-member discriminator, `archived_by IS NULL` unless `including_archived`, scope predicate | `:384` |
| Deterministic tiebreak | after declared `order` terms: subject identity `ASC` for ungrouped non-distinct reads; group keys `ASC` when grouped; nothing for `distinct` | `order_clause` (`:458`) |
| Nested children | `ChildPlan` with `$parent` + own `$k0`, ordered by the child's `order`-flagged uses then identity; `last N` wraps in a descending `ROW_NUMBER() OVER (PARTITION BY parent …)` | `lower_nested` (`:474`) |
| Composition | `within` inlines the inner read's `SELECT identity FROM …` | `key_select` (`:406`), `visit_Within` (`:231`) |

Verified — a grouped static query with arithmetic, a registry call and a
non-path order key:

```
sales_static.revenue_open_by_customer  noun=query shape=grouped
SELECT j1."co_1e32478f5c" AS "$k0", j1."co_1e32478f5c" AS "customer",
       SUM(s0."co_26bff25d88") AS "revenue", COUNT(*) AS "orders",
       ROUND((CAST(SUM(s0."co_26bff25d88") AS REAL) / COUNT(*)), 2) AS "average_order"
  FROM "ta_8d09f00415" AS s0
  LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7"
 WHERE ((s0."co_7cbde43f56" = 'open') AND (s0."co_26bff25d88" >= :floor))
 GROUP BY j1."co_1e32478f5c" HAVING (SUM(s0."co_26bff25d88") > :floor)
 ORDER BY SUM(s0."co_26bff25d88") DESC, LENGTH(j1."co_1e32478f5c") ASC,
          j1."co_1e32478f5c" ASC
params: ('floor',)  keys: ('$k0',)
cols: ('customer', 'revenue', 'orders', 'average_order')
```

**DDL.** `lower_ddl(world)` (`:605`) emits one `CREATE TABLE` per storable
carrier — identity `INTEGER PRIMARY KEY`, `NOT NULL` where required, literal
defaults, `CHECK` membership for closed sets, `UNIQUE` over key columns, the
family `kind` column with its member `CHECK` — plus a `FOREIGN KEY … ON DELETE
RESTRICT|CASCADE|SET NULL` only when the link's enforcement is not `unenforced`,
and then the three engine tables (generations, revisions, ledger). For an
`external_captured` world it appends `lower_capture_ddl` (`:666`).

Verified — REPORTING declares `reporting.Invoice.customer` with `unenforced`, so
its DDL contains no foreign key at all:

```
CREATE TABLE "ta_342006d009" (
  "id_dea8a7c8d9" INTEGER PRIMARY KEY,
  "co_95da97f99a" TEXT NOT NULL,
  "co_ba8dae4721" REAL NOT NULL,
  "co_13dd0e180e" INTEGER NOT NULL,
  "li_c21e9feb86" INTEGER NOT NULL,
  UNIQUE ("co_95da97f99a")
);
FOREIGN KEY count in the whole REPORTING schema: 0
```

Member-only columns are nullable at the family table (`:621`), because a family's
members share one relation.

## Phase 5: Engine

**Ship.** `Store.__init__(world, path=":memory:")` (`engine.py:164`) connects with
`PRAGMA foreign_keys = ON`; `Store.ship(generation=1, revision=0)` (`:171`) runs
the DDL as one script and inserts the generation row (`ordinal`, `ir_digest`,
`storage_digest`, `shipped_at_revision`). **Execute.**
`Engine.execute(read_qid, params, scope, capabilities, clock)` (`:282`) resolves
the read by qualified name only (`_read`, `:207` → `READ_UNKNOWN`), memoises its
`Plan` (`plan`, `:201`), and binds strictly through `bind_params` (`:305`):

| Condition | Refusal |
|---|---|
| parameter not a declared given | `PARAM_UNKNOWN` |
| required given absent and no default | `PARAM_REQUIRED` |
| wrong Python type / non-member of a closed set | `PARAM_TYPE` |
| scoped plan executed without a scope | `SCOPE_REQUIRED` |
| `unscoped C` read without capability `C` | `CAPABILITY_REQUIRED` |

`list_of` givens are JSON-encoded for `json_each`. `execute_plan` (`:287`) splits
each row into hidden key columns and shown columns, then attaches children via
`_attach_children` (`:356`), which passes parent identities as `:_parents`.

**Transactions.** `Engine.transaction(writer, transaction_id, clock)` (`:214`)
yields a `Transaction`. On `__enter__` (`:399`) it validates the writer and the
transaction id, then `BEGIN`. `mint` (`:445`), `change` (`:496`) and `delete`
(`:527`) each run `LedgerValidator` checks *before* issuing SQL, then evaluate
the carrier's invariants as SQL over the written row (`_check_invariants`,
`:544`). `__exit__` (`:408`) commits through `Engine._commit` (`:217`), which
writes the revision row and one ledger row per delta, `COMMIT`s, and only then
notifies listeners — so a rolled-back transaction produces no revision, no ledger
row and no batch. Scope keys come from `scope_key_of` (`:246`).

## Phase 6: Footprint

`footprint.py::derive_footprint(world, read)` (`:217`) refuses `QUERY_NOT_LIVE`
at stage `validate` for a query (`:219`) and otherwise walks the question IR
through `FootprintDeriver`, an exhaustive `visit.Visitor`.

Collected as `Atom(carrier, field)` where field is a use qid, a link qid, or `"*"`
for structural change (`STRUCTURE`, `:19`): subject structure and the family's
structure for a member subject; the `archived_by` use; both ends of every path
step (the link on its owner, the structure of the reached carrier); projections
including nested shows and the child's `order`-flagged uses; order keys; group
keys; and the scope-path links (`derive_into`, `:185`; `scope_links_of`, `:211`).
`Within` recurses into the whole inner question and records it in `composes`,
refusing `QUESTION_COMPOSE_CYCLE` on re-entry (`:149`).

Static-only nodes refuse `QUESTION_NOT_FOOTPRINTABLE` rather than being
approximated: `ClockRef`, `Arith`, `Negate`, `StaticAggregate`, `Call`, `Truth`,
`ShowScalar`, plus `having` and `distinct` on the read itself (`_static_only`,
`:49`).

Verified for `sales.open_orders`:

```
atoms: (sales.Customer, *)          (sales.Customer, sales.Customer.name)
       (sales.Order, *)             (sales.Order, sales.Order.created_at)
       (sales.Order, sales.Order.customer)
       (sales.Order, sales.Order.status)
       (sales.Order, sales.Order.total)
composes: []   scope_links: []   subject: sales.Order
```

## Phase 7: Live

`LiveEngine(engine)` (`live.py:156`) appends `on_commit` to `engine.listeners`.
`subscribe(read_qid, params, scope, capabilities)` (`:184`) refuses
`QUERY_NOT_LIVE` at stage `runtime` for a query (`:187`), derives the footprint,
performs the initial fetch, and **only then** registers index entries — so a
failed initial fetch leaves no partial registration.

`on_commit(revision, deltas)` (`:231`) calls `match(deltas)` (`:212`), which
probes only the keys a delta can touch, then refreshes each affected instance in
sorted id order. `Instance.refresh` (`:135`) re-executes the shared plan, diffs
the keyed state, and returns a `Batch` — or `None` when nothing changed, so a
result-neutral routed write emits no batch. `_fetch` (`:118`) enforces
`live bounded N`, refusing `LIVE_BOUND_EXCEEDED` at `runtime` (`:121-122`).
`fold(initial, keys, batches)` (`:244`) replays batches onto an initial keyed
state.

## Phase 8: Capture

`CaptureAdapter(engine)` (`capture.py:23`) refuses `CAPTURE_NOT_DECLARED` unless
the world declares `writers external_captured`. `check_coverage()` (`:31`) reads
`PRAGMA table_info` for each mapped changelog table and refuses
`WRITER_CAPTURE_INCOMPLETE` at stage `load` if the table is absent or a declared
field is missing — before any effect; its return value is the per-relation field
count, which is also the measured coverage denominator.

`acquire(transaction_id)` (`:47`) validates writer and transaction id, re-checks
coverage, selects rows whose revision column is null ordered by each relation's
own `seq`, stable-sorts the merged entries by `seq` (`:66`), builds typed deltas
validated by the same `LedgerValidator`, then in one transaction writes the
revision row, the ledger rows, and stamps the consumed changelog rows, and
finally notifies live listeners. `before` rows are buffered; an `update` without
its before-image refuses `CAPTURE_SEQUENCE_INVALID`; an unknown op refuses
`CAPTURE_OP_UNKNOWN`.

## Phase 9: Evolution

`classify(before, after, history, retention)` (`evolution.py:56`) compares two
resolved programs by **qualified identity** and produces `Event`s over eighteen
kinds (`intent_renamed`, `intent_relocated`, `meaning_delta`, `retype`,
`add_intent`, `retire_intent`, `restore_intent`, `move_home`, `add_carrier`,
`retire_carrier`, `lifecycle`, `carry_added`, `use_added`, `use_removed`,
`tighten`, `link_added`, `link_policy`, `link_removed`) plus a `compat` of
`additive` / `deprecating` / `breaking` (`Classification.compat`, `:38`). A
`renamed_from` naming an identity in another module is a relocation; an
undeclared move is a retirement plus a mint and demands a tombstone. Twelve
`ship`-stage codes live here (`_ship`, `:51`).

`migrate(conn, before, after, classification, generation)` (`:220`) executes
against a real store inside one transaction: `ALTER TABLE … RENAME COLUMN` for
continued identities, `ADD COLUMN` plus a repair `UPDATE` for new required uses
(`TIGHTEN_REPAIR_REQUIRED` when there is no repair), a
`<table>__quarantine_<generation>` side table for quarantined retirements, then
`DROP COLUMN`, and finally the new generation row. A column that disappears
without a classified disposition refuses `MIGRATION_UNSUPPORTED` (`:311`). Any
exception rolls the whole migration back (`:321-323`).

`open_store(conn, world, deployment)` (`:327`) refuses `STORE_UNSHIPPED` (no
generation table or row), `STORE_BEHIND` (recorded IR/storage digests differ from
the source) and `STORE_DRIFT` (a table lacks a declared column, or carries an
undeclared one). `check_window` (`:353`) refuses
`GENERATION_OUTSIDE_WINDOW`.

## Phase 10: Generation

`generate.py::generate(world, out_dir)` (`:55`) removes `out_dir` if present,
recreates `queries/`, `questions/`, `python/`, `rust/`, writes every product, and
returns `path → sha256`. Products are listed in
[ARCHITECTURE.md](ARCHITECTURE.md#generated-targets); the manifest schema is
`garns-v9-5/generated-manifest/1` and carries `world`, `ir_digest`,
`storage_digest` and the file digest map (`:87-96`).

The query/question split is enforced here: only `read.is_question` adds
`.footprint.json`, `.binding.json` and `.routing.json` (`:76-80`).
`tree_digest(directory)` (`:100`) hashes relative path + content for every file,
and is what regeneration checks compare.

## Phase 11: Surfaces

Three pure text emitters over a `Plan`. `python_surface(plan)`
(`surfaces.py:8`) writes `READ`, `NOUN`, `SQL`, `PARAMS`, `KEY_COLUMNS`,
`COLUMNS`, `SCOPED`, `USES_CLOCK`, `CHILDREN` and a `rows(connection, params)`
helper; `rust_surface(plan, ident)` (`:30`) writes the same constants as
`pub const`s with the SQL in a raw string; `rust_main(idents)` (`:45`) emits a
binary matching a qualified read name to its SQL. The SQL is embedded unchanged.

## Phase 12: CLI

`cli.py::main` (`:71`) exposes four subcommands — `resolve`, `generate`, `ddl`,
`execute` — over a source **directory**. `--world`, `--binding` and `--read` are
required arguments, so nothing is selected by position. Any `Refusal` prints
`refused: CODE [stage] at file:line:col` on stderr and exits `2` (`:85-87`).
Exact invocations: [INTEGRATION.md](INTEGRATION.md#cli).

## Earliest pre-effect validation boundary

The claim: **`validate` is strictly earlier than any effect**, so a refusal at
`validate` guarantees no store, schema, ledger row, generated artifact or
migration exists. The proof is structural, not behavioural.

1. Deployments are resolved *inside* the resolver's own run — `resolve_worlds`
   (`resolve.py:1023`) calls `resolve_deployment` for every declared deployment,
   and `resolve_files` is `Resolver(files).run()` (`:1375`). A refusal there means
   `run()` never returns, so no `ir.Program` is ever produced.
2. Every effectful entry point takes a `WorldIR`, and the only producer of a
   `WorldIR` is `bind_world(program: I.Program, world_name: str, binding_path:
   Path)` (`storage.py:170`) — which *requires* that `Program`:

| Effect | Entry signature | Location |
|---|---|---|
| store creation | `Store.__init__(self, world: WorldIR, path=":memory:")` | `engine.py:164` |
| schema + generation row | `Store.ship(self, generation=1, revision=0)` | `engine.py:171` |
| ledger / live | `Engine.__init__(self, store: Store, …)` | `engine.py:186` |
| artifact generation | `generate(world: WorldIR, out_dir: Path)` | `generate.py:55` |
| migration | `migrate(conn, before: WorldIR, after: WorldIR, …)` | `evolution.py:220` |
| store open | `open_store(conn, world, deployment)` | `evolution.py:327` |

So schema DDL, store creation, ledger rows, artifact generation and migration are
all downstream of a resolved `Program`. Refusing inside `resolve_deployment` is
therefore provably before any effect.

**Worked example — `ENGINE_LOWERING_ABSENT`.** `postgres` is a recognised engine
but has no lowering in this build. `resolve_deployment` keeps its existing
`ENGINE_UNKNOWN` check on the `engine` item (`resolve.py:1258-1259`), records that
item's position in `engine_at` (`:1261`), and after the required-item loop
(`world`, `engine`, `at`, `ship`, `mode`, `snapshot`) applies the guard at
`resolve.py:1292-1299`:

```python
engine = str(values["engine"])
if engine not in LOWERED_ENGINES:
    refuse("ENGINE_LOWERING_ABSENT", "validate",
           engine_at if engine_at is not None else node.name, …)
```

Only after that guard is `ir.Deployment` built and memoised (`:1300-1305`).
Verified against the committed fixture:

```
ENGINES         = ['postgres', 'sqlite']       # src/garns/resolve.py:27
LOWERED_ENGINES = ['sqlite']                   # src/garns/resolve.py:28
corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns
  → refused: ENGINE_LOWERING_ABSENT  validate  24:10
```

The position is the declaration's `engine` item. A PostgreSQL base reached
through `extends` refuses while resolving that base; the deployment-name
fallback is defensive and currently unreachable. An unknown engine still refuses `ENGINE_UNKNOWN`, which keeps
"recognised" and "lowerable" observably distinct. See
[LIMITATIONS.md](LIMITATIONS.md#inventory) and [PROVENANCE.md](PROVENANCE.md).

Two consequences worth internalising before changing this code:

* A new *pre-effect* check belongs in `resolve.py` / `resolve_read.py` /
  `storage.py` at stage `validate`. Putting it in `engine.py` or `generate.py`
  moves it *after* an effect boundary.
* `lower_sqlite.py` raises three of its five codes at stage `validate`
  (`NESTED_SHOW_PATH`, `QUANTIFIER_MULTIPLE_MANY`, `GIVEN_NAME_RESERVED`),
  attributing them to the source, and only two at stage `lower`
  (`LOWER_INVERSE_OUTSIDE_QUANTIFIER`, `LOWER_QUANTIFIER_WITHOUT_MANY`) as
  internal guards the resolver normally pre-empts.

## Generated artifact lifecycle

**Products per world** — `queries/` and `questions/` SQL, `python/` and `rust/`
surfaces, `schema.sql`, `ir.json`, `manifest.json`; see the table in
[ARCHITECTURE.md](ARCHITECTURE.md#generated-targets). **Producer** —
`tools/generate_all.py` deletes `generated/`, regenerates the eight committed
worlds from their sources and bindings, and writes `generated/INDEX.json`
(schema `garns-v9-5/generated-index/1`) with each world's source, binding, file
count and `tree_sha256`.

**Byte-regeneration expectation.** A generated artifact counts only if deleting
and regenerating it from Garns source through the resolved IR reproduces it
byte-for-byte. Three properties make that achievable: `generate` deletes the
output tree before writing (`generate.py:57-58`); reads are emitted in sorted qid
order (`:72`); and `StorageMapping.source` records only the binding's file name,
so no filesystem path leaks into `ir.json` or `manifest.json`
(`storage.py:300-301`). **How the gate checks it** — `tools/check.py::g9` (`:529`)
regenerates every non-evolution world into a temporary directory and compares
`tree_digest` against the committed tree (`check.py:544`), then generates
PRACTICE twice into two fresh directories and compares those digests (`:547`);
`tests/` asserts the same property, including regeneration from a relocated copy
of the corpus.

**Verifiable file counts** (from `generated/INDEX.json`, confirmed by an on-disk
count):

| World | Files | Source |
|---|---:|---|
| APPFLOWY | 5 | `corpus/worlds/appflowy` |
| APPFLOWY_VEC | 5 | `corpus/worlds/appflowy` |
| EVERBILITY | 32 | `corpus/worlds/everbility` |
| LEDGERHOUSE | 32 | `corpus/conformance/worlds/ledgerhouse` |
| PRACTICE | 50 | `corpus/worlds/practice` |
| REPORTING | 8 | `corpus/conformance/worlds/reporting` |
| SALES | 20 | `corpus/conformance/worlds/sales` |
| VAULTWARDEN | 20 | `corpus/worlds/vaultwarden` |
| **Sum of per-world counts** | **172** | + `generated/INDEX.json` = 173 files under `generated/` |

Verified for SALES (20 files, generated into a temporary directory): three
`queries/*.sql`, four `questions/sales.open_orders.*`, four `python/*.py`, four
`rust/*.rs` plus `rust/main.rs` and `rust/sqlite.rs`, `schema.sql`, `ir.json`,
`manifest.json`. No query produces a footprint, binding or routing descriptor.

## Diagnostic ownership by phase

Which module raises which stage. Counts are distinct code literals / raise sites
from a read-only scan of `src/**/*.py` for the first string argument of
`refuse(`, `Refusal(`, `_runtime(`, `_ship(` and `_fail(`.

| Module | Stages it raises | Distinct codes | Raise sites |
|---|---|---:|---:|
| `parse.py` | `decode` | 6 | 8 |
| `resolve.py` | `validate` | 120 | 143 |
| `resolve_read.py` | `validate` | 56 | 92 |
| `storage.py` | `validate` (2 direct + 31 via `_fail`) | 19 | 33 |
| `lower_sqlite.py` | `validate` (3), `lower` (2) | 5 | 5 |
| `footprint.py` | `validate` | 3 | 3 |
| `engine.py` | `runtime` (via `_runtime`) | 19 | 32 |
| `live.py` | `runtime` | 2 | 2 |
| `capture.py` | `runtime` (via `_runtime`), `load` (2) | 4 | 5 |
| `evolution.py` | `ship` (via `_ship`), `load` (7) | 16 | 24 |
| **Total** | | **241** | **347** |

**21 further codes are chosen through a variable** rather than a literal, in
three shapes: a ternary at the raise site (`LINK_ENFORCEMENT_REPEATED` /
`LINK_FLAG_REPEATED` at `resolve.py:526`, `QUESTION_LIVE_BOUND_DUPLICATED` /
`READ_ITEM_REPEATED` at `resolve_read.py:529`, `CONSTRAINT_VIOLATED` at
`engine.py:489`, `:522`); a required-item loop over `(key, code)` pairs (the six
`WORLD_*_REQUIRED` / `QUARANTINE_RETENTION_REQUIRED` codes at
`resolve.py:1043-1052` and the six deployment ones at `resolve.py:1282-1291`);
and a code passed to a helper that raises it — `lookup` / `lookup_qualified`
(`missing_code`), `literal_of_type` and `given_ref` (`code`), which is the only
way `CARRIER_UNKNOWN`, `EXEMPT_UNKNOWN`, `GIVEN_DEFAULT_TYPE` and `PAGE_TYPE`
are reachable. **241 + 21 = 262.** Because the helper form takes a code as data,
the scan must follow call sites; the full derivation and the per-code catalogue
are in [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue).

Four codes are deliberately raised at **two different stages** by two different
owners, and every spelling is correct:

| Code | `validate` owner | Other stage |
|---|---|---|
| `QUERY_NOT_LIVE` | `footprint.py:219` (deriving a footprint for a query) | `runtime` — `live.py:187` (subscribing a query) |
| `READ_UNKNOWN` | `resolve_read.py` (`within` names an unresolvable read), `resolve.py::resolve_bulk` (`bulk over` an unknown read) | `runtime` — `engine.py:211` (a read qid the world does not hold) |
| `VERB_INPUT_ENGINE_OWNED` | `resolve.py:918`, `:943` (a bulk `set` or `restricted accepts` naming a stamped use) | `runtime` — `engine.py:429` (a write supplying a stamped use) |
| `WRITER_CAPTURE_INCOMPLETE` | `storage.py` (binding does not map every field) | `load` — `capture.py:41,43` (real changelog table missing a declared field) |

The authoritative code list, with meanings and fixtures, is
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue).
