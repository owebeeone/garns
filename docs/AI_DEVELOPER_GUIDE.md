# AI developer guide

Operating manual for an agent (or human) modifying the Garns implementation.
Load it at the start of any change; it tells you *which* files to open, what may
not be broken, and what must be re-run before the change is done.

## Purpose and how to use this guide

- **Audience:** AI coding agents first, humans second. Everything here is a
  lookup, not a narrative: use the tables, do not read end to end.
- **Selective loading.** Start at `## Read these files for this task`, open only
  the files that recipe names, then check `## Change-impact map` for what your
  edit invalidates and `## Definition of done for implementation changes`
  before you claim completion.
- **Scope.** This guide owns *process*. It does not restate:
  language surface → `DSL_REFERENCE.md`; component boundaries and dependency
  direction → `ARCHITECTURE.md`; phase order and the pre-effect boundary →
  `COMPILER_PIPELINE.md`; refusal codes → `DIAGNOSTICS.md` (`## Catalogue`);
  commands and regression style → `TESTING.md`; embedding Garns in a host →
  `INTEGRATION.md`; what is deliberately absent → `LIMITATIONS.md`
  (`## Inventory`). How to *add* something is `EXTENDING_GARNS.md`.
- **Evidence rule.** Every claim below is traceable to code, a gate check, a
  test, or a corpus fixture, cited as `path::symbol` or `path:line`. If you
  change the code, change the citation.

## Repository map

`F` = frozen input (never edit). `A` = authored input (hand-maintained source of
truth). `G` = generated output (never hand-edit; regenerate). `E` = evidence-only
machinery (proves properties; no product depends on it at runtime).

