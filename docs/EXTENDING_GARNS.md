# Extending Garns

How to add language, semantics, lowering, backends, targets and adapters
without breaking the properties the implementation exists to guarantee.
Companion to `AI_DEVELOPER_GUIDE.md`, which tells you *which files* a task
touches and what must be re-run; this document tells you *how* to make the
change correctly. Language surface belongs to `DSL_REFERENCE.md`, component
boundaries to `ARCHITECTURE.md`, phase order to `COMPILER_PIPELINE.md`, refusal
codes to `DIAGNOSTICS.md` (`## Catalogue`), commands to `TESTING.md`, and known
gaps to `LIMITATIONS.md` (`## Inventory`).

## Principles

1. **One meaning.** Source resolves once into `ir.Program`. Every product —
   DDL, SQL, footprints, bindings, routing, ledger, capture, migration,
   surfaces — is a *consumer* of that IR. An extension that restates a source
   fact in a second table is wrong even if its tests pass.
2. **Qualified identity.** Everything the IR names is `module.Name`,
   `module.Carrier.link` or `module.Carrier.intent`. Bare names live only
   inside `Resolver.lookup` (`src/garns/resolve.py:119-137`).
3. **Physical names are inputs.** Tables, identity columns, scalar columns,
   link columns, family discriminators, engine tables and changelog fields come
   from the world's storage binding. Missing or ambiguous → refuse.
4. **Refuse before effect.** A construct that cannot be lowered, footprinted or
   validated refuses at the earliest stage in `refuse.STAGES`
   (`decode, validate, lower, generate, ship, load, runtime`) — never silently
   degraded, never approximated.
5. **Both nouns share one lowering.** A `query` and a `question` over the same
   algebra produce the same `Plan` shape from the same `lower_read`. Never add
   a second query engine.
6. **Extensions must be exhaustive.** A new IR node without a handler in every
   consumer visitor fails loudly (`src/garns/visit.py:34-50`), and a new bound
   identifier without a reference-map entry silently breaks the metamorphic
   rename.
7. **Evidence, not assertion.** A new behaviour ships with an executable
   fixture: a refusal fixture, a mutant, a unit test, and — when it changes a
   product — regenerated `generated/` bytes.

## Playbook: add a construct

`grammar/garns.lark` is **frozen in v9-5**: it is byte-identical to the lane
grammar and its digest is recorded in
`the historical v9-5 lane/FROZEN.json`; G0 compares all three
(`tools/check.py:132-135`). Report a grammar defect to the operator. The
sequence below is the path in a future repository where the grammar is live.

1. **Grammar rule.** Add the rule or the item alternative in
   `grammar/garns.lark`. Read items hang off `q_item` (question) and
   `query_item` (query); carrier items off `carrier_item` / `member_item`;
   world items off the `world_decl` item list; deployment items off `dep_item`.
   Keep the grammar LALR — G1 reads `parser().options.parser == "lalr"` off the
   live parser object (`tools/check.py:145`).
2. **AST node.** Add a frozen dataclass to `src/garns/ast.py` carrying a `Loc`.
   Every identifier occurrence must be an `ast.Name`, because `_Builder.name()`
   appends it to `SourceFile.names` — that is what makes the reference map and
   therefore the metamorphic rename possible (`src/garns/parse.py:135-138`).
3. **Builder method.** Extend the matching `_Builder` method in
   `src/garns/parse.py` — `read_item`, `carrier_item`, `intent_item`,
   `world_decl`, `deployment_decl`, `decl`, `toplevel`. These dispatch on the
   Lark token type or tree `data` and end in
   `raise AssertionError(f"… {kw}")`, so an unhandled shape crashes loudly
   during development rather than being dropped.
4. **Resolver.** Resolve it in `src/garns/resolve.py` (declarations, carriers,
   verbs, worlds, deployments, scope paths) or
   `src/garns/resolve_read.py` (paths, expressions, shapes, givens). Record a
   reference for **every** bound identifier occurrence with
   `Resolver.ref(name, identity, role)` (`src/garns/resolve.py:92-93`).
