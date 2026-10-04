# Garns v9-5 — independent initial review R1

Date: 2026-09-04 (Australia/Sydney)

Scope: B1, B2, and B3 at the bytes present when this review began.  I read the
required inputs in the mandated order, froze `reviews/R1/PRIVATE_ATTACKS.md`
before executing a build, did not read or communicate with R2, used no network
or git operation, and did not modify an original build.  Commands which write
reports or generated products ran only in the mirror at
`reviews/R1/work/lane/`.

## Outcome

B2 is the only implementation that survives G0-G11 and the frozen R1 private
attacks.  B1 and B3 both have multiple independently reproduced P1 defects,
including forbidden coupling/provenance failures.  These are implementation
defects, not a contradiction in the frozen language.

B2 has one bounded P2 hardening repair: its resolver admits `engine postgres`
although the implementation has only a SQLite lowering.  Until a PostgreSQL
consumer exists, validation or the first pre-effect ship boundary should refuse
that deployment with `ENGINE_LOWERING_ABSENT`.  This does not affect the
SQLite/Python/Rust G0-G11 evidence or the selection among the three builds.

## Commands, exits, and evidence

All relative commands below start at the lane root unless a `cd` is shown.
The long `python -B -` probes used the literal sources recorded in the
"Mandatory and private attacks" section; their observed output is preserved
there.  Every Python command set `PYTHONDONTWRITEBYTECODE=1`.

| ID | Exact command | Exit | Evidence |
|---|---|---:|---|
| C0 | `sha256sum grammar/garns.lark build/B1/grammar/garns.lark build/B2/grammar/garns.lark build/B3/grammar/garns.lark` | 0 | all four `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8` |
| C1 | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_scaffold.py` | 0 | stdout ended `PASS v9-5 scaffold`; rerun after testing also exited 0 |
| C2 | `mkdir -p reviews/R1/work/lane && rsync -a --exclude 'reviews/' --exclude '.git/' --exclude 'build/B3/rust/target/' ./ reviews/R1/work/lane/` | 0 | isolated mirror `reviews/R1/work/lane/` |
| C3-B1 | `cd reviews/R1/work/lane/build/B1 && PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py` | 0 | `reviews/R1/work/lane/build/B1/gate_report.json`; self-report green, contradicted below |
| C3-B2 | `cd reviews/R1/work/lane/build/B2 && PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py` | 0 | `reviews/R1/work/lane/build/B2/gate-report.json`; 121/121 checks pass |
| C3-B3 | `cd reviews/R1/work/lane/build/B3 && PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py` | 0 | `reviews/R1/work/lane/build/B3/generated/report/exit_matrix.json`; self-report green, contradicted below |
| C4-B1 | `cd reviews/R1/work/lane/build/B1 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover -s tests -t .` | 0 | 16 tests, OK |
| C4-B2 | `cd reviews/R1/work/lane/build/B2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover -s tests -t .` | 0 | 98 tests, OK |
| C5-B1 | `cd reviews/R1/work/lane/build/B1 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -` (nine calls to `parse_and_resolve_dir`: appflowy, everbility, practice, vaultwarden, evolution/g1-g5) | 0 | all 9 directories resolved; counts recorded below |
| C6-all | `cd reviews/R1/work/lane/build/Bn && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -` (common enforcement/static-only source table below) | 0 for each | common-source observations below |
| C7-all | same interpreter command, source `# harmless\nnot_garns\n` then `# SELECT\nnot_garns\n` | 0 for each | B1/B3 code changes; B2 invariant |
| C8-all | same interpreter command, two-module collision source below | B1 0, B2 probe 1 because the reporting wrapper assumed a `Refusal` instead of the actual `KeyError`, B3 0 | B1 bare selection reproduced; B2 production runtime was separately probed and refused `READ_UNKNOWN`; B3 refused `QUESTION_AMBIGUOUS` |
| C9-B1 | same interpreter command, build the composed `inner_named`/`outer_named` source then call `lower_decl_sql` for both | 0 (probe caught failures) | both lowerings raised `NameError: _path_tuple is not defined` |
| C9-B3 | same interpreter command, install `corpus/fixtures/tenancy.garns`, initialise inner/outer live instances, mutate `title`, commit its delta | 1 | failed before registration in `lower_question`: `TypeError: expression visitor received None` |
| C10-B1 | same interpreter command, snapshot `generated/`, delete it, resolve the two conformance positives, call `generate_all_artifacts`, compare path+SHA-256 maps | 0 | 10/10 paths returned, `byte_identical False`; exact divergent copies remain at original `build/B1/generated/` and regenerated `reviews/R1/work/lane/build/B1/generated/` |
| C10-B2 | same interpreter command, snapshot/delete `generated/`, then subprocess `python -B tools/generate_all.py`, compare path+SHA-256 maps | 0 | producer 0; 173/173, `byte_identical True`; `reviews/R1/work/lane/build/B2/generated/INDEX.json` |
| C10-B3 | same interpreter command for `generated/g9`, then subprocess `python -B tools/check.py --gate G9` | 0 | producer 0; 14/14, `byte_identical True`; `reviews/R1/work/lane/build/B3/generated/report/G9.json` |
| C11-B2 | import `tools/check.py`, replace only the metamorphic name seed with `R1-private-20260904|<builder-seed>`, call its G5 attack in an R1 temp directory | 0 | 12/12 private checks pass, including 68 semantic identities, all physical/capture fields, rows, routing, deltas, counters, collisions, writer identity |
| C12 | `rg -n --glob '*.py' --glob '*.rs' '(worlds\\[0\\]|questions\\[0\\]|queries\\[0\\]|_DECODE_SCANNERS|scope_id|captured_at_revision|change_seq|listener_scans is NEVER|listener_scans.*strictly 0|return f"\\{module\\}__\\{name\\}")' build/Bn/src build/Bn/rust/src` | 0 | exact source witnesses cited in findings |