| path | responsibility | owner / boundary |
|---|---|---|
| `grammar/garns.lark` | the canonical LALR grammar; the only definition of admitted syntax | **F** — byte-identical to the lane grammar (G0, `tools/check.py:132-135`) |
| `src/garns/__init__.py` | package docstring and `__version__` | A |
| `src/garns/refuse.py` | `Refusal` dataclass, the seven `STAGES`, `refuse()` | A — single failure channel |
| `src/garns/types.py` | builtin scalars, `TypeRef`, `comparable`, `ordered`, `sql_storage_type` | A — the only place a Garns type maps to a SQL storage class |
| `src/garns/calls.py` | `REGISTRY` of admitted static functions with purity and SQL template | A — a `call` resolves against this and nothing else |
| `src/garns/ast.py` | located source nodes (`Loc`, `Name`, one node per grammar shape) | A — mirrors the grammar; no semantics |
| `src/garns/parse.py` | Lark driver, `_Builder` tree→AST, `classify_decode` | A — decode codes come from parser state only |
| `src/garns/resolve.py` | declarations, imports, intents, carriers, verbs, worlds, deployments, scope paths, the reference map | A — owns every naming rule |
| `src/garns/resolve_read.py` | paths, typed expressions, shapes, givens for both nouns | A — dynamic algebra is the closed subset of the static one |
| `src/garns/ir.py` | the typed qualified IR, `canonical`, `canonical_json`, `digest` | A — the one meaning; all consumers read it |
| `src/garns/visit.py` | `Visitor` base, `union_members`, `check_exhaustive`, `assert_exhaustive` | A — exhaustiveness mechanism |
| `src/garns/storage.py` | binding schema, `bind_world`, `WorldIR`, `binding_document` | A — physical names are inputs, never guesses |
| `src/garns/lower_sqlite.py` | the single relational/SQL lowering, `Plan`/`ChildPlan`, `lower_ddl`, `lower_capture_ddl` | A — one lowering for query *and* question |
| `src/garns/engine.py` | `Store`, `Engine`, `Transaction`, `LedgerValidator`, `Delta` | A — typed pre-effect validation before any statement |
| `src/garns/live.py` | `LiveEngine`, `Registry`, `Instance`, `Stats`, `fold` | A — partitioned routing; measured counters |
| `src/garns/footprint.py` | `derive_footprint`, `FootprintDeriver`, `Atom` | A — questions only; static-only nodes refuse |
| `src/garns/capture.py` | `CaptureAdapter.check_coverage` / `.acquire` for `external_captured` worlds | A |
| `src/garns/evolution.py` | `classify`, `migrate`, `open_store`, `check_window` | A |
| `src/garns/generate.py` | `generate`, `tree_digest`, binding/routing descriptors | A — produces `generated/` |
| `src/garns/surfaces.py` | Python and Rust surface text embedding the lowered SQL | A |
| `src/garns/metamorphic.py` | rename-through-the-reference-map harness, `normalized_program_json` | **E** |
| `src/garns/mutants.py` | `observe_single`, `observe_scenario`, `observe_all` | **E** |
| `src/garns/cli.py` | `resolve` / `generate` / `ddl` / `execute` entry points | A |
| `src/garns_rust/sqlite.rs` | raw `#[link(name = "sqlite3")]` FFI used by generated Rust runners (no crates) | A — copied verbatim into every `generated/*/rust/sqlite.rs` |
| `tools/check.py` | runs G0–G11 and writes `gate-report.json` | **E** — the gate runner |
| `tools/generate_all.py` | deletes and regenerates `generated/` for the eight worlds, writes `generated/INDEX.json` | A (producer) — **destructive** |
| `tools/make_mutants.py` | rewrites `corpus/mutants/` and its `expected.json` | A (producer) — **destructive** |
| `tools/migrate_seed_corpus.py` | rewrites `corpus/worlds/` and `MIGRATION.md` from the frozen seed | A (producer) — **destructive** |
| `tools/storage_template.py` | prints a complete binding for a world (authoring aid) | A — the compiler never calls it |
| `tests/` | 103-case `unittest` suite over the production pipeline | **E** |
| `corpus/conformance/static/`, `corpus/conformance/dynamic/` | the lane's frozen conformance sources, copied byte-identically | **F** (copies; G0 compares bytes) |
| `corpus/conformance/worlds/` | `sales`, `reporting`, `ledgerhouse` sources **plus** their `storage-*.json` bindings | A |
| `corpus/conformance/refusals/` | 12 refusal fixtures + `expected.json` | A |
| `corpus/metamorphic/collision/` | `alpha`/`beta` modules with identical local names | A |
| `corpus/worlds/` | migrated seed worlds + `MIGRATION.md` (produced) + `storage-*.json` (authored) | mixed: sources **G**, bindings **A** |
| `corpus/mutants/` | 131 single-file mutants, 37 scenario directories, `expected.json` | **G** (from `tools/make_mutants.py`) |
| `generated/` | 8 world trees + `INDEX.json` | **G** (from `tools/generate_all.py`); G9 proves byte identity |
| `gate-report.json` | machine-readable gate evidence, schema `garns/v9-6-w0-gate-report/1` | **G** (from `tools/check.py`) |

## Read these files for this task

Ordered recipes. Open in order and stop when the change is covered; the file
after the last arrow is where the change is *proved*.

**Add or change a grammar construct** — *the v9-5 grammar is frozen; this path
applies to the future repository only. In v9-5, report a grammar defect to the
operator instead of editing `grammar/garns.lark`.*
`grammar/garns.lark` (the rule and its item list) → `src/garns/ast.py` (a located
node) → `src/garns/parse.py::_Builder` (the `*_decl` / `*_item` method that
builds it) → `src/garns/resolve.py` or `src/garns/resolve_read.py` →
`src/garns/ir.py` (node + membership in `Expr` / `Operand` / `ShowTerm`) →
**every** consumer visitor (`src/garns/footprint.py`,
`src/garns/lower_sqlite.py::_Lowerer` and `::_ShowLowerer`) →
`tests/test_parse.py`, `tests/test_resolve.py` → `EXTENDING_GARNS.md`
`## Playbook: add a construct`.

**Add a semantic rule or refusal** — `src/garns/refuse.py` (pick the stage from
`STAGES`) → the owning resolver: `resolve.py` for declarations, worlds,
deployments; `resolve_read.py` for reads; `storage.py` for bindings;
`engine.py` / `capture.py` for runtime → `DIAGNOSTICS.md` `## Catalogue` →
`corpus/conformance/refusals/` + its `expected.json` → `tools/make_mutants.py`
(`NEW_MUTANTS` or `scenario()`) → a case in the matching `tests/test_*.py`.