5. **IR node.** Add the frozen dataclass to `src/garns/ir.py` and put it in the
   right union — `Terminal`, `Operand`, `Expr`, `ShowTerm` — because
   `src/garns/visit.py:27-31` derives the node sets from those unions with
   `union_members`. A new *declaration* also belongs in
   `visit.DECLARATION_NODES` and, if it is a top-level list, in
   `metamorphic._resort`'s kind set (`src/garns/metamorphic.py:113-116`) so a
   rename cannot reorder it.
6. **Every consumer visitor.** At minimum:
   `src/garns/footprint.py::FootprintDeriver` (contribute atoms, or raise
   `_static_only(node)` if the construct has no write footprint),
   `src/garns/lower_sqlite.py::_Lowerer` (expressions and operands) and
   `::_ShowLowerer` (show terms). `ir.canonical` walks dataclass fields
   generically and skips `loc`, `references` and `file`
   (`src/garns/ir.py:754-773`), so a new field is canonicalised automatically —
   which also means it changes every IR digest and every `generated/ir.json`.
7. **Tests and mutants.** Add a positive parse case to `tests/test_parse.py`, a
   resolution case to `tests/test_resolve.py`, and — for each way the construct
   can be wrong — a mutant in `tools/make_mutants.py` and a fixture in
   `corpus/conformance/refusals/`.
8. **Docs.** `DSL_REFERENCE.md` for the surface, `DIAGNOSTICS.md` for new codes,
   `AI_DEVELOPER_GUIDE.md` `## Change-impact map` if the blast radius changes.

**Exhaustiveness is asserted, not hoped for.** `visit.check_exhaustive(visitor,
nodes)` returns the names of node classes with no handler;
`assert_exhaustive` raises. `tests/test_resolve.py::TestExhaustiveVisitors`
calls it for all three visitors and additionally dispatches an unhandled node
to prove `Visitor.visit` raises `TypeError`. G10 repeats both checks and
constructs a `Phantom` subclass of an IR node to prove the mechanism still
detects a gap (`tools/check.py:611-618`). Measured on the current tree:
`FootprintDeriver` 26 handlers, `_Lowerer` 20, `_ShowLowerer` 6, **zero**
missing nodes; `check_exhaustive(FootprintDeriver, (Phantom,)) == ['Phantom']`.

## Playbook: add a semantic rule or diagnostic

1. **Choose the stage.** `refuse.STAGES` is ordered
   `decode → validate → lower → generate → ship → load → runtime`
   (`src/garns/refuse.py:11-19`); the first refusal wins. Pick the *earliest*
   stage at which the fact is knowable:

   | stage | owner | typical rule |
   |---|---|---|
   | `decode` | `src/garns/parse.py::classify_decode` | shape the grammar rejects; classified from the LALR value stack, expected-terminal set and failing token only |
   | `validate` | `resolve.py`, `resolve_read.py`, `storage.py` | names, types, algebra, world/deployment facts, binding completeness |
   | `lower` | `lower_sqlite.py` | internal guards (`LOWER_INVERSE_OUTSIDE_QUANTIFIER`, `LOWER_QUANTIFIER_WITHOUT_MANY`) the resolver should normally pre-empt |
   | `generate` | — | **declared but currently unused**: no raise site in `src/**` names this stage. Use it only for a fault that is first knowable while writing artifacts; otherwise refuse at `validate`. |
   | `ship` | `evolution.py` | continuity, retirement policy, retype, repair, `move_home` |
   | `load` | `evolution.open_store`, `capture.check_coverage` | store drift, lag, retention window, changelog coverage |
   | `runtime` | `engine.py`, `live.py`, `capture.py` | parameters, scope, capability, ledger identity, live bound |

2. **Position `refuse()` before the effect it prevents.** `refuse(code, stage,
   loc, detail)` accepts anything with `file`/`line`/`column`, or an object with
   a `.loc` (`src/garns/refuse.py:51-59`). Place the call so that no IR node,
   file, connection or row exists yet. The canonical worked example is the
   engine guard: `Resolver.resolve_deployment` collects items, runs the
   required-item loop, and only then checks lowerability — *before*
   `I.Deployment` is constructed (`src/garns/resolve.py:1292-1305`). Because
   every effectful entry point (`Store`, `Engine`, `generate`,
   `evolution.migrate`, `evolution.open_store`) takes a `WorldIR`, and the only
   producer of a `WorldIR` is `bind_world(program, …)`, refusing before a
   `Program` exists is provably pre-effect.