The C5 B1 production-resolver counts were: appflowy 8 modules/21 carriers/0
reads; everbility 8/16/9; practice 7/10/11; vaultwarden 6/31/5;
evolution g1 2/4/0, and g2-g5 each 2/5/0.  B2's C3 G1 resolved and bound 13
world/generation entries.  B3's C3 G1 resolved all 9 migrated directories.

## Mandatory and private attacks

### Enforcement and the query/question boundary

The common source declared `Parent`, `Item`, `key`, and `amount`, then varied
only the link flags or one question item.

| Attack | B1 | B2 | B3 |
|---|---|---|---|
| direct `unenforced` | accept | accept | accept |
| `unenforced unenforced` | refuse validate `LINK_ENFORCEMENT_CONFLICT` | refuse validate `LINK_ENFORCEMENT_REPEATED` | refuse validate `LINK_ENFORCEMENT_CONFLICT` |
| `unenforced end restrict` | refuse validate `LINK_ENFORCEMENT_CONFLICT` | same | same |
| `end restrict end cascade` | refuse validate `LINK_ENFORCEMENT_CONFLICT` | refuse validate `LINK_ENFORCEMENT_REPEATED` | refuse validate `LINK_ENFORCEMENT_CONFLICT` |
| question `call money.round(...)` | refuse decode | refuse decode | refuse decode |
| question arithmetic | refuse decode | refuse decode | refuse decode |
| question aggregate show | refuse decode | refuse decode | refuse decode |
| question `having` | refuse decode | refuse decode | refuse decode |
| question `distinct` | refuse decode | refuse decode | refuse decode |
| question non-path ordering expression | refuse decode | refuse decode | refuse decode |

The richer static query (group, having, division, `money.round`, and order by
`sum(...)`) executed in all three C3 suites, and no candidate generated a live
product whose identity was that query.  Shared-subset query/question rows also
matched in all three C3 suites.  B1 nevertheless fails the registry contract:
`money.round(amount)` with one argument resolved and lowered to
`ROUND(t0.amount)` even though its own registry declares `(Money, Integer)` at
`build/B1/src/garns/resolve.py:69`.  B2 refused it as `CALL_ARITY`; B3 refused it
as `CALL_ARITY`.