**Change SQL lowering** — `src/garns/lower_sqlite.py` (`Plan`, `ChildPlan`,
`_Frame`, `_Lowerer`, `_ShowLowerer`, `lower_read`, `lower_ddl`) →
`src/garns/engine.py::Engine.execute_plan` (it consumes `key_columns`,
`columns`, `children`, `total_sql`) → `src/garns/surfaces.py` →
`tools/generate_all.py` → `tests/test_static_dynamic.py`,
`tests/test_generate.py` → G4/G9/G11 in `tools/check.py`.

**Change live routing or footprints** — `src/garns/footprint.py`
(`FootprintDeriver`, `derive_footprint`) → `src/garns/live.py`
(`LiveEngine.routing_keys`, `.match`, `Instance.refresh`, `Registry`) →
`src/garns/generate.py::routing_descriptor` (it must agree with
`routing_keys`) → `tests/test_live.py` → `tools/check.py::g7`.

**Change ledger or capture** — `src/garns/engine.py` (`LedgerValidator`,
`Transaction`, `Delta`) → `src/garns/capture.py` (`check_coverage`, `acquire`)
→ `src/garns/lower_sqlite.py::lower_capture_ddl` → `src/garns/storage.py`
(`CaptureMapping` and the `capture` branch of `bind_world`) →
`tests/test_capture_ledger.py` → `tools/check.py::g8`.

**Change evolution or migration** — `src/garns/evolution.py` (`classify`,
`migrate`, `open_store`, `check_window`) → `corpus/worlds/evolution/g1..g5`
and their `storage-PRACTICE.json` bindings → the `ship`/`load` scenario mutants
in `tools/make_mutants.py` → `tests/test_evolution.py` → `tools/check.py::g6`.

**Add a generated target** — `src/garns/resolve.py::TARGETS` →
`src/garns/surfaces.py` → `src/garns/generate.py` → `tools/check.py::g11` →
`EXTENDING_GARNS.md` `## Playbook: add a generated target`.

**Add an engine backend** — `src/garns/resolve.py:27-28` (`ENGINES`,
`LOWERED_ENGINES`) → `src/garns/resolve.py::Resolver.resolve_deployment`
(`:1292-1299`) → `src/garns/lower_sqlite.py` (every SQLite assumption) →
`src/garns/engine.py::Store` → `src/garns/capture.py` and
`src/garns/evolution.py` (both read `PRAGMA table_info`) →
`EXTENDING_GARNS.md` `## Playbook: add an engine backend`. Read that playbook
**before** touching `LOWERED_ENGINES`.

**Add a corpus world or binding** — `tools/storage_template.py` (emit a
complete binding) → `src/garns/storage.py::bind_world` (the exhaustive checks
your document must satisfy) → place sources and `storage-<WORLD>.json` under
`corpus/conformance/worlds/<world>/` → register the world in
`tools/generate_all.py::WORLDS` and `tools/check.py:51-53` →
`tests/support.py::discovered_worlds` picks it up from the binding filename
automatically.

**Add a mutant** — `tools/make_mutants.py`: a single-file case goes in
`NEW_MUTANTS` (or `SEED_MUTANTS` with edits); a staged case goes through
`scenario(name, stage, code, steps)` → `src/garns/mutants.py::observe_scenario`
for the admitted step vocabulary (`resolve`, `bind`, `lower`, `generate`,
`ship`, `sql`, `open`, `migrate`, `classify`, `window`, `write`, `capture`,
`execute`, `subscribe`) → regenerate the corpus → `tests/test_mutants.py`.

**Investigate a failing gate** — `gate-report.json`
(`gates[].checks[].label` / `.detail`, `gates[].commands[].exit` and output
tails) → the failing check in `tools/check.py` → the module it exercises →
`TESTING.md` `## Commands` for a narrower re-run. A crashed runner is recorded
as a failed check, never a skipped gate (`tools/check.py:709-710`).

**Update docs** — this file → `EXTENDING_GARNS.md` → the document that owns the
fact (see `## Purpose and how to use this guide`) → re-verify every cited
`path:line` against the current source.

## Architectural invariants

Break one of these and the build stops being Garns. Each is enforced, not
merely intended.