3. **Reuse an existing code where the meaning matches.** Adding a synonym
   fragments `DIAGNOSTICS.md` and the mutant corpus. The current inventory,
   measured by scanning `src/**/*.py` for the first string argument of
   `refuse(`, `Refusal(`, `_runtime(`, `_ship(`, `_fail(`, is **241 distinct
   codes at 347 raise sites**. **21 more** are selected through a variable and
   so escape that scan: a ternary at the raise site —
   `LINK_ENFORCEMENT_REPEATED` / `LINK_FLAG_REPEATED`
   (`src/garns/resolve.py:526`), `QUESTION_LIVE_BOUND_DUPLICATED` /
   `READ_ITEM_REPEATED` (`src/garns/resolve_read.py:529`) and
   `CONSTRAINT_VIOLATED` (`src/garns/engine.py:489`, `:522`); the two
   required-item loops over `(key, code)` pairs (`src/garns/resolve.py:1043-1052`
   for worlds, `:1282-1291` for deployments); and a code passed to a helper that
   raises it (`lookup` / `lookup_qualified`'s `missing_code`, `literal_of_type`'s
   and `given_ref`'s `code`, which is the only way `CARRIER_UNKNOWN`,
   `EXEMPT_UNKNOWN`, `GIVEN_DEFAULT_TYPE` and `PAGE_TYPE` are reachable).
   **241 + 21 = 262** distinct implemented codes. `DIAGNOSTICS.md`
   `## Catalogue` is the authority: 262 codes in 266 code/stage rows.
4. **Add a refusal fixture.** Put a minimal `.garns` source in
   `corpus/conformance/refusals/` and one case in its `expected.json`
   (`{"file": …, "stage": …, "code": …}`). G1 observes each fixture
   independently with `mutants.observe_single` and only *then* compares it with
   the manifest (`tools/check.py:163-167`) — the manifest is an assertion, never
   a detector input.
5. **Or add a mutant.** For later-stage rules use `tools/make_mutants.py`:
   `NEW_MUTANTS` for a single-file source, `scenario(name, stage, code, steps)`
   for a staged one. Then regenerate the corpus — the tool deletes
   `corpus/mutants/` first. G9 executes all cases and requires zero mismatches
   plus invariance under renaming, comment stripping and manifest corruption
   (`tools/check.py:549-577`).
6. **Add a unit test** in the matching `tests/test_*.py`, computing its own
   oracle. `TESTING.md` `## Constructing a strong regression` owns the style.
7. **Update `DIAGNOSTICS.md`** `## Catalogue` with the code, its stage, what it
   defends and where it is raised.

## Playbook: change or add a lowering

`src/garns/lower_sqlite.py` is the single relational/SQL lowering. `lower_read`
is the only entry point; `Engine.execute` and live refresh both go through it
(asserted by G4, `tools/check.py:217`).

**The `Plan` contract** (`src/garns/lower_sqlite.py:57-70`) — `read`, `noun`,
`sql`, `params` (declared given names, `_`-prefixed engine params excluded),
`key_columns`, `columns` (shown columns, in order), `children`, `total_sql`,
`scoped`, `uses_clock`, `shape`, `live_bound`. A `ChildPlan` (`:46-54`) adds
`parent_column` and its own `key_columns`/`columns`/`children`.
`Engine.execute_plan` consumes exactly these fields (`src/garns/engine.py:287-303`),
so anything you add to a plan must be consumed there or it is dead weight.

**Hidden key columns.** Result identity travels in `$k`-prefixed columns that
are deliberately absent from `Plan.columns`: `$k0` is the subject identity for
collections and windows; grouped reads get one `$k0…$kN` per group key;
`distinct` uses the shown columns as the key; nested children add `$parent` and
their own `$k0` (`:543-554`, `:494`). Measured on `sales.open_orders`: `"$k0"`
appears in the SQL and not in `Plan.columns`. Keep new key columns hidden the
same way — a caller that starts seeing `$k0` as a result column is a regression.

**Reserved parameters.** `:_scope`, `:_clock`, `:_parents` are engine-owned
(`SCOPE_PARAM`, `CLOCK_PARAM`, `PARENTS_PARAM`, `:22-25`). A given whose name
starts with `_` refuses `GIVEN_NAME_RESERVED` in both the resolver
(`src/garns/resolve_read.py:48-49`) and `lower_read`
(`src/garns/lower_sqlite.py:528-530`); keep both guards if you add another
reserved name.