### Fresh metamorphic rename, physical mappings, and collisions

B2 passed the independent private seed with all semantic dimensions, physical
tables, identity/scalar/link columns, multihop scope path, engine/ledger names,
writer, changelog table, and every changelog field renamed.  Normalized rows,
routing, deltas, and runtime measures were equal.  Its missing-binding probe
refused at validate as `STORAGE_BINDING_UNREADABLE`.

B3 passed a fresh-seed simple `shop` source/storage rename and rejected bare
`listed` as `QUESTION_AMBIGUOUS`, but it accepted a source with no authored
physical mapping and silently produced `shop.Item -> shop__Item / sku`.  That
is the forbidden default path in `build/B3/src/garns/storage.py:28-99`, not
provenance from an input binding.

B1 accepted a source with no authored mapping and produced:

```text
reporting.Customer customer customer_id [] None _changelog_customer
reporting.Invoice invoice invoice_id ['customer_id'] None _changelog_invoice
```

The implementation is explicit at `build/B1/src/garns/resolve.py:1266-1317`:
lowercase carrier table, `<link>_id`, `scope_id`, and `_changelog_<table>` are
synthesised.  A changelog whose fields were consistently renamed to
`seqx/revx/verbx/pkx/valx` then crashed B1 capture with SQLite
`OperationalError: no such column: captured_at_revision`; see
`build/B1/src/garns/capture.py:31-41`.

The common collision source used the same local `Item`, `Peer`, `key`, `name`,
`peer`, `report`, and `watch` in modules `alpha` and `beta`.  B1 resolved both
qualified questions but `question_by_name("watch")` returned `alpha.watch`.
Generation of two queries and two questions produced only `sql/report.sql` and
`sql/watch.sql`; the surviving footprint was for `beta.watch`.  The overwritten
products are preserved at `reviews/R1/evidence/b1-collision-generated/`.
B2's production `Engine.execute("open_orders")` and `Engine.execute("")` both
refused runtime `READ_UNKNOWN`; B3 refused the bare collision as
`QUESTION_AMBIGUOUS`.

### Live correctness, groups, composition, neutral/cross-scope/rollback

B2 reproduced all required behaviours in one integrated engine:

- deliberate registry iteration incremented the scan counter, proving it is
  live; normal routing later measured zero scans;
- an inner write routed both the inner and outer composed questions;
- the routed-but-neutral outer emitted no batch;
- irrelevant and cross-scope writes caused no inappropriate routing;
- a real transaction rollback produced no revision, ledger row, routing, or
  batch;
- moving `open -> sealed` emitted delete old group/upsert new group; and
- folding matched one-shot recomputation after every subsequent revision.

Exact results are in the G7 entry of
`reviews/R1/work/lane/build/B2/gate-report.json`.

B1's isolated footprint index did route a changed `m.Item.title` to two
registered inner/outer footprints (2 candidates, 0 scans), and its manual group
refresh updated both groups.  But both production lowerings of the composed
questions crashed on the undefined `_path_tuple`, and B1 has no integrated
transaction/live coordinator at all.  Its `listener_scans` counter is expressly
"NEVER incremented" (`build/B1/src/garns/live.py:75,122`), so zero is not the
required measured result.

B3's recorded grouped batch refreshed old `g1` and new `g9`, and its simple
scope route/fold checks worked.  Its purported composition check only compared
the carrier sets of two footprints.  The private execution attack showed that
`tenancy.inner_named.where` resolves to `ContainsExpr(..., value=None)`; lowering
then raises `TypeError` before the instances can register.  B3 also has no
transaction coordinator: its rollback evidence manually rolls SQLite back and
then calls `commit(5, [])`.  This proves an empty delta list does nothing, not
that a rolled-back Garns write cannot leak a batch.

### Ledger, capture, mutant independence, and regeneration