| invariant | enforced by |
|---|---|
| **One meaning / single IR.** Source resolves once into `ir.Program`; DDL, SQL, footprints, bindings, routing, ledger, capture, migration and surfaces are consumers. No second table of source facts. | `src/garns/ir.py`; G4 "one lowering entry point serves execute() and live refresh" (`tools/check.py:217`) |
| **Qualified identities everywhere.** `module.Name`, `module.Carrier.link`, `module.Carrier.intent`. Bare names exist only inside `Resolver.lookup`. | `src/garns/engine.py:211` (`READ_UNKNOWN`, "reads are selected by qualified name"); measured: `execute("open_orders")` → `READ_UNKNOWN [runtime]`, `mint("Order", …)` → `LEDGER_CARRIER_UNKNOWN [runtime]` |
| **Explicit storage binding; no naming guesses.** Every table, identity, scalar column, link column, family discriminator, engine table and changelog field is read from the binding document. | `src/garns/storage.py::bind_world` (17 `STORAGE_*` codes); G10 scans (`tools/check.py:584-600`) |
| **One lowering for both nouns.** `lower_read` produces the same `Plan` type for a query and a question. | `tools/check.py:213-215`; measured: both `sales_static.open_orders_once` and `sales.open_orders` yield `key_columns ('$k0',)`, `columns ('identity','customer','total')` |
| **Queries derive no live artifacts.** A query has no `live` item by construction (`grammar/garns.lark::query_item`) and produces SQL + surfaces only. | `src/garns/generate.py:76-80`; measured on SALES: three `queries/*.sql`, and `.footprint.json`/`.binding.json`/`.routing.json` only for `sales.open_orders` |
| **Questions derive complete footprints or refuse.** Static-only nodes raise `QUESTION_NOT_FOOTPRINTABLE`; a query raises `QUERY_NOT_LIVE`. | `src/garns/footprint.py::_static_only`, `:217-219` |
| **Refusal before effect.** The first refusal wins and every effectful entry point is downstream of a resolved `Program`. | `src/garns/refuse.py::STAGES`; `COMPILER_PIPELINE.md` `## Earliest pre-effect validation boundary` |
| **Exhaustive visitors.** A visitor without a handler raises `TypeError`; `check_exhaustive` names the gap. | `src/garns/visit.py:34-50`; measured: `FootprintDeriver` 26 handlers (11 expr + 9 operand + 6 show), `_Lowerer` 20, `_ShowLowerer` 6, all with **no** missing nodes |
| **Measured instrumentation.** `Stats.probes`, `.candidates`, `.listener_scans` increment where the operation happens; `Registry.__iter__` is the only way to visit all instances and counts each visit. | `src/garns/live.py:81-84`, `:206-210`; G7 forces a deliberate scan first (`tools/check.py:437`) before measuring zero (`:453`) |
| **No corpus-vocabulary, expected-answer, filename or comment detectors.** Decode codes come from the LALR value stack, the expected-terminal set and the failing token. | `src/garns/parse.py:51-110`; G9 invariance under rename + comment strip + manifest corruption (`tools/check.py:555-577`) |
| **Deterministic byte-identical generation.** Delete `generated/`, regenerate, get the same bytes. | `src/garns/generate.py`; measured: all 8 worlds' fresh `tree_digest` equal both the committed tree and `generated/INDEX.json` |
| **Reserved `_` parameter names.** `:_scope`, `:_clock`, `:_parents` are engine-owned; a given starting with `_` refuses `GIVEN_NAME_RESERVED` in the resolver *and* in `lower_read`. | `src/garns/resolve_read.py:48-49`, `src/garns/lower_sqlite.py:528-530` |
| **Hidden `$k` keys.** Result identity travels in `$k0…$kN` columns absent from `Plan.columns`. | `src/garns/lower_sqlite.py:543-554`; measured on `sales.open_orders`: `"$k0"` in the SQL, not in `Plan.columns` |
| **PostgreSQL is recognised but refused.** `ENGINES = {postgres, sqlite}`; `LOWERED_ENGINES = {sqlite}`. | `src/garns/resolve.py:27-28`, `::resolve_deployment` `:1292-1299`; measured: `engine postgres` → `ENGINE_LOWERING_ABSENT [validate] at 24:10`, `engine oracle` → `ENGINE_UNKNOWN [validate]` |