**Joins come from resolved edges only.** A forward `LinkStep` becomes
`LEFT JOIN target AS jN ON jN.<identity> = prev.<link column>` in
`_Frame.alias_for` (`:90-108`); an inverse step starts a correlated subquery
built by `many_subquery_from_prefix` (`:261-299`) — `EXISTS`/`NOT EXISTS` for
`some`/`every`, a scalar subquery for `count`/`max`/`min`. `scope_predicate`
(`:370-381`) walks the resolved scope-path tuple recursively to the root
against `:_scope`. Nothing inspects a name; do not introduce a branch that does.

**One lowering, both nouns.** `lower_read` never asks whether the read is a
question except to carry `live_bound` through. Measured: the query
`sales_static.open_orders_once` and the question `sales.open_orders` produce the
same `Plan` type with `key_columns ('$k0',)` and
`columns ('identity','customer','total')`.

**Deterministic tiebreaks.** `order_clause(..., with_tiebreak=True)` appends
subject identity `ASC` for ungrouped non-distinct reads, the group keys `ASC`
when grouped, and nothing for `distinct`; `rank` reuses the same order inside
`ROW_NUMBER() OVER (…)` (`:458-471`). Changing a tiebreak changes every
generated `.sql`, the Rust parity rows and every recorded live batch — treat it
as a breaking change.

**DDL.** `lower_ddl` (`:605-663`) emits one `CREATE TABLE` per storable
carrier — identity as `INTEGER PRIMARY KEY`, `NOT NULL` where required, literal
defaults, `CHECK` membership for closed sets, `UNIQUE` over key columns, the
family `kind` column with its member `CHECK` — plus a `FOREIGN KEY … ON DELETE
RESTRICT|CASCADE|SET NULL` **only** when enforcement is not `unenforced`, and
the three engine tables. Measured on REPORTING: `reporting.Invoice.customer`
resolves with `enforcement=unenforced` and `inverse=invoices`, and the DDL
contains no `FOREIGN KEY` at all.

**After any lowering change:** regenerate `generated/` with
`tools/generate_all.py`, confirm G9 byte identity (measured: all eight worlds'
fresh `tree_digest` equal both the committed tree and the digests in
`generated/INDEX.json`), and re-verify Rust parity — G11 compiles
`generated/<WORLD>/rust/main.rs` with `rustc -O` and compares seven reads row
for row against Python running the same SQL (`tools/check.py:622-683`). The
Rust side embeds the lowered SQL *unchanged* (`src/garns/surfaces.py`), so a
lowering change is a parity change.

## Playbook: add an engine backend

Today there is exactly one lowered engine. `ENGINES = frozenset({"sqlite",
"postgres"})` and `LOWERED_ENGINES = frozenset({"sqlite"})`
(`src/garns/resolve.py:27-28`), and `Resolver.resolve_deployment` refuses a
recognised-but-unlowered engine at `validate`, positioned at the deployment's
`engine` item, or at the deployment name when the engine arrives through
`extends` (`:1292-1299`). Measured:
`engine postgres` → `ENGINE_LOWERING_ABSENT [validate] at 24:10`;
`engine oracle` → `ENGINE_UNKNOWN [validate]`; the `engine sqlite` twin of the
same source resolves. See `LIMITATIONS.md` and the wave-3 repair log
`../evidence/v9-5-b2/REPAIR.md` §1.

**The honest path — in this order:**

1. Write the lowering: a `lower_<engine>.py` producing the same `Plan` /
   `ChildPlan` contract, plus DDL and capture DDL.
2. Write the store: a `Store` equivalent that owns connection, `ship()` and the
   engine tables, and an `Engine` that binds parameters in that engine's style.
3. Write the capture triggers and the coverage probe for that engine.
4. Prove parity: the new backend's rows must equal SQLite's for the shared
   corpus, canonically encoded.
5. Add mutants and refusal fixtures for the new backend's failure modes.
6. **Only then** add the engine name to `LOWERED_ENGINES`.

