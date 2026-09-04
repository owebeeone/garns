# Testing

How Garns is verified, what each verification layer actually establishes, and how
to add a regression that cannot be satisfied by a lucky guess.

Refusal codes belong to [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue); construct
semantics to [DSL_REFERENCE.md](DSL_REFERENCE.md); module ownership to
[ARCHITECTURE.md](ARCHITECTURE.md); phase boundaries to
[COMPILER_PIPELINE.md](COMPILER_PIPELINE.md); the honest list of what is not
implemented to [LIMITATIONS.md](LIMITATIONS.md#inventory).

One rule governs every layer below, and it is the reason the harness is shaped
the way it is:

> **A test that supplies an expected code, SQL string, stage, or row to the
> detector is circular and does not count.** Expectation files
> (`corpus/mutants/expected.json`, `corpus/conformance/refusals/expected.json`)
> are read *only after* an outcome has been observed by running the production
> pipeline, and only to assert against it.

`tools/check.py:4-6` states this in its own module docstring; `tests/README.md`
repeats it as a suite rule.

---

## Layers

| Layer | What runs | What it proves | What it does **not** prove |
|---|---|---|---|
| **Unit suite** — `tests/` (10 modules, 103 tests) | `python -m unittest discover -s tests -t .`; drives the public modules from outside, computing its own oracles from rows it seeded (`tests/support.py:99-137`) | Parse/resolve/bind of every discovered world; qualified identities; scope paths; visitor exhaustiveness; query/question parity; live routing, rollback, fold; typed pre-effect ledger refusals; capture coverage; g1→g5 evolution; determinism of generation | Nothing about the *lane*'s frozen inputs, and nothing about Rust. `tools/check.py` does **not** invoke it — see `## Commands` |
| **Conformance corpus** — `corpus/conformance/` | G1–G4, G7, G8 and much of the unit suite | Two frozen sources parse and execute byte-identically (`static/reporting.garns`, `dynamic/open_orders.garns`); SALES gives a query/question parity pair plus a strictly richer static query; LEDGERHOUSE gives a private captured schema with a two-hop scope path | That any *other* schema shape works — that is what the metamorphic layer is for |
| **Refusal fixtures** — `corpus/conformance/refusals/` (12 sources + `expected.json`) | G1 sweeps all of them (`tools/check.py:163-167`); `tests/test_parse.py::TestFrozenRefusals` re-observes them | Each named misuse refuses with a stable `(stage, code)` at a real source position | That the code is *unique* to that misuse; a fixture asserts one direction only |
| **Migrated seed corpus** — `corpus/worlds/` + `corpus/worlds/MIGRATION.md` | G1 resolve+bind of 13 world/binding pairs | Four real third-party-shaped schemas (practice, everbility, vaultwarden, appflowy) and five evolution generations resolve, bind and (for PRACTICE) migrate on a real store. Every edit to the v9-4 seed is logged with its language reason | That the seed's *original* spelling was wrong — `MIGRATION.md` records a v9-5 language consequence per edit, not a defect claim |
| **Mutants** — `corpus/mutants/` (131 single-file + 37 scenarios = 168 cases) | `garns.mutants.observe_all`, swept by G9 (`tools/check.py:549-554`) and `tests/test_mutants.py` | Later stages genuinely execute: scenarios ship real stores, run external SQL, migrate, write, capture, execute and subscribe (`src/garns/mutants.py:62-143`). Observed `(stage, code)` matches the authored manifest for all 168 | That every refusal code in the implementation is covered — 124 outcomes out of 262 implemented codes are asserted here |
| **Mutant invariance** — same corpus, shadowed | G9 (`tools/check.py:555-577`), `tests/test_mutants.py::TestDetectionIsContentOnly` | Detection reads content only: every file renamed to `mNNN.garns`, every comment stripped, every scenario directory renamed to a hash, `expected.json` overwritten with `{"corrupted": true}` — 168/168 outcomes unchanged, keyed by content digest | That the *classifier* is minimal; it proves independence from names/comments/manifest, not taxonomy quality |
| **Metamorphic rename** — `src/garns/metamorphic.py` | G5 (`tools/check.py:221-341`), `tests/test_metamorphic.py` | A full deterministic rename through the resolver's own reference map leaves normalized IR, rows, routing decisions, delta batches and routing measures equal, while every physical name in the SQL changes. Applied to PRACTICE and to the captured LEDGERHOUSE (writer source and changelog names included) | That an *unseen* schema shape works — the transform renames an existing world, it does not invent a new topology |
| **Collision suite** — `corpus/metamorphic/collision/` | G5 (`tools/check.py:296-302`), `tests/test_metamorphic.py::TestShortNameCollision` | Two modules with identical local names (`Root`, `Item`, `heavy`, `code`, `amount`) stay apart: disjoint qualified index keys, one-sided routing, distinct rows per qualified read | Anything about three-way or cross-world collisions |
| **Delete/regenerate byte identity** | G9 (`tools/check.py:534-547`), `tests/test_generate.py::TestCommittedTree` | The committed `generated/<WORLD>` trees are reproduced byte-for-byte from source through the resolved IR, from the original *and* from a relocated copy of the corpus | That the generated Rust or Python is *useful* — only that it is reproducible |
| **Python/Rust parity** — `generated/<WORLD>/rust/` | G11 (`tools/check.py:622-683`) | `rustc -O` compiles the generated runner, and 7 reads across 2 worlds produce byte-identical `[type_code, text]` rows against the same SQLite file | Nothing about a Rust *implementation* of Garns. Both sides run the same SQL text; see [LIMITATIONS.md](LIMITATIONS.md#inventory) |
| **Repository integrity** — G0 plus `tools/check_docs.py` | G0 checks repository metadata, the root/package grammar pair, and both baseline conformance sources; the documentation checker verifies the eleven-document graph and cache hygiene | That a language-baseline change is desirable; it only proves the repository is internally consistent |
| **Master gate** — `tools/check.py` | G0–G11, 128 checks, writes `gate-report.json` | The exit-matrix contract end to end, with subprocess commands, exit codes and evidence paths recorded machine-readably | G12 (comparative closure) — that is the reviewers' gate, not the build's |

---

## Commands

All commands are offline and install nothing. `lark` is supplied by
`uv --with lark`; the Rust toolchain must already be present for G11.

### Why `PYTHONDONTWRITEBYTECODE=1` is mandatory

The repository checks refuse `__pycache__` directories. `tools/check.py` sets
`sys.dont_write_bytecode`, purges repository caches before and after the run,
and exports `PYTHONDONTWRITEBYTECODE=1` into subprocesses. Set it yourself for
everything else. `python -B` covers only the top-level process.

### Read-only commands (safe to run at any time)

| Command | Working directory | Writes |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m unittest discover -s tests -t .` | repository root | nothing outside `tempfile` directories it removes on teardown |
| `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_docs.py` | repository root | nothing |
| `PYTHONPATH=src … python -B -m garns.cli …` | repository root | only what `--out` / `--store` name |
| `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/storage_template.py WORLD DIR [--out F] [--fresh SEED]` | repository root | stdout, or `--out` |

`tests/` puts `src` and the repository root on `sys.path` itself
(`tests/__init__.py:15-19`), so no `PYTHONPATH` and no install step is needed for
the unit suite. The installed CLI is `garns`; from a source checkout, use
`PYTHONPATH=src` and `python -m garns.cli` for the equivalent entry point.

### Commands that rewrite committed artifacts

Run these deliberately, never casually, and never as part of "just checking".

| Command | Rewrites | Notes |
|---|---|---|
| `… python -B tools/check.py [--quick]` | **`gate-report.json`** (overwritten in place, `tools/check.py:722`) | To inspect the last recorded run without disturbing it, read `gate-report.json` instead of re-running. `--quick` is accepted but has no effect: it is parsed (`tools/check.py:688`), passed to `g11` (`:702`) and never read |
| `… python -B tools/generate_all.py` | **`generated/`** — deletes the whole tree first (`tools/generate_all.py:39-40`), then rewrites 8 worlds and `generated/INDEX.json` | The delete/regenerate gate (G9) compares committed trees against a *fresh temp* generation and does not need this driver |
| `python3 tools/make_mutants.py` | **`corpus/mutants/`** and its `expected.json` | Deletes its output tree first. Part of no gate |
| `python3 tools/migrate_seed_corpus.py` | **`corpus/worlds/`** and `corpus/worlds/MIGRATION.md` | Deletes its output tree first. Reads the frozen `seed/`. Part of no gate |

### Two harness one-liners

Observe every mutant through the production pipeline (no manifest is read):

```sh
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -c "
from pathlib import Path; from garns.mutants import observe_all, observe_scenario
for name, obs in sorted(observe_all(Path('corpus/mutants')).items()):
    print(f'{name:56s} {obs.stage:9s} {obs.code}')
print(observe_scenario(Path('corpus/mutants/scenarios/LIVE_BOUND_EXCEEDED')).as_dict())
"
```

Rename every bound identifier and re-resolve, comparing normalised IR:

```sh
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -c "
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

---

## Gate matrix G0–G11

Read from `gate-report.json` (schema `garns/gate-report/1`). Every gate is a
function in `tools/check.py`; a crash inside a gate is recorded as a **failed**
check, never as a skip (`tools/check.py:709-710`).

| Gate | Requirement | Checks | Key check labels | Evidence recorded |
|---|---|---:|---|---|
| G0 | Repository integrity | 4 | repository metadata present; root/package grammar byte-identical; static and dynamic baseline sources remain admitted | `grammar/garns.lark`, `src/garns/garns.lark` |
| G1 | Grammar and corpus | 28 | `parser is LALR`; 13 × `resolve+bind <WORLD> (<dir>)`; `standalone unenforced resolves as a typed link without a foreign key`; `unenforced link emits no FOREIGN KEY`; 12 × `refusal <file>: observed <stage>/<code>` | `corpus/conformance/refusals/expected.json`, `corpus/worlds/MIGRATION.md` |
| G2 | Static query | 5 | `richer static query (group/having/arithmetic/call/non-path order) executes`; `distinct static query executes`; `queries generate SQL only; no footprint/binding/routing artifact for any query`; `subscribing a query refuses before any registration`; `deriving a footprint for a query refuses` | `corpus/conformance/worlds/sales/parity.garns` |
| G3 | Dynamic question | 8 | `question footprint covers subject structure, predicate, projections, link and order fields`; 5 × `static-only/unbounded form in a question refuses pre-effect: …`; `valid question subscribes, derives its footprint and routes`; `relevant write routes and emits a batch` | *(none listed)* |
| G4 | Shared lowering | 3 | `query one-shot rows == question initial live rows (canonical bytes)`; `both nouns lower through one plan type with the same key/column shape`; `one lowering entry point serves execute() and live refresh` | `src/garns/lower_sqlite.py` |
| G5 | Schema independence | 12 | `normalized IR equal after full rename`; `rows equivalent after rename (normalized column names)`; `routing decisions equivalent`; `delta batches equivalent`; `routing measures equivalent (probes, candidates, zero scans)`; `generated SQL uses the new physical names and none of the old ones`; 3 × `collision: …`; 3 × `captured world: …` | `src/garns/metamorphic.py`, `corpus/metamorphic/collision` |
| G6 | Identity/world/evolution | 24 | `postgres deployment refuses ENGINE_LOWERING_ABSENT at validate, positioned at its engine item`; `no database effect: the store file was never created …`; `the otherwise identical sqlite twin ships and writes …`; `postgres stays a recognised engine: an unknown engine refuses ENGINE_UNKNOWN instead`; `a postgres engine reached through extends refuses the same way`; `scenario mutant: bind refuses before the ship and write steps execute`; 7 × single-file validate mutants; `g1->g5 classify, migrate on a real store, and reopen at each generation`; `renamed column kept its data through the migration`; 6 × `evolution scenario … -> ship/…` | `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns`, `corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT` |
| G7 | Live correctness | 11 | `listener-scan counter is a live measurement (deliberate iteration increments it)`; `nested composition: a write inside the inner question routes inner and outer`; `scope-partitioned: the other scope's instance is not routed`; `result-neutral routed write emits no batch (outer unchanged)`; `irrelevant write … routes nothing and emits no batch`; `cross-scope write routes only the matching partition`; `zero listener scans across all commits (measured)`; `rolled-back transaction: no revision, no ledger row, no batch`; `moving a grouped key refreshes both the old and the new group`; `folded deltas equal one-shot recomputation after every committed revision`; `live bound is enforced at refresh (measured row count)` | `src/garns/live.py` |
| G8 | Ledger and capture | 12 | `declared changelog triggers exist in the generated schema with mapped names`; `external writes are captured as typed deltas with scope keys through a two-hop path`; `capture coverage denominators are measured from PRAGMA table_info`; `ledger records carry typed carrier/identity/scope/writer/transaction`; `incomplete changelog coverage refuses at load before any effect`; 7 × `pre-effect typed validation <CODE> -> <CODE>` | `corpus/conformance/worlds/ledgerhouse` |
| G9 | Evidence honesty | 5 | `delete/regenerate: committed generated/ trees are byte-identical to fresh generation`; `two generations in fresh directories are byte-identical`; `168 mutants execute real stages and match authored expectations`; `mutants cover decode, validate, ship, load, and runtime stages`; `detection unchanged after renaming files, stripping comments, and corrupting the manifest` | `corpus/mutants/expected.json`, `generated/` |
| G10 | Forbidden coupling | 14 | 8 × `no <forbidden pattern> in src/` (pluralization helper, `_id` suffix inference, `scope_id` column, first-item selection, corpus vocabulary, fallback SQL, numbered case dispatch, filename detector); `generated SQL contains no unmapped id/scope_id/_id conventions in physical names`; `public boundaries select worlds and reads by qualified name only`; `instrumentation counters increment on real operations only`; 2 × visitor exhaustiveness; `an unhandled IR node fails loudly in every visitor` | `src/garns/visit.py` |
| G11 | Target parity and measures | 2 | `rustc available`; `Python/Rust row-shape parity over unchanged generated SQL` | measures JSON: `live_bound` verified, `capture_denominators` verified, `rust_parity` verified, `token_bound` **`"unverified: not measurable from inside the build"`** |

**Total: 12 gates, 128 checks.** G11 is the only gate that shells out
(9 subprocess commands: 2 `rustc -O` compiles, 7 runner invocations). `tools/check.py` returns
`0 if report["all_pass"] else 1` (`tools/check.py:731`) and prints one
`PASS Gn <requirement>: k/n checks` line per gate followed by `ALL PASS`.

---

## What each layer proves and does not prove

**The unit suite proves the pipeline, not the lane.** `tests/` computes its own
oracles: SALES row expectations are recomputed in Python from the literal seed
tuples the test itself wrote (`tests/test_static_dynamic.py:25-47`), capture
denominators are recomputed from `expected_relation_keys` rather than pasted
(`tests/test_capture_ledger.py:133-139`), and physical column names are read back
out of the world's storage binding rather than spelled
(`tests/test_evolution.py:92-102`). Worlds are *discovered* from
`storage-<WORLD>.json` files on disk (`tests/support.py:47-58`), so adding a world
to the corpus extends coverage without editing the suite. What it cannot prove:
grammar freezing, cross-lane hygiene, and Rust parity — all of which live in
`tools/check.py`.

**The gate proves the exit-matrix contract, not the unit suite.** `tools/check.py`
does not invoke `tests/`; the two are independent readings of the same public
modules. Both must be run.

**Mutants prove later stages execute.** A single-file mutant only reaches
`decode`/`validate` (`src/garns/mutants.py:45-54`). A *scenario* mutant runs a
step list — `resolve`, `bind`, `lower`, `generate`, `ship`, `sql`, `open`,
`migrate`, `classify`, `window`, `write`, `capture`, `execute`, `subscribe`
(`src/garns/mutants.py:68-140`) — against a real in-memory SQLite store, so a
`ship`/`load`/`runtime` code is observed from a real state transition, not from a
constructed exception. 37 of the 168 cases are scenarios; the observed stage set
is `{accepted, decode, validate, ship, load, runtime}`.

**Mutant invariance proves the detector reads content only.** The shadow copy
renames every file, strips every comment, hashes every scenario directory name
and corrupts the manifest, then keys each observation by a digest of the mutant's
*bytes* (`tools/check.py:567-577`). Because the keys are content digests, the
check simultaneously proves that no two mutants have the same content
(`tests/test_mutants.py:102`).

**Metamorphic rename proves schema independence, not schema generality.** The
transform replays the resolver's own `Reference` map, so compiler code is never
touched; a rename that the compiler could special-case would show up as unequal
normalized IR. What it does not do is invent an unseen topology — a genuinely new
schema shape is still an unproved case, which is why a reviewer's private seed
(`tools/check.py:225`, the seed string is a parameter) is the right substitution
point for an independent attack.

**Parity proves encoding agreement, not a second implementation.** Both sides
execute the *same* generated SQL text against the *same* SQLite file; the Rust
side just uses SQLite's own text conversion through a 105-line FFI shim
(`src/garns_rust/sqlite.rs`) so that Python's `[type_code, text]` cells and
Rust's are comparable. See [ARCHITECTURE.md](ARCHITECTURE.md#generated-targets).

**Measures are reported honestly.** G11 emits four measure verdicts. Three name
the operation that measured them; `token_bound` is reported verbatim as
`"unverified: not measurable from inside the build"` (`tools/check.py:625`). If
`rustc` is absent, G11 records `rust_parity: "unverified: no Rust toolchain"` and
**fails** the check rather than skipping it (`tools/check.py:626-630`).

---

## Constructing a strong regression

Each playbook names the existing pattern to copy and the anti-pattern that makes
the result worthless. The universal anti-pattern: **never feed an expected code,
expected SQL, expected row, filename, comment marker, or stage into the thing
being tested.**

### Physical naming — metamorphic transform with a fresh seed

**Pattern.** Parse and resolve the world, call
`metamorphic.transform(files, program, world_name, seed, resolve_after)`, write
`tr.binding` to a temp file, `bind_world` the renamed program against it, and
compare `normalized_program_json(before) == normalized_program_json(after, tr.forward)`
plus rows, routing, batches and `live.stats`. Assert *positively* that the new SQL
contains a new physical name and *negatively* that it contains none of the old
ones. Reference: `tools/check.py:221-277`, `tests/test_metamorphic.py:33-71`.

**Use a seed nobody has used.** The seed is a plain parameter
(`tools/check.py:225` uses `"meta-seed-7"`); substituting your own is the whole
point of an independent attack. Both v9-5 reviewers substituted private seeds
at ratification; see [PROVENANCE.md](PROVENANCE.md).

**Anti-pattern.** Asserting a specific renamed table name, or reusing the
committed binding for the renamed program. Both re-introduce a naming convention
through the test.

### Comment and filename independence

**Pattern.** Copy `corpus/mutants` to a temp tree; strip every `#…` comment;
rename every `*.garns` to `mNNN.garns`; rename every scenario directory to a hash
of its old name; overwrite `expected.json` with `{"corrupted": true}`. Run
`observe_all` on both trees and compare **keyed by a digest of the comment-stripped
content**, not by name. Reference: `tools/check.py:555-577`,
`tests/test_mutants.py:63-109`.

**Anti-pattern.** Comparing by file name (the rename defeats it), or asserting
that the corrupted manifest "still loads" — it must be *unusable*, which
`tests/test_mutants.py:105-109` checks separately.

### Collisions

**Pattern.** Two modules declaring identical local names in two worlds, as in
`corpus/metamorphic/collision/{alpha,beta}.garns`. Build both worlds through
`binding_document(program, world, physical_scheme(world))` into temp bindings,
ship both, subscribe the same *local* read name in each, then assert: index key
sets disjoint and every key's carrier qualified with its own module prefix; a
write in one world routes that world only and the other's `last_routing` is
empty; the two same-named reads return different rows. Reference:
`tools/check.py:279-302`, `tests/test_metamorphic.py:74-128`.

**Anti-pattern.** Selecting a read by its bare local name. The public boundary
refuses that (`READ_UNKNOWN`, `src/garns/engine.py:211`), so a test that "works"
with a bare name is testing a helper you added, not the engine.

### Transactions

**Pattern.** Snapshot `engine.revision`, `len(engine.ledger_rows())`,
`live.last_routing` and every instance's `seq`; raise inside the
`with engine.transaction(...)` block; then assert *all four* are unchanged and
`tx.rolled_back` is true. Reference: `tools/check.py:454-465`,
`tests/test_live.py:86-115`. The mirror-image assertions — that a *committed*
transaction advances the revision by exactly one and appends exactly the expected
number of ledger rows — belong in the same test
(`tests/test_capture_ledger.py:87-93`).

**Anti-pattern.** Checking only the row count. Notification happens after commit
(`src/garns/engine.py:232-237`), so a rollback that still emitted a batch would
pass a row-only assertion.

### Capture

**Pattern.** Ship an `external_captured` world, write its tables with **raw SQL
through `store.conn`** — as the outside writer would — then call
`CaptureAdapter.acquire(txid)` and assert typed deltas, scope keys, writer and
transaction id. For the coverage refusal, do real DDL damage:
`ALTER TABLE <changelog> DROP COLUMN <mapped field>`, then assert
`WRITER_CAPTURE_INCOMPLETE` at stage `load` **and** that `engine.revision` is
unchanged. Reference: `tools/check.py:500-525`,
`tests/test_capture_ledger.py:113-167`. Denominators come from
`PRAGMA table_info` on the real changelog tables (`src/garns/capture.py:31-45`);
recompute the expected value from `expected_relation_keys` rather than pasting an
integer.

**Anti-pattern.** Writing through `tx.mint` in a captured world. That exercises
the governed path, not capture, and proves nothing about the triggers.

### Backend admission

**Pattern.** Take an *otherwise complete* deployment on freshly named
declarations — every required item present (`world`, `engine`, `at`, `ship`,
`mode`, `snapshot`, and here `pool 4`) — and attempt the whole effect path:
resolve → build a binding document → `bind_world` → `Store(...).ship()` →
`transaction(...).mint(...)`, against a **file-backed** store path. Then assert
three things together: the refusal is `("validate", "ENGINE_LOWERING_ABSENT", line, column)`
at the `engine` item; the store file **was never created**; and the otherwise
identical `engine sqlite` twin *does* ship and write. Add the negative control —
an unrecognised engine name still refuses `ENGINE_UNKNOWN`, proving `postgres`
remains recognised rather than deleted. Reference:
`tools/check.py::engine_lowering_regression` (`tools/check.py:346-385`, six
checks) and `tests/test_repair_engine_lowering.py` (five cases). Extend it with a
staged scenario mutant whose steps are bind → ship → write, so the later steps
can be *observed* not to run (`corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT`).

**Anti-pattern.** Asserting only that the resolver raised. Without the
"no store file exists" assertion and the SQLite twin, the test cannot distinguish
a pre-effect refusal from a post-effect one, nor a genuine engine guard from a
broken fixture.

---

## Snapshot counts

**Snapshot date 2026-09-04.** These are measurements of one tree at one moment,
not invariants. Re-measure rather than cite. "Verified here" means this document's
author re-ran the measurement; "read from" means it was taken from a recorded
artifact without re-running the writer.

| Quantity | Value | Source | Verified here |
|---|---|---|---|
| Unit tests | **103** across **10** modules (`test_capture_ledger` 15, `test_resolve` 16, `test_parse` 13, `test_live` 12, `test_static_dynamic` 12, `test_evolution` 10, `test_metamorphic` 8, `test_generate` 6, `test_mutants` 6, `test_repair_engine_lowering` 5) | `python -m unittest discover -s tests -t .` | yes — `Ran 103 tests … OK`, exit 0 |
| Gates / gate checks | **12** gates, **128** checks, all `ok`, `all_pass: true` | `gate-report.json` | read from the file (re-running rewrites it) |
| Mutant cases | **168** = **131** single-file + **37** scenario directories | `corpus/mutants/expected.json`, on-disk counts | yes — `observe_all` returned 168 with 0 mismatches |
| — by stage | validate **99**, decode **40**, runtime **18**, ship **6**, load **4**, accepted **1** | same | yes — observed stage histogram matches the manifest exactly |
| — distinct asserted codes | **124** | same | yes |
| Refusal fixtures | **12** sources + `expected.json` | `corpus/conformance/refusals/` | yes |
| Generated artifacts | **172** files across **8** worlds (APPFLOWY 5, APPFLOWY_VEC 5, EVERBILITY 32, LEDGERHOUSE 32, PRACTICE 50, REPORTING 8, SALES 20, VAULTWARDEN 20), plus `generated/INDEX.json` = 173 files on disk | `generated/INDEX.json`, on-disk count | yes — both agree; a fresh `generate()` of SALES into a temp dir reproduced the committed tree digest `7240ee4d…` exactly |
| World/binding pairs | **13** (`storage-<WORLD>.json` under `corpus/worlds` and `corpus/conformance/worlds`; 8 distinct worlds + 5 PRACTICE evolution generations) | on-disk count; matches G1's 13 `resolve+bind` checks | yes |
| Seed migration edits | **37**, each logged with its language reason | `grep -c '^- ' corpus/worlds/MIGRATION.md` (47-line file) | yes |
| `.garns` in `corpus/` | **254** (mutants 182, worlds 49, refusals 12, conformance worlds 6, metamorphic 3, static 1, dynamic 1) | `find corpus -name '*.garns'` | yes |
| Refusal codes implemented | **262** distinct (241 literal + 21 variable-chosen), catalogued as 266 code/stage rows | see below; [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) | yes — the 241/347 literal scan reproduced exactly, and the 21 variable-chosen codes were enumerated from their call sites |
| Python/Rust parity reads | **7** across 2 worlds | `gate-report.json` G11 | yes — an independent `rustc -O` compile of a temp copy of `generated/SALES/rust`, run against a temp store, matched Python's `[type_code, text]` rows byte-for-byte |

**How the refusal-code count is taken.** A read-only scan of every `src/**/*.py`
for the first string-literal argument of `refuse("…"`, `Refusal("…"`,
`_runtime("…"`, `_ship("…"` and `_fail("…"` yields **241 distinct codes at 347
raise sites** (distinct codes by file: `resolve.py` 120, `resolve_read.py` 56,
`engine.py` 19, `storage.py` 19, `evolution.py` 16, `parse.py` 6,
`lower_sqlite.py` 5, `capture.py` 4, `footprint.py` 3, `live.py` 2). **21
further codes** are selected through a variable rather than a literal argument
and so escape that scan: a ternary at the raise site
(`LINK_ENFORCEMENT_REPEATED` / `LINK_FLAG_REPEATED`, `src/garns/resolve.py:526`;
`QUESTION_LIVE_BOUND_DUPLICATED` / `READ_ITEM_REPEATED`,
`src/garns/resolve_read.py:529`; `CONSTRAINT_VIOLATED`,
`src/garns/engine.py:489`, `:522`), the two required-item loops over
`(key, code)` pairs (`src/garns/resolve.py:1043-1052`, `:1282-1291`), and a code
passed to a helper that raises it (`lookup` / `lookup_qualified`'s
`missing_code`, `literal_of_type`'s and `given_ref`'s `code`) — giving **262**.
Following the call sites is what makes 262 a measured total rather than a floor;
the per-code catalogue is [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue). The seven
stages are fixed in `src/garns/refuse.py:11`: `decode, validate, lower, generate,
ship, load, runtime`.

**Distribution of raise sites by stage** (same scan): validate 243, load 9,
decode 8, runtime 3, lower 2, ship 2 — plus the `_runtime(…)` and `_ship(…)`
helpers, which account for the bulk of the runtime and ship codes.
`generate` is a declared stage with **zero** raise sites; `lower` has exactly two,
both internal guards in `src/garns/lower_sqlite.py` (`:100`, `:242`) that the
resolver normally reaches first. See
[LIMITATIONS.md](LIMITATIONS.md#inventory).
