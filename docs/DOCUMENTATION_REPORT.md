# Documentation report

> Historical v9-5 documentation-production record. Commands and lane paths in
> this file are evidence history, not current v9-6 operating instructions.

How this documentation set was produced, what was checked against the running
implementation, what was changed to make eleven documents agree, and what is
still open. Written at the close of the v9-5 documentation pass, 2026-09-04.

Scope note: this report is **v9-5-lane machinery**. It describes a review lane
that will not exist in the Garns repository; see
[`## Recommended documentation to carry into a future garns-wz repository`](#recommended-documentation-to-carry-into-a-future-garns-wz-repository).

---

## Files produced

Eleven documents, 4,644 lines. Nine were drafted by four parallel agents;
[README.md](README.md) and this report were written in the closing pass, which
also performed the cross-document consistency edits recorded below.

| File | Lines | Author agent role | Scope |
|---|---:|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 467 | structure & pipeline | Components, dependency direction, identity/scope/routing/transaction models, generated targets, adapter seams, per-component sustainability verdict |
| [COMPILER_PIPELINE.md](COMPILER_PIPELINE.md) | 518 | structure & pipeline | Twelve phases with inputs, outputs, invariants and owned diagnostics; the pre-effect boundary proof; artifact lifecycle |
| [DSL_REFERENCE.md](DSL_REFERENCE.md) | 924 | language & diagnostics | The whole surface language, construct by construct, with the rule each refuses on; three runnable minimal examples; a refusal-snippet table |
| [DIAGNOSTICS.md](DIAGNOSTICS.md) | 553 | language & diagnostics | The canonical refusal catalogue (262 codes, 266 code/stage rows), how codes are produced and positioned, and the non-`Refusal` exceptions that still escape |
| [AI_DEVELOPER_GUIDE.md](AI_DEVELOPER_GUIDE.md) | 256 | process & verification | Agent operating manual: repository map, per-task reading recipes, invariants, traps, change-impact map, definition of done |
| [TESTING.md](TESTING.md) | 361 | process & verification | What each verification layer proves and does not prove; every command with its blast radius; gate matrix; how to write a non-circular regression; snapshot counts |
| [EXTENDING_GARNS.md](EXTENDING_GARNS.md) | 471 | process & verification | Playbooks for adding a construct, diagnostic, lowering, engine backend, target or adapter, and the rules each must not break |
| [LIMITATIONS.md](LIMITATIONS.md) | 182 | honesty & integration | Inventory of refused / narrow / unconsumed / absent behaviour with the code that proves it; caller assumptions to avoid; evidence-only surfaces |
| [INTEGRATION.md](INTEGRATION.md) | 449 | honesty & integration | Python API, CLI, generated descriptors and Rust surface, dependency direction, proposed (**not implemented**) `garns-glade` shape |
| [README.md](README.md) | 220 | documentation close | What Garns is and is not, toolchain and targets, five-minute orientation, document map, reading paths, status snapshot |
| [DOCUMENTATION_REPORT.md](DOCUMENTATION_REPORT.md) | 243 | documentation close | This report |

Agent attribution is **inferred**, not recorded: the drafts carry no author
metadata, so the groupings above come from modification-time clusters at
drafting (16:03–16:04, 16:08, 16:15–16:16, 16:30) plus each pair's internal
cross-referencing. Treat the "author agent role" column as a description of
scope ownership, not as provenance.

## Implementation sources used per document

Every document was written against `build/B2` as it stands. Paths are relative
to that build root, which is also the future repository layout.

| Document | Primary implementation sources | Corpus / artifacts | Lane evidence |
|---|---|---|---|
| ARCHITECTURE.md | all of `src/garns/` (dependency direction), `ir.py`, `storage.py`, `lower_sqlite.py`, `engine.py`, `live.py`, `footprint.py`, `capture.py`, `evolution.py`, `generate.py`, `surfaces.py`, `visit.py`, `src/garns_rust/sqlite.rs` | `corpus/conformance/worlds/{sales,reporting,ledgerhouse}`, `generated/` | `build/B2/README.md`, `REPAIR.md` |
| COMPILER_PIPELINE.md | `parse.py`, `resolve.py`, `resolve_read.py`, `storage.py`, `lower_sqlite.py`, `engine.py`, `footprint.py`, `live.py`, `capture.py`, `evolution.py`, `generate.py`, `surfaces.py`, `cli.py`, `refuse.py` | `generated/INDEX.json`, `corpus/conformance/refusals/` | `gate-report.json`, `REPAIR.md` §1.2 |
| DSL_REFERENCE.md | `grammar/garns.lark`, `ast.py`, `parse.py`, `resolve.py`, `resolve_read.py`, `types.py`, `calls.py`, `storage.py`, `evolution.py`, `footprint.py` | `corpus/worlds/MIGRATION.md`, `corpus/conformance/worlds/ledgerhouse`, three purpose-built temp worlds | `brief/00-Constitution.md`, `brief/01-GrammarDecision.md` |
| DIAGNOSTICS.md | `refuse.py`, and a full scan of `src/garns/**/*.py` for every refusal construction; `parse.py::classify_decode`; `mutants.py` | `corpus/mutants/expected.json`, `corpus/conformance/refusals/expected.json`, `tests/` | `gate-report.json`, both `reviews/*/REVIEW.md` |
| AI_DEVELOPER_GUIDE.md | the module inventory of `src/garns/`, `tools/*.py`, `tests/` | `corpus/**`, `generated/**`, `gate-report.json` | `tools/check_scaffold.py`, `FROZEN.json` |
| TESTING.md | `tools/check.py` (gate bodies and check labels), `mutants.py`, `metamorphic.py`, `tests/**` | `corpus/mutants/`, `corpus/metamorphic/collision/`, `generated/INDEX.json` | `gate-report.json`, both reviews' rerun lists |
| EXTENDING_GARNS.md | `visit.py`, `ir.py`, `resolve.py` registries, `lower_sqlite.py`, `surfaces.py`, `generate.py`, `calls.py`, `types.py`, `storage.py` | `tools/make_mutants.py`, `corpus/conformance/refusals/` | `REPAIR.md`, R1's wave-4 P3 note |
| LIMITATIONS.md | `resolve.py`, `lower_sqlite.py`, `engine.py`, `live.py`, `capture.py`, `evolution.py`, `generate.py`, `surfaces.py`, `types.py`, `ir.py`, `cli.py`, `tools/check.py` | `generated/**/schema.sql` (index scan), `corpus/worlds/MIGRATION.md` | `gate-report.json` G11 measures |
| INTEGRATION.md | `parse.py`, `resolve.py`, `storage.py`, `engine.py`, `live.py`, `capture.py`, `evolution.py`, `generate.py`, `cli.py`, `src/garns_rust/sqlite.rs` | `generated/SALES/**`, `corpus/conformance/worlds/sales`, `corpus/worlds/practice` | — |
| README.md | `cli.py`, `resolve.py` registries, `generate.py`, `refuse.py` | `generated/INDEX.json`, `corpus/mutants/expected.json` | `gate-report.json`, `REPAIR.md`, `reviews/R1/REVIEW.md`, `reviews/R2/REVIEW.md` |

## Commands and examples independently checked

All commands are offline, install nothing, and were run with
`PYTHONDONTWRITEBYTECODE=1` and `python -B`. "This pass" = re-run while writing
this report; "drafting" = performed by one of the four drafting agents and
recorded here without re-running.

| # | Command / probe | Run | Exit | Observed |
|---|---|---|---:|---|
| V1 | `uv run --offline --with lark python -B -m unittest discover -s tests -t .` (from `build/B2`) | this pass | 0 | `Ran 103 tests in 1.762s` … `OK` |
| V2 | `… -m garns.cli resolve corpus/conformance/worlds/sales` | this pass | 0 | `resolved 2 modules, 2 carriers, 4 reads, 1 worlds` |
| V3 | `… -m garns.cli ddl … --world SALES --binding …/storage-SALES.json` | this pass | 0 | `CREATE TABLE "ta_6e060cc01b" ( "id_268d9db70b" INTEGER PRIMARY KEY, … UNIQUE ("co_7ed8c48383") );` — every name from the binding |
| V4 | `… -m garns.cli generate … --world SALES --binding … --out <tmp>` | this pass | 0 | `generated 20 files under <tmp>` (matches INDEX.json's SALES count) |
| V5 | `… -m garns.cli execute … --read sales_static.open_orders_once --ship` | this pass | 0 | `{"rows": [], "total": null}` — a freshly shipped empty store |
| V6 | `… -m garns.cli execute … --read sales.not_a_read --ship` | this pass | **2** | `refused: READ_UNKNOWN [runtime] at 1:1: … reads are selected by qualified name` |
| V7 | `uv run … python -B tools/check_scaffold.py` (from the lane root) | this pass | 0 | five `PASS` lines ending `PASS v9-5 scaffold`; `positive=51; decode_refusals=3; validate_inputs=3` |
| V8 | `garns.mutants.observe_all(Path('corpus/mutants'))` compared with `expected.json` **after** observation | this pass | 0 | 168 observed, 168 in the manifest, key sets equal, **0 mismatches**; 37 scenarios; stages validate 99 / decode 40 / runtime 18 / ship 6 / load 4 / accepted 1; 124 distinct codes |
| V9 | `check_exhaustive` over `FootprintDeriver`, `_Lowerer`, `_ShowLowerer` | this pass | 0 | `[]`, `[]`, `[]`; node unions 11 expr / 9 operand / 6 show |
| V10 | `lower_read` on `sales_static.open_orders_once` and `sales.open_orders` | this pass | 0 | same `Plan` type, `columns ('identity','customer','total')`, `key_columns ('$k0',)`, **byte-identical SQL**; `live_bound` `None` vs `20` |
| V11 | `derive_footprint` on a query | this pass | 0 | refuses `QUERY_NOT_LIVE` at `validate` |
| V12 | `resolve_files` on `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns` | this pass | 0 | `ENGINE_LOWERING_ABSENT validate 24:10` |
| V13 | `generate.tree_digest('generated/SALES')` vs `INDEX.json` | this pass | 0 | both `7240ee4d12f9e8e5e82b1c174a27dd98d107e6410a6fcf64882d365dcf2f7505` |
| V14 | AST scan of `src/garns/**/*.py` for `refuse` / `Refusal` / `_runtime` / `_ship` / `_fail` first arguments | this pass | 0 | 240 literal codes at 345 sites + 22 variable-chosen = **262** distinct (a text scan reports 241/347; see M10) |
| V15 | Parse of the DIAGNOSTICS catalogue table | this pass | 0 | 266 rows, 262 distinct codes, stages decode 6 / validate 216 / lower 2 / ship 12 / load 5 / runtime 25; four dual-stage codes |
| V16 | Corpus and artifact census (`find`, `wc`, `INDEX.json`) | this pass | 0 | 254 `.garns` (mutants 182, worlds 49, refusals 12, conformance worlds 6, metamorphic 3, static 1, dynamic 1); 131 single-file mutants; 37 scenarios; `MIGRATION.md` 47 lines / 37 edits; 13 world bindings; **172** generated world files + `INDEX.json` |
| V17 | `wc -l src/garns/*.py`, `src/garns_rust/sqlite.rs`, `tools/*.py` | this pass | 0 | **8,008** lines / 22 modules; `resolve.py` 1382, `parse.py` 813, `ast.py` 810, `resolve_read.py` 789, `ir.py` 781, `lower_sqlite.py` 700, `engine.py` 564; `sqlite.rs` 105; `check.py` 735, `make_mutants.py` 318, `migrate_seed_corpus.py` 117, `storage_template.py` 69, `generate_all.py` 54 |
| V18 | Read of `gate-report.json` (**not** re-run) | this pass | — | schema `garns-v9-5/gate-report/1`, `all_pass: true`, 12 gates, 128 checks, 128 `ok`, `seconds 3.2`, python 3.10.17, sha256 `a84da3d9…0be1`, mtime 15:46:13 |
| V19 | Source read of `resolve.py::resolve_deployment` | this pass | — | `extends` bases resolve **before** the child's lowerability guard, so the documented "position at the deployment name" fallback is unreachable from source (M8) |
| V20 | Markdown link/anchor checker over all eleven documents | this pass | 0 | 0 broken file targets, 0 missing anchors |
| D1 | Unit suite | drafting (×3) | 0 | `Ran 103 tests … OK` |
| D2 | Lane scaffold check | drafting (×2) | 0 | `PASS v9-5 scaffold` |
| D3 | Regeneration of all 8 worlds into a temp tree | drafting | 0 | byte-identical to `generated/`, digests equal `INDEX.json` |
| D4 | `rustc -O` compile of a copy of `generated/SALES/rust` + runner | drafting | 0 | rows byte-identical to the Python `[type_code, text]` encoding |
| D5 | The three DSL_REFERENCE minimal examples (INVENTORY, SUPPORT scoped live, DEPOT captured) | drafting | 0 | resolved, bound, lowered, shipped; quoted SQL and rows; capture ordering limitation observed live |
| D6 | 71 refusal snippets; engine inheritance/override batch; `storage_template --fresh`; CLI refusal probes (`SCOPE_REQUIRED`, `CAPABILITY_REQUIRED`, `ENGINE_LOWERING_ABSENT` with no output directory created) | drafting | 2 (refusals) | codes and positions as documented |
| D7 | INTEGRATION.md's whole-seam tour script | drafting | 0 | reproduced line for line, including `stats {'probes': 62, …, 'listener_scans': 0, 'batches': 1}` |

**Deliberately not run in this pass**, and why: `tools/check.py` (rewrites
`gate-report.json` in place — the recorded artifact is the evidence),
`tools/generate_all.py`, `tools/make_mutants.py`, `tools/migrate_seed_corpus.py`
(each deletes its output tree first). No `git`, no network. Caches were purged
at the end of the pass.

## Consistency edits made in this pass

Nineteen edits across seven documents. Every edit is a number, a citation or a
link that two documents disagreed about; no claim was added, softened or
removed.

| # | File | Edit | Why |
|---|---|---|---|
| E1 | ARCHITECTURE.md | `18 STORAGE_* codes` → `17` | [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) catalogues exactly 17 `STORAGE_*` rows, and `grep` over `src/garns/storage.py` finds 17 distinct `STORAGE_*` literals |
| E2 | AI_DEVELOPER_GUIDE.md | same, in the invariants table | same |
| E3 | COMPILER_PIPELINE.md | same, in the phase-3 row | same — and the document's own §Diagnostic ownership table already said `storage.py` raises 19 distinct codes, which is 17 + `WORLD_UNKNOWN` + `WRITER_CAPTURE_INCOMPLETE` |
| E4 | INTEGRATION.md | same, in the "must not do" list | same |
| E5 | LIMITATIONS.md | same, in the storage-binding row | same |
| E6 | DSL_REFERENCE.md | `eighteen STORAGE_*` → `seventeen` | same |
| E7 | COMPILER_PIPELINE.md | §Phases counts: "five further codes … giving 246" → 21 further codes, **262** total, with a pointer to the catalogue | DIAGNOSTICS.md and DSL_REFERENCE.md state 262; three siblings still carried the 246 literal-scan floor inherited from `build/B2/REPORT.md` |
| E8 | COMPILER_PIPELINE.md | §Diagnostic ownership closing paragraph: enumerates the 21 variable-chosen codes in their three shapes; `241 + 21 = 262` | same; removes the "floor, not a proven ceiling" hedge that the catalogue has since closed |
| E9 | COMPILER_PIPELINE.md | "Two codes are … raised at two different stages" → **four**, adding the `READ_UNKNOWN` and `VERB_INPUT_ENGINE_OWNED` rows | DIAGNOSTICS.md names four dual-stage codes and its catalogue carries 266 rows for 262 codes; two was a direct contradiction |
| E10 | EXTENDING_GARNS.md | principle 3: "Five more … giving 246 as a floor" → the 21 variable-chosen codes and `241 + 21 = 262` | same as E7 |
| E11 | TESTING.md | layers table: "124 of ~246 are asserted" → "124 outcomes out of 262 implemented codes" | same as E7 |
| E12 | TESTING.md | snapshot row "Refusal codes implemented **246** — a floor" → **262** (241 literal + 21 variable-chosen), 266 rows, with the verification column corrected | same as E7 |
| E13 | TESTING.md | "How the refusal-code count is taken" rewritten to the three variable-chosen shapes and 262 | same as E7 |
| E14 | LIMITATIONS.md | verbs row: "verb codes listed in `README.md` §3" → link to [DIAGNOSTICS.md](DIAGNOSTICS.md#catalogue) | that citation meant `build/B2/README.md`; with a `README.md` now in this directory it resolved to the wrong file |
| E15 | LIMITATIONS.md | decode row: "`README.md` §2.1" → link to DIAGNOSTICS.md `### Decode classification` | same collision |
| E16 | LIMITATIONS.md | PostgreSQL row: bare `REPAIR.md` → `../evidence/v9-5-b2/REPAIR.md` | DSL_REFERENCE.md and DIAGNOSTICS.md already cite it fully qualified; a bare name resolves to nothing in this directory and to nothing in a future repository |
| E17 | ARCHITECTURE.md | same | same |
| E18 | COMPILER_PIPELINE.md | same | same |
| E19 | EXTENDING_GARNS.md | same | same |

No other document text was changed. `build/B2/`, the frozen grammar, corpus,
briefs, seed, `reviews/`, `tools/` and `gwz.conf` were not written to.

## Ambiguities and mismatches found

Recorded, **not fixed** — every row below is outside `docs-staging/F51` or is a
judgement the documentation set cannot make on its own.

| # | Where | What | Evidence | Suggested owner action |
|---|---|---|---|---|
| M1 | `build/B2/REPORT.md` §1; `REPAIR.md` §2.1 | The `gate-report.json` stamp is stale: sha256 `8b422ddf…`, mtime 15:43:55, `seconds 3.1`. On disk: sha256 `a84da3d91488dd80348dc30f2e8b9548371a31d55eb761be49035e8e750b0be1`, mtime 15:46:13, `seconds 3.2`. Content is equivalent — 128/128, `all_pass: true` | V18 | Re-stamp both documents from the current artifact, or drop the digest and cite the file |
| M2 | `build/B2/REPORT.md` §10 addendum | Still says 166 mutants / validate 97 / 123 codes / 245 implemented, while §4 and the tree say 168 / 99 / 124 / 246 (literal-scan) | V8, V14 | Delete the superseded addendum bullet; §4 is already correct |
| M3 | `build/B2/README.md` §1, `REPORT.md` §4 | Counts predate the wave-3 repair: "129 single-file mutants + 36 scenarios" (131 + 37), "11 refusal sources" (12), "249 `.garns`" (254), "178 under `corpus/mutants`" (182), "36 migration edits / 46-line MIGRATION.md" (37 / 47), `src/garns/*.py` 8001 lines (8008) | V16, V17 | Re-measure §1/§4 in one pass; the F51 set already carries the current figures |
| M4 | `build/B2/REPORT.md` | Stale line citations: `tools/check.py:688` → `:731` (the `all_pass` return), `resolve.py:1163` → `:1160` (`compute_scope_paths`), `resolve_read.py:696` → `:698`; §3 G1 says "11 × refusal" where the gate now sweeps 12 | V16, source reads | Re-verify every `path:line` in REPORT.md; consider a citation checker (below) |
| M5 | `build/B2/README.md` §1 vs `REPORT.md` §4 | Generated file count 173 vs 172 | V16 | Both are defensible (172 world files; 173 including `INDEX.json`). Say which, once. F51 states both explicitly |
| M6 | `build/B2/REPORT.md` §4; `README.md` §3 | The 246 refusal-code figure is a literal-scan **floor**; a full scan finds 262. Separately, README §3's enumeration lists 261 codes and omits `NESTED_SHOW_WITH_DISTINCT` | V14, V15 | Regenerate README §3's list and REPORT §4's count from the code; do not maintain either by hand |
| M7 | `build/B2/tests/README.md` §"Known failure" | Documents `test_regeneration_from_a_relocated_copy_of_the_corpus_is_byte_identical` as failing because `StorageMapping.source` leaked an absolute path. That was fixed (REPORT §10) and the suite is 103/103 green | V1; `storage.py:300-301` | Delete the section; it now misinforms a reader about a passing test |
| M8 | `build/B2/REPAIR.md` §1.1, echoed in four F51 documents | The refusal position "the deployment name when the engine is inherited through `extends`" is **unreachable from source**: `resolve_deployment` resolves the base first, so a base declaring `postgres` refuses at its own `engine` item | V19 (`resolve.py:1235-1240` vs `:1292-1299`) | Either state the fallback as defensive-only (as DSL_REFERENCE.md already does) or remove it and refuse at the item unconditionally |
| M9 | `tools/check.py` ~`:377-379`; `tests/test_repair_engine_lowering.py:65-69` | The check/test labelled "engine inherited through `extends`" builds a SQLite base and a child that **overrides** it with `engine postgres` — an override, not inheritance | R1's wave-4 appendix (non-blocking P3); EXTENDING_GARNS.md already flags it | Rename to "postgres override in an extending deployment" and add a case whose *base* carries the unlowered engine |
| M10 | Counting method | A text scan reports 241 literal codes at 347 sites; an AST scan reports 240 at 345. The difference is `KEY_DUPLICATED`, written as a ternary inside `_runtime(…)` at `engine.py:489`, `:522` | V14 | Pick one method and ship it as a script; the 262 total is identical either way |
| M11 | `build/B2/REPORT.md` §5, `README.md` §2.3 | Say "18 `STORAGE_*` codes"; the implementation has 17 | E1–E6 | Correct the build documents, or accept that F51 supersedes them |
| M12 | AI_DEVELOPER_GUIDE.md (change-impact map; definition of done) | Cites `REPORT.md` as a live document; it is lane-specific and will not exist in a future repository | reading | Replace with the repository's own evidence convention at the move |
| M13 | `build/B2/README.md` §6, `REPORT.md` §8 | Several real gaps are absent from the build's own limitation lists: `generate()` ignores `World.generated`; `at`/`mode`/`snapshot`/`pool` and `durability` are validated and never read; `--quick` is inert; `generate` is a declared stage with zero raise sites; no `CREATE INDEX` is ever emitted; `MEMBER_OF_NON_FAMILY` and one `resolve_read.py` assertion are unreachable; `_check_param` raises `TypeError` before its list guard; `Engine(store)` on an unshipped store and a second `Store.ship()` raise `sqlite3.OperationalError`; a malformed `--param` exits 1 with a traceback; `Program.carrier/intent/read/world/link/module` raise `KeyError` | [LIMITATIONS.md](LIMITATIONS.md#inventory), [DIAGNOSTICS.md](DIAGNOSTICS.md#guaranteed-diagnostics-versus-incidental-exceptions) | Either adopt the F51 inventory as the build's limitation list or fix the code; each row is small and independently addressable |

## Unresolved truth gaps

Things no document in this set could establish, listed so no reader mistakes
silence for evidence.

* **`token_bound` is unmeasured.** G11 reports it verbatim as
  `"unverified: not measurable from inside the build"`. No token-cost
  measurement exists anywhere in the implementation, so no document can say what
  a question costs.
* **The gate was read, not re-run.** 128/128 comes from the recorded
  `gate-report.json` (V18). That run predates this documentation directory; a
  fresh run would rewrite the artifact, which this pass was not permitted to do.
* **130 of 262 refusal codes have no fixture or unit test.** They are reachable
  and implemented, but nothing in this corpus pins them; DIAGNOSTICS.md marks
  each with `—` rather than claiming coverage.
* **Rust "parity" is row-shape parity.** Seven reads in two worlds, both sides
  running the *same* SQL text against the *same* SQLite file. Nothing
  demonstrates a Rust implementation of anything.
* **Schema independence is proved by renaming an existing topology.** The
  metamorphic transform renames every identity and physical name of a world that
  already exists; a genuinely unseen schema *shape* remains an unproved case.
  Both reviewers substituted private seeds, which is the strongest available
  attack and still not the same thing.
* **Concurrency is undefined, not merely limited.** One connection, hand-managed
  transactions, no busy handling, no thread-safety statement anywhere in the
  code to document.
* **Intent behind the unconsumed declarations is unknown.** Whether `at`,
  `mode`, `snapshot`, `pool`, `durability`, `ordered_within`, `history kept`,
  `filter`, `pattern` and `length` were meant to be consumed later or were
  specified speculatively is not recorded in anything this pass read.
* **Drafting-agent validations D1–D7 are reported, not re-run here.** The
  `rustc` parity compile, the eight-world regeneration byte-identity check and
  the 71 refusal snippets were reproduced once each, by their authors.
* **Authorship of the nine drafts is inferred** from modification-time clusters;
  the files carry no author metadata.

## Recommended documentation to carry into a future garns-wz repository

**Carry verbatim** (they describe code, and the repository layout is already the
one they cite — `src/garns/…`, `tools/…`, `corpus/…`, `generated/…`):

| Document | Note on the move |
|---|---|
| DSL_REFERENCE.md | Only lane-absolute paths in it (`brief/…`, `build/B2/REPAIR.md`) need re-pointing |
| ARCHITECTURE.md | Drop the `## Sustainability assessment` rows for `tools/check.py`, `make_mutants.py`, `migrate_seed_corpus.py` if those tools do not travel |
| COMPILER_PIPELINE.md | Keep whole; it is the only document that proves the pre-effect boundary |
| EXTENDING_GARNS.md | Un-freeze the grammar caveat in `## Playbook: add a construct` once the grammar is live |
| AI_DEVELOPER_GUIDE.md | Replace the `REPORT.md`/`REPAIR.md` evidence-style references (M12) with the repository's own convention |
| INTEGRATION.md | Keep, including the clearly-marked proposed adapter section |
| README.md | Keep; replace `## Status and evidence snapshot` with the repository's release snapshot |

**Regenerate from code every release** — these are measurements, and the drift
in `build/B2`'s own documents (M1–M6) is what happens when they are hand-kept:

| Regenerated artifact | Source of truth |
|---|---|
| DIAGNOSTICS.md `## Catalogue` (code, stage, raise site, trigger, position) | a scan of `src/garns/**/*.py` that follows both literal and variable-chosen forms |
| DIAGNOSTICS.md coverage numbers | `corpus/mutants/expected.json`, `corpus/conformance/refusals/expected.json`, `tests/**` |
| TESTING.md `## Snapshot counts` | `find`/`wc`, `generated/INDEX.json`, the manifests, one unit-suite run |
| TESTING.md `## Gate matrix G0–G11` check labels | `gate-report.json` |
| LIMITATIONS.md's measured rows (line numbers, file counts, code counts) | the same scans |
| README.md `## Status and evidence snapshot` | the release's own gate artifact |

**v9-5-lane-specific — drop or archive with the lane, do not carry:**

* This report (archive it with the lane; it documents a review process, not the
  code).
* Every reference to `build/B2/REPORT.md`, `build/B2/REPAIR.md`,
  `gate-report.json`, `reviews/R1/`, `reviews/R2/`, `FROZEN.json`, `brief/`,
  `seed/`, `prompts/` and `tools/check_scaffold.py` — the last of these
  explicitly never travels (it verifies the lane, never imports the
  implementation).
* The "selected build B2 / wave-3 repair / wave-4 ratification" framing in
  README.md and in the PostgreSQL rows of several documents: keep the *refusal*,
  drop the *provenance*.
* `tools/check.py`'s G0–G11 identity if the exit matrix does not travel; the
  checks themselves are worth keeping as CI, but "G6" means nothing outside this
  lane.

**Suggested doc build and verification hooks** — cheap, and each would have
caught something this pass fixed by hand:

| Hook | What it does | Would have caught |
|---|---|---|
| **Link/anchor checker** | Parses every inline markdown link, resolves the file part relative to the doc and the fragment against that file's GitHub-style heading slugs; fails on the first miss | The `README.md` §3 / §2.1 citations that silently changed meaning once a sibling `README.md` existed (E14, E15) |
| **Counts snapshot script** | Emits one JSON of every measured number (tests, gates, checks, mutants by stage, refusal codes by stage, `.garns` by directory, generated files per world, `wc -l` per module) and diffs it against the values embedded in the docs | M1–M6, M11 — every stale count in `build/B2`'s own documents |
| **Citation checker** | For each `path:line` and `path::symbol` in the docs, asserts the file exists and the line still contains the named symbol or code | M4's three stale line numbers |
| **Executable-example harness** | Extracts fenced `sh`/`console`/`python` blocks marked as verified and runs them in a temp directory, comparing stdout | Any drift in the README orientation sequence and the INTEGRATION tour |
| **Generated catalogue** | Makes DIAGNOSTICS.md `## Catalogue` a build product rather than a maintained table | M6 and the 246-vs-262 split this pass reconciled |

The first two are the ones to build first: together they cover every
inconsistency recorded above.

## Post-pass direction addendum — 2026-10-03

The original documentation pass above remains a historical report over eleven
files. A twelfth document, [GARNS_DIRECTION.md](GARNS_DIRECTION.md), was added
after PostgreSQL and asynchronous database access became the proposed focus of
the next Garns cycle. It is intentionally a direction document rather than a
claim about the repaired B2 implementation.

The addendum also linked the new document from [README.md](README.md) and added
a planning-specific reading path. No file under `build/B2/`, the ratified
reviews, frozen grammar, corpus, briefs, seed, prompts or lane tools was changed.

The new document records:

- PostgreSQL as the proposed production reference backend;
- an async-only public runtime/database/subscription API;
- a synchronous pure compiler boundary;
- SQLite as a secondary local/test backend behind the same async-facing
  contract;
- durable capture with notifications used only as wakeups;
- a four-phase delivery plan after promotion of repaired B2;
- executable evidence required before PostgreSQL/async claims can ship; and
- ten ADR topics that remain decisions rather than implementation facts.

Relative Markdown links in `GARNS_DIRECTION.md`, the updated README document
map and this addendum were checked after the edit. The earlier line counts,
authorship inference and V20 result remain measurements of the 2026-09-04
eleven-document snapshot and were not retroactively rewritten.