**Never** bypass the refusal to "unblock" work, and **never** special-case an
engine name with a string comparison outside a registry. `ENGINES` /
`LOWERED_ENGINES` are the registry; a dispatch table keyed by engine name is
the correct shape for a second lowering. A stray `if engine == "postgres"` in
lowering, storage or the engine is exactly the schema-name branching the build
forbids (G10, `tools/check.py:584-600`).

**Everything that currently assumes SQLite** — audit each before claiming a
second backend:

| assumption | where |
|---|---|
| `sqlite3.connect`, `PRAGMA foreign_keys = ON`, `executescript` for DDL | `src/garns/engine.py::Store` (`:161-177`) |
| `sqlite3.IntegrityError`, and the `"UNIQUE" in str(exc)` test that splits `KEY_DUPLICATED` from `CONSTRAINT_VIOLATED`; `cur.lastrowid` for minted identity | `src/garns/engine.py:484-490`, `:517-522`, `:535-540` |
| named `:param` binding and `list_of` givens JSON-encoded for `json_each` | `src/garns/engine.py::bind_params` (`:305-332`) |
| `INTEGER PRIMARY KEY`, `ON DELETE RESTRICT/CASCADE/SET NULL`, `CHECK`, `UNIQUE` | `src/garns/lower_sqlite.py::lower_ddl` (`:605-663`) |
| storage classes `INTEGER` / `REAL` / `BLOB` / `TEXT` (and `Instant → INTEGER`) | `src/garns/types.py::sql_storage_type` (`:106-114`) |
| `json_each(...)` for `in` and for the nested-child `:_parents` list | `src/garns/lower_sqlite.py:223`, `:505` |
| `instr(...)` for `contains`; `CAST(… AS REAL)` for division | `src/garns/lower_sqlite.py:219`, `:165-167` |
| `ROW_NUMBER() OVER (…)` for `rank` and for `last N` children | `src/garns/lower_sqlite.py:443-446`, `:512-520` |
| the static-call SQL templates (`LOWER`, `TRIM`, `UPPER`, `LENGTH`, `\|\|`, `ABS`, `ROUND`, `CAST(… AS INTEGER)`) | `src/garns/calls.py::REGISTRY` (`:25-41`) |
| `AUTOINCREMENT` changelog sequences and `CREATE TRIGGER … AFTER INSERT/UPDATE/DELETE … BEGIN … END` with `OLD`/`NEW` | `lower_sqlite.lower_capture_ddl` (`:666-700`) |
| `PRAGMA table_info` as the coverage denominator | `src/garns/capture.py::check_coverage` (`:31-45`) |
| `PRAGMA table_info`, `ALTER TABLE … RENAME COLUMN / ADD COLUMN / DROP COLUMN`, the `value ANY` quarantine column, `sqlite3.OperationalError` | `src/garns/evolution.py::migrate` (`:220-324`), `::open_store` (`:327-350`) |
| double-quote identifier quoting | `lower_sqlite.q` (`:28-30`) |
| the raw `#[link(name = "sqlite3")]` FFI parity runner, copied verbatim into every generated tree | `src/garns_rust/sqlite.rs`, `src/garns/generate.py:86` |
| the G11 parity harness runs the compiled binary against a SQLite file | `tools/check.py:646-680` |

**One naming imprecision to fix while you are here.** The check and test called
"engine inherited through `extends`" actually build a SQLite base and a child
that *overrides* it with `engine postgres` (`tools/check.py:377-379`,
`tests/test_repair_engine_lowering.py:65-69`). R1's ratification records this as
a non-blocking P3 label defect and suggests renaming it to "postgres override in
an extending deployment"
(`../evidence/v9-5-b2/R1-REVIEW.md`). A
genuinely PostgreSQL base is already refused at its own `engine` item, so no
acceptance path is exposed — but if you touch this area, fix the label and add
a case where the base itself carries the unlowered engine.

## Playbook: add a generated target

`TARGETS = frozenset({"python", "rust"})` (`src/garns/resolve.py:26`). Any other
name in a world's `generated` list refuses `TARGET_UNKNOWN` at validate.
Measured: `generated python, rust, typescript` →
`TARGET_UNKNOWN [validate] at 5:85: generated target typescript has no surface
in this build`. That is why `tools/migrate_seed_corpus.py` drops `typescript`
from three migrated seed worlds, each edit logged with its reason in
`corpus/worlds/MIGRATION.md`.

