# B2 test suite

A stdlib `unittest` suite that exercises the B2 implementation through its
public modules — the same surfaces `tools/check.py` uses, driven from the
outside.

## Running

From `build/B2`:

```
uv run --offline --with lark python -m unittest discover -s tests -t .
```

Add `-v` for per-test names, or run one module:

```
uv run --offline --with lark python -m unittest tests.test_live -v
```

`tests/__init__.py` and `tests/support.py` put `build/B2/src` on `sys.path`, so
no install step and no `PYTHONPATH` are needed. `lark` is the only third-party
dependency. Nothing outside `build/B2/tests` is written: stores are in-memory
or in `tempfile` directories that are removed on teardown, and the committed
`generated/` tree is only ever read.

## What each module covers

| Module | Area |
|---|---|
| `test_parse.py` | Every admitted corpus source parses with locations; the frozen refusals in `corpus/conformance/refusals` reproduce their recorded stage and code; decode codes come from parser state (`SOURCE_NOT_GARNS`, `MEANS_REQUIRED`, `SOURCE_TRUNCATED`, `EXPR_NOT_ADMITTED`). |
| `test_resolve.py` | Every world discovered from a `storage-<WORLD>.json` resolves and binds; qualified identities everywhere; multihop scope paths (`clients.Contact`, `pantry.Jar`); exhaustive visitor checks over `FootprintDeriver`, `_Lowerer` and `_ShowLowerer`. |
| `test_static_dynamic.py` | SALES: query/question row parity through `canonical_rows`; the richer static query (group / having / arithmetic / call / non-path order) executes; subscribing a query refuses `QUERY_NOT_LIVE` before any registration; no live artifact is generated for a static read. |
| `test_live.py` | PRACTICE: recursive composition routing, scope partitioning, zero listener scans, result-neutral writes, rollback; LEDGERHOUSE: old/new group keys under external capture and fold-equals-one-shot at every revision. |
| `test_capture_ledger.py` | Typed pre-effect ledger refusals (writer, transaction, carrier, field, value, scope) with the store proven unchanged; capture coverage measured from `PRAGMA table_info`; a dropped changelog column refuses `WRITER_CAPTURE_INCOMPLETE` at load. |
| `test_evolution.py` | g1→g5 classify, migrate and reopen on one real store; renamed and restored columns keep their data; the six ship-stage evolution scenarios refuse with their own codes. |
| `test_metamorphic.py` | A full deterministic rename leaves `normalized_program_json` unchanged and moves every physical name; the collision fixture keeps two identically-named modules apart at runtime. |
| `test_mutants.py` | `observe_all` matches `corpus/mutants/expected.json`; detection is unchanged after copying the corpus with renamed files, stripped comments and a corrupted manifest. |
| `test_generate.py` | Generation is deterministic and self-cleaning; the committed `generated/<WORLD>` trees are reproduced by a fresh generation. |

## Rules the suite follows

- **Expectation files are assertions, never inputs.** `expected.json` (refusals
  and mutants) is read only after the outcome has been observed by running the
  production pipeline.
- **No answers are supplied to the implementation.** No SQL text, no expected
  refusal code, and no corpus-specific hint reaches the compiler. Row
  expectations are computed in the test from the rows the test itself seeded
  (`tests/support.py`), and physical names are read back out of the world's
  storage binding rather than spelled here.
- **Selection is by qualified name only**, because that is the only selection
  the public boundaries admit.
- **Worlds are discovered, not listed.** `discovered_worlds()` finds every
  `storage-<WORLD>.json` in the corpus, so a new world is covered without
  editing the suite.

## Known failure

`test_generate.TestCommittedTree.test_regeneration_from_a_relocated_copy_of_the_corpus_is_byte_identical`
fails against the current tree. `StorageMapping.source` keeps the storage
binding path exactly as it was passed to `bind_world`, and `generate()`
serializes it into `generated/<WORLD>/ir.json` (one `"source"` line per world,
currently an absolute path on the build machine) and therefore into
`manifest.json`. Regenerating from a copy of the corpus at any other location
produces different bytes, so delete/regenerate byte identity only holds from
the exact directory that produced the committed tree. Everything else in the
suite passes.
