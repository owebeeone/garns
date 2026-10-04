# R2 initial comparative review — Garns v9-5

## Independence and method

I read the required inputs in the mandated order, then B1, B2, and B3. I did
not open any other review. Private attacks were frozen before execution in
`reviews/R2/ATTACKS_FROZEN.md` (SHA-256
`975a2356c7a7d1648afc1a7f2658d72611b598be709f035381891601127c4165`).
Candidate master checks were executed only in the isolated copies under
`reviews/R2/sandbox/garns-v9-5/build/`; source inspection used the immutable
candidate trees. This review does not propose a fourth implementation.

## Outcome

B2 is the only build for which I reproduced every hard gate without finding a
contradicting private attack or forbidden coupling. B1 and B3 share two serious
implementation defects—live bounds are descriptive rather than enforced, and
decode classifications depend on comment text—but these are not frozen-spec
defects: B2 rejects both attacks correctly. B1 additionally guesses storage,
selects first items, has constant scan instrumentation, omits transaction
identity, and does not run Rust for its parity claim. B3 additionally creates
canonical storage by convention, admits bare runtime aliases, has constant scan
instrumentation, and omits transaction identity.

No shared specification contradiction was found. Similar failures in B1 and B3
are implementation-specific because B2 implements the same frozen grammar and
contract without them.

## Findings

### P1 — B1 and B3 do not enforce `live bounded N`

Reproduced fact: `reviews/R2/private_live_bound.py` resolves an unseen question
with `live bounded 1`, inserts two matching rows, and initializes the live
instance. B1 returns two rows and exits 1; B3 returns two rows and exits 1. B2
observes `runtime/LIVE_BOUND_EXCEEDED` and exits 0.

- B1 `LiveInstance.__init__` and `refresh` accept every returned row and never
  inspect the question bound: `build/B1/src/garns/live.py:126-190`.
- B3 has the same omission: `build/B3/src/garns/live.py:100-146`; the only
  production `LIVE_BOUND_EXCEEDED` occurrence across the builds is B2 at
  `build/B2/src/garns/live.py:121-122`.

This fails G3 and G7 for B1 and B3.

### P1 — B1 and B3 decode results are comment-sensitive detectors

Reproduced fact: the same malformed source was run with a harmless comment and
with a comment containing only the word `SELECT`. B1 changes
`EXPR_NOT_ADMITTED` to `SQL_ESCAPE`; B3 changes `DECL_SHAPE_INVALID` to
`SQL_ESCAPE`; both private runs exit 1. B2 reports `DECL_SHAPE_INVALID` for both
and exits 0.

B1 and B3 scan the complete source text with vocabulary regular expressions
before returning a decode code (`build/B1/src/garns/parse.py:42-115`,
`build/B3/src/garns/parse.py:42-115`). B1 is still more direct: lines 112-115
condition on `U12` in the filename. B2 classifies from Lark parser state
(`build/B2/src/garns/parse.py:51-110`). This is a reproduced comment detector,
not an inference. It fails G9 and G10 for B1 and B3.

### P1 — B1 contains forbidden storage guesses and first-item selection

Reproduced source facts:

- Missing key mappings fall back to `id`; link columns are constructed as
  `<link>_id`; scope is `scope_id`; table and changelog names are derived from
  source names (`build/B1/src/garns/resolve.py:1278-1317`).
- Footprints and generation select `worlds[0]`
  (`build/B1/src/garns/footprint.py:132-134`,
  `build/B1/src/garns/generate.py:43-45`).
- `stable_key` guesses `id`, `_id`, or `key`
  (`build/B1/src/garns/live.py:51-61`).

Executable PA-03 fact: resolving `reporting.garns` with no binding succeeds and
reports table `invoice`, identity `invoice_id`, and link column `customer_id`.
The command exits 0 instead of refusing missing storage. B2's equivalent bind
attempt refuses `validate/STORAGE_BINDING_UNREADABLE`.

This fails G5 and G10. The successful B1 metamorphic test changes only a narrow
source/storage subset and cannot negate the direct production fallbacks.

### P1 — B3 has an implicit canonical storage adapter and bare runtime aliases

Reproduced source facts:

- With no storage input, `canonical_storage` derives tables as
  `<module>__<carrier>`, derives identity/scalar/link/scope/changelog names, and
  mirrors writer names (`build/B3/src/garns/storage.py:22-96`). Resolution calls
  it automatically (`build/B3/src/garns/resolve.py:1910-1913`).