B2 passed typed pre-effect carrier/field/scope/writer/transaction validation,
real mapped triggers, a two-hop capture scope, incomplete real and binding
coverage refusals, and PRAGMA-measured denominators.  The fresh rename also
exercised renamed writer/changelog metadata.

B1 and B3 ledger records have no transaction identity column or delta member
(`build/B1/src/garns/ledger.py:10-47` and
`build/B3/src/garns/ledger.py:11-55`).  B1's tests populate validator allowlists
by hand rather than deriving a complete mutation boundary from the selected
world; B3 validates a delta but likewise has no transaction.  The common rogue
world (`writers rogue`, otherwise complete) was accepted by B1 and B3; B2
refused `WRITER_CLASS_UNKNOWN`.

Detector independence used identical malformed text with only its comment
changed:

```text
             harmless comment              comment containing SELECT
B1           decode EXPR_NOT_ADMITTED       decode SQL_ESCAPE
B2           decode SOURCE_NOT_GARNS        decode SOURCE_NOT_GARNS
B3           decode DECL_SHAPE_INVALID      decode SQL_ESCAPE
```

B1 also classified the identical member/lifecycle source as `U12_INTERACT`
when the filename was `U12_INTERACT-1.garns`, but
`FAMILY_LIFECYCLE_FIXED` when renamed to `renamed.garns`.  The direct filename
branches are at `build/B1/src/garns/parse.py:108-117`; both B1 and B3 run raw
source regex scanners before returning a decode code.  B2's 166 observed
mutants remained identical after every file was renamed, comments stripped,
and the expected manifest corrupted; detection covered decode, validate, ship,
load, and runtime.

Deletion/regeneration was byte-identical for B2 (173 files) and B3's G9 source
product (14 files).  B1 recreated the same 10 paths but not the same bytes.  The
five divergent B1 products are `manifest.json`, `sql/schema.sql`,
`sql/open_orders.sql`, `python/open_orders.py`, and `rust/open_orders.rs`: the
committed versions used unquoted `order`, while current production generation
uses `"order"`.  Thus the committed B1 artifacts are stale and do not count.

### Forbidden coupling and target parity

Reproduced source witnesses, not raw-grep inference:

- B1: regex/file dispatch (`parse.py:42-119`); short-name first-match lookup
  (`ir.py:478-506`); physical naming guesses (`resolve.py:1266-1317`);
  first-world selection (`footprint.py:133`, `generate.py:43`); `_id` stable-key
  inference (`live.py:59`); fixed capture fields (`capture.py:31-41`); constant
  scan evidence (`live.py:75,122`).
- B3: raw-source regex classifier (`parse.py:42-110`); automatic canonical
  physical schema/changelog construction (`storage.py:22-99`); missing writer
  class validation (`resolve.py:1462-1505`).
- B2: the same searches found no production corpus/schema dispatch, naming
  inference, first-item selection, expected-answer input, or constant runtime
  counter.  The only broad token hit was the metamorphic transform's keyword
  set, which is test transformation logic and does not dispatch compilation.

B2 compiled native Rust runners with installed `rustc` and compared typed rows
for 7 reads across PRACTICE and SALES; all child exits were 0.  B3 built and ran
its Rust/sqlite3 parity executable and its rows matched in this environment.
B1 did not execute Rust: `verify_surface_parity` in
`build/B1/src/garns/surfaces.py:38-52` labels a second Python `sqlite3.execute`
call as `rust_rows`; no Rust toolchain or generated Rust code is invoked.

B2 reports live-bound and capture denominators verified, Rust parity verified,
and token bound explicitly unverified.  B3 explicitly reports token/external
bounds unverified.  B1 makes no independently measured denominator claim.

## Findings by severity

### P1 — disqualifying

1. **B1 physical provenance and capture are guessed.** Lowercase tables,
   `<link>_id`, `scope_id`, and fixed changelog names/fields survive in
   production.  This fails G5, G8, and G10.
2. **B1 runtime identities are not qualified at public helpers/products.** A
   bare collision selects the first module, first-world paths exist, and
   same-local-name generated products overwrite.  This fails G5, G6, G9, and
   G10.