To add one:

1. **Surface writer.** Add `<target>_surface(plan, ident)` to
   `src/garns/surfaces.py`. Embed `plan.sql` **unchanged** — the parity claim is
   that both sides execute identical SQL — plus `read`, `noun`, `params`,
   `key_columns`/`columns`, `scoped`, `uses_clock`.
2. **Registry entry.** Add the name to `TARGETS`.
3. **Emission.** Call it from `src/garns/generate.py::generate` (`:72-86`) and
   list its files in the manifest via the same `write()` helper, so the file
   lands in the returned path→sha256 map and therefore in `tree_digest`.
4. **Parity harness.** Extend `tools/check.py::g11` to build and run the new
   runner and compare typed rows against Python, and record the outcome in the
   G11 `measures` object (`tools/check.py:625`, `:682-683`) — `verified` only
   when it really ran; otherwise a truthful `"unverified: …"` string *and* a
   failed check, never a silent skip (`tools/check.py:626-630`).
5. **Determinism.** No timestamps, no absolute paths, no dictionary-order
   dependence. `StorageMapping.source` records only the binding's file *name*
   for exactly this reason (`src/garns/storage.py:300-301`); regeneration from a
   relocated checkout must stay byte-identical
   (`tests/test_generate.py::test_regeneration_from_a_relocated_copy_of_the_corpus_is_byte_identical`).
6. **Regenerate and re-verify G9.**

**Known gap to close if you touch this area:** `generate()` does not filter
surfaces by `World.generated` — it always writes the Python and Rust surfaces
plus `rust/main.rs` and `rust/sqlite.rs`. Measured on a world declaring
`generated python` only: `rust/m__q.rs`, `rust/main.rs` and `rust/sqlite.rs`
were still emitted. The corpus does not expose this because all eight worlds
declare `generated python, rust`. A third target makes the gap load-bearing, so
gate emission on `world.world.generated` in the same change and add a world that
declares a single target.

## Playbook: add an integration adapter

Consume the public modules; never bind by convention. `INTEGRATION.md` owns the
worked examples — this is the contract an adapter must respect.

- **Select explicitly.** `bind_world(program, world_name, binding_path)` is the
  only producer of a `WorldIR` (`src/garns/storage.py:170`). An unknown world
  refuses `WORLD_UNKNOWN`; an unreadable binding refuses
  `STORAGE_BINDING_UNREADABLE` — both at `validate`, before anything exists.
- **Address reads by qualified name.** `Engine.execute(read_qid, params, scope,
  capabilities, clock)`; `LiveEngine.subscribe(read_qid, params, scope,
  capabilities)`. Measured: `execute("open_orders")`, `execute("")` and
  `execute("sales.nope")` all refuse `READ_UNKNOWN [runtime]` with "reads are
  selected by qualified name"; `mint("Order", …)` refuses
  `LEDGER_CARRIER_UNKNOWN`; `bind_world(program, "NOPE", …)` refuses
  `WORLD_UNKNOWN`.
- **Do not re-derive artifacts.** Take `Plan` from
  `lower_sqlite.lower_read(world, read)` or `Engine.plan(read_qid)`, and
  `Footprint` from `footprint.derive_footprint(world, read)`; both refuse rather
  than approximating. A query has no footprint (`QUERY_NOT_LIVE`) and no live
  products.
- **Read results through `Plan.columns`.** `Engine.execute` returns
  `Result(rows, keys, total)`; `rows` carry only the declared columns, `keys`
  carry the hidden `$k` tuple. Never parse the SQL.
- **Live batches are keyed deltas.** `Batch(instance, base_seq, seq, revision,
  changes)` with `upsert`/`delete` `Change`s; `None` means the routed write was
  result-neutral. `live.fold(initial, keys, batches)` replays them and is what
  fold-equivalence is measured against (`tools/check.py:488-491`).
- **Writes go through a transaction.** `Engine.transaction(writer,
  transaction_id)` validates the writer against the world and the transaction id
  against `^[A-Za-z0-9_-]{1,64}$` on entry, before `BEGIN`; every
  `mint`/`change`/`delete` is typed-validated before a statement is issued; the
  ledger row and listener notification happen only after commit.