- The ledger validator explicitly adds unqualified `local_name` values as
  admitted intent aliases (`build/B3/src/garns/ledger.py:86-94`), while footprint
  and routing keys use local link/intent strings
  (`build/B3/src/garns/footprint.py:88-110`,
  `build/B3/src/garns/live.py:74-97`).

Executable PA-03 fact: resolving the SHOP world with no binding succeeds and
reports the derived table `shop__Item`; the command exits 0. This contradicts
the required refusal of missing mappings and the prohibition on adapter-style
defaults. B3's G5 transform covers only 11 identities in the simple SHOP
fixture; it does not exercise a multihop scope, links, writer identity, or
capture metadata. This fails G5 and G10.

### P1 — B1 and B3 omit typed transaction identity from the ledger

Both ledger schemas and `DataDelta` types carry revision, carrier, row identity,
operation, changes, scope, and writer, but no transaction identity
(`build/B1/src/garns/ledger.py:12-67,155-186` and
`build/B3/src/garns/ledger.py:13-68,148-183`). B1's validator is optionally
populated by callers rather than obligatorily derived from the resolved world
(`build/B1/src/garns/ledger.py:78-114`); its capture adapter also defaults `id`,
`deployment`, fixed changelog metadata names, and an `id` fallback
(`build/B1/src/garns/capture.py:19-70`).

B2 validates transaction IDs before opening a transaction and stores the ID in
revision and ledger rows (`build/B2/src/garns/engine.py:72-99,213-241,388-410`).
This is an implementation-specific G8 failure in B1 and B3.

### P1 — B1's Rust parity claim executes Python twice

`verify_surface_parity` executes the same SQL twice on the same Python
`sqlite3.Connection` and labels the second result Rust
(`build/B1/src/garns/surfaces.py:38-53`). G11 merely runs that Python unit test
(`build/B1/tools/check.py:273-284`). No Rust compiler or binary appears in the
evidence path. This fails G11.

B2 independently compiles generated Rust with `rustc`, runs seven reads, and
compares typed row encodings. B3 also compiled and ran its parity binary in the
isolated check, so this finding is B1-specific.

### P1 — B1's scan counter is constant evidence

B1 documents that `listener_scans` is “strictly 0” and its routing path never
increments it (`build/B1/src/garns/live.py:64-123`). B3 likewise exposes the
field but contains no increment anywhere (`build/B3/src/garns/live.py:57-97`).
Thus both builds report a constant zero rather than measuring listener
iteration. B2's `Registry.__iter__` increments the counter on each visited
instance (`build/B2/src/garns/live.py:65-84`), and the reproduced G7 check first
forces a deliberate scan to show the counter is live before resetting it.

This fails G7 and G10 for B1 and B3.

### P2 — B1 and B3 do not provide executable coverage for all of G6

B1's G6 runner invokes three narrow unit tests: g1→g2 classification,
`move_home` parsing/classification, and bare `renamed_from` rejection
(`build/B1/tests/test_evolution.py:14-84`). It does not execute migration/reopen
or attack listed modules, scope roots, exemptions, and capabilities. B3's G6
checks one classified move, an undeclared move, and reads scope metadata
(`build/B3/tools/check.py:571-595`); it likewise does not migrate a real store or
attack exemptions/capabilities. A claimed gate without executable evidence is a
gate failure. B2 executes g1→g5 migration/reopen and the required identity,
world, scope, exemption, capability, retirement, and move scenarios.

### P2 — B1's G9 checker omits mandatory mutant independence

B1 G9 only generates two fresh temporary trees and compares the returned digest
map (`build/B1/tools/check.py:245-258`). It neither deletes and regenerates the
committed products nor executes later-stage mutants after filename/comment and
manifest corruption. This is independently aggravated by the reproduced
filename/comment dispatch above. B2 exercises 166 mutants spanning decode,
validate, ship, load, and runtime, then renames all fixtures, strips comments,
and corrupts the manifest with unchanged outcomes. B3 does regenerate but fails
G9 because the private comment mutation changes the detector.

## Reproduced command log

All commands were run from `/Users/owebeeone/limbo/datascad/garns-v9-5`
unless a candidate directory is stated.