3. **B1 live correctness is not executable end-to-end.** Composed lowering
   crashes and there is no transaction-to-ledger-to-router coordinator.  This
   fails G3 and G7.
4. **B1 generated provenance is stale.** Deletion/regeneration changes five
   committed artifacts.  This fails G9.
5. **B1 detection consumes filename/comment vocabulary.** Identical invalid
   source changes code under filename/comment rename.  This fails G9/G10.
6. **B1 Rust parity is circular Python/Python execution.** This fails G11.
7. **B3 physical mappings are optional guesses.** Missing mapping input is
   silently replaced with compiler-created tables/columns/changelogs.  This
   fails G5/G10 even though an explicit override can be renamed.
8. **B3 composed live questions cannot execute.** The frozen B3 fixture's
   given operand becomes `None` and lowering crashes; its public G7 check never
   executed the claim.  This fails G3/G7.
9. **B3 lacks transaction identity and transaction-coupled rollback.** This
   fails G7/G8.
10. **B3 detection consumes comments.** The `SELECT` comment changes the
    observed code.  This fails G9/G10.

### P2 — significant, bounded

1. **B1 does not validate registered-call arity/type.** One-argument
   `money.round` is accepted despite its declared two-argument signature.  This
   fails complete semantic resolution in G1.
2. **B1 and B3 accept an undeclared writer class.** `writers rogue` resolves;
   B2 refuses `WRITER_CLASS_UNKNOWN`.  This fails the world/identity portion of
   G6 for B1/B3.
3. **B3's zero-scan/rollback evidence is not live instrumentation.** There is
   no operation that increments `listener_scans`, and rollback submits an empty
   delta list after a manual SQLite rollback.  This reinforces G7/G10 failure.
4. **B2 admits an unavailable backend.** Reproduced with a complete deployment:
   `engine postgres` resolves to `ACCEPT [('D', 'postgres')]`, while only
   `lower_sqlite.py`/SQLite `Store` exists.  Bounded repair: remove `postgres`
   from `ENGINES` or refuse it at the first pre-effect deployment/ship boundary.

### P3 — non-blocking observations

1. B2 honestly declares that verbs have no runtime, nested shows are limited to
   one inverse hop, cross-relation capture order is `(seq, carrier)`, and token
   cost is unverified.  None contradicts a mandatory G0-G11 attack used for
   this initial comparison, but the limits should remain explicit.
2. B3's regeneration and native row-parity attacks did pass despite its other
   disqualifying defects.

## Reproduced fact versus inference

Everything labelled with an exit, refusal code, exception, row/batch result,
hash comparison, or source line above is reproduced fact.  The conclusions
that B1 lacks a relational result IR and that the B1/B3 rollback designs cannot
meet atomic notification are architectural inferences from the reproduced
absence of a coordinator plus the source call paths; they are not used alone
to disqualify either build.

No shared specification contradiction was reproduced.  The frozen positive
language files intentionally do not themselves carry a world storage-binding
document; that makes the builders' local conformance-world wrappers necessary,
not contradictory.  B2 proves that an explicit, refusal-on-missing binding can
satisfy the same frozen grammar and corpus, so B1/B3's automatic naming cannot
be attributed to a shared specification defect.

## Implementation-by-gate matrix

`PASS` means independently executable evidence satisfied the whole gate;
`FAIL` cites the finding IDs above, not merely a failed self-test.  G12 is not
an initial builder gate and remains pending manager selection/repair and both
ratifications.

