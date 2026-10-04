# Limitations

What Garns does **not** do, stated plainly, with the code that makes each
statement true. Nothing here is aspirational and nothing is hidden behind a
euphemism: if a feature parses and validates but nothing executes it, this
document says so.

Refusal codes are catalogued in [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue);
where each guarantee is enforced is in [ARCHITECTURE.md](ARCHITECTURE.md); how to
add a backend or a target is in [EXTENDING_GARNS.md](EXTENDING_GARNS.md); how the
claims below are tested is in [TESTING.md](TESTING.md#gate-matrix-g0g11).

**Status vocabulary**

| Status | Meaning |
|---|---|
| **deliberate refusal** | The construct is recognised and then refused, on purpose, with a stable code and a source position. Not a bug and not a gap to be silently worked around. |
| **conformance implementation** | Implemented, correct for the cases it admits, but deliberately narrower than the language a production system would want. It refuses outside its range rather than approximating. |
| **generated evidence only** | Exists so an exit-matrix gate can be *measured*. Not a client-facing capability. |
| **production-ready capability** | Complete for its stated contract; listed here only because it constrains callers. |
| **not implemented** | Resolves and validates, but no consumer executes it. Nothing runs. |

---

## Inventory

| Area | Status | Detail | Evidence |
|---|---|---|---|
| **PostgreSQL backend** | deliberate refusal | `postgres` is a *recognised* engine but not a *lowered* one. Any deployment naming it refuses `ENGINE_LOWERING_ABSENT` at stage `validate`, positioned at the `engine` item (or at the deployment name when the engine arrives through `extends`), **before** any `I.Deployment` is constructed and therefore before any binding, schema, store, ledger, generation or migration effect. An unrecognised engine still refuses `ENGINE_UNKNOWN`, which is what proves `postgres` was not merely deleted. | `src/garns/resolve.py:27-28` (`ENGINES` vs `LOWERED_ENGINES`), guard at `resolve.py:1293-1299`; `../evidence/v9-5-b2/REPAIR.md` §1; 6 G6 checks at `tools/check.py:346-385`; 5 cases in `tests/test_repair_engine_lowering.py`; `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns`; `corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT` |
| **Only SQLite has a lowering or a store** | conformance implementation | `src/garns/lower_sqlite.py` *is* the dialect; `Store` opens `sqlite3.connect` directly (`src/garns/engine.py:167`). There is no dialect seam and no second `Store`. `LOWERED_ENGINES` makes that absence explicit rather than latent. | `src/garns/lower_sqlite.py`, `src/garns/engine.py:161-180` |
| **Verbs have no runtime** | not implemented | `alias`, `bulk`, `restricted` and `compound` resolve into `ir.Alias` / `ir.Bulk` / `ir.Restricted` / `ir.Compound` and are fully validated (derived-verb membership, bulkable verbs, set targets and types, accepted inputs, step ordering, bind types — 20 refusal codes). **No consumer executes them and no surface is generated for them**: `generate()` iterates `world.reads` only. The engine exposes `mint` / `change` / `delete` directly. | `src/garns/generate.py:72` (`for read in sorted(world.reads, …)`); verb codes catalogued in [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) |
| **Nested shows follow exactly one inverse link** | conformance implementation | `lower_nested` refuses `NESTED_SHOW_PATH` unless the path is a single inverse step; a deeper chain is not lowered. A nested show on a non-to-many path refuses earlier with `NESTED_SHOW_NOT_TO_MANY`. | `src/garns/lower_sqlite.py:478`; `src/garns/resolve_read.py:735` |
| **A quantified comparison follows one to-many prefix** | conformance implementation | `visit_Quantified` refuses `QUANTIFIER_MULTIPLE_MANY` when the body mentions more than one distinct inverse prefix; a body with none refuses `QUANTIFIER_WITHOUT_TO_MANY` at resolve. | `src/garns/lower_sqlite.py:245`; `src/garns/lower_sqlite.py:242` (internal `lower`-stage guard) |
| **`within` composes parameterless inners only** | conformance implementation | An inner read that declares givens refuses `COMPOSE_INNER_GIVENS`: the composed subquery cannot be parameterised per outer row. Composition is narrowed further by `QUESTION_COMPOSE_PAGED`, `QUESTION_COMPOSE_UNSCOPED`, `QUESTION_COMPOSE_STATIC` and `QUESTION_COMPOSE_CYCLE`. | `src/garns/resolve_read.py:771`; cycle detection at `src/garns/footprint.py:149` |
| **Nested shows are refused in grouped and distinct results** | deliberate refusal | In a grouped read, `identity`, `rank` and nested shows refuse `AGGREGATE_MISUSED` — a grouped row has no subject identity to attach children to. In a `distinct` read a nested show refuses `NESTED_SHOW_WITH_DISTINCT` for the same reason. | `src/garns/resolve_read.py:698` (`"identity, rank, and nested shows do not appear in grouped results"`); `src/garns/resolve_read.py:651` |
| **`Instant` is stored as `INTEGER`** | conformance implementation | `sql_storage_type` maps `integer / boolean / instant → INTEGER`, `decimal → REAL`, `opaque / vector → BLOB`, everything else `→ TEXT`. There is no date/time type in the store, and no timezone semantics anywhere. | `src/garns/types.py:106-114` |
| **Capture ordering inside one acquisition is `(seq, carrier)`** | conformance implementation | Each relation's changelog carries its own `AUTOINCREMENT` sequence. `acquire` selects each relation's unassigned rows `ORDER BY seq`, appends them in world-relation order, then stable-sorts by `seq` alone — so cross-relation ties break by carrier qid, not by a true global order. An `update` row arriving without its buffered `before` image refuses `CAPTURE_SEQUENCE_INVALID`. | `src/garns/capture.py:62-66`, `:89` |
| **Migration is column- and table-level only** | conformance implementation | `migrate` emits `ALTER TABLE … RENAME COLUMN`, `ADD COLUMN` (plus a repair `UPDATE`), `DROP COLUMN`, a `<table>__quarantine_<generation>` side table for quarantined retirements, and `CREATE TABLE` for a new relation. A column that disappears without a classified disposition refuses `MIGRATION_UNSUPPORTED`; a new required use with no repair refuses `TIGHTEN_REPAIR_REQUIRED`. Arbitrary in-place type changes are not performed. | `src/garns/evolution.py:220-325`, refusals at `:311` and `:266` |
| **The decode taxonomy is 6 codes derived from parser state** | conformance implementation | `SOURCE_NOT_GARNS`, `SOURCE_TRUNCATED`, `MEANS_REQUIRED`, `TYPE_SHAPE_INVALID`, `EXPR_NOT_ADMITTED`, `DECL_SHAPE_INVALID`, selected from the LALR value stack, the expected-terminal set and the failing token — never from text patterns, filenames, comments or markers. Finer decode diagnostics do not exist; 40 of the 168 mutant cases land on this taxonomy. | `src/garns/parse.py::classify_decode`; [DIAGNOSTICS.md](DIAGNOSTICS.md#decode-classification) |
| **`token_bound` is unverified** | not implemented | G11 reports it verbatim as `"unverified: not measurable from inside the build"`. No token-cost measurement exists anywhere in the implementation. `live_bound`, `capture_denominators` and `rust_parity` each name the operation that measured them. | `tools/check.py:625`; `gate-report.json` G11 evidence |
| **`typescript` (and every target but `python`/`rust`)** | deliberate refusal | `TARGETS = frozenset({"python", "rust"})`. A world listing any other target refuses `TARGET_UNKNOWN` at validate. Three seed worlds had `typescript` removed for exactly this reason. | `src/garns/resolve.py:26`, refusal at `resolve.py:1079`; `corpus/worlds/MIGRATION.md:16`, `:18`, `:23` |
| **The `generate` stage is declared but never raised** | conformance implementation | `refuse.py:STAGES` declares seven stages. `generate` has **zero** raise sites in `src/`. `lower` has exactly **two**, both internal guards (`LOWER_INVERSE_OUTSIDE_QUANTIFIER`, `LOWER_QUANTIFIER_WITHOUT_MANY`) that the resolver normally reaches first; a caller should not expect to observe them. | `src/garns/refuse.py:11-19`; `src/garns/lower_sqlite.py:100`, `:242`; verified by scanning every `refuse(` / `Refusal(` / `_runtime(` / `_ship(` / `_fail(` call in `src/` |
| **Unscoped instances are indexed conservatively** | conformance implementation | A live instance of an `unscoped C` read registers under the `global` partition **and** a `*` partition for each footprint atom, so it is probed for writes in *every* scope. Scope partitioning applies to scoped instances only. Cost, not correctness. | `src/garns/live.py:194-200`; probe side at `live.py:216` |
| **`with_total` is a second `COUNT(*)`** | conformance implementation | The total is a separate query over the same `FROM`/`WHERE` (and `GROUP`/`HAVING` when grouped), not a total derived from the page query. Two round trips per paged read. | `src/garns/lower_sqlite.py:591-596`; consumed at `src/garns/engine.py:301-302` |
| **`Engine.row_values` reads whole rows** | conformance implementation | Building a before-image for `change` / `delete` selects *every* mapped column of the relation rather than projecting the touched fields. | `src/garns/engine.py:266-279`, called from `engine.py:500`, `:531` |
| **Unenforced links produce no `FOREIGN KEY`** | production-ready capability | `unenforced` is a standalone link flag, not an `end` action. The link stays typed, keeps its inverse, and participates in path resolution, storage mapping and footprints — only the `FOREIGN KEY` clause is omitted, so referential integrity is the writer's problem. Combining it with any `end` action refuses `LINK_ENFORCEMENT_CONFLICT`; repeating either refuses `LINK_ENFORCEMENT_REPEATED`; `end unenforced` is a decode-stage `DECL_SHAPE_INVALID`. | `src/garns/lower_sqlite.py:640-643`; `src/garns/resolve.py:526`; G1 checks on REPORTING plus four refusal fixtures |
| **Deployment-scoped worlds are not row-scoped** | conformance implementation | `world … { scope deployment }` sets `deployment_scoped`, which switches off row-level scoping everywhere at once: `scope_key_of` returns the global scope, plans emit no `:_scope` predicate, footprint routing keys are all `global`, and live partitions collapse to `global`. Isolation is then the deployment's responsibility, not the engine's. | `src/garns/ir.py:663`; `engine.py:249`, `lower_sqlite.py:397`, `live.py:179`, `:215`, `generate.py:50`, `footprint.py:212` |
| **The storage binding must be authored; there are no defaults** | production-ready capability | `bind_world` only ever reads a JSON document from disk. Every table, identity column, scalar column, link column, family discriminator, engine table and changelog field is an explicit input. A missing, unknown, colliding, world-mismatched or unreadable mapping refuses (17 `STORAGE_*` codes plus `WORLD_UNKNOWN` and `WRITER_CAPTURE_INCOMPLETE`) before anything is lowered. `binding_document` and `tools/storage_template.py` are authoring aids the compiler never calls. | `src/garns/storage.py:170-303`, `load_binding` at `storage.py:140-147`; `binding_document` at `storage.py:305` |
| **The CLI has no console script** | conformance implementation | There is no `pyproject.toml`, no `setup.py` and no installed `garns` entry point. Invocation is `PYTHONPATH=src … python -m garns.cli`. `--world`, `--binding` and `--read` are required: nothing is selected by position. A refusal prints `refused: CODE [stage] at file:line:col` on stderr and exits `2`. | `src/garns/cli.py:71-88`; see [INTEGRATION.md](INTEGRATION.md#cli) |
| **Generated surfaces embed SQL and nothing else** | generated evidence only | `python_surface` emits constants (`READ`, `NOUN`, `SQL`, `PARAMS`, `KEY_COLUMNS`, `COLUMNS`, `SCOPED`, `USES_CLOCK`, `CHILDREN`) plus a five-line `rows(connection, params)` helper. `rust_surface` emits constants only. Neither validates parameters, binds a scope, enforces a capability, applies a live bound, or attaches nested children — all of that lives in `Engine`. | `src/garns/surfaces.py:8-42`; compare `src/garns/engine.py:305-332` |
| **The Rust runner is a parity instrument** | generated evidence only | `generated/<WORLD>/rust/` is a `rustc`-compilable binary that runs one read's SQL through a 105-line raw FFI shim and prints `[type_code, text]` rows so Python and Rust encodings can be compared. It is not a bindings library, has no crate, no error type, no connection pooling and no async, and links the *system* `libsqlite3`. | `src/garns_rust/sqlite.rs`; `src/garns/surfaces.py:45-64`; G11 at `tools/check.py:622-683` |
| **Declared facts that no consumer reads** | not implemented | `ordered_within`, `history kept`, the `filter` flag on uses and links, and the `pattern` / `length` intent refinements resolve, qualify and reach the IR, but no DDL, index, query, footprint or runtime check consumes them. `dimension` is checked only for positivity on a `Vector` intent (`DIMENSION_NOT_POSITIVE`, `DIMENSION_NOT_VECTOR`). | `src/garns/ir.py:55-57`, `:81`, `:109`, `:138-139`; `src/garns/resolve.py:361-363`, `:378-381` |
| **`live bounded N` refuses; it never truncates** | conformance implementation | A refresh whose row count exceeds the declared bound raises `LIVE_BOUND_EXCEEDED` at `runtime` from inside `Instance._fetch`, so the instance's state is left at its previous revision and no partial batch is emitted. There is no degrade-to-page behaviour. | `src/garns/live.py:118-122` |
| **`tools/check.py --quick` has no effect** | not implemented | The flag is parsed and passed to `g11`, which never reads it. Every gate runs at full cost. | `tools/check.py:688`, `:702`, `:622` |
| **`tools/check.py` does not run `tests/`** | conformance implementation | The gate runner and the unit suite are two independent readings of the same public modules. A green `gate-report.json` says nothing about `tests/`, and vice versa. Run both. | `tools/check.py:699-708` (no `unittest` runner) |
| **`generated/` is not regenerated per world generation** | conformance implementation | G9 and `tools/generate_all.py` cover the 8 distinct worlds and skip the five PRACTICE evolution generations, which are exercised by migration rather than generation. | `tools/check.py:534-536`; `tools/generate_all.py:25-34` |
| **`generated <targets>` does not gate what is emitted** | not implemented | A world's `generated` list is validated (`TARGET_UNKNOWN`, `WORLD_TARGET_REPEATED`) and reaches `ir.World.generated`, but `generate()` reads it nowhere: it always writes `python/` **and** `rust/` for every read. Verified by generating a copy of the SALES world edited to `generated python` — the full `rust/` tree, `main.rs` and `sqlite.rs` included, was still produced. Every corpus world happens to declare both targets, so the committed evidence cannot show this. | `src/garns/generate.py:55-97` (no reference to `world.world.generated`); `src/garns/ir.py:653` |
| **Most deployment items are validated and then unused** | not implemented | `at` (`Location`), `mode`, `snapshot` and `pool` are required, type-checked and carried into `ir.Deployment`, but no consumer reads them: `Store(world, path)` takes its path from the *caller*, not from the deployment. The single exception is `deployment.ship`, read by `open_store` to choose between two `STORE_BEHIND` messages. A world's `durability` is likewise validated (`DURABILITY_UNKNOWN`) and never consumed. | `src/garns/ir.py:675-687`; only use at `src/garns/evolution.py:339`; `src/garns/engine.py:164-168` |
| **No indexes are generated** | not implemented | `CREATE INDEX` appears nowhere in `src/` or in any committed `generated/**/schema.sql`. The DDL emits `INTEGER PRIMARY KEY` identities, `NOT NULL`, literal defaults, closed-set `CHECK`s, `UNIQUE` over key columns, the family `kind` column with its member `CHECK`, and enforced `FOREIGN KEY`s — nothing else. The `filter` and `order` use/link flags, which are the natural index hints, are among the unconsumed facts above. | `src/garns/lower_sqlite.py:605-664`; verified by scanning `src/` and `generated/` |
| **Live subscriptions cannot be cancelled** | conformance implementation | `LiveEngine` has `subscribe` but no `unsubscribe`, and `Registry` has `add`/`get` but no removal. Every `Instance` also retains its full materialised keyed state *and* an append-only `log` of every batch it has ever emitted, neither of which is ever trimmed. Fine for a gate run; not a server. | `src/garns/live.py:65-88`, `:110-112`, `:151` |
| **Capabilities are caller-asserted, not authenticated** | conformance implementation | `Engine.execute(..., capabilities={...})` compares the read's declared `unscoped C` against a set the caller passes in. There is no principal, no token and no authorisation layer; `CAPABILITY_REQUIRED` only detects a caller that did not assert the capability. The same is true of `writer`: `LEDGER_WRITER_UNKNOWN` checks the *name* against the world's declaration. | `src/garns/engine.py:328-329`; `src/garns/engine.py:89-91` |
| **Invariants are re-evaluated as one SQL query per written row** | conformance implementation | After each `mint` / `change`, every invariant of the carrier (and of its family) is lowered afresh and run as `SELECT <pred> FROM <table> AS s0 … WHERE s0.<identity> = ?`; a false result rolls the transaction back and refuses `INVARIANT_VIOLATED`. Correct, but one lowering plus one round trip per invariant per row. | `src/garns/engine.py:544-564` |
| **One connection, no pooling, no concurrency model** | conformance implementation | `Store` opens a single `sqlite3.connect(path, isolation_level=None)` with `PRAGMA foreign_keys = ON` and manages `BEGIN`/`COMMIT`/`ROLLBACK` by hand. There is no pool, no thread-safety statement, no retry on `SQLITE_BUSY`, and no async surface. `list_of` givens are passed as JSON text and expanded with `json_each` (`… IN (SELECT value FROM json_each(:p))`), which is a SQLite-specific construct. | `src/garns/engine.py:164-168`, `:320-321`; `src/garns/lower_sqlite.py:223`, `:505` |

### Shape of the gaps

Three patterns account for nearly every row above.

1. **Declared, validated, unconsumed.** A construct is parsed, qualified, typed
   and carried into the IR, and then no downstream consumer reads it: verbs,
   `generated <targets>`, `at` / `mode` / `snapshot` / `pool`, `durability`,
   `ordered_within`, `history kept`, the `filter` flag, `pattern`, `length`.
   These are the cheapest gaps to close — the IR already carries the fact — and
   the most dangerous to assume closed, because nothing refuses when you rely on
   them.
2. **Narrow but honest.** A feature is implemented for a bounded shape and
   *refuses* outside it rather than approximating: one inverse hop for nested
   shows, one to-many prefix for quantifiers, parameterless composed inners,
   column- and table-level migration, six parser-state decode codes. These are
   safe to build on, because the boundary announces itself with a code.
3. **Single-backend by construction.** SQLite is not a default that a
   configuration switch can change; it is the shape of `lower_sqlite.py`,
   `Store`, the trigger-based changelog and the `json_each` list expansion.
   `LOWERED_ENGINES` exists precisely so that this is a visible refusal rather
   than a latent assumption.

---

## Assumptions downstream consumers must not make

Each of these is a mistake a caller can make that the code will refuse — but
refusing late is expensive, so know them up front.

- **Do not assume a default physical name.** There is no pluraliser, no `id`
  convention, no `<link>_id` convention and no `scope_id` column anywhere. If a
  binding does not map something, the world does not bind. G10 scans `src/` for
  each of these conventions and asserts zero hits (`tools/check.py:584-600`).
- **Do not select anything by a bare name.** `Engine.execute`, `Engine.plan`,
  `LiveEngine.subscribe`, `tx.mint` / `change` / `delete`, `bind_world` and the
  CLI all take a *qualified* identity — `module.read`, `module.Carrier`,
  `module.Carrier.field`, and the world name. A bare name refuses `READ_UNKNOWN`
  / `LEDGER_CARRIER_UNKNOWN` / `LEDGER_FIELD_UNKNOWN` / `WORLD_UNKNOWN`. Two
  modules may legitimately declare the same local name.
- **Do not assume an engine other than `sqlite`.** See the first inventory row.
- **Do not expect a verb to execute.** Write through
  `Engine.transaction(...)` and `mint` / `change` / `delete`.
- **Do not read row identity from the visible columns.** Result identity travels
  in hidden `$k`-prefixed columns absent from `Plan.columns`: `$k0` is the
  subject identity for collections and windows; grouped reads carry one
  `$k0…$kN` per group key; a `distinct` read's key *is* its shown columns;
  nested children add `$parent` plus their own `$k0`
  (`src/garns/lower_sqlite.py:25`, `:547-554`). Batch `Change.key` tuples are
  built from exactly these.
- **Do not name a parameter starting with `_`.** `:_scope`, `:_clock` and
  `:_parents` are engine-owned; a given whose name starts with `_` refuses
  `GIVEN_NAME_RESERVED` in both the resolver (`src/garns/resolve_read.py:49`) and
  the lowering (`src/garns/lower_sqlite.py:530`).
- **Do not reuse the reserved terms** `identity`, `kind`, `rank`, `count`,
  `engine_clock`, `ship_clock` as an intent, carrier or member name — they refuse
  `TERM_RESERVED` (`src/garns/types.py:30`, `src/garns/resolve.py:104`).
- **Do not assume cross-scope routing precision for unscoped reads.** An
  `unscoped C` instance is registered under `global` and `*` and will be probed —
  and refreshed — for writes in scopes it does not display.
- **Do not treat a routed write as a changed result.** Routing means "a footprint
  atom was touched"; `Instance.refresh` returns `None` when the diff is empty, so
  a result-neutral routed write emits no batch (`src/garns/live.py:147-148`).
- **Do not assume notification order relative to commit.** Listeners fire *after*
  `COMMIT` (`src/garns/engine.py:232-237`); a rolled-back transaction produces no
  revision, no ledger row and no batch.
- **Do not assume `total` is populated.** `Result.total` is `None` unless the read
  declares `with_total` (`src/garns/engine.py:300-303`).
- **Do not write to a family carrier.** `check_carrier` refuses
  `LEDGER_CARRIER_ABSTRACT`; write through one of its members
  (`src/garns/engine.py:100-101`).
- **Do not mix writer classes.** A `governed` world admits only the writer
  `"governed"`; an `external_captured` world admits only its declared
  `writer_source`, and constructing a `CaptureAdapter` on a governed world
  refuses `CAPTURE_NOT_DECLARED` (`src/garns/capture.py:27-28`,
  `src/garns/engine.py:86-91`).
- **Do not assume the store tolerates extra columns.** `open_store` refuses
  `STORE_DRIFT` both when a declared column is missing *and* when the table
  carries an undeclared one (`src/garns/evolution.py:346-349`).
- **Do not treat `generated/` as a build output you can regenerate casually.**
  It is committed evidence; `tools/generate_all.py` deletes the tree before
  rewriting it. See [TESTING.md](TESTING.md#commands).
- **Do not read a deployment as a connection string.** `at env ARCHIVE_URL`,
  `mode readwrite`, `snapshot before_ship` and `pool 4` are validated and then
  ignored; the store path is whatever the caller passes to `Store(world, path)`.
  Only `ship` is read, and only by `open_store`.
- **Do not infer emitted targets from `generated <targets>`.** Both Python and
  Rust surfaces are always written. Filter by directory after the fact if you
  need only one.
- **Do not assume an index exists** because a use carries `filter` or `order`.
  None is created.
- **Do not hold a subscription open indefinitely.** There is no `unsubscribe`,
  and each `Instance` keeps its full state plus every batch it has emitted.
- **Do not treat a capability set or a writer name as an authorisation.** Both
  are strings the caller supplies; Garns checks them against the world's
  declaration and nothing more.
- **Do not share one `Store` across threads or processes.** A single
  `sqlite3` connection, hand-managed transactions, no busy handling.

---

## Evidence-only surfaces

These modules and tools exist to satisfy the v9-5 exit matrix. They import the
production pipeline; the production pipeline must never import them. In a
production repository they would be re-scoped or dropped — see
[ARCHITECTURE.md](ARCHITECTURE.md#sustainability-assessment).

| Surface | Why it exists | Note |
|---|---|---|
| `tools/check.py` | Runs G0–G11 and writes `gate-report.json` (12 gates, 128 checks) | The lane's exit-matrix runner, not a CI entry point. Rewrites `gate-report.json` on every run |
| `src/garns/mutants.py` | Observes each mutant through the real stages and returns `(stage, code, line, column)` | Never reads an expectation manifest; the manifests are assertions checked elsewhere |
| `src/garns/metamorphic.py` | Replays the resolver's `Reference` map to rename a whole world and re-key its binding | Proves schema independence without touching compiler code |
| `src/garns_rust/sqlite.rs` + `generated/<WORLD>/rust/` | Makes Python/Rust row encoding comparable for G11 | Copied verbatim into every generated tree (`src/garns/generate.py:86`) |
| `tools/storage_template.py` | Emits a complete binding from a naming callback so an author can start from one and rename anything | The compiler never calls it; `--fresh SEED` emits opaque hashed names so they cannot be mistaken for a convention |
| `tools/make_mutants.py` | Rebuilds `corpus/mutants/` and its authored manifest | Destructive; part of no gate |
| `tools/migrate_seed_corpus.py` | Rebuilds `corpus/worlds/` from the frozen seed and writes `MIGRATION.md` | Destructive; part of no gate |
| `tools/generate_all.py` | Produces the committed `generated/` trees and `INDEX.json` | Destructive by design (deletes first); G9 compares against an independent fresh generation, not against this driver's output |
| `the historical v9-5 lane/tools/check_scaffold.py` | Verifies the frozen v9-5 lane inputs and cache hygiene | Belongs to the review lane, not to the Garns repository; it never imports the implementation |