| Purpose | Exact command | Exit / observed result | Evidence |
|---|---|---|---|
| Frozen scaffold | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_scaffold.py` | 0; frozen inputs, LALR 51 positives, hygiene, identical prompts | `FROZEN.json`, `tools/check_scaffold.py` |
| Grammar identity | `sha256sum grammar/garns.lark build/B1/grammar/garns.lark build/B2/grammar/garns.lark build/B3/grammar/garns.lark` | 0; all `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8` | four grammar files |
| B1 unit suite | `(cd build/B1 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover tests)` | 0; 16 tests | `build/B1/tests/` |
| B2 unit suite | `(cd build/B2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover tests)` | 0; 98 tests | `build/B2/tests/` |
| B1 public G0–G11 | `(cd reviews/R2/sandbox/garns-v9-5/build/B1 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/check.py)` | 0; builder reports all pass; contradicted below | `reviews/R2/sandbox/garns-v9-5/build/B1/gate_report.json` |
| B2 public G0–G11 | `(cd reviews/R2/sandbox/garns-v9-5/build/B2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/check.py)` | 0; 121/121 recorded checks pass | `reviews/R2/sandbox/garns-v9-5/build/B2/gate-report.json` |
| B3 public G0–G11 | `(cd reviews/R2/sandbox/garns-v9-5/build/B3 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/check.py)` | 0; builder reports all pass; contradicted below | `reviews/R2/sandbox/garns-v9-5/build/B3/generated/report/G0.json` through `G11.json` |
| Private enforcement/static/comment attacks | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/private_parse_attacks.py Bn` | B1=1, B2=0, B3=1; enforcement/static-only pass all, comment invariance fails B1/B3 | `reviews/R2/private_parse_attacks.py` |
| Private live-bound overflow | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/private_live_bound.py Bn` | B1=1 (`rows=2,bound=1`), B2=0 (`LIVE_BOUND_EXCEEDED`), B3=1 (`rows=2,bound=1`) | `reviews/R2/private_live_bound.py` |
| Migrated corpora | Candidate-specific `uv run --offline --with lark python -B -c` loop over appflowy, everbility, practice, vaultwarden, and evolution g1–g5 using respectively `parse_and_resolve_sources`, `resolve_files`, and `parse_and_resolve` | B1=0, B2=0, B3=0; 9/9 each | `build/B1/corpus/`, `build/B2/corpus/worlds/`, `build/B3/corpus/migrated/` |
| Missing physical mapping | Candidate-specific `uv run --offline --with lark python -B -c` resolving/lowering REPORTING or SHOP without a binding; B2 calls `bind_world(..., reviews/R2/no-such-binding.json)` | all command exits 0; observation is B1 accepted derived `invoice/invoice_id/customer_id`, B2 refused `STORAGE_BINDING_UNREADABLE`, B3 accepted derived `shop__Item/sku` | storage source paths cited in findings |
| Forbidden coupling audit | `rg -n -i '(case[_ -]?[0-9]+|numbered|expected|fallback|plural|scope_id|worlds\[0\]|questions\[0\]|queries\[0\]|reads\[0\]|listener_scans\s*=\s*0|book|author|everbility|vaultwarden|appflowy|practice)' build/Bn/src` plus targeted `nl -ba ... | sed -n ...p` inspection | 0; semantic hits cited above | `build/B1/src/`, `build/B2/src/`, `build/B3/src/` |

The public B2 report additionally records the exact `rustc` commands, binary
commands, exits, and typed stdout for seven parity reads. Its G5 evidence records
68 renamed identities plus a separately renamed captured world, arbitrary
tables/identity/scalar/link/scope/changelog names, equivalent rows/routing/deltas,
and qualified collision keys. Its G7/G8 evidence records recursive inner/outer
routing, old/new grouped changes, neutral/cross-scope/rollback behavior, measured
zero scans, actual triggers, two-hop scope capture, and PRAGMA-derived coverage
denominators.

## Implementation-by-gate matrix

`P` means independently reproduced with adequate executable evidence. `F`
means contradicted by a private attack/source fact or missing mandatory
executable evidence.

| Gate | B1 | B2 | B3 | R2 basis |
|---|---:|---:|---:|---|
| G0 | P | P | P | scaffold exit 0; identical grammar hash |
| G1 | P | P | P | private policy variants; 9/9 migrated units each |
| G2 | P | P | P | rich static execution and zero query live products reproduced by isolated checks; static-only private refusals |
| G3 | F | P | F | private `bounded 1` overflow accepted by B1/B3 |
| G4 | P | P | P | shared-pair canonical rows and common lowering entry points reproduced |
| G5 | F | P | F | B1/B3 incomplete rename evidence and production defaults/bare aliases; B2 full rename + collision |
| G6 | F | P | F | B1/B3 lack full executable world/evolution coverage; B2 migrates/reopens g1→g5 and attacks all listed facts |
| G7 | F | P | F | B1/B3 ignore bound and publish constant scan count; B1 omits recursive-route attack, B3 only inspects footprint sets |
| G8 | F | P | F | B1/B3 omit transaction identity; B1 also defaults capture names; B2 typed pre-effect + mapped triggers/coverage |
| G9 | F | P | F | B1 omits mutant attack and has filename/comment dispatch; B3 comment-sensitive; B2 166 rename/manifest-invariant mutants + regeneration |
| G10 | F | P | F | direct source coupling above; B2 targeted audit and source inspection clean |
| G11 | F | P | P | B1 Python-twice claim; B2 and B3 compile/run distinct Rust binaries; unmeasured token bounds reported unverified |

## B2 selection and bounded repairs

Required bounded repair: none found for G0–G11. Preserve the reviewed B2 bytes;
do not fold in B1/B3 parser, storage, ledger, live, or parity code. The manager
may proceed directly to the prescribed ratification pass, where R2 will rerun
the whole matrix against the selected bytes. Documentation-only Rust naming
warnings are non-gating and do not justify a semantic repair.

fold B2

## Final ratification — Wave 4

This section is appended to the frozen initial review above. Before this append,
that 223-line file had SHA-256
`c09599b38f00a19a05bbe8dd00b89a2e47d8c57fdc68950cb37a9ad9314f7c2b`;
the initial findings and `fold B2` verdict are unchanged. As permitted only
after both initial reviews were frozen, I read `build/B2/REPAIR.md`, R1's review,
and my own review, then independently inspected and executed the repaired B2.
I did not edit B2 or R1.

### Exact-byte scope and repair disposition

Reproduced facts:

- The reviewed repaired B2 snapshot contains 569 non-`__pycache__` files and
  has SHA-256 tree digest
  `09591d3f6809b33a7edeffe6f3251075f9486dae517ed633a0a9abd6d3d2247a`
  when hashing each sorted relative path, NUL, bytes, NUL.
- `build/B2/src/garns/resolve.py` is
  `0df6e52de2a80e8a5ae4a3c311c4eeb9ae8bc304705d23a2a1183746dca1d2b5`.
  The independent lane copy has the same hash.
- The root, B2, and independent-lane grammar files all have SHA-256
  `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`.
- The production change separates recognised engines (`sqlite`, `postgres`)
  from lowered engines (`sqlite`) and raises typed
  `validate/ENGINE_LOWERING_ABSENT` before constructing or retaining an
  `I.Deployment` (`resolve.py:27-28,1229-1305`). The accompanying conformance
  refusal, unit coverage, scenario mutant, generated evidence, and PRACTICE
  fixture update described in `REPAIR.md` are present.
- A recursive source search found no production first-world selection,
  storage-name guessing/derivation, filename/comment dispatch, or corpus-case
  branches. Its only engine-boundary hits were the declared sets and the two
  typed refusals at `resolve.py:1258-1298`.

Inference from those facts and the executions below: R1's initial P2.4 was an
implementation-specific defect and is repaired at the earliest available
semantic boundary. I found no shared specification defect and no new P1, P2,
or P3 finding in the repaired bytes.

### Independent commands, exits, and evidence

All commands ran from `/Users/owebeeone/limbo/datascad/garns-v9-5` unless the
command itself changes directory. `TMPDIR` values below are under
`reviews/R2/ratification/tmp`; bytecode writing was disabled. The exact-byte
lane is `reviews/R2/ratification/lane`.

| Check | Exact command | Exit and reproduced result | Evidence |
|---|---|---|---|
| Frozen lane/scaffold | `(cd reviews/R2/ratification/lane && TMPDIR="$PWD/../tmp/scaffold" PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check_scaffold.py)` | 0; frozen inputs, LALR corpus (`51` positive, `3` decode refusal, `3` validate input), hygiene, and identical builder prompts pass | `reviews/R2/ratification/lane/FROZEN.json`, `reviews/R2/ratification/lane/grammar/garns.lark` |
| Complete B2 unit suite | `(cd reviews/R2/ratification/lane/build/B2 && TMPDIR="$PWD/../../../tmp/unit" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B -m unittest discover -s tests -t .)` | 0; 103 tests, `OK` | `reviews/R2/ratification/lane/build/B2/tests/` |
| Complete G0-G11 | `(cd reviews/R2/ratification/lane/build/B2 && TMPDIR="$PWD/../../../tmp/gates" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. uv run --offline --with lark python -B tools/check.py)` | 0; 128/128 checks pass | `reviews/R2/ratification/lane/build/B2/gate-report.json` (SHA-256 `a16528d4a6d5ae4dba1ffd8db92aeebec7c2cff9cffb96f0de363c0b3c0af60b`) |
| Original PA-01/PA-02 parser attacks | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/private_parse_attacks.py B2` | 0; direct `unenforced` accepted; invalid enforcement forms and every static-only question form typed-refuse; comment mutations preserve the refusal | `reviews/R2/private_parse_attacks.py` |
| Original PA-06 live-bound attack | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/private_live_bound.py B2` | 0; `runtime/LIVE_BOUND_EXCEEDED`, bound 1 | `reviews/R2/private_live_bound.py` |
| Fresh-seed complete PA-03/PA-04 rename | `TMPDIR="$PWD/reviews/R2/ratification/tmp/private-g5" PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/ratify_private_g5.py` | 0; 12/12, including 68 renamed identities, changed physical SQL, qualified collisions, captured writer/capture names, equal rows/routes/deltas/measures | `reviews/R2/ratify_private_g5.py`, `reviews/R2/ratification/private-g5/` |
| Original missing-binding attack | `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/ratify_missing_binding.py` | 0; `('validate', 'STORAGE_BINDING_UNREADABLE', 1, 1)` | `reviews/R2/ratify_missing_binding.py`, `build/B2/src/garns/storage.py:137-174`; the asserted missing path remains absent |
| Fresh PostgreSQL boundary/pre-effect attack | `TMPDIR="$PWD/reviews/R2/ratification/tmp/postgres" PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B reviews/R2/ratify_postgres.py` | 0; PostgreSQL is recognised/not lowered and refuses `('validate','ENGINE_LOWERING_ABSENT',17,10)`; no Program, binding, or DB exists. SQLite twin ships and commits one ledger row; unknown Oracle refuses `ENGINE_UNKNOWN` | `reviews/R2/ratify_postgres.py`, `reviews/R2/ratification/postgres-probe/` |
| Forbidden-coupling audit | `rg -n -i '(worlds\\[0\\]|first[ _-]?(world|module|carrier|deployment)|derive.{0,32}(table|column|binding|storage)|guess.{0,32}(table|column|binding|storage)|filename.{0,32}(dispatch|case)|comment.{0,32}(dispatch|case)|if .{0,28}(g1|g2|g3|g4|g5|practice|reporting|orders|pantry))' build/B2/src || true` | 0; no matches; semantic inspection clean | `build/B2/src/` |

The PostgreSQL probe deliberately uses fresh names (`r2probe`, `R2ARCHIVE`,
`R2ARCHIVE_STORE`) and follows the potential effect path resolve → binding
document → bind → store ship → transaction. For PostgreSQL, resolution never
returns a Program, so none of the later operations can run; neither a binding
nor database file is created. The successful SQLite twin demonstrates that the
probe does reach those effects when lowering exists. The full gate and unit
suite additionally exercise the conformance source, an `extends` deployment,
and a scenario whose later bind/ship/write steps must remain unexecuted.

The original frozen PA-03 through PA-10 obligations are also covered by the
fresh G5 run and complete gates: recursive/grouped delta behavior (G7), measured
routing and transaction/capture precision (G7-G8), regeneration and detector
independence (G9), coupling audit (G10), and independently compiled Rust parity
(G11). G9 executes 168 mutants across decode, validate, ship, load, runtime, and
accepted outcomes; all 168 retain their observations after filename renaming,
comment stripping, and manifest corruption. G11 compiles two Rust runners and
matches seven typed/ordered reads against Python. These are reproduced facts;
the conclusion that no regression remains is the review inference.

### Final implementation-by-gate matrix

| Gate | Repaired B2 | Fresh result |
|---|---:|---|
| G0 | P | 4/4; includes the repaired engine refusal and pre-effect checks |
| G1 | P | 28/28 |
| G2 | P | 5/5 |
| G3 | P | 8/8 |
| G4 | P | 3/3 |
| G5 | P | 12/12; independently repeated with fresh R2 seeds |
| G6 | P | 24/24 |
| G7 | P | 11/11 |
| G8 | P | 12/12 |
| G9 | P | 5/5; 168 mutants and 168/168 detector-independence observations |
| G10 | P | 14/14 plus the independent source audit |
| G11 | P | 2/2; real Rust compilation/execution and seven parity reads |

No bounded repair is required. The repaired B2 passes the complete matrix and
the originally frozen private attack suite without contradicting evidence.

ratify