| Gate | B1 | B2 | B3 |
|---|---|---|---|
| G0 frozen inputs | PASS | PASS | PASS |
| G1 grammar/corpus/semantic resolve | FAIL — P2.1 call signature | PASS | PASS |
| G2 static query separation | PASS | PASS | PASS |
| G3 dynamic/recursive footprint | FAIL — P1.3 | PASS | FAIL — P1.8 |
| G4 shared lowering | FAIL — no typed relational/result plan; direct raw-tree SQL path (inference corroborated by P1.3) | PASS | PASS on executed shared subsets |
| G5 schema independence | FAIL — P1.1/P1.2 | PASS | FAIL — P1.7 |
| G6 identity/world/evolution | FAIL — P1.2/P2.2 | PASS | FAIL — P2.2 |
| G7 live correctness | FAIL — P1.3 | PASS | FAIL — P1.8/P1.9/P2.3 |
| G8 ledger/capture | FAIL — P1.1/P1.3/P1.9 analogue | PASS | FAIL — P1.9 |
| G9 evidence honesty | FAIL — P1.2/P1.4/P1.5 | PASS | FAIL — P1.10 |
| G10 forbidden coupling | FAIL — P1.1/P1.2/P1.5 | PASS | FAIL — P1.7/P1.10/P2.3 |
| G11 parity/measures | FAIL — P1.6 | PASS | PASS (Rust verified; bounds honestly unverified) |
| G12 comparative closure | pending | pending | pending |

## Bounded repair for the selected build

Required bounded repair for B2 before ratification:

1. At validation or the earliest pre-effect deployment/ship boundary, refuse
   `engine postgres` with `ENGINE_LOWERING_ABSENT` until an actual PostgreSQL
   lowering exists.  Add an executable regression using a renamed, otherwise
   complete deployment.  Do not broaden this into a PostgreSQL implementation.

Ratification must rerun C0/C1, B2's entire G0-G11 checker, the 98-test suite,
the fresh R1 rename, missing-binding/collision/comment probes, regeneration,
live transactional sequence, capture coverage, and native parity against the
repaired bytes.  Initial findings above must remain intact.

fold B2

# Final ratification — repaired B2

Date: 2026-09-04 (Australia/Sydney)

This section is appended to, and does not replace or revise, the frozen initial
review above.  For wave 4 I read `build/B2/REPAIR.md`, the frozen R1 review, and
the frozen R2 review; inspected the repaired B2 source, tests, corpus additions,
generated products, and report; and independently exercised only a copy under
`reviews/R1/ratify_work/lane/`.  I did not edit B2 or R2, use git, or use the
network.

## Ratification outcome

The bounded P2.4 repair is effective.  `postgres` remains a recognised engine,
but is absent from `LOWERED_ENGINES`; a complete PostgreSQL deployment now
refuses `ENGINE_LOWERING_ABSENT` at validate before deployment IR, binding,
generation, schema, store, ledger, capture, or migration effects can occur.
The repaired build passes the 103-test suite, all 128 G0-G11 checks, the frozen
R1 attacks under a new private rename seed, regeneration, and the independent
pre-effect CLI probe.  No P1 or P2 finding remains.

One P3 documentation/test-label observation does not block ratification: the
check called “engine inherited through extends” constructs a SQLite base and a
child which explicitly overrides it with `engine postgres`
(`tests/test_repair_engine_lowering.py:65-69`, mirrored in
`tools/check.py:377-379`).  It tests an override in an `extends` declaration,
not inheritance of the engine value.  A genuinely PostgreSQL base is already
refused at its own engine item, so this imprecision does not expose an
acceptance or effect path.  The smallest optional cleanup is to rename that
test/check “postgres override in an extending deployment”, without changing
semantics.

## Commands, exits, and evidence

Commands below use the lane root as the working directory unless their leading
`cd` says otherwise.  The mirror was made before any mutating checker ran.