- **Never construct a binding at runtime.** `storage.binding_document` exists for
  authoring and for the metamorphic harness; on the production path
  `bind_world` only ever reads a document from disk. Its only callers are
  `src/garns/metamorphic.py:98` (evidence machinery),
  `tools/storage_template.py:59` (authoring aid) and `tools/check.py:287`,
  `:359` (gate fixtures).

## Visitor and reference-map exhaustiveness

**Visitors.** `src/garns/visit.py` defines `Visitor.visit`, which dispatches on
the exact class name to `visit_<ClassName>` and raises
`TypeError(f"{visitor} has no handler for IR node {node}")` when there is none
(`:34-41`). `union_members` expands the IR unions into node tuples
(`EXPR_NODES`, `OPERAND_NODES`, `SHOW_NODES`, `TERMINAL_NODES`) so the node sets
follow `ir.py` automatically. `check_exhaustive(visitor, nodes)` returns missing
handler names; `assert_exhaustive` raises with the list.

Consumers that must stay exhaustive: `footprint.FootprintDeriver` (expressions,
operands, shows), `lower_sqlite._Lowerer` (expressions, operands),
`lower_sqlite._ShowLowerer` (shows). Both `tests/test_resolve.py` and G10 assert
emptiness and prove the detector still works using a `Phantom` subclass.
Measured: 26 / 20 / 6 handlers, no missing nodes,
`check_exhaustive(_Lowerer, (Phantom,)) == ['Phantom']`, and
`Visitor.visit(Phantom(...))` raises
`TypeError: FootprintDeriver has no handler for IR node Phantom`.

*What breaks if you forget:* the unit suite and G10 fail immediately for a node
in a covered union. A node reached only at runtime raises `TypeError` — not a
`Refusal` — so it escapes the refusal channel entirely and surfaces as a crash
in whatever host called the engine. Add the handler in the same commit as the
node.

**Reference map.** The resolver records an `ir.Reference(file, line, column,
text, identity, role)` for every bound identifier occurrence
(`src/garns/resolve.py:92-93`), and `Program.references` carries them.
`metamorphic.rename_sources` replays those positions to rewrite the source text
(`src/garns/metamorphic.py:53-77`), asserting that the recorded text really sits
at the recorded column — a wrong or missing position raises
`AssertionError("reference map mismatch at …")`. Roles that participate are
listed in `RENAMED_ROLES` (`:22-25`): `module`, `intent`, `intent-alias`,
`intent-previous`, `newtype`, `closedtype`, `carrier`, `member`, `link`,
`inverse`, `read`, `alias`, `bulk`, `restricted`, `compound`, `tombstone`,
`capability`, `writer`, `world`, `deployment`.

*What breaks if you forget:* an unrecorded occurrence is **not** renamed, so the
transformed source still mentions the old spelling. Either it fails to resolve
(the rename looks broken) or — worse — it resolves against a stale name and G5
reports unequal normalized IR. Because G5 is the schema-independence gate, a
missing `ref()` call reads as a semantic defect rather than as the bookkeeping
omission it is. When you add a new identifier position, add the `ref()` call and
the role, extend `RENAMED_ROLES` if the role is new, and re-run G5. Aliases and
inverse names use decorated identities (`…#alias`, `…#inverse`,
`<read>#<given>`, `<world>#capability:<name>`) so distinct occurrences never
collide; `metamorphic.rename_qualified` resolves a qualified key segment by
segment against the *original* program so shared local spellings stay distinct
(`:128-151`).

## Avoiding schema/name guessing and backend leakage

Concrete rules, each with the code that makes it true and the check that catches
a violation.