## Frozen inputs and generated-output boundaries

| artifact | rule |
|---|---|
| `grammar/garns.lark` | **Frozen in v9-5.** Byte-identical to the lane grammar (sha256 `3a453f5a…d4e8`, recorded in `the historical v9-5 lane/FROZEN.json`). Grammar defects are reported to the operator, not repaired. G0 compares lane copy, build copy and the recorded digest three ways. |
| `corpus/conformance/static/reporting.garns`, `corpus/conformance/dynamic/open_orders.garns` | Frozen copies; G0 compares raw bytes against the lane originals. |
| `corpus/worlds/*.garns`, `corpus/worlds/MIGRATION.md` | Produced by `tools/migrate_seed_corpus.py` from the frozen seed. Edit the tool's `EDITS` list, not the copies; every edit carries its reason into `MIGRATION.md`. |
| `corpus/worlds/**/storage-*.json`, `corpus/conformance/worlds/**/storage-*.json` | **Authored** inputs. The migration tool deliberately leaves them alone (`tools/migrate_seed_corpus.py:86-90`). |
| `corpus/mutants/**` including `expected.json` | Produced by `tools/make_mutants.py`, which **deletes the tree first**. `expected.json` is an assertion, never a detector input (`corpus/mutants/expected.json` `note`). |
| `generated/**` and `generated/INDEX.json` | Produced by `tools/generate_all.py`, which deletes `generated/` first. G9 compares the committed trees with an independent fresh generation (`tools/check.py:534-547`). |
| `gate-report.json` | Written by `tools/check.py` at the end of every run (`tools/check.py:713-722`); exit code is `0 if all_pass else 1`. |

Product-baseline hygiene: `tools/check_product.py` refuses `__pycache__`, `.pyc`
and `.pyo` anywhere in the repository. Always run Python with
`PYTHONDONTWRITEBYTECODE=1` (and `-B`); `tools/check.py` additionally purges
caches before and after its own run.

## Common traps and forbidden shortcuts

Each line names the trap, then what actually catches it.

- **Pluralising a carrier name into a table name.** Tables come from `relations[<qid>].table`. G10 scans `src/**` for pluralisation helpers (`tools/check.py:585`).
- **Appending `_id` to a link name, or assuming an `id` identity column.** Link columns come from `relations[<qid>].links[<link qid>]` via `WorldIR::link_column_of`; identity from `relations[<qid>].identity`. G10 scans for both (`tools/check.py:586`, `:603`).
- **Adding a `scope_id` column.** Scope is a *link path* (`Program.scope_paths`), woven into a `:_scope` predicate by `lower_sqlite::scope_predicate`. Measured: `pantry.Jar → ('pantry.Jar.shelf', 'pantry.Shelf.keeper')`. G10 scans for the token (`tools/check.py:587`).
- **First-item selection** (`worlds[0]`, `reads[0]`, "the only question"). Every public boundary takes a qualified name. G10 scans (`tools/check.py:588`).
- **Bare names at runtime.** `Engine.execute`, `tx.mint/change/delete`, `LiveEngine.subscribe` all refuse unqualified input.
- **Fallback SQL** when lowering cannot proceed. There is none: `lower_sqlite` refuses (`LOWER_*`, `NESTED_SHOW_PATH`, `QUANTIFIER_MULTIPLE_MANY`). G10 scans for the word (`tools/check.py:590`).
- **Constant counters.** Never write `listener_scans = 0` or return a fixed measure. G10 asserts the increments exist and that no reset hides in source (`tools/check.py:607`).
- **Reading `expected.json` inside a detector.** Both manifests are assertions compared *after* an independent observation (`tools/check.py:163-167`, `:549-552`). `src/garns/mutants.py` never opens them.
- **Running `tools/check.py`, `tools/generate_all.py`, `tools/make_mutants.py` or `tools/migrate_seed_corpus.py` casually.** The last three delete and rewrite their output trees; the first rewrites `gate-report.json`. Read `gate-report.json`, `generated/INDEX.json` and the corpus instead when you only need to know the current state.
- **Leaving `__pycache__` behind.** The product baseline check fails on it; a bare `check_product.py` run right after the unit suite will fail until caches are purged.
- **Positional `Ctx` construction in `resolve_read.py`.** Two call sites build `Ctx` positionally (`src/garns/resolve_read.py:346`, `:737`); every other site uses `Ctx(**{**ctx.__dict__, …})`. Adding a field in the middle of `Ctx` silently mis-assigns those two. Prefer the keyword form, and if you add a field, append it last and fix both sites.
- **Forgetting a visitor handler.** Adding an IR node without updating `FootprintDeriver`, `_Lowerer` or `_ShowLowerer` fails `check_exhaustive` in `tests/test_resolve.py` and G10 (`tools/check.py:611-618`).
- **Editing a generated file by hand.** `generated/**` and `corpus/mutants/**` are rewritten wholesale; hand edits vanish and break G9 byte identity.
- **Changing an ordering tiebreak.** `order_clause(..., with_tiebreak=True)` appends subject identity (ungrouped, non-distinct) or the group keys; `rank` reuses the same order inside `ROW_NUMBER()`. Changing it changes every generated `.sql`, the Rust parity rows and every recorded live batch.
- **Assuming `Instant` is a date/time type.** `sql_storage_type` maps `integer`/`boolean`/`instant` → `INTEGER`, `decimal` → `REAL`, `opaque`/`vector` → `BLOB`, else `TEXT` (`src/garns/types.py:106-114`). There is no temporal type in the store.
- **Treating a recognised engine as available.** `postgres` parses and resolves as an engine name and then refuses; see `## Architectural invariants`.
- **Assuming verbs execute.** `alias`, `bulk`, `restricted`, `compound` resolve and validate but have no runtime and no generated surface (`LIMITATIONS.md`).