| ID | Exact command | Exit and reproduced result | Evidence |
|---|---|---|---|
| R0 | `[ ! -e reviews/R1/ratify_work ] && mkdir -p reviews/R1/ratify_work/lane && rsync -a --exclude 'reviews/' --exclude '.git/' --exclude 'build/B3/rust/target/' ./ reviews/R1/ratify_work/lane/` | 0; isolated repaired-byte mirror created | `reviews/R1/ratify_work/lane/build/B2/` |
| R1 | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_scaffold.py` | 0 both before and after attacks; ends `PASS v9-5 scaffold` | `FROZEN.json`, `tools/check_scaffold.py` |
| R2 | `shasum -a 256 grammar/garns.lark build/B2/grammar/garns.lark FROZEN.json` | 0; grammar hashes both `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`; `FROZEN.json` `149e82348a7b75e5981bd9e1c4993cba5b5d357da018991cc11caf874ecc84fc` | named files |
| R3 | `find build/B2 -type f ! -path '*/__pycache__/*' -print0 \| sort -z \| xargs -0 shasum -a 256 \| shasum -a 256` | 0; composite digest `eaf4937f853861f76c26be55f5f8903b8b90caeb729ecec40315f93f3b5eb60b` before and after all work | original `build/B2/`; proves R1 did not mutate it |
| R4 | `cd reviews/R1/ratify_work/lane/build/B2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover -s tests -t .` | 0; `Ran 103 tests in 1.861s`, `OK` | mirrored `tests/`, including `tests/test_repair_engine_lowering.py` |
| R5 | `cd reviews/R1/ratify_work/lane/build/B2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/check.py` | 0; twelve PASS lines, 128/128, `ALL PASS` | `reviews/R1/ratify_work/lane/build/B2/gate-report.json`, SHA-256 `04564de49fe33d17bfe34b91bd712faab43ecf63db4f3f4f0ba0df687aea62aa` |
| R6 | import `tools/check.py`, replace only `garns.metamorphic.fresh_names(program, seed)` with `fresh_names(program, "R1-ratify-20260904\|" + seed)`, then call `g5(Gate(...), Path(private_tempdir))` under the R4 environment | 0; 12/12 | terminal record here; new full rename covered 68 semantic identities, physical names, multihop scope, captured writer/changelog names, rows, routing, deltas, counters, and qualified collisions |
| R7 | under the R4 environment, resolve PRACTICE then call `bind_world(program, "PRACTICE", Path("reviews/R1/ratify_work/missing-binding-does-not-exist.json"))`; create a shipped SALES store and call `Engine.execute("open_orders")` and `Engine.execute("")` | 0 probe; observed `validate/STORAGE_BINDING_UNREADABLE`, then `runtime/READ_UNKNOWN` twice; no missing file created | production `src/garns/storage.py`, `src/garns/engine.py` in mirror |
| R8 | under the R4 environment, resolve identical `CALL_ARITY-1.garns` text as `CALL_ARITY-1.garns`, `opaque-filename.garns`, `another-name.txt` with hostile SQL/fallback comment, and `case-999.garns` with numbered/query comment | 0 probe; all four `validate/CALL_ARITY`; only physical line changed with inserted comments | mirrored `corpus/mutants/CALL_ARITY-1.garns`, `src/garns/parse.py` |
| R9 | `cd reviews/R1/ratify_work/lane/build/B2 && mv generated generated.before-r1 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/generate_all.py && diff -qr generated.before-r1 generated` | 0; 173/173 files byte-identical; both `INDEX.json` hashes `9901d1a3d3733740f56da23c91926f7b42d861cd8f825ae2d444a85fb405f9c4` | `reviews/R1/ratify_work/regeneration.diff` (empty), the two mirrored generated trees |
| R10 | `rg -n "postgres\|LOWERED_ENGINES\|ENGINE_LOWERING_ABSENT" src tests corpus README.md REPORT.md tools` plus the frozen forbidden-coupling search from C12 | 0; the only production lowering remains `src/garns/lower_sqlite.py`; the resolver guard is at `src/garns/resolve.py:1292-1299`; no filename/comment/corpus/default physical coupling found | original repaired B2 sources; R5 G10 has 14/14 executable checks |

The exact targeted effect-path command, run from the mirrored B2 directory, was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m garns.cli generate /Users/owebeeone/limbo/datascad/garns-v9-5/reviews/R1/ratify_work/pg_cli_case/source --world ARCHIVE --binding /Users/owebeeone/limbo/datascad/garns-v9-5/reviews/R1/ratify_work/pg_cli_case/DOES-NOT-EXIST.json --out /Users/owebeeone/limbo/datascad/garns-v9-5/reviews/R1/ratify_work/pg_cli_case/SHOULD-NOT-EXIST
```

