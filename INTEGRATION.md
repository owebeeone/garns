# Integration

How another system talks to Garns: the Python API, the CLI, the generated Rust
surface, which way dependencies point, and — clearly marked as **not
implemented** — the shape a `garns-glade` adapter would take. Construct semantics
belong to [DSL_REFERENCE.md](DSL_REFERENCE.md), module ownership to
[ARCHITECTURE.md](ARCHITECTURE.md), refusal codes to
[DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue), and the honest list of what does not
work to [LIMITATIONS.md](LIMITATIONS.md#inventory). Every command and every
output below was executed against the repository as it stands.

## Integration surfaces

| Surface | Entry point | Stability | Use it for | Do not use it for |
|---|---|---|---|---|
| **Python API** | `garns.parse`, `garns.resolve`, `garns.storage`, `garns.engine`, `garns.live`, `garns.capture`, `garns.evolution`, `garns.generate` | The real contract. Everything else is built on it | Embedding Garns in a Python service or tool; every gate and every test drives exactly these modules | Anything that needs a bare (unqualified) name |
| **CLI** | `garns` (or `python -m garns.cli`) — `resolve`, `generate`, `ddl`, `execute` | Thin argparse wrapper over the Python API | Scripting, inspection, CI probes, refusal checks by exit code | Serving traffic. `execute` opens a fresh store per invocation |
| **Generated SQL** | `generated/<WORLD>/queries/<qid>.sql`, `questions/<qid>.sql`, `schema.sql` | Byte-reproducible from source through the IR | Reading exactly what Garns will run; feeding a non-Python client | Editing. It is regenerated wholesale |
| **Generated descriptors** | `questions/<qid>.footprint.json`, `.binding.json`, `.routing.json` (questions only) | Byte-reproducible | Driving a client-side subscription — parameters, shape, scoped/capability, live bound, routing keys | Queries. A static query produces SQL and surfaces and nothing live-derived |
| **Generated Python surface** | `generated/<WORLD>/python/<qid with . → __>.py` | Constants + a 5-line `rows()` helper | Reading the lowered SQL and its column/key shape from another Python process | Execution with parameter validation, scope, capability or nested children — that is `Engine` |
| **Generated Rust surface** | `generated/<WORLD>/rust/` + `main.rs` + `sqlite.rs` | Parity instrument | Proving another language reads the same rows | A client library. See below |
| **Storage binding** | `storage-<WORLD>.json`, schema `garns-v9-5/storage-binding/1` | Versioned input document | Owning your physical names; renaming anything without touching Garns | Omitting a mapping. There are no defaults |
| **Gate report** | `gate-report.json`, schema `garns-v9-5/gate-report/1` | Machine-readable record of one run | Reading gate results, subprocess argv/exit codes, evidence paths | Trusting it after the tree changed — it describes its own mtime |
| **Generated index** | `generated/INDEX.json`, schema `garns-v9-5/generated-index/1` | Per-world `source`, `binding`, `files`, `tree_sha256` | Verifying committed artifacts without regenerating | — |

## Python API

The call sequence is the same in every consumer — `tools/check.py`, `tests/`,
`src/garns/cli.py` and `src/garns/mutants.py` all follow it:

```
garns_files(dir) ─► parse_paths ─► resolve_files ─────────────────────► ir.Program
                             storage-<WORLD>.json ─► bind_world(program, "WORLD", path)
                                                                      ─► WorldIR
   ├─ Store(world, path).ship() ─► Engine(store, clock=…)
   │        ├─ engine.execute(read_qid, params, scope, capabilities)   ─► Result
   │        ├─ engine.transaction(writer, tx_id) ─► .mint / .change / .delete
   │        ├─ LiveEngine(engine).subscribe(read_qid, …) ─► Instance, Batch, fold(…)
   │        ├─ CaptureAdapter(engine).acquire(tx_id)      (external_captured worlds)
   │        └─ evolution.classify / migrate / open_store
   ├─ generate(world, out_dir)                            ─► path -> sha256
   └─ derive_footprint(world, read)                       ─► Footprint (questions only)
```

Three rules the boundary enforces, so callers should not fight them:

* **Everything is selected by qualified name** — `bind_world(program, "SALES", …)`,
  `engine.execute("sales_static.open_orders_once")`,
  `tx.mint("sales.Customer", {"sales.Customer.name": …})`,
  `live.subscribe("sales.open_orders")`. A bare name refuses `WORLD_UNKNOWN` /
  `READ_UNKNOWN` / `LEDGER_CARRIER_UNKNOWN` / `LEDGER_FIELD_UNKNOWN`.
* **The binding is an input** — `bind_world` reads a JSON document from disk and
  never invents a name; `binding_document(program, world, names)` is an authoring
  aid the compiler never calls.
* **Refusal is the only failure channel** — catch `garns.refuse.Refusal`, which
  carries `code`, `stage`, `file`, `line`, `column`, `detail` and `as_dict()`.

### A complete pass through every seam

Run from the repository root; the store lives in a `tempfile` directory and
nothing in the repository is written.

```python
"""One pass through every public seam of Garns, against the SALES world."""
import tempfile
from pathlib import Path
from garns.capture import CaptureAdapter
from garns.engine import Engine, Store
from garns.evolution import classify, open_store
from garns.footprint import derive_footprint
from garns.live import LiveEngine, canonical_rows, fold
from garns.parse import garns_files, parse_paths
from garns.refuse import Refusal
from garns.resolve import resolve_files
from garns.storage import bind_world

SRC = Path("corpus/conformance/worlds/sales")
TMP = Path(tempfile.mkdtemp(prefix="garns-tour-"))
key = lambda row: canonical_rows([row])
ORDERS = [("A", "open", 120, 5), ("A", "open", 30, 7), ("B", "open", 200, 6), ("B", "closed", 999, 8)]

# 1-2  decode + validate -> one Program; then select one world by name and bind it
program = resolve_files(parse_paths(garns_files(SRC)))
world = bind_world(program, "SALES", SRC / "storage-SALES.json")
print("1 program:", len(program.modules), "modules,", len(program.carriers), "carriers,",
      len(program.reads), "reads |  2 world:", world.world.name, [c.qid for c in world.relations])

# 3  ship: DDL + generation row on a real file-backed store
store = Store(world, str(TMP / "sales.sqlite")); store.ship()
engine = Engine(store, clock=lambda: 50); live = LiveEngine(engine)
print("3 shipped:", open_store(store.conn, world, program.deployments[0])["generation"])

# 4  write: one transaction, typed pre-effect validation, one revision
with engine.transaction("governed", "seed") as tx:
    cust = {c: tx.mint("sales.Customer", {"sales.Customer.customer_id": c, "sales.Customer.name": n})
            for c, n in (("A", "Acme"), ("B", "Bolt"))}
    ids = [tx.mint("sales.Order", {"sales.Order.order_id": f"O{n}", "sales.Order.status": s,
                                   "sales.Order.total": t, "sales.Order.created_at": at,
                                   "sales.Order.customer": cust[c]})
           for n, (c, s, t, at) in enumerate(ORDERS)]
print("4 revision", engine.revision, "| ledger rows", len(engine.ledger_rows()))

# 5-6  a static query by qualified name; then a question, its footprint and its rows
print("5 query:", engine.execute("sales_static.revenue_open_by_customer", {"floor": 10}).rows)
inst = live.subscribe("sales.open_orders")
print("6 initial:", canonical_rows(inst.rows()))
print("6 atoms:", sorted((a.carrier, a.field)
                         for a in derive_footprint(world, program.read("sales.open_orders")).atoms))

# 7  route: a relevant write emits one batch; folding it equals recomputation
before, before_keys = inst.rows(), list(inst.order)
with engine.transaction("governed", "t2") as tx:
    tx.change("sales.Order", ids[3], {"sales.Order.status": "open"})
batch = live.last_batches[inst.id]
print("7 routed:", live.last_routing, "| changes:", [(c.op, c.key) for c in batch.changes],
      "| stats:", live.stats.as_dict())
print("7 fold == one-shot:", canonical_rows(sorted(fold(before, before_keys, [batch]), key=key))
      == canonical_rows(sorted(engine.execute("sales.open_orders").rows, key=key)))

# 8  delete commits; an aborted transaction leaves revision and ledger untouched
with engine.transaction("governed", "t3") as tx:
    tx.delete("sales.Order", ids[0])
mark = (engine.revision, len(engine.ledger_rows()))
try:
    with engine.transaction("governed", "t4") as tx:
        tx.delete("sales.Order", ids[1]); raise RuntimeError("abort")
except RuntimeError:
    pass
print("8 committed", mark, "| after rollback", (engine.revision, len(engine.ledger_rows())),
      "| rolled_back", tx.rolled_back)

# 9-10  capture is per world (SALES is governed, so it refuses); then classify and reopen
try:
    CaptureAdapter(engine).acquire("ext-1")
except Refusal as r:
    print("9 capture:", r.code, f"[{r.stage}]")
print("10 classify:", classify(program, program).compat,
      "| reopen:", open_store(store.conn, world, program.deployments[0])["generation"])
```

Invocation and its verified output:

```console
$ PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tour.py
1 program: 2 modules, 2 carriers, 4 reads |  2 world: SALES ['sales.Customer', 'sales.Order']
3 shipped: 1
4 revision 1 | ledger rows 6
5 query: [{'customer': 'Bolt', 'revenue': 200.0, 'orders': 1, 'average_order': 200.0}, {'customer': 'Acme', 'revenue': 150.0, 'orders': 2, 'average_order': 75.0}]
6 initial: [{"customer":"Acme","identity":2,"total":30.0},{"customer":"Bolt","identity":3,"total":200.0},{"customer":"Acme","identity":1,"total":120.0}]
6 atoms: [('sales.Customer', '*'), ('sales.Customer', 'sales.Customer.name'), ('sales.Order', '*'), ('sales.Order', 'sales.Order.created_at'), ('sales.Order', 'sales.Order.customer'), ('sales.Order', 'sales.Order.status'), ('sales.Order', 'sales.Order.total')]
7 routed: {'inst1': True} | changes: [('upsert', (4,))] | stats: {'probes': 62, 'candidates': 1, 'refreshes': 1, 'listener_scans': 0, 'batches': 1}
7 fold == one-shot: True
8 committed (3, 8) | after rollback (3, 8) | rolled_back True
9 capture: CAPTURE_NOT_DECLARED [runtime]
10 classify: additive | reopen: 1
```

Reading it: 6 ledger rows for 6 mints in one revision; the footprint covers
subject structure (`*`), every projected and predicated field, and the joined
carrier; one relevant write routes exactly one instance and emits a single
`upsert` keyed by the hidden `$k0` identity `4`; `listener_scans` stays `0`
because routing probes the index rather than iterating the registry; and the
aborted transaction leaves revision and ledger at `(3, 8)`, where the committed
delete left them.

### Signatures and their refusals

| Call | Contract |
|---|---|
| `Store(world, path=":memory:")` / `.ship(generation=1, revision=0)` | runs the whole DDL as one script, then inserts the generation row (`ordinal`, `ir_digest`, `storage_digest`, `shipped_at_revision`) |
| `Engine(store, clock=None)` / `.transaction(writer, transaction_id, clock=None)` | validates the writer and the id (`^[A-Za-z0-9_-]{1,64}$`) **before** `BEGIN`; `mint`/`change`/`delete` each run typed pre-effect ledger validation before any statement; on normal exit it writes the revision row plus one ledger row per delta, commits, and **then** notifies listeners |
| `Engine.execute(read_qid, params=None, scope=None, capabilities=(), clock=None)` | binds strictly — `PARAM_UNKNOWN`, `PARAM_REQUIRED`, `PARAM_TYPE`, `SCOPE_REQUIRED`, `CAPABILITY_REQUIRED` — and returns `Result(rows, keys, total)`; `total` is `None` unless the read declares `with_total` |
| `LiveEngine.subscribe(read_qid, params=None, scope=None, capabilities=())` | refuses `QUERY_NOT_LIVE` for a static query *before any registration*; derives the footprint, does the initial fetch, and only then registers routing keys, so a failed fetch leaves no partial registration |
| `CaptureAdapter(engine).acquire(transaction_id)` | `writers external_captured` worlds only (`CAPTURE_NOT_DECLARED` otherwise); checks changelog coverage against `PRAGMA table_info` first (`WRITER_CAPTURE_INCOMPLETE`, stage `load`, before any effect), then writes one revision of typed deltas and notifies |
| `classify(before, after, history, retention)` → `migrate(conn, before_world, after_world, cl, generation)` → `open_store(conn, world, deployment)` | the generation walk; `open_store` refuses `STORE_UNSHIPPED`, `STORE_BEHIND` or `STORE_DRIFT` |

## CLI

The `pyproject.toml` installs a `garns` console script. From a source checkout,
invoke the equivalent module directly:
`PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m garns.cli <subcommand> …`

| Subcommand | Signature | Prints |
|---|---|---|
| `resolve` | `resolve <source-dir> [--json]` | a one-line summary, or the canonical IR with `--json` |
| `generate` | `generate <source-dir> --world W --binding B --out DIR` | `generated N files under DIR` |
| `ddl` | `ddl <source-dir> --world W --binding B` | the schema DDL on stdout |
| `execute` | `execute <source-dir> --world W --binding B --read module.name [--param k=v]… [--scope N] [--capability C]… [--store PATH] [--ship]` | `{"rows": …, "total": …}` as JSON |

`--world`, `--binding` and `--read` are **required**; nothing is selected by
position. `--param` values are JSON (`floor=10`, `kind="sister"`, `ids=[1,2]`);
`--capability` repeats; `--store` defaults to `:memory:`, so a one-shot `execute`
normally wants `--ship` too — and then reads an empty store. **Exit codes:** `0`
success; `2` a `Refusal`, printed to **stderr** as
`refused: CODE [stage] at file:line:col: detail` (`src/garns/cli.py:85-87`);
argparse's own `2` for a usage error.

### Verified transcripts

```console
$ S=corpus/conformance/worlds/sales; R=corpus/conformance/worlds/reporting
$ PYTHONPATH=src … -m garns.cli resolve $S                            # exit 0
resolved 2 modules, 2 carriers, 4 reads, 1 worlds
$ PYTHONPATH=src … -m garns.cli generate $S --world SALES \
      --binding $S/storage-SALES.json --out /tmp/gen-sales            # exit 0
generated 20 files under /tmp/gen-sales
$ PYTHONPATH=src … -m garns.cli ddl $R --world REPORTING \
      --binding $R/storage-REPORTING.json | head -5                   # exit 0
CREATE TABLE "ta_a841ea5a67" (
  "id_56e790d195" INTEGER PRIMARY KEY,
  "co_1672fa0252" TEXT NOT NULL,
  "co_01dbbfc0f1" TEXT NOT NULL,
  UNIQUE ("co_1672fa0252")
```

Against a store shipped and seeded beforehand (`--store` pointing at that file),
scope and capability behave exactly as the Python boundary does. All four runs
below use `P=corpus/worlds/practice` with
`--world PRACTICE --binding $P/storage-PRACTICE.json --store /tmp/practice.sqlite`:

```console
$ … --read labels.vip_clients --scope 1
{ "rows": [ { "preferred_name": "Ann" } ], "total": null }             # exit 0

$ … --read labels.vip_clients                                # no --scope
refused: SCOPE_REQUIRED [runtime] at 1:1: labels.vip_clients is scoped; a scope identity is required
                                                                       # exit 2

$ … --read clients.all_clients_for_audit                     # no --capability
refused: CAPABILITY_REQUIRED [runtime] at 1:1: clients.all_clients_for_audit is unscoped behind capability practice_audit
                                                                       # exit 2

$ … --read clients.all_clients_for_audit --capability practice_audit
{ "rows": [ { "archived_at": null, "owner.email": "one@x",
              "preferred_name": "Ann" } ], "total": null }             # exit 0

$ … --read sales.not_a_read --ship                           # against SALES
refused: READ_UNKNOWN [runtime] at 1:1: sales.not_a_read is not a read of world SALES; reads are selected by qualified name
                                                                       # exit 2
```

(The two successful payloads are shown compacted; the CLI pretty-prints with
`indent=1`.) The CLI is also the cleanest way to prove a refusal is
**pre-effect**: point `generate` at a source whose deployment names an unlowered
engine, with a deliberately missing binding and a nonexistent `--out`.

```console
$ PYTHONPATH=src … -m garns.cli generate /tmp/pgcase --world ARCHIVE \
      --binding /tmp/pgcase/NO-SUCH.json --out /tmp/pgcase/SHOULD-NOT-EXIST
refused: ENGINE_LOWERING_ABSENT [validate] at /tmp/pgcase/ENGINE_LOWERING_ABSENT-1.garns:24:10: deployment ARCHIVE_STORE uses engine postgres, which this build recognises but cannot lower (lowered engines: sqlite)
                                                                       # exit 2
$ ls /tmp/pgcase
ENGINE_LOWERING_ABSENT-1.garns
```

The refusal names the `engine` item's own position (24:10); `SHOULD-NOT-EXIST`
was never created and the missing binding was never opened. See
[COMPILER_PIPELINE.md](COMPILER_PIPELINE.md#earliest-pre-effect-validation-boundary).

## Generated Rust surface

`generated/<WORLD>/rust/` contains, per world:

| File | Contents |
|---|---|
| `<qid with . → __>.rs` | one constants module per read: `READ`, `NOUN`, `SQL` (the lowered plan text, **unchanged**, as a raw string), `PARAMS`, `COLUMNS`, `SCOPED`, `USES_CLOCK` |
| `main.rs` | a binary that matches the qualified read name to its `SQL` + `PARAMS` and calls `sqlite::run` |
| `sqlite.rs` | 105 lines of raw `#[link(name = "sqlite3")]` FFI, copied verbatim from `src/garns_rust/sqlite.rs` |

**Compile** — no crate, no `Cargo.toml`, no dependencies:
`rustc -O -o /tmp/runner <copy>/rust/main.rs`. Verified with `rustc 1.96.0`; it
emits snake-case naming warnings only (`warning: 4 warnings emitted`), exit 0.

**Argument encoding** — `runner <db> <read> [name=kind:value …]`, where `kind` is
`i` (int), `f` (float), `s` (text) or `n` (null). The name is bound as `:name`;
an argument naming a parameter the SQL does not use is skipped silently
(`src/garns_rust/sqlite.rs:64-76`). Engine-owned parameters go through the same
channel: `_scope=i:1`, `_clock=i:50`, `_parents=s:[1,2,3]`.

**Output encoding** — one JSON array per row, one `[type_code, text]` cell per
column, using SQLite's own text conversion. Type codes are SQLite's:
`1` integer, `2` float, `3` text, `4` blob (hex), `5` null.

**Verified transcript** (temp copy of `generated/SALES/rust`, temp store seeded by
Python, same read, same parameters):

```console
$ rustc -O -o /tmp/runner /tmp/rustwork/rust/main.rs         # exit 0, 4 warnings
$ /tmp/runner /tmp/sales.sqlite sales_static.revenue_open_by_customer floor=i:10
[[3,"Bolt"],[3,"Bolt"],[2,"200.0"],[1,"1"],[2,"200.0"]]
[[3,"Acme"],[3,"Acme"],[2,"150.0"],[1,"2"],[2,"75.0"]]
                                                                      # exit 0
$ diff python-rows.txt rust-rows.txt && echo IDENTICAL
IDENTICAL

$ /tmp/runner /tmp/sales.sqlite sales.open_orders                     # exit 0
[[1,"2"],[1,"2"],[3,"Acme"],[2,"30.0"]]
[[1,"3"],[1,"3"],[3,"Bolt"],[2,"200.0"]]
[[1,"1"],[1,"1"],[3,"Acme"],[2,"120.0"]]
$ /tmp/runner /tmp/sales.sqlite nope.read                             # exit 3
unknown read nope.read
$ /tmp/runner                                                         # exit 2
usage: runner <db> <read> [name=kind:value ...]
```

The leading duplicate cell in each row is the hidden `$k0` identity column, which
the SQL selects and `Plan.columns` excludes — the runner prints raw columns, so
hidden keys are visible here in a way they never are through `Engine`.

**Honest limitations of this surface.** It is a parity and evidence instrument,
not a client library.

* Not a bindings library: no crate, no published API, no error type, no
  connection reuse, no async, no pooling. `main.rs` opens the database, runs one
  statement and exits; failure paths `std::process::exit` with bare codes (`4`
  open, `5` prepare, `6` step). It links the **system** `libsqlite3`.
* The SQL is embedded unchanged, and the runner performs **none** of `Engine`'s
  checks — no parameter typing, no `SCOPE_REQUIRED`, no `CAPABILITY_REQUIRED`, no
  live bound, no nested-child attachment, no `with_total`.
* `world … { generated <targets> }` does not gate emission: the Rust tree is
  written for every world regardless of the declared target list — see
  [LIMITATIONS.md](LIMITATIONS.md#inventory). How the surface is produced is in
  [ARCHITECTURE.md](ARCHITECTURE.md#generated-targets); what G11 proves about it
  is in [TESTING.md](TESTING.md#gate-matrix-g0g11).

## Dependency direction

Garns depends on **nothing outside the standard library except `lark`**, and on
no other repository. There is no Glade code, no Taut code and no reference to
either in the implementation, the corpus or the generated artifacts. `rustc` is
required only to run G11.

```
   garns  (this repository: lark + stdlib, nothing else)
     ▲            ▲                    ▲
     │            │                    │
garns-glade   other adapters   downstream services importing garns directly
(proposed)
```

Consequences, in both directions:

* **Garns must never import an adapter.** The moment it does, "one IR, many
  consumers" becomes "one IR, one privileged consumer", and the
  schema-independence property that G5 measures stops being structural.
* **Adapters import Garns, pinned by version.** They consume `WorldIR`, `Plan`,
  `Footprint`, `Delta`, `Batch` and the generated descriptors; they never
  re-derive a source fact and never construct a physical name.
* **The repository layout is stable** — `grammar/garns.lark`,
  `src/garns/`, `src/garns_rust/sqlite.rs`, `tests/`, `tools/`, `corpus/`,
  `generated/`. Paths throughout this documentation set use that layout.

## Proposed garns-glade integration shape

> **PROPOSED — NOT IMPLEMENTED.** No `garns-glade` package, module, branch or
> stub exists in this repository. Nothing below has been built or tested. It is
> recorded so that a future adapter is an *addition* at seams that already exist,
> rather than a rewrite. Read every sentence in this section as design intent,
> not as a description of code.

**Shape.** A thin, stateless adapter over the existing SQLite runtime, consuming
`WorldIR` / `Plan` / `Footprint` through the seams enumerated in
[ARCHITECTURE.md](ARCHITECTURE.md#seams-for-a-future-rustglade-adapter). It would
own transport, session and presentation, and no semantics at all.

### Public symbols it would import

| From | Symbols | Why |
|---|---|---|
| `garns.parse` / `garns.resolve` | `garns_files`, `parse_paths`, `resolve_files` | source discovery and the single Program |
| `garns.storage` | `bind_world`, `WorldIR` | world selection + authored physical names |
| `garns.engine` | `Store`, `Engine`, `Result`, `Delta`, `FieldChange` | execution and governed writes |
| `garns.live` | `LiveEngine`, `Instance`, `Batch`, `Change`, `fold`, `canonical_rows` | subscriptions and deltas |
| `garns.footprint` | `derive_footprint`, `Footprint`, `Atom` | routing keys, if not read from descriptors |
| `garns.capture` | `CaptureAdapter` | `external_captured` worlds only |
| `garns.evolution` | `classify`, `migrate`, `open_store`, `check_window` | generation lifecycle |
| `garns.refuse` | `Refusal` | the single failure channel; map `(code, stage)` to transport status |

It would **not** import `garns.metamorphic`, `garns.mutants`, `garns.lower_sqlite`
internals (`_Frame`, `_Lowerer`, `_ShowLowerer`), or
`garns.storage.binding_document`.

### What it must not do

* **No name guessing** — never construct or infer a table, column, identity or
  changelog name, and never call `binding_document`.
* **No bypassing `bind_world`** — building a `WorldIR` / `StorageMapping` /
  `RelationMapping` directly skips 17 `STORAGE_*` validations and reintroduces
  exactly the adapter-defaults defect the binding exists to prevent.
* **No second query path** — all SQL comes from `lower_read` via `Engine`; no
  hand-written SQL, no interpolation into a `Plan`, no "fast path".
* **No bare names at the boundary** — reads, carriers, fields and worlds stay
  qualified all the way to the wire.
* **No reconstructed row identity** — use `Result.keys` and `Change.key`, never
  re-derive from visible columns, never expose the hidden `$k` columns.
* **No swallowed refusals** — translate `(code, stage, position)`; do not turn a
  `Refusal` into an empty result.

### How live batches would plug in

`LiveEngine` is already a listener on `Engine` (`engine.listeners`), and
`on_commit(revision, deltas)` returns `{instance_id: Batch | None}` after
refreshing every routed instance. An adapter would `subscribe(read_qid, params,
scope, capabilities)` per client subscription, keep the returned `Instance.id`
beside the transport channel, send `Instance.rows()` plus `Instance.seq` as the
initial snapshot, then forward `Batch.as_dict()` (`instance`, `base_seq`, `seq`,
`revision`, `changes` of `upsert`/`delete` keyed by the plan's key tuple) for the
instances a client holds. A `None` batch is a routed but result-neutral write:
send nothing. `base_seq`/`seq` give gap detection — on a gap, resubscribe rather
than guess — and `fold(initial, keys, batches)` is the same client-side
reconciliation the fold-equivalence gate compares against a one-shot
recomputation.

Two properties must survive the adapter and are measurable from
`LiveEngine.stats`: routing must never iterate the registry
(`listener_scans == 0`), and a rolled-back transaction must produce no revision,
no ledger row and no batch. Assert both in the adapter's own tests. Four
constraints it inherits and cannot soften: a refresh over `live bounded N`
refuses `LIVE_BOUND_EXCEEDED` rather than truncating; there is no `unsubscribe`,
so instance lifetime is the adapter's problem; `unscoped C` instances are probed
in every scope; and capabilities and writer names are caller-asserted strings,
not authorisations — see
[LIMITATIONS.md](LIMITATIONS.md#assumptions-downstream-consumers-must-not-make).

### How a PostgreSQL backend would later replace the refusal

Today a deployment naming `postgres` refuses `ENGINE_LOWERING_ABSENT` at
`validate`, before any effect, because `LOWERED_ENGINES = {"sqlite"}`
(`src/garns/resolve.py:28`). That refusal is the *specification* of the work: it
disappears exactly when a lowering exists, and not before. The order that keeps
it honest at every step: add a sibling lowering module producing the same `Plan`
contract; introduce a dialect seam so `Engine` selects a lowering from the
deployment's engine instead of importing `lower_sqlite` directly; provide the
store, the changelog acquisition mechanism (the current one is SQLite triggers)
and the migration statements; then, and only then, add `"postgres"` to
`LOWERED_ENGINES`. Removing it from the set any earlier re-admits a deployment
that cannot ship — the precise defect the refusal was added to close. The
regressions that must keep passing are
`tools/check.py::engine_lowering_regression` and
`tests/test_repair_engine_lowering.py`; when PostgreSQL lands they become the
template for whichever engine is *next* recognised but not yet lowered, not
files to delete.

The full playbook — adding a target, adding a backend, adding an IR node, adding
a refusal code — is in [EXTENDING_GARNS.md](EXTENDING_GARNS.md).