## Change-impact map

| when you change | inspect | regenerate | run |
|---|---|---|---|
| `grammar/garns.lark` *(frozen in v9-5)* | `src/garns/ast.py`, `src/garns/parse.py::_Builder`, both resolvers | `generated/`, `corpus/mutants/` | whole suite + `tools/check.py` (G0 will fail until the lane grammar and `FROZEN.json` agree) |
| `src/garns/ast.py` | `src/garns/parse.py::_Builder`, `src/garns/resolve*.py` | — | `tests/test_parse.py`, `tests/test_resolve.py` |
| `src/garns/resolve.py` | reference-map `ref()` calls for any new identifier occurrence; `metamorphic.RENAMED_ROLES` | `generated/` (IR digest changes) | `tests/test_resolve.py`, `tests/test_metamorphic.py`, G1/G5/G6 |
| `src/garns/resolve_read.py` | `Ctx` field order, `check_compositions`, `check_grouped` | `generated/` | `tests/test_static_dynamic.py`, G2/G3/G4 |
| `src/garns/ir.py` | **every** visitor (`footprint.py`, `lower_sqlite.py`), `visit.py` node unions, `canonical()` field skips, `metamorphic._resort` | `generated/` (`ir.json`, `manifest.json`, all digests) | `tests/test_resolve.py` exhaustiveness cases, G9, G10 |
| `src/garns/types.py` | `lower_sqlite.lower_ddl` column types, `engine.LedgerValidator.check_value`, `evolution.migrate` | `generated/schema.sql` | `tests/test_capture_ledger.py`, G1/G8 |
| `src/garns/calls.py` | `resolve_read.call`, `lower_sqlite::_Lowerer.visit_Call` | `generated/queries/*.sql` | `tests/test_static_dynamic.py`, mutants `CALL_*` |
| `src/garns/storage.py` | every `corpus/**/storage-*.json`, `tools/storage_template.py`, `metamorphic.binding_document` consumers | `generated/` | `tests/test_resolve.py`, `tests/test_metamorphic.py`, G5, storage scenario mutants |
| `src/garns/lower_sqlite.py` | `engine.execute_plan`, `surfaces.py`, `capture.lower_capture_ddl` callers, `evolution.migrate` | `generated/` (SQL, surfaces, `schema.sql`) | `tests/test_static_dynamic.py`, `tests/test_generate.py`, G4, G9, **G11 Rust parity** |
| `src/garns/engine.py` | `live.py` (it calls `engine.execute`), `capture.py` (shares `LedgerValidator`, `Delta`) | — | `tests/test_live.py`, `tests/test_capture_ledger.py`, G7/G8 |
| `src/garns/live.py` | `generate.routing_descriptor` (must agree with `LiveEngine.routing_keys`) | `generated/questions/*.routing.json` | `tests/test_live.py`, G7 |
| `src/garns/footprint.py` | `live.LiveEngine.footprint`, `generate.py` | `generated/questions/*.footprint.json` | `tests/test_static_dynamic.py`, `tests/test_live.py`, G3/G7 |
| `src/garns/capture.py` | `lower_capture_ddl`, `storage.CaptureMapping` | `generated/LEDGERHOUSE/schema.sql` | `tests/test_capture_ledger.py`, G8 |
| `src/garns/evolution.py` | `corpus/worlds/evolution/g1..g5`, scenario mutants | — | `tests/test_evolution.py`, G6 |
| `src/garns/generate.py`, `src/garns/surfaces.py`, `src/garns_rust/sqlite.rs` | `tools/generate_all.py`, `tools/check.py::g11` | `generated/` (all worlds) | `tests/test_generate.py`, G9, G11 |
| `src/garns/cli.py` | `INTEGRATION.md` examples | — | manual `-m garns.cli` smoke; no gate covers the CLI |
| `tools/check.py` | `gate-report.json` schema consumers, `REPORT.md` line citations | `gate-report.json` | `tools/check.py` itself |
| `corpus/worlds/**`, `corpus/conformance/worlds/**` | `tools/generate_all.py::WORLDS`, `tools/check.py:51-53`, `tests/support.py::discovered_worlds` | `generated/` | G1, G9, whole suite |
| `corpus/mutants/**` | `tools/make_mutants.py` (the real source), `tests/test_mutants.py` | `corpus/mutants/` | G9 |
| `tests/**` | nothing downstream | — | the suite; note `tools/check.py` does **not** invoke it |