It exited 2 with `ENGINE_LOWERING_ABSENT [validate]` at 24:10.  The deliberately
missing binding remained absent and the output directory was not created.  The
stderr is preserved at `reviews/R1/ratify_work/pg_cli_case/stderr.txt`.  This is
stronger timing evidence than merely checking a resolver result: the public
generation path stopped before its next binding and generation operations.
The G6 regression also independently established that the SQLite twin ships
and writes, an `oracle` engine instead gives `ENGINE_UNKNOWN`, no PostgreSQL
database appears, and the bind→ship→write scenario stops at bind.

## Private attacks and implementation-specific evidence

- Fresh full rename/collision/capture: 12/12 pass under the new R1 seed.
  Qualified collision keys are disjoint; an alpha write routes alpha only;
  same-local-name reads return their distinct rows; all renamed generated SQL,
  capture deltas, writer identity, and live measurements agree after
  normalization.
- Missing mapping and public selection: missing storage refuses at validate;
  bare and empty read names refuse at runtime.  No default physical naming or
  first-item selection was observed.
- Detection independence: 168/168 mutants still match across decode, validate,
  ship, load, runtime, and accepted stages after file renames, comment stripping,
  and manifest corruption.  The independent hostile comment/filename probe
  above agrees.
- Live transaction/capture: G7's 11/11 includes deliberate scan-counter
  liveness, inner/outer composition, relevant/neutral/irrelevant/cross-scope
  writes, rollback, old/new group movement, fold equivalence after every
  revision, and measured `LIVE_BOUND_EXCEEDED`; G8's 12/12 includes mapped real
  triggers, two-hop scope capture, typed transaction/carrier/field/scope/writer
  validation, incomplete-coverage refusal, and PRAGMA denominators
  `{pantry.Jar: 8, pantry.Shelf: 6, tenancy.Household: 6}`.
- Native parity: G11 invoked `/Users/owebeeone/.cargo/bin/rustc -O` twice (exit
  0), then invoked the distinct PRACTICE and SALES binaries for seven qualified
  reads (every exit 0).  Python/Rust typed row encodings matched at row counts
  1, 1, 3, 2, 3, 2, and 3.  Exact argv, exits, stdout tails, and warning-only
  stderr tails are in the G11 command array of the mirrored gate report.

These are reproduced B2 facts.  The conclusion that validation is pre-effect
is an inference from two independent reproduced facts: the resolver refuses
before returning a `Program`, and the public generate command neither reaches
binding validation nor creates its output.  The only new observation, the P3
`extends` label above, is documentation-specific.  I reproduced no shared
specification defect and no remaining implementation-specific P1/P2 defect.

## Repaired-B2 gate matrix

| Gate | Final R1 result | Principal reproduced evidence |
|---|---|---|
| G0 | PASS 4/4 | frozen scaffold and identical grammar |
| G1 | PASS 28/28 | LALR, 13 resolve/bind cases, all refusals including PostgreSQL |
| G2 | PASS 5/5 | rich static execution and static/live separation |
| G3 | PASS 8/8 | complete footprint and pre-effect static-only refusals |
| G4 | PASS 3/3 | canonical rows and one shared plan/lowering entry |
| G5 | PASS 12/12 | fresh full rename, mappings, capture, collisions |
| G6 | PASS 24/24 | PostgreSQL refusal plus executable g1→g5 evolution |
| G7 | PASS 11/11 | live transaction/routing/group/fold/bound sequence |
| G8 | PASS 12/12 | real mapped capture and typed pre-effect ledger boundary |
| G9 | PASS 5/5 | 173-file regeneration and 168 invariant mutants |
| G10 | PASS 14/14 | forbidden-coupling source and visitor attacks |
| G11 | PASS 2/2 | two real Rust compilations and seven typed parity runs |

ratify
