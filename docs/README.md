# Garns

Garns is a declarative language for **stating what data means once** and then
deriving everything else from that one statement: relational schema, SQL, live
subscription footprints, routing keys, a ledger, capture from external writers,
migrations, and generated Python and Rust surfaces.

This directory is the complete documentation set for the implementation. It is
written for **AI coding agents first**: every claim cites a file, a symbol or a
line, and every command below was executed against the tree it describes. Start
at [AI_DEVELOPER_GUIDE.md](AI_DEVELOPER_GUIDE.md) if you are here to change the
code; use [`## Reading paths`](#reading-paths) otherwise.

Paths written `src/garns/resolve.py` are relative to the Garns repository root.
Fully qualified paths name v9-5 review-lane evidence that does not travel with
the code.

---

## What Garns is

| Commitment | What it means in practice | Where it lives |
|---|---|---|
| **One meaning** | Source is resolved **once**. DDL, SQL, footprints, bindings, routing, ledger, capture, migration and surfaces are *consumers* of that result; none re-parses source or re-derives a source fact. | `src/garns/resolve.py`, `src/garns/ir.py` |
| **A typed, module-qualified IR** | Every identity is `module.Name`, `module.Carrier.link`, `module.Carrier.intent`. Bare names exist only inside `Resolver.lookup`; every public boundary refuses an unqualified one. | `src/garns/ir.py`, `src/garns/engine.py:211` |
| **Explicit storage binding** | Every table, identity column, scalar column, link column, family discriminator, engine table and changelog field is read from a per-world JSON document. Nothing is pluralised, defaulted or guessed; a missing or colliding mapping refuses before anything is lowered. | `src/garns/storage.py:170` (`bind_world`) |
| **A static `query` and a dynamic `question`** | Two nouns, one algebra core, **one** lowering entry point. A query is one-shot and may use arithmetic, aggregates, `distinct`, `having` and registry calls; a question is live, closed-algebra and must state `live bounded N`. | `src/garns/lower_sqlite.py:526` (`lower_read`) |
| **Live footprints, not polling** | A question derives a footprint of `(carrier, field)` atoms, which become routing keys. Committed deltas probe only the keys they can touch — routing never iterates the registry, and that zero is measured, not asserted. | `src/garns/footprint.py`, `src/garns/live.py` |
| **A ledger, and capture for outside writers** | Governed writes are typed-validated before any statement is issued, then written as one revision plus one ledger row per delta, with listeners notified only after `COMMIT`. An `external_captured` world instead reads declared changelog tables back into the same typed deltas. | `src/garns/engine.py`, `src/garns/capture.py` |
| **Evolution as a first-class event** | Two resolved generations are compared by qualified identity into 18 event kinds and an `additive` / `deprecating` / `breaking` verdict, then migrated against a real store. | `src/garns/evolution.py` |

## What Garns is not

| Not | Why, and what happens instead |
|---|---|
| **Not an ORM** | There are no objects, no session, no identity map and no lazy loading. You get `Result(rows, keys, total)` of plain values, and row identity travels in hidden `$k` columns you never name. |
| **Not a query builder with defaults** | Nothing is inferred from a name. No pluraliser, no `id` identity, no `<link>_id`, no `scope_id` column. Without a binding document the world does not bind (`STORAGE_BINDING_UNREADABLE`). |
| **Not a PostgreSQL system — yet** | `postgres` is a *recognised* engine that this build cannot lower. A deployment naming it refuses `ENGINE_LOWERING_ABSENT` at stage `validate`, before any effect. |
| **Not a verb runtime** | `alias`, `bulk`, `restricted` and `compound` resolve and validate fully, but nothing executes them and no surface is generated for them. Write through `Engine.transaction(...)` and `mint` / `change` / `delete`. |
| **Not a production-hardened engine** | One SQLite connection, no pool, no concurrency statement, no `unsubscribe`, no indexes, caller-asserted capabilities. |

Each row above is an entry in [LIMITATIONS.md](LIMITATIONS.md#inventory), with
the code that makes it true; the caller-facing consequences are in
[LIMITATIONS.md](LIMITATIONS.md#assumptions-downstream-consumers-must-not-make).

## Implementation language and generated targets

| Item | Value |
|---|---|
| Implementation | **Python 3.11+**, standard library only **plus `lark`** (LALR parser over the frozen `grammar/garns.lark`) |
| Store | **SQLite** through the stdlib `sqlite3` module; `src/garns/lower_sqlite.py` *is* the dialect |
| Generated per read | `queries/<qid>.sql` **or** `questions/<qid>.sql`; a Python surface `python/<qid>.py`; a Rust surface `rust/<qid>.rs` |
| Generated per question only | `.footprint.json`, `.binding.json`, `.routing.json` |
| Generated per world | `schema.sql`, `ir.json`, `manifest.json`, `rust/main.rs`, `rust/sqlite.rs` |
| Rust parity runner | `rust/main.rs` + `rust/sqlite.rs` compile with plain `rustc -O` — **no crate, no `Cargo.toml`, raw `#[link(name = "sqlite3")]` FFI** — and print `[type_code, text]` cells so Python and Rust encodings are comparable |
| Recognised targets | `TARGETS = {python, rust}` (`src/garns/resolve.py:26`). `typescript` refuses `TARGET_UNKNOWN` at `validate` |
| Recognised engines | `ENGINES = {sqlite, postgres}`, `LOWERED_ENGINES = {sqlite}` (`resolve.py:27-28`). `postgres` refuses `ENGINE_LOWERING_ABSENT` at `validate` |

The Rust surface is a **parity instrument, not a client library**: it embeds the
lowered SQL unchanged and performs none of `Engine`'s parameter, scope,
capability or live-bound checks. See
[INTEGRATION.md](INTEGRATION.md#generated-rust-surface). Note also that a world's
`generated <targets>` list is validated but does **not** gate emission — Python
and Rust surfaces are always written
([LIMITATIONS.md](LIMITATIONS.md#inventory)).

## Five-minute orientation

**The pipeline in one table.** Twelve phases; full mechanics in
[COMPILER_PIPELINE.md](COMPILER_PIPELINE.md#phases).

| # | Phase | Entry point | Produces |
|---|---|---|---|
| 1 | Parse | `parse.py::parse_text` | `ast.SourceFile` — located nodes, one `Name` per identifier occurrence |
| 2 | Resolve | `resolve.py::resolve_files` | `ir.Program` + the reference map |
| 3 | Storage binding | `storage.py::bind_world` | `WorldIR` — one world plus its physical names |
| 4 | Lowering | `lower_sqlite.py::lower_read`, `::lower_ddl` | one `Plan` for either noun; DDL text |
| 5 | Engine | `engine.py::Store.ship`, `::Engine.execute`, `::Engine.transaction` | shipped store, `Result`, revisions + ledger rows |
| 6 | Footprint | `footprint.py::derive_footprint` | `Footprint` (questions only) |
| 7 | Live | `live.py::LiveEngine.subscribe`, `::on_commit` | `Instance`, `Batch`, `fold` |
| 8 | Capture | `capture.py::CaptureAdapter.acquire` | one revision of typed deltas from changelog rows |
| 9 | Evolution | `evolution.py::classify`, `::migrate`, `::open_store` | `Classification`, executed DDL, generation record |
| 10 | Generation | `generate.py::generate` | the artifact tree + `manifest.json` |
| 11 | Surfaces | `surfaces.py::python_surface`, `::rust_surface`, `::rust_main` | Python / Rust text |
| 12 | CLI | `cli.py::main` | `resolve`, `generate`, `ddl`, `execute`; exit `2` on any refusal |

**A smallest runnable sequence.** Offline, writes nothing, four commands. Run
from the repository root:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src
S=corpus/conformance/worlds/sales
G="uv run --offline --with lark python -B -m garns.cli"

$G resolve $S
$G ddl $S --world SALES --binding $S/storage-SALES.json | head -6
$G execute $S --world SALES --binding $S/storage-SALES.json --read sales_static.open_orders_once --ship
$G execute $S --world SALES --binding $S/storage-SALES.json --read sales.not_a_read --ship
```

Observed output, verbatim (exit codes `0`, `0`, `0`, `2`):

```
resolved 2 modules, 2 carriers, 4 reads, 1 worlds
CREATE TABLE "ta_6e060cc01b" (
  "id_268d9db70b" INTEGER PRIMARY KEY,
  "co_7ed8c48383" TEXT NOT NULL,
  "co_1e32478f5c" TEXT NOT NULL,
  UNIQUE ("co_7ed8c48383")
);
{
 "rows": [],
 "total": null
}
refused: READ_UNKNOWN [runtime] at 1:1: sales.not_a_read is not a read of world SALES; reads are selected by qualified name
```

Read it as: the physical names are opaque because they come from
`storage-SALES.json` and nothing else; `--ship` builds a **fresh empty**
in-memory store, so `rows` is legitimately empty; an unknown read is refused at
the boundary rather than guessed. Adding `generate … --out DIR` prints
`generated 20 files under DIR`. Seeded transcripts: [INTEGRATION.md](INTEGRATION.md#cli).

**The three verification commands**, exactly as run:

| What | Command | From | Expected |
|---|---|---|---|
| Product baseline check | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_product.py` | the repository root | five `PASS` lines ending `PASS W0 product baseline`, exit 0 |
| Unit suite | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m unittest discover -s tests -t .` | the repository root | `Ran 103 tests … OK`, exit 0. `tests/` puts `src` on `sys.path` itself |
| Master gate G0–G11 | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py` | the repository root | twelve `PASS Gn …` lines then `ALL PASS`, exit 0 (128/128 checks) |

Two warnings that matter more than they look:

* **`tools/check.py` rewrites `gate-report.json` in place** at the end of every
  run. If you only need to know the recorded state, *read* the committed
  `gate-report.json` instead of re-running the gate. `tools/generate_all.py`,
  `tools/make_mutants.py` and `tools/migrate_seed_corpus.py` are worse: each
  **deletes its output tree first**.
* **`PYTHONDONTWRITEBYTECODE=1` is mandatory**, not hygiene theatre. The product
  baseline check refuses `__pycache__` / `.pyc` anywhere in the repository, so
  a plain `python` invocation can fail G0 on bytecode it wrote itself. `-B`
  covers the top-level process only; the environment variable propagates to
  children.

## Document map

| Document | Scope |
|---|---|
| [GARNS_DIRECTION.md](GARNS_DIRECTION.md) | Post-v9-5 north-star: PostgreSQL-primary, async runtime, preserved semantic invariants, phased delivery, evidence requirements and ADRs still needed |
| [README.md](README.md) | This orientation: what Garns is and is not, the toolchain, the five-minute path, and where every other document starts |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, dependency direction, identity and scope models, routing, transactions, generated targets, and a per-component sustainability verdict |
| [COMPILER_PIPELINE.md](COMPILER_PIPELINE.md) | Phase-by-phase mechanics, what each phase guarantees and which refusals it owns, and the proof that `validate` is pre-effect |
| [DSL_REFERENCE.md](DSL_REFERENCE.md) | The language: lexical elements, modules, types, intents, carriers, reads, expressions, verbs, worlds, deployments, evolution, plus runnable minimal examples |
| [DIAGNOSTICS.md](DIAGNOSTICS.md) | The canonical refusal catalogue — 262 codes in 266 code/stage rows — with trigger, position, pre-effect status, evidence, and the non-`Refusal` exceptions that can still escape |
| [EXTENDING_GARNS.md](EXTENDING_GARNS.md) | Playbooks: add a construct, a diagnostic, a lowering, an engine backend, a generated target, an integration adapter — and the rules each must not break |
| [AI_DEVELOPER_GUIDE.md](AI_DEVELOPER_GUIDE.md) | Operating manual for an agent changing the code: repository map, per-task reading recipes, architectural invariants, traps, change-impact map, definition of done |
| [TESTING.md](TESTING.md) | What each verification layer proves and does not prove, every command with its blast radius, the gate matrix, and how to build a non-circular regression |
| [LIMITATIONS.md](LIMITATIONS.md) | The honest inventory of what is refused, narrow, unconsumed or absent; the assumptions a caller must not make; the evidence-only surfaces |
| [INTEGRATION.md](INTEGRATION.md) | Python API, CLI, generated descriptors and Rust surface, dependency direction, and the proposed (**not implemented**) `garns-glade` adapter shape |
| [DOCUMENTATION_REPORT.md](DOCUMENTATION_REPORT.md) | How this set was produced and checked: sources per document, commands re-run, consistency edits, open mismatches, and what to carry into a future repository |

## Reading paths

**Planning the next Garns iteration**
[GARNS_DIRECTION.md](GARNS_DIRECTION.md) →
[ARCHITECTURE.md](ARCHITECTURE.md) for the current implementation →
[LIMITATIONS.md](LIMITATIONS.md#inventory) for the gaps being replaced →
[EXTENDING_GARNS.md](EXTENDING_GARNS.md) for change mechanics.

**Writing Garns source (DSL users)**
[DSL_REFERENCE.md](DSL_REFERENCE.md) → its `## Minimal valid examples` →
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) when something refuses →
[LIMITATIONS.md](LIMITATIONS.md#inventory) before relying on a construct.

**Embedding Garns (integrators)**
[INTEGRATION.md](INTEGRATION.md#python-api) →
[ARCHITECTURE.md](ARCHITECTURE.md) for the model behind the API →
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) to map `(code, stage)` onto your
transport →
[LIMITATIONS.md](LIMITATIONS.md#assumptions-downstream-consumers-must-not-make).

**Maintaining the compiler (maintainers)**
[ARCHITECTURE.md](ARCHITECTURE.md) →
[COMPILER_PIPELINE.md](COMPILER_PIPELINE.md#phases) →
[EXTENDING_GARNS.md](EXTENDING_GARNS.md) →
[TESTING.md](TESTING.md#constructing-a-strong-regression) →
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue).

**AI coding agents**
[AI_DEVELOPER_GUIDE.md](AI_DEVELOPER_GUIDE.md) **first** — open only the files
its `## Read these files for this task` recipe names → the matching playbook in
[EXTENDING_GARNS.md](EXTENDING_GARNS.md) →
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) and
[TESTING.md](TESTING.md#commands) for evidence → the guide's
`## Definition of done for implementation changes` before claiming completion.
Check [LIMITATIONS.md](LIMITATIONS.md#inventory) before "fixing" anything that
looks unfinished: much of it is refused on purpose.

## Status and evidence snapshot

**Snapshot 2026-09-04.** These are measurements of one tree at one moment, not
invariants; re-measure rather than cite.

| Fact | Value | Evidence |
|---|---|---|
| Selected build | **B2**, chosen after two independent peer-blind reviews — both initial reviews close with the line `fold B2` | `../evidence/v9-5-b2/R1-REVIEW.md`, `../evidence/v9-5-b2/R2-REVIEW.md` |
| Wave-3 repair | One bounded repair: a deployment on a recognised-but-unlowered engine now refuses `ENGINE_LOWERING_ABSENT` at `validate`, before any effect (R1 finding P2.4) | `../evidence/v9-5-b2/REPAIR.md` |
| Unit suite | **103 tests**, `OK` | `Ran 103 tests … OK`, exit 0 |
| Master gate | **128/128 checks over 12 gates**, `all_pass: true` | `../evidence/v9-5-b2/gate-report.json` |
| Mutant corpus | **168/168** observed outcomes match the authored manifest (131 single-file + 37 scenarios; validate 99, decode 40, runtime 18, ship 6, load 4, accepted 1) | `corpus/mutants/expected.json`, re-swept with `garns.mutants.observe_all` |
| Generated artifacts | **172 files across 8 worlds**, plus `generated/INDEX.json` = 173 files on disk; committed trees reproduce byte-for-byte | `generated/INDEX.json` |

**Wave-4 ratification, as recorded at the end of each review file.** Both
reviewers appended a ratification section and both end with the same single-word
verdict line:

* R1 — "The bounded P2.4 repair is effective." … "No P1 or P2 finding remains."
  One non-blocking P3 remains open: the check and test labelled *"engine
  inherited through `extends`"* actually exercise an **override** in an
  extending deployment, not inheritance. Final line: `ratify`.
* R2 — "No bounded repair is required. The repaired B2 passes the complete
  matrix and the originally frozen private attack suite without contradicting
  evidence." Final line: `ratify`.

Neither reviewer reproduced a shared specification defect. Not claimed anywhere:
G12 comparative closure (the reviewers' gate, not the build's), and
`token_bound`, reported verbatim as `"unverified: not measurable from inside the
build"`.