## Definition of done for implementation changes

Work through in order; each line is a command or an inspection, not an opinion.

1. **Unit suite green.** From the build root:
   `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m unittest discover -s tests -t .` → `Ran 103 tests … OK`, exit 0.
2. **Regenerate `generated/` when IR, lowering, storage or surfaces changed.**
   `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/generate_all.py`, then confirm G9 reports byte identity (delete/regenerate must reproduce the committed trees and `generated/INDEX.json` digests exactly).
3. **Regenerate mutants when expectations changed.** `tools/make_mutants.py`, then confirm G9's "N mutants execute real stages and match authored expectations" is 100 % with zero mismatches (currently 168 cases: 131 single-file + 37 scenarios, 124 distinct codes, stages `accepted/decode/validate/ship/load/runtime`).
4. **Full gate run.** `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py` → twelve `PASS` lines and `ALL PASS`, exit 0, with `gate-report.json` rewritten. Current baseline: 128 checks, `all_pass: true`.
5. **G10 forbidden-pattern scan clean.** No pluralisation, `_id`, `scope_id`, first-item selection, corpus vocabulary, fallback SQL, numbered-case dispatch or filename detector in `src/**` (`tools/check.py:584-600`); qualified-only public boundaries and live counters still asserted (`:605`, `:607`).
6. **Exhaustiveness holds.** `check_exhaustive` empty for `FootprintDeriver`, `_Lowerer` and `_ShowLowerer`; a phantom node still reported by both (`tools/check.py:611-618`).
7. **No caches.** `find . -name __pycache__ -type d` is empty, then the product baseline check passes: `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_product.py` → ends `PASS W0 product baseline`, exit 0.
8. **Pinned inputs untouched.** Grammar digest unchanged and the two `corpus/conformance/static|dynamic` sources match `BASELINE.json`.
9. **Docs updated.** The document that owns the changed fact (see `## Purpose and how to use this guide`), plus this guide's `## Change-impact map` and `## Architectural invariants` if the boundary moved. Re-verify every `path:line` you cite — several citations in the build's own `REPORT.md` have already drifted from the current line numbers.
10. **Evidence written in `REPAIR.md`/`REPORT.md` style.** Name the command, its exit code, and the evidence path (`gate-report.json` check label, `corpus/...` fixture, `path:line`). A claimed pass without an executable path does not count (`brief/04-ExitMatrix.md`).
