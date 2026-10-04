# Garns v9-5 — build B2

> Historical selected-build reference. Use the repository `README.md` and
> `docs/TESTING.md` for current v9-6 W0 commands and paths.

One implementation of the frozen v9-5 language. Source is parsed against `grammar/garns.lark`
(byte-identical to the lane's frozen grammar, sha256 `3a453f5a…d4e8`) and resolved **once** into a typed,
module-qualified IR (`src/garns/ir.py`). Storage DDL, SQL, footprints, bindings, routing, ledger records,
capture descriptors, migrations and target surfaces are consumers of that one IR through exhaustive
visitors; none re-derives a source fact, and none branches on a schema, corpus or file name.

Every physical name — table, identity column, scalar column, link column, family discriminator, engine
table, changelog table and changelog field — comes from an explicit per-world storage binding document. A
missing or ambiguous mapping refuses; nothing is guessed.

---

## 1. Layout

```
build/B2/
├── README.md, REPORT.md             this document; the build's evidence report
├── gate-report.json                 the machine-readable gate report tools/check.py writes
├── grammar/garns.lark               the frozen grammar, copied byte-for-byte
├── src/garns/
│   ├── refuse.py, types.py, calls.py   Refusal + stage order; type universe; static call registry
│   ├── ast.py, parse.py                located source nodes; LALR driver + decode classification
│   ├── resolve.py, resolve_read.py     names/worlds/verbs; paths, typed expressions, read shapes
│   ├── ir.py, visit.py                 the typed qualified IR + canonical encoding; exhaustive visitors
│   ├── storage.py                      binding schema, bind_world, WorldIR, binding_document
│   ├── lower_sqlite.py                 the single relational/SQL lowering + DDL + capture DDL
│   ├── engine.py                       Store.ship, Engine.execute, Transaction, LedgerValidator
│   ├── live.py, footprint.py           partitioned routing, refresh, fold; footprint derivation
│   ├── capture.py, evolution.py        changelog acquisition; classify / migrate / open_store
│   ├── generate.py, surfaces.py        deterministic artifacts; Python and Rust surfaces
│   ├── metamorphic.py, mutants.py      reference-map renaming; mutant observation
│   └── cli.py                          resolve / generate / ddl / execute
├── src/garns_rust/sqlite.rs         raw SQLite FFI used by generated Rust runners (no crates)
├── tests/                           unit suite over the production pipeline (unittest)
├── tools/
│   ├── check.py                     runs G0–G11 and writes gate-report.json
│   ├── storage_template.py          authoring aid: emit a binding (the compiler never calls it)
│   └── migrate_seed_corpus.py, make_mutants.py   regenerate corpus/worlds and corpus/mutants (destructive)
├── corpus/
│   ├── conformance/static|dynamic/  the lane's frozen conformance sources, byte-identical
│   ├── conformance/worlds/          those sources in worlds + the SALES static twins + LEDGERHOUSE
│   │                                (a private captured schema with a two-hop scope path)
│   ├── conformance/refusals/        11 refusal sources + expected.json (assertions, not detectors)
│   ├── metamorphic/collision/       ALPHA and BETA: identical local names in two modules
│   ├── mutants/                     129 single-file mutants + 36 scenarios + expected.json
│   └── worlds/                      migrated seed worlds (practice, everbility, vaultwarden, appflowy,
│                                    evolution/g1..g5) + MIGRATION.md + storage-*.json
└── generated/                       committed generation for 8 worlds + INDEX.json (produced by tools/generate_all.py)
```

`corpus/` holds 249 `.garns` files and 8 storage bindings; `generated/` holds 173 files across
`APPFLOWY`, `APPFLOWY_VEC`, `EVERBILITY`, `LEDGERHOUSE`, `PRACTICE`, `REPORTING`, `SALES`,
`VAULTWARDEN`.

---

## 2. Pipeline

### 2.1 Parse — `parse.py`

`parser()` builds one `Lark(grammar_text(), parser="lalr", propagate_positions=True,
maybe_placeholders=False, keep_all_tokens=True)` over the frozen grammar file. `_Builder` turns the tree
into `ast.py` nodes; every identifier occurrence becomes its own `Name` with a `Loc`, which is what makes
the reference map — and therefore the metamorphic rename — possible.

Decode refusals are classified from **parser state only**: the value stack, the expected-terminal set, and
the token at the failure point. No text pattern, filename, comment or marker participates. `classify_decode`
decides in order:

| code | condition |
|---|---|
| `SOURCE_TRUNCATED` | `UnexpectedEOF`, or the offending token is `$END` |
| `MEANS_REQUIRED` | only `STRING` was expected and the preceding token is not one that takes a non-meaning string (`pattern`, `breaking`, `path`, `default`) |
| `TYPE_SHAPE_INVALID` | the last token opens a type position (`:`, `optional`, `list_of`, `of`) and only `NAME`/`optional`/`list_of` were expected |
| `EXPR_NOT_ADMITTED` | inside an open body, an expression keyword (`where`, `having`, `invariant`) opened the current item and no later item closed |
| `DECL_SHAPE_INVALID` | inside an open body otherwise, or a malformed top-level declaration |
| `SOURCE_NOT_GARNS` | the failure is at top level with nothing but completed trees on the stack |

### 2.2 Resolve — `resolve.py`, `resolve_read.py`

`Resolver.run()` runs ordered phases: collect declarations → imports and module cycles → intents and
newtypes → carriers (trait-composition order, then members, then inverse edges, then link-target and
mint-cycle checks) → reads and invariants → verbs and evolution statements → tombstones → worlds,
capabilities and deployments → homeless-intent and unused-import closure. Every identity is qualified
(`module.Name`, `module.Carrier.link`, `module.Carrier.intent_local_name`); bare names exist only inside
`lookup()`. Alongside the IR the resolver records a **reference map** — `Reference(file, line, column, text,
identity, role)` per bound identifier occurrence — which `metamorphic.py` replays to rename sources without
touching compiler code.

`resolve_read.py` resolves both nouns into the same expression IR. Paths walk resolved edges only: a link
becomes a forward `LinkStep`, an inverse name a reverse `LinkStep` (`many` unless the source link is the
carrier's sole key), ending in a `UseTerminal`, `LinkTerminal`, `IdentityTerminal` or `KindTerminal`. The
dynamic algebra is the closed subset; the static algebra adds arithmetic, aggregates, `distinct`, `having`
and `call`.

### 2.3 Storage binding — `storage.py`

One JSON document per world, schema `garns-v9-5/storage-binding/1`:

```json
{"schema": "garns-v9-5/storage-binding/1", "world": "LEDGERHOUSE",
 "engine": {"ledger": "lh_journal", "generations": "lh_epochs", "revisions": "lh_ticks"},
 "relations": {"pantry.Jar": {"table": "jar", "identity": "jar_no",
    "columns": {"pantry.Jar.jar_label": "lbl", "pantry.Jar.grams": "mass_g"},
    "links": {"pantry.Jar.shelf": "on_shelf"},
    "kind": "<family discriminator column; families only>"}},
 "capture": {"pantry.Jar": {"table": "jar_trail", "fields": {
    "seq": "trail_seq", "op": "verb", "revision": "tick", "identity": "jar_ref",
    "columns": {"pantry.Jar.grams": "mass_v"}, "links": {"pantry.Jar.shelf": "on_shelf_v"}}}}}
```

`bind_world(program, world_name, path)` selects the world explicitly and checks the document exhaustively
before anything is lowered: every storable carrier of the world is mapped; every use key and link key of
that carrier — including the member-qualified keys a family member adds — has a column; every physical name
is a plain identifier; tables and columns collide with nothing, including the engine tables; `kind` is
admitted only for families; `capture` is required exactly when the world declares `writers
external_captured`. Its refusal codes are the `STORAGE_*` family plus `WORLD_UNKNOWN` and
`WRITER_CAPTURE_INCOMPLETE` (§3).

`binding_document(program, world, names)` builds such a document from a naming callback. It exists for
authoring (`tools/storage_template.py`) and for the metamorphic harness; **the compiler never calls it** —
`bind_world` only ever reads a document from disk.

### 2.4 Lowering — `lower_sqlite.py`

`lower_read(world, read)` is the single entry point and produces one `Plan` for both nouns (`sql`, `params`,
`key_columns`, `columns`, `children`, `total_sql`, `scoped`, `uses_clock`, `shape`, `live_bound`).
`Engine.execute` and live refresh both go through it; there is no second query engine.

- **Hidden key columns.** Result identity travels in `$k`-prefixed columns absent from
  `Plan.columns`: `$k0` = subject identity for collections and windows; one `$k0…$kN` per group
  key when grouped; for `distinct` the shown columns are the key. Nested children add `$parent`
  and their own `$k0`.
- **Reserved parameters.** `:_scope`, `:_clock`, `:_parents` are engine-owned; a given whose
  name starts with `_` refuses (`GIVEN_NAME_RESERVED`) in both the resolver and `lower_read`.
- **Joins from edges only.** A forward step becomes
  `LEFT JOIN target AS jN ON jN.<identity> = prev.<link column>`; an inverse step starts a
  correlated subquery (`EXISTS`/`NOT EXISTS` for `some`/`every`, a scalar subquery for
  `count(…)`/`max(…)`/`min(…)`). Nothing inspects a name. `scope_predicate` walks the resolved
  scope path (a tuple of link qids) recursively to the root against `:_scope`, nesting
  `IN (SELECT identity FROM parent WHERE …)` for multi-hop paths.
- **Deterministic tiebreak.** After the declared `order` terms the plan appends `subject
  identity ASC` for ungrouped non-distinct reads, or the group keys `ASC` when grouped (distinct
  adds nothing); `rank` uses the same order plus tiebreak inside `ROW_NUMBER() OVER (…)`. Nested
  children order by their carrier's `order`-flagged uses then identity; `last N` wraps them in a
  descending `ROW_NUMBER() OVER (PARTITION BY parent …)`.
- **Base predicates.** Family-member discriminator, `archived_by IS NULL` unless
  `including_archived`, and the scope predicate.
- **DDL.** One `CREATE TABLE` per storable carrier (identity `INTEGER PRIMARY KEY`, `NOT NULL`
  where required, literal defaults, `CHECK` membership for closed sets, `UNIQUE` over key columns,
  the family `kind` column with its member `CHECK`), a `FOREIGN KEY … ON DELETE
  RESTRICT|CASCADE|SET NULL` only when enforcement is not `unenforced`, plus the three engine
  tables.

### 2.5 Engine — `engine.py`

`Store.ship()` runs the DDL as one script and inserts the generation row (`ordinal`, `ir_digest`,
`storage_digest`, `shipped_at_revision`); `PRAGMA foreign_keys = ON` is set on connect.
`Engine.transaction(writer, transaction_id)` yields a `Transaction` that, on entry, validates the writer
against the world (`governed`, or the declared `writer_source`) and the transaction id
(`^[A-Za-z0-9_-]{1,64}$`) and opens `BEGIN`. `mint` / `change` / `delete` each run **typed pre-effect ledger
validation** through `LedgerValidator` — carrier known and not an abstract family, field a real use or link
of that carrier (a member name may denote a family field), value of the right type class and closed-set
member, scope identity resolvable in the scope root's table — before any statement is issued; invariants are
re-evaluated as SQL against the written row. On normal exit the transaction inserts the revision row and one
ledger row per delta, commits, and only then notifies listeners; on an exception it rolls back, so a
rolled-back transaction produces no revision, no ledger row and no batch. Scope keys come from
`scope_key_of`, which follows the carrier's resolved scope path through the store (reading intermediate rows
for multi-hop paths) to a root identity; deltas carry `scope_before` and `scope_after`.
`Engine.execute(read_qid, params, scope, capabilities, clock)` binds strictly — undeclared →
`PARAM_UNKNOWN`, missing required → `PARAM_REQUIRED`, wrong type → `PARAM_TYPE`, `list_of` givens
JSON-encoded for `json_each`, scoped plan without a scope → `SCOPE_REQUIRED`, `unscoped C` without
capability `C` → `CAPABILITY_REQUIRED` — and addresses reads by qualified name only.

### 2.6 Live — `live.py`

`LiveEngine` registers as an engine listener. Instances are indexed by `(partition, carrier, field)`, where
`partition` is `scope:<identity>` when the atom's carrier has a scope path in a scoped world and `global`
otherwise; unscoped instances additionally register under `global` and `*`. `match(deltas)` probes only the
keys a delta can touch — its partitions (`scope_before`, `scope_after`, plus `*`), its carrier and that
carrier's family, and its changed fields plus `*` for inserts and deletes. Every probe increments
`Stats.probes`; every id returned increments `Stats.candidates`. The routing path never iterates the
registry, so `Stats.listener_scans` stays at zero by construction — and that counter is genuinely live,
because `Registry.__iter__` is the only way to visit all instances and it increments the same counter.
`Instance.refresh` re-executes the shared plan, diffs the keyed state and emits a `Batch(instance, base_seq,
seq, revision, changes)` of `upsert`/`delete` changes — or `None` when nothing changed, so a result-neutral
routed write emits no batch. A refresh whose row count exceeds `live bounded N` refuses with
`LIVE_BOUND_EXCEEDED`. `fold(initial, keys, batches)` replays batches onto the initial keyed state and is
what fold-equivalence compares against a one-shot recomputation.

### 2.7 Footprints — `footprint.py`

`derive_footprint(world, read)` refuses for a query (`QUERY_NOT_LIVE`) and otherwise walks the question IR
recursively through an exhaustive visitor, collecting `Atom(carrier, field)` where `field` is a use qid, a
link qid, or `"*"` for structural change. It covers subject structure, the archived-by use, predicate paths
(both ends of each step: the link on its owner, the structure of the reached carrier), projections including
nested shows and their child's `order`-flagged uses, order keys, group keys, the scope-path links, and —
through `Within` — the whole inner question, recorded in `composes` with a cycle refusal. Static-only nodes
refuse with `QUESTION_NOT_FOOTPRINTABLE` rather than being approximated: `ClockRef`, `Arith`, `Negate`,
`StaticAggregate`, `Call`, `Truth`, `ShowScalar`, `having`, `distinct`.

### 2.8 Capture — `capture.py`

For `writers external_captured`, `lower_capture_ddl` emits one changelog table per relation plus three
**declared triggers** (`AFTER INSERT`, `AFTER UPDATE`, `AFTER DELETE`) using the mapped names; the update
trigger writes a `before` row from `OLD` and then an `update` row from `NEW`, so every update carries its
before-image. Coverage is checked twice: at **bind** time the binding must map every field of every relation
(`WRITER_CAPTURE_INCOMPLETE`, stage `validate`); at **load** time `check_coverage()` reads `PRAGMA
table_info` on the real changelog tables and refuses if a declared field is missing (same code, stage
`load`) before any effect — those `PRAGMA` counts are also the measured coverage denominators.
`acquire(transaction_id)` reads rows whose revision column is still null, orders each relation by its own
`seq` and merges by `seq` (ties broken by relation order, i.e. carrier qid, since each changelog has its own
sequence), builds typed deltas validated by the same `LedgerValidator`, writes one revision plus its ledger
rows, stamps the consumed changelog rows with that revision, and notifies live listeners. An `update`
without its buffered before-image refuses (`CAPTURE_SEQUENCE_INVALID`).

### 2.9 Evolution — `evolution.py`

`classify(before, after, history, retention)` produces `Event`s over eighteen kinds — `intent_renamed`,
`intent_relocated`, `meaning_delta`, `retype`, `add_intent`, `retire_intent`, `restore_intent`, `move_home`,
`add_carrier`, `retire_carrier`, `lifecycle`, `carry_added`, `use_added`, `use_removed`, `tighten`,
`link_added`, `link_policy`, `link_removed` — and a `compat` of `additive` / `deprecating` / `breaking`.
Continuity is by qualified identity: `renamed_from` carries an identity (a different module makes it a
relocation); an undeclared move is a retirement plus a mint and demands a tombstone. `migrate(conn, before,
after, classification, generation)` executes against the real store — `ALTER TABLE … RENAME COLUMN` for
continued identities, `ADD COLUMN` plus a repair `UPDATE` for new required uses, a
`<table>__quarantine_<generation>` table for quarantined retirements, then `DROP COLUMN` — and records the
new generation row. `open_store(conn, world, deployment)` refuses `STORE_UNSHIPPED` (no generation table or
row), `STORE_BEHIND` (recorded IR/storage digests differ from the source) and `STORE_DRIFT` (a table lacks a
declared column, or carries an undeclared one); `check_window` refuses `GENERATION_OUTSIDE_WINDOW`.

### 2.10 Generation and Rust parity — `generate.py`, `surfaces.py`

`generate(world, out_dir)` deletes and rewrites the tree and returns path → sha256. Per world: `schema.sql`,
`ir.json` (canonical IR + world + storage + scope paths), `python/<qid with . → __>.py`, `rust/<…>.rs`,
`rust/main.rs`, `rust/sqlite.rs` (copied verbatim from `src/garns_rust/sqlite.rs`) and `manifest.json`. Per
read: `queries/<qid>.sql` **or** `questions/<qid>.sql`; **only** questions additionally get
`.footprint.json`, `.binding.json` and `.routing.json` — a query produces SQL and surfaces and nothing
live-derived. `tree_digest` is what the delete/regenerate check compares; `generated/INDEX.json` (schema
`garns-v9-5/generated-index/1`) lists each world's source, binding, file count and tree digest.

Each generated `rust/<read>.rs` is a constants module holding the lowered SQL unchanged, and `rust/main.rs`
matches the qualified read name to its SQL and calls `sqlite::run`, a raw `#[link(name = "sqlite3")]` FFI
shim with no crates that prints one JSON array per row of `[type_code, text]` cells using SQLite's own text
conversion, so Python and Rust encode identically. `tools/check.py` compiles that tree with `rustc -O -o
runner main.rs` and compares row for row against Python running the same SQL.

---

## 3. Language decisions the resolver enforces

A refusal carries a code, a stage (`decode`, `validate`, `lower`, `generate`, `ship`, `load`, `runtime`) and
a source position. The first refusal wins.

**decode (6)** — `SOURCE_NOT_GARNS`, `SOURCE_TRUNCATED`, `MEANS_REQUIRED`, `TYPE_SHAPE_INVALID`,
`EXPR_NOT_ADMITTED`, `DECL_SHAPE_INVALID`.

**validate**, grouped by what each group defends:

| group | codes |
|---|---|
| Modules / imports | `MODULE_DUPLICATED`, `MODULE_UNKNOWN`, `MODULE_CYCLE`, `IMPORT_UNKNOWN`, `IMPORT_SELF`, `IMPORT_NOT_OWNER`, `IMPORT_AMBIGUOUS`, `IMPORT_UNUSED`, `NAME_AMBIGUOUS`, `NAME_NOT_IMPORTED`, `QNAME_REQUIRED` |
| Identity | `ID_DUPLICATED`, `ID_RESERVED`, `TERM_RESERVED`, `TERM_UNKNOWN`, `CARRIER_UNKNOWN`, `TRAIT_UNKNOWN`, `READ_UNKNOWN`, `EXEMPT_UNKNOWN`, `INTENT_HOMELESS`, `RETIRE_REASON_REQUIRED` |
| Types / intents | `TYPE_UNKNOWN`, `NEWTYPE_SHAPE`, `INTENT_TYPE_SHAPE`, `INTENT_ITEM_REPEATED`, `INTENT_ITEM_CONFLICT`, `INTENT_REFINEMENT_TYPE`, `DIMENSION_NOT_POSITIVE`, `DIMENSION_NOT_VECTOR`, `DIMENSION_REQUIRED`, `LENGTH_RANGE_INVALID`, `CLOSED_SET_TYPE`, `CLOSED_SET_CONFLICT`, `CLOSED_SET_MEMBER_DUPLICATED`, `CLOSED_SET_MEMBER_UNKNOWN`, `DEFAULT_TYPE`, `REPAIR_TYPE`, `GIVEN_DEFAULT_TYPE` |
| Carriers / traits / members | `TRAIT_CYCLE`, `TRAIT_LIFECYCLE`, `CARRY_NOT_TRAIT`, `CARRY_REPEATED`, `TRAIT_POLICY_CONFLICT`, `TRAIT_WIDENED`, `USE_DUPLICATED`, `USE_FLAG_REPEATED`, `USE_FLAG_CONFLICT`, `STAMP_NOT_INSTANT`, `OPAQUE_POLICY`, `LIFECYCLE_REPEATED`, `ARCHIVED_BY_INVALID`, `ASSOCIATION_ARITY`, `ORDERED_WITHIN_NOT_EVENT`, `ORDERED_WITHIN_REPEATED`, `ORDERED_WITHIN_UNKNOWN`, `PRESET_CONFLICT`, `TIGHTEN_UNKNOWN`, `TIGHTEN_PATH_INVALID`, `MEMBER_OF_NON_FAMILY` |
| Links | `LINK_DUPLICATED`, `LINK_TO_TRAIT`, `LINK_CYCLE_UNMINTABLE`, `LINK_FLAG_REPEATED`, `LINK_FLAG_CONFLICT`, `LINK_ENFORCEMENT_REPEATED`, `LINK_ENFORCEMENT_CONFLICT`, `DETACH_NOT_OPTIONAL`, `INVERSE_DUPLICATED` |
| Reads — shape and window | `SHAPE_CONFLICT`, `PAGE_LIMIT_PAIR`, `PAGE_TYPE`, `WITH_TOTAL_WITHOUT_PAGE`, `FIRST_NOT_POSITIVE`, `LAST_NOT_POSITIVE`, `BY_NOT_GIVEN`, `BY_TYPE`, `READ_ITEM_REPEATED`, `READ_OF_TRAIT`, `INCLUDING_ARCHIVED_NOT_ARCHIVABLE`, `RANK_WITHOUT_ORDER`, `SHOW_ALIAS_REQUIRED`, `SHOW_COLUMN_DUPLICATED`, `SHOW_LITERAL`, `ORDER_BY_LITERAL`, `NESTED_SHOW_NOT_TO_MANY` |
| Reads — givens and paths | `GIVEN_DUPLICATED`, `GIVEN_UNKNOWN`, `GIVEN_UNUSED`, `GIVEN_NAME_RESERVED`, `GUARD_NOT_OPTIONAL_GIVEN`, `OPTIONAL_PARAM_UNGUARDED`, `PATH_THROUGH_SCALAR`, `TERM_TO_MANY_UNQUANTIFIED`, `QUANTIFIER_WITHOUT_TO_MANY`, `AGG_NOT_TO_MANY` |
| Reads — typing | `EXPR_TYPE`, `IS_NOT_LINK`, `IS_TYPE`, `IN_NOT_LIST`, `CONTAINS_NOT_TEXT`, `OPAQUE_COMPARED`, `AGGREGATE_MISUSED`, `HAVING_WITHOUT_GROUP`, `WITHIN_NOT_LINK` |
| Static calls | `CALL_UNKNOWN`, `CALL_VOLATILE`, `CALL_EFFECTFUL`, `CALL_ARITY`, `CALL_ARGUMENT_TYPE` |
| Query / question boundary | `QUESTION_LIVE_BOUND_REQUIRED`, `QUESTION_LIVE_BOUND_DUPLICATED`, `QUESTION_LIVE_BOUND_INVALID`, `QUESTION_NOT_FOOTPRINTABLE`, `QUESTION_CLOCK_NOT_A_TERM`, `QUESTION_INTENT_RETIRED`, `QUESTION_COMPOSE_STATIC`, `QUESTION_COMPOSE_PAGED`, `QUESTION_COMPOSE_UNSCOPED`, `QUESTION_COMPOSE_CYCLE`, `COMPOSE_INNER_GIVENS`, `COMPOSE_SUBJECT_MISMATCH`, `QUERY_NOT_LIVE` |
| Invariants | `INVARIANT_COMPOSES`, `INVARIANT_CLOCK` |
| Verbs | `ALIAS_NOT_DERIVED`, `VERB_ON_TRAIT`, `VERB_NOT_ADMITTED`, `FAMILY_MEMBER_MINT_ONLY`, `VERB_INPUT_ENGINE_OWNED`, `BULK_NOT_DERIVED_VERB`, `BULK_OVER_MISMATCH`, `BULK_OVER_PAGED`, `BULK_SET_UNKNOWN`, `BULK_SET_TYPE`, `BULK_PARAM_UNDECLARED`, `SET_ABSENT_REQUIRED`, `RESTRICTED_ACCEPTS_UNKNOWN`, `STEP_NAME_DUPLICATED`, `STEP_CYCLE`, `STEP_BIND_PATH`, `STEP_BIND_UNKNOWN`, `STEP_BIND_TYPE`, `STEP_REFERENCE_UNRESOLVED`, `EVOLUTION_STATEMENT_HOMELESS` |
| Worlds / scope / capabilities | `WORLD_DUPLICATED`, `WORLD_UNKNOWN`, `WORLD_ITEM_REPEATED`, `WORLD_MODULES_REQUIRED`, `WORLD_DURABILITY_REQUIRED`, `WORLD_WRITERS_REQUIRED`, `WORLD_GENERATED_REQUIRED`, `WORLD_SCOPE_REQUIRED`, `WORLD_REQUIRES_REQUIRED`, `QUARANTINE_RETENTION_REQUIRED`, `QUARANTINE_RETENTION_INVALID`, `WORLD_MODULE_REPEATED`, `WORLD_MODULE_COLLISION`, `MODULE_NOT_LISTED`, `WORLD_TARGET_REPEATED`, `TARGET_UNKNOWN`, `DURABILITY_UNKNOWN`, `WRITER_CLASS_UNKNOWN`, `WRITER_SOURCE_REQUIRED`, `WRITER_SOURCE_NOT_ADMITTED`, `REQUIRES_NOT_TRAIT`, `EXEMPT_NOT_CARRIER`, `EXEMPT_REDUNDANT`, `EXEMPT_REPEATED`, `SCOPE_PATH_INVALID`, `SCOPE_ROOT_MISMATCH`, `SCOPE_ROOT_NOT_SCOPED`, `SCOPE_LINK_UNKNOWN`, `SCOPE_LINK_NOT_ROOT`, `SCOPE_VIA_REPEATED`, `SCOPE_VIA_UNKNOWN`, `SCOPE_PATH_AMBIGUOUS`, `SCOPE_PATH_TO_EXEMPT`, `TRAIT_REQUIRED`, `CAPABILITY_REPEATED`, `CAPABILITY_UNKNOWN` |
| Deployments | `DEPLOYMENT_DUPLICATED`, `DEPLOYMENT_ITEM_REPEATED`, `DEPLOYMENT_EXTENDS_UNKNOWN`, `DEPLOYMENT_EXTENDS_CYCLE`, `DEPLOYMENT_WORLD_REQUIRED`, `ENGINE_REQUIRED`, `ENGINE_UNKNOWN`, `ENGINE_LOWERING_ABSENT`, `DEPLOYMENT_LOCATION_REQUIRED`, `SHIP_MODE_REQUIRED`, `SHIP_MODE_UNKNOWN`, `DEPLOYMENT_MODE_REQUIRED`, `DEPLOYMENT_MODE_UNKNOWN`, `DEPLOYMENT_SNAPSHOT_REQUIRED`, `SNAPSHOT_UNKNOWN` |
| Storage binding | `STORAGE_BINDING_UNREADABLE`, `STORAGE_SCHEMA_UNKNOWN`, `STORAGE_WORLD_MISMATCH`, `STORAGE_ENGINE_TABLES_MISSING`, `STORAGE_RELATIONS_MISSING`, `STORAGE_RELATION_MISSING`, `STORAGE_RELATION_UNKNOWN`, `STORAGE_COLUMNS_MISSING`, `STORAGE_COLUMN_MISSING`, `STORAGE_COLUMN_UNKNOWN`, `STORAGE_COLUMN_COLLISION`, `STORAGE_LINK_MISSING`, `STORAGE_LINK_UNKNOWN`, `STORAGE_TABLE_COLLISION`, `STORAGE_NAME_INVALID`, `STORAGE_KIND_NOT_ADMITTED`, `STORAGE_CAPTURE_NOT_ADMITTED`, `WRITER_CAPTURE_INCOMPLETE` |
| Raised while lowering, attributed to the source | `NESTED_SHOW_PATH`, `QUANTIFIER_MULTIPLE_MANY` |

Three of those groups carry the load-bearing decisions. `unenforced` is a standalone link flag: combining it
with any `end` action refuses with `LINK_ENFORCEMENT_CONFLICT` and repeating either refuses with
`LINK_ENFORCEMENT_REPEATED`, while the link stays typed and joins normally — only the `FOREIGN KEY` is
omitted. Only the registry in `calls.py` admits a `call`: `clock.now` and `random.uniform` are volatile and
`store.purge` is effectful, so they refuse with their own codes rather than as unknown names. And a query
has no live item by construction (the grammar admits none) and never derives a footprint.

**lower (2)** — `LOWER_INVERSE_OUTSIDE_QUANTIFIER`, `LOWER_QUANTIFIER_WITHOUT_MANY` (internal guards; the
resolver normally refuses first).

**ship (12)** — `RENAME_TARGET_UNKNOWN`, `RETIREMENT_POLICY_REQUIRED`, `RETYPE_ADAPTER_REQUIRED`,
`RETYPE_INCONSISTENT`, `RETYPE_KEY_EQUALITY`, `TIGHTEN_REPAIR_REQUIRED`, `ACCESSOR_BREAKING_UNACKNOWLEDGED`,
`MOVE_HOME_INCONSISTENT`, `RESTORE_TARGET_UNKNOWN`, `RESTORE_DATA_UNAVAILABLE`, `RESTORE_OUTSIDE_RETENTION`,
`MIGRATION_UNSUPPORTED`.

**load (5)** — `STORE_UNSHIPPED`, `STORE_BEHIND`, `STORE_DRIFT`, `GENERATION_OUTSIDE_WINDOW`,
`WRITER_CAPTURE_INCOMPLETE`.

**runtime (25)** — `READ_UNKNOWN`, `PARAM_UNKNOWN`, `PARAM_REQUIRED`, `PARAM_TYPE`, `SCOPE_REQUIRED`,
`CAPABILITY_REQUIRED`, `IDENTITY_UNKNOWN`, `KEY_DUPLICATED`, `CONSTRAINT_VIOLATED`, `LINK_RESTRICTED`,
`INVARIANT_VIOLATED`, `VERB_INPUT_REQUIRED`, `VERB_INPUT_ENGINE_OWNED`, `LEDGER_WRITER_UNKNOWN`,
`LEDGER_TRANSACTION_INVALID`, `LEDGER_CARRIER_UNKNOWN`, `LEDGER_CARRIER_ABSTRACT`, `LEDGER_FIELD_UNKNOWN`,
`LEDGER_VALUE_TYPE`, `LEDGER_SCOPE_UNKNOWN`, `QUERY_NOT_LIVE`, `LIVE_BOUND_EXCEEDED`,
`CAPTURE_NOT_DECLARED`, `CAPTURE_OP_UNKNOWN`, `CAPTURE_SEQUENCE_INVALID`.

---

## 4. Seed migration and the defects removed

`tools/migrate_seed_corpus.py` copies the v9-4 non-numbered corpora (`seed/v9-4/c3-core/corpus`) into
`corpus/worlds/` and applies **36** edits, each logged with its reason in `corpus/worlds/MIGRATION.md`:
**21** reads become `query` instead of `question` (a one-shot read with no live bound is static in v9-5);
**3** questions gain `live bounded N` (`labels.vip_clients`, `labels.vip_contacts`, `notes.dormant_clients`
use `some`, `count(…)` and `within`, so they stay questions and must state a bound); **1** path correction
(`some labels.label_name` → `some labels.label.label_name`, because paths traverse resolved edges: the
inverse `labels` reaches `ClientLabel`, whose `label` link reaches `Label.label_name`); **3** drops of
`typescript` from `generated` (`TARGET_UNKNOWN`); **3** module-list trims for modules the seed never ships
(`MODULE_UNKNOWN`); **2** unused intents removed (`INTENT_HOMELESS`); **2** `use archived_at { optional }`
added where `archived_by` had no declared optional `Instant` use; **1** inverse removed from a trait link
that composed into every carrier of the trait (`INVERSE_DUPLICATED`).

The seed's own defects do not survive in `build/`:

| seed defect | replacement |
|---|---|
| implicit `id` identity column | `relations[<carrier>].identity` in the binding; `bind_world` requires it; `lower_ddl` emits it as `INTEGER PRIMARY KEY` |
| English plural table names | `relations[<carrier>].table`; no pluralisation code exists (`tools/check.py` G10 scans `src/` for one) |
| guessed `<link>_id` columns | `relations[<carrier>].links[<link qid>]`, read through `WorldIR.link_column_of` |
| the book/author join and projection branch | no entity-pair branch: `_Frame.alias_for` joins forward `LinkStep`s and `many_subquery_from_prefix` handles inverse steps generically |
| implicit `scope_id` column | `World.scope` → `ScopeRoot(trait, link, root)` and `Program.scope_paths` from `Resolver.compute_scope_paths`; `lower_sqlite.scope_predicate` walks that link path and binds `:_scope`. No scope column exists in any schema |
| preloaded scope/writer names | writers come from the world (`governed`, or the declared `writer_source`) via `LedgerValidator`; scopes are row identities validated by `LedgerValidator.check_scope` against the scope root's table |
| short-name runtime aliases | every runtime boundary takes a qualified identity — `Engine.execute(read_qid)`, `tx.mint(carrier_qid, {field_qid: value})`, `LiveEngine.subscribe(read_qid)` — otherwise `READ_UNKNOWN` / `LEDGER_CARRIER_UNKNOWN` / `LEDGER_FIELD_UNKNOWN` |
| regex/filename decode classifier | `parse.classify_decode` reads only the LALR value stack, the expected-terminal set and the failing token |
| adapter-style defaults | `bind_world` refuses on any missing or unknown mapping; `binding_document` is an authoring aid the compiler never calls |

`corpus/conformance/static/reporting.garns` and `corpus/conformance/dynamic/open_orders.garns` are
byte-identical copies of the lane's frozen conformance sources, reused unchanged inside
`corpus/conformance/worlds/reporting` and `…/sales`.

---

## 5. How to run

Regenerate every committed generated tree (delete + regenerate, writes `generated/INDEX.json`):

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python tools/generate_all.py
```

From `build/B2` (the lane root is `../..`). Python 3.10+, `lark` supplied by `uv`, no network.

```sh
# frozen-input scaffold check (resolves the lane root from its own path)
uv run --offline --with lark python ../../tools/check_scaffold.py

# every hard gate G0–G11; writes gate-report.json next to this README
uv run --offline --with lark python tools/check.py

# unit suite (tests/ puts src and the build root on sys.path itself)
uv run --offline --with lark python -m unittest discover -s tests -t .
```

`gate-report.json` uses schema `garns-v9-5/gate-report/1`: per gate its checks, the subprocess commands with
exit codes and output tails, and evidence paths.

**CLI** — `src/garns/cli.py`; there is no installed console script, so use `PYTHONPATH=src` and `-m`.
`--world`, `--binding` and `--read` are required: nothing is selected by position. A refusal prints
`refused: CODE [stage] at file:line:col` on stderr and exits 2.

```sh
S=corpus/conformance/worlds/sales

# resolve a source directory; --json prints the canonical IR
PYTHONPATH=src uv run --offline --with lark python -m garns.cli resolve $S
# → resolved 2 modules, 2 carriers, 4 reads, 1 worlds

# schema DDL for one world through its binding
PYTHONPATH=src uv run --offline --with lark python -m garns.cli ddl \
  corpus/conformance/worlds/reporting --world REPORTING \
  --binding corpus/conformance/worlds/reporting/storage-REPORTING.json

# every artifact of one world into a fresh directory
PYTHONPATH=src uv run --offline --with lark python -m garns.cli generate $S \
  --world SALES --binding $S/storage-SALES.json --out /tmp/gen-sales

# execute one read by qualified name (--param values are JSON; also --scope N,
# --capability C (repeatable), --store PATH, default :memory:)
PYTHONPATH=src uv run --offline --with lark python -m garns.cli execute $S \
  --world SALES --binding $S/storage-SALES.json \
  --read sales_static.revenue_open_by_customer --param floor=10 --ship
```

**Mutant runner** — parses, resolves, ships, migrates, writes and subscribes for real; the expectation
manifests are never inputs to detection:

```sh
PYTHONPATH=src uv run --offline --with lark python -c "
from pathlib import Path; from garns.mutants import observe_all, observe_scenario
for name, obs in sorted(observe_all(Path('corpus/mutants')).items()):
    print(f'{name:56s} {obs.stage:9s} {obs.code}')
print(observe_scenario(Path('corpus/mutants/scenarios/LIVE_BOUND_EXCEEDED')).as_dict())
"
```

**Metamorphic harness** — renames every bound identifier through the reference map, re-resolves and compares
normalised IR (`transform` also returns a freshly named binding in `tr.binding`):

```sh
PYTHONPATH=src uv run --offline --with lark python -c "
from pathlib import Path; from garns.parse import garns_files, parse_paths, parse_text
from garns.resolve import resolve_files
from garns.metamorphic import transform, normalized_program_json
files = parse_paths(garns_files(Path('corpus/metamorphic/collision')))
program = resolve_files(files)
after = lambda t: resolve_files([parse_text(x, p) for p, x in t.items()])
tr = transform(files, program, 'ALPHA', 'demo', after)
print(len(tr.mapping), 'renamed;', normalized_program_json(program)
      == normalized_program_json(after(tr.sources), tr.forward))
"
```

**Authoring aids** (no gate uses them). `tools/storage_template.py WORLD DIR` prints a complete binding
(`--fresh SEED` gives opaque names); `tools/migrate_seed_corpus.py` and `tools/make_mutants.py` regenerate
`corpus/worlds/` and `corpus/mutants/` and **delete their output tree first**.

---

## 6. Known limitations

Visible in the code as it stands:

- **Verbs have no runtime.** `alias`, `bulk`, `restricted` and `compound` resolve into `ir.Alias` /
  `ir.Bulk` / `ir.Restricted` / `ir.Compound` and are fully validated (derived-verb membership, bulkable
  verbs, set targets and types, accepted inputs, step ordering and bind types), but no consumer executes
  them: the engine exposes `mint` / `change` / `delete` directly and nothing generates a verb surface.
- **Postgres has no lowering, and a deployment using it refuses before any effect.** `engine postgres` is
  a recognised engine (`ENGINES = {"sqlite", "postgres"}` in `resolve.py`) but not a lowered one
  (`LOWERED_ENGINES = {"sqlite"}`); `Resolver.resolve_deployment` refuses `ENGINE_LOWERING_ABSENT` at
  validate, positioned at the `engine` item (or the deployment name when inherited through `extends`),
  before any schema, store, ledger, generation, or migration effect. An unknown engine still refuses
  `ENGINE_UNKNOWN`. This is the wave-3 repair of R1 finding P2.4; see `REPAIR.md`.
- **Nested shows follow exactly one inverse link.** `lower_nested` refuses `NESTED_SHOW_PATH` unless the
  path is a single inverse step; deeper chains are not lowered.
- **Quantified comparisons follow one to-many prefix.** `visit_Quantified` refuses
  `QUANTIFIER_MULTIPLE_MANY` when the body mentions to-many paths with more than one distinct inverse
  prefix.
- **`within` composes parameterless inners only.** An inner read that declares givens refuses with
  `COMPOSE_INNER_GIVENS`; the composed subquery cannot be parameterised per outer row.
- **Capture ordering is per-sequence, not global.** Each relation's changelog has its own `AUTOINCREMENT`
  sequence; `acquire` merges them by `seq` with ties broken by relation order (carrier qid), so interleaving
  across relations within one acquisition is `(seq, carrier)`, not a true global order.
- **Some declared facts are carried but not enforced downstream.** `ordered_within`, `history kept`, the
  `filter` use/link flag and the intent refinements `pattern` and `length` are resolved, qualified and
  present in the IR, but no DDL, index, query or runtime check consumes them; `dimension` is only checked
  for positivity on a `Vector` intent.
- **Three smaller edges.** Unscoped live instances register under `global` and a `*` partition, so they are
  probed for writes in every scope; `Engine.row_values` loads every mapped column to build a before-image
  rather than projecting the touched fields; and `with_total` is a second `COUNT(*)` over the same
  `FROM`/`WHERE` rather than a total derived from the page query.