| rule | do this | never this | caught by |
|---|---|---|---|
| Table names | `world.storage.relation(qid).table` | pluralise or case-fold a carrier name | G10 "no pluralization helper" (`tools/check.py:585`) |
| Identity columns | `world.relation_of(qid).identity` | assume `id` | G10 `:586`, `:603` |
| Link columns | `world.link_column_of(carrier_qid, link)` (`src/garns/storage.py:119-121`) | build `f"{link.name}_id"` | G10 `:586` |
| Scope | walk `world.scope_path(carrier)` and bind `:_scope` | add a `scope_id` column | G10 `:587`; measured paths: `pantry.Jar → ('pantry.Jar.shelf','pantry.Shelf.keeper')`, `clients.Contact → ('clients.Contact.client','clients.Client.owner')` |
| Member/family storage | `WorldIR.storage_use_key` / `storage_link_key` resolve a member field to its family key | branch on the member's name | `src/garns/storage.py:102-121` |
| Selection | take a qualified name at every public boundary | `worlds[0]`, `reads[0]`, "the only question" | G10 `:588`, `:605` |
| Corpus vocabulary | keep example names out of `src/` entirely | `if module == "practice"`, `book`/`author` special cases | G10 `:589` |
| Failure | `refuse(...)` | emit fallback SQL or a default mapping | G10 `:590` |
| Case dispatch | resolve from the IR | numbered cases, filename or comment tests | G10 `:591-592`; G9 invariance `:555-577` |
| Instrumentation | increment where the operation happens | assign a constant, or reset a counter to fake zero | G10 `:607` |
| Binding construction | read the document from disk | synthesise one when it is missing | `storage.load_binding` → `STORAGE_BINDING_UNREADABLE` (`:140-144`) |
| Backend detail outside lowering | keep SQL text inside `lower_sqlite.py` (and `calls.py` templates) | inline SQL in `live.py`, `footprint.py`, `generate.py` | review + the table in `## Playbook: add an engine backend` |

Two further habits that keep backends from leaking:

- **Result identity stays hidden.** Consumers use `Plan.key_columns` and
  `Result.keys`, never a column literal. Adding a visible identity column would
  change every generated artifact and every live batch key.
- **Physical names never reach the IR.** `ir.Program` contains only qualified
  semantic identities; physical names live in `StorageMapping`. The metamorphic
  gate depends on this split: renaming physical names must change generated SQL
  while leaving normalized IR identical (`tools/check.py:273-277`).

## Files and tests normally affected

| change | source | corpus / fixtures | generated | tests | gates |
|---|---|---|---|---|---|
| grammar construct *(future repo)* | `grammar/garns.lark`, `ast.py`, `parse.py`, `resolve*.py`, `ir.py`, `visit.py`, all visitors | conformance source + refusal fixtures + mutants | all worlds | `test_parse.py`, `test_resolve.py` | G0, G1, G9, G10 |
| semantic rule / diagnostic | the owning resolver or runtime module | `corpus/conformance/refusals/**`, `tools/make_mutants.py` | usually none | the matching `test_*.py` | G1, G3, G6, G8, G9 |
| SQL lowering | `lower_sqlite.py`, `surfaces.py`, `engine.py` | — | all worlds (`*.sql`, `schema.sql`, surfaces) | `test_static_dynamic.py`, `test_generate.py` | G4, G9, G11 |
| footprints / routing | `footprint.py`, `live.py`, `generate.py` | — | `questions/*.footprint.json`, `*.routing.json` | `test_live.py`, `test_static_dynamic.py` | G3, G7 |
| ledger / capture | `engine.py`, `capture.py`, `lower_sqlite.py`, `storage.py` | `corpus/conformance/worlds/ledgerhouse`, ledger scenario mutants | `LEDGERHOUSE/schema.sql` | `test_capture_ledger.py` | G8 |
| evolution / migration | `evolution.py` | `corpus/worlds/evolution/g1..g5`, ship/load scenarios | — | `test_evolution.py` | G6 |
| storage binding schema | `storage.py`, `tools/storage_template.py` | every `storage-*.json` | all worlds (`ir.json`, `manifest.json`) | `test_resolve.py`, `test_metamorphic.py` | G1, G5, G9 |
| engine backend | `resolve.py` registry, new `lower_*`/`Store`, `capture.py`, `evolution.py` | new refusal fixtures + mutants | possibly new trees | new backend tests + `test_repair_engine_lowering.py` | G1, G6, G9, G11 |
| generated target | `resolve.py::TARGETS`, `surfaces.py`, `generate.py`, `tools/check.py::g11` | a world declaring the target | all worlds | `test_generate.py` | G9, G11 |
| integration adapter | none (consume public modules) | optionally a new conformance world | none | adapter-side tests | none directly; keep G10's qualified-selection assertion true |

Before declaring any of these done, work through
`AI_DEVELOPER_GUIDE.md` `## Definition of done for implementation changes`.
