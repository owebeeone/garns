# Wave-3 repair log — B2

| Field | Value |
|---|---|
| Selected build | **B2** (`build/B2/`) |
| Manager decision | **fold B2** — both frozen reviews close with the line `fold B2` |
| Repair scope | **one bounded repair**: R1 finding **P2.4**, "B2 admits an unavailable backend" |
| Write boundary | only `build/B2/` was written; no other `build/Bn/` was opened or read |
| Frozen inputs | `grammar/`, `brief/`, `corpus/` (lane), `seed/`, `prompts/`, `FROZEN.json` untouched |
| Reviews | `reviews/R1/REVIEW.md` and `reviews/R2/REVIEW.md` read only; **not modified** |
| Tooling | no git operation, no network, no dependency installed |

This document maps **every** finding in both frozen reviews to a repair, a
justified non-change, or an explicit unresolved defect, as `brief/05-ManagerRunbook.md`
requires of a wave-3 pass.

---

## 1. The repair

### 1.1 What changed

`postgres` was already a *recognised* engine, but no PostgreSQL lowering exists
in this build (`src/garns/lower_sqlite.py` and the SQLite `Store` are the only
storage backend). The resolver therefore accepted a deployment that could never
be shipped. The repair splits recognition from lowerability:

- `src/garns/resolve.py:27` — `ENGINES = frozenset({"sqlite", "postgres"})  # recognised engines`
- `src/garns/resolve.py:28` — `LOWERED_ENGINES = frozenset({"sqlite"})`

`Resolver.resolve_deployment` (`src/garns/resolve.py:1229`) keeps its existing
`ENGINE_UNKNOWN` check on the `engine` item (`resolve.py:1258-1259`), records the
position of that item in `engine_at` (`resolve.py:1245`, assigned at
`resolve.py:1261`), and after the required-item loop
(`resolve.py:1282-1291`, which covers `world`, `engine`, `at`, `ship`, `mode`,
`snapshot`) applies the new guard:

- `resolve.py:1292` — `engine = str(values["engine"])`
- `resolve.py:1293` — `if engine not in LOWERED_ENGINES:`
- `resolve.py:1296-1299` — `refuse("ENGINE_LOWERING_ABSENT", "validate", engine_at if engine_at is not None else node.name, …)`

Only after that guard is the IR value built and memoised
(`resolve.py:1300-1304`, `resolve.py:1305`).

| Property | Value |
|---|---|
| Refusal code | `ENGINE_LOWERING_ABSENT` |
| Stage | `validate` |
| Position | the deployment's `engine` item; **or** the deployment name when the engine is inherited through `extends` and the deriving deployment states no `engine` item of its own |
| Unknown engine | still `ENGINE_UNKNOWN` (`resolve.py:1258-1259`) — proving `postgres` remains *recognised*, not deleted |

### 1.2 Why `validate` is the earliest pre-effect boundary in B2

R1 asked for "validation or the first pre-effect ship boundary". In B2 validation
*is* the earlier of the two, and strictly so:

- Deployments are resolved inside the resolver's own run, before a `Program`
  exists: `resolve.py:1034-1035` calls `resolve_deployment` for every declared
  deployment, and `resolve_files` returns `Resolver(files).run()`
  (`resolve.py:1375-1376`). A refusal here means no `I.Program` is ever returned.
- Every effectful entry point takes a `WorldIR`, and the only producer of a
  `WorldIR` is `bind_world(program: I.Program, world_name: str, binding_path: Path)`
  (`src/garns/storage.py:170`), which requires that `Program`:
  - `Store.__init__(self, world: WorldIR, path=":memory:")` — `src/garns/engine.py:164`; `Store.ship` — `engine.py:171`
  - `Engine.__init__(self, store: Store, …)` — `engine.py:186`
  - `generate(world: WorldIR, out_dir: Path)` — `src/garns/generate.py:55`
  - `evolution.migrate(conn, before: WorldIR, after: WorldIR, …)` — `src/garns/evolution.py:220`; `evolution.open_store(conn, world, deployment)` — `evolution.py:327`

So schema DDL, store creation, ledger rows, artifact generation and migration are
all *downstream* of a resolved `Program`. Refusing in `resolve_deployment` is
therefore provably before any effect — asserted rather than asserted-by-argument
by the "no database effect" checks in §2.

### 1.3 What was deliberately NOT done

- **No PostgreSQL implementation.** No `lower_postgres.py`, no second `Store`, no
  dialect switch. R1 explicitly bounded this: "Do not broaden this into a
  PostgreSQL implementation."
- **No deployment redesign.** Grammar untouched (`grammar/garns.lark` is frozen
  and byte-identical); `A.DeploymentDecl`, `I.Deployment`, `extends` inheritance,
  the required-item set and every existing deployment refusal code
  (`ENGINE_UNKNOWN`, `ENGINE_REQUIRED`, `SHIP_MODE_REQUIRED`,
  `DEPLOYMENT_MODE_REQUIRED`, `DEPLOYMENT_SNAPSHOT_REQUIRED`,
  `DEPLOYMENT_LOCATION_REQUIRED`, `DEPLOYMENT_EXTENDS_CYCLE`,
  `DEPLOYMENT_EXTENDS_UNKNOWN`, `DEPLOYMENT_DUPLICATED`) are unchanged.
- **`postgres` was not removed from `ENGINES`.** R1 offered removal as an
  alternative; refusing at the boundary was chosen because it keeps the
  recognised/unlowered distinction visible in a *different* refusal code, which
  is itself testable.
- **No B1/B3 code was folded in**, as R2 required: "Preserve the reviewed B2
  bytes; do not fold in B1/B3 parser, storage, ledger, live, or parity code."

---

## 2. Regression evidence

Counts below are placeholders filled by the builder from the final run on the
repaired bytes: `103` unit tests, `12` gates, `128` gate
checks, `168` mutants.

### 2.1 Commands the builder runs

```
cd build/B2 && PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -m unittest discover -s tests -t .
cd build/B2 && PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python tools/check.py
PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python tools/check_scaffold.py      # from the lane root
```

Expected: `Ran 103 tests … OK`; `12` gates with `128` checks
and a final `ALL PASS`; `PASS v9-5 scaffold`.

**Observed on the repaired bytes (builder, 2026-09-04 15:43):** `Ran 103 tests in 1.745s — OK` (exit 0); `tools/check.py` printed twelve `PASS` lines (G0 4/4, G1 28/28, G2 5/5, G3 8/8, G4 3/3, G5 12/12, G6 24/24, G7 11/11, G8 12/12, G9 5/5, G10 14/14, G11 2/2) and `ALL PASS` (exit 0), writing `gate-report.json` with sha256 `8b422ddfb688a446501f2406e1a15dd1e4ea80984e9941e3904ae08fb905a8f4` (mtime 2026-09-04 15:43:55, `seconds 3.1`); the lane-root scaffold check printed its five `PASS` lines ending `PASS v9-5 scaffold` (exit 0); `grammar/garns.lark` and `build/B2/grammar/garns.lark` both hash `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`; 168/168 mutants matched their authored expectations. `PYTHONDONTWRITEBYTECODE=1` is
mandatory — the frozen scaffold check refuses `__pycache__` anywhere in the lane
(`REPORT.md:259`).

### 2.2 Artifacts

| Artifact | What it proves | Asserted by |
|---|---|---|
| `src/garns/resolve.py:27-28` | `postgres` is recognised but not lowered; the two sets are distinct | `tests/test_repair_engine_lowering.py:45` (`test_postgres_is_recognised_but_not_lowered`) |
| `src/garns/resolve.py:1292-1299` | the refusal sits after all required items and before `I.Deployment` is built | G6 check *"postgres deployment refuses ENGINE_LOWERING_ABSENT at validate, positioned at its engine item"* (`tools/check.py:371`) |
| `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns` | a freshly named, otherwise complete deployment `ARCHIVE_STORE` on world `ARCHIVE` (every required item present, `pool 4` as well); `engine postgres` at **line 24, column 10** | G1 refusal sweep (`tools/check.py:163-167`); G6 check at `tools/check.py:371` pins `("validate", "ENGINE_LOWERING_ABSENT", 24, 10)`; `tests/…:50` |
| `corpus/conformance/refusals/expected.json` | authored expectation `{"file": "ENGINE_LOWERING_ABSENT-1.garns", "stage": "validate", "code": "ENGINE_LOWERING_ABSENT"}` — 12th case; the file is an assertion the runner never reads to decide an outcome | G1 (`tools/check.py:163-168`) |
| no store file after the refusal | no schema, ledger, generation or migration effect ran | G6 check *"no database effect: the store file was never created…"* (`tools/check.py:372`); `tests/…:53` |
| the `engine sqlite` twin of the same source | the refusal is engine-specific, not a defect in the fixture | G6 check at `tools/check.py:374`; `tests/…:55` (`test_sqlite_twin_ships_and_writes`) |
| `engine oracle` variant | `postgres` stays recognised: an unknown engine still refuses `ENGINE_UNKNOWN` | G6 check at `tools/check.py:376`; `tests/…:60` |
| `deployment ARCHIVE_MIRROR … extends ARCHIVE_STORE { engine postgres }` | an engine reached through `extends` refuses identically | G6 check at `tools/check.py:379`; `tests/…:65` |
| `corpus/mutants/ENGINE_LOWERING_ABSENT-1.garns` | migrated-seed single-file mutant (17 lines, deployment `P`, `engine postgres`), generated by `tools/make_mutants.py:88` | G9 mutant sweep (`tools/check.py:549-552`) and the rename/comment/manifest-corruption invariance check (`tools/check.py:577`) |
| `corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT/` (`scenario.json`, `pg/world.garns`, `g1/world.garns`, `g1/storage-W.json`) | steps are **bind → ship → write**; the bind step refuses, so ship and write never execute — a staged, executable pre-effect proof | G6 check *"scenario mutant: bind refuses before the ship and write steps execute"* (`tools/check.py:382-383`); G9 sweep |
| `corpus/mutants/expected.json` | both cases recorded: `ENGINE_LOWERING_ABSENT-1.garns → validate/ENGINE_LOWERING_ABSENT` and `scenarios/ENGINE_LOWERING_ABSENT → validate/ENGINE_LOWERING_ABSENT`; `168` cases total | G9 (`tools/check.py:549-554`) |
| `tools/check.py:346-385` `engine_lowering_regression` | six checks, run first inside G6 (`tools/check.py:388-389`) | the gate itself; `gate.evidence` records both corpus paths (`tools/check.py:384-385`) |
| `tests/test_repair_engine_lowering.py` | five `unittest` cases over the production pipeline, independent of `tools/check.py` | the unit suite |
| `corpus/worlds/practice/deployments.garns:18` (`PROD`) and `:26-27` (`AUDIT extends PROD`) | the migrated corpus still resolves after the repair | G1 resolve+bind of `PRACTICE` (`tools/check.py:147-154`) |
| `corpus/worlds/MIGRATION.md:17` | the corpus edit is declared as a language consequence, with its reason | G1 evidence (`tools/check.py:169`) |
| `generated/PRACTICE/ir.json` (`program.deployments`: `DEV`, `TEST`, `PROD`, `AUDIT`, all `"engine": "sqlite"`), `generated/INDEX.json` | the regenerated products embed the migrated deployment and are byte-reproducible | G9 delete/regenerate check (`tools/check.py:544`) and the twice-generate check (`tools/check.py:547`) |

Note on the mutant count: R2 reproduced **166** mutants on the pre-repair bytes.
The repair adds exactly two cases (one single-file, one scenario), so the final
figure is `168` (`corpus/mutants/` holds 131 single-file sources and 37
scenario directories). Nothing was removed, and the invariance property asserted
at `tools/check.py:577` is unchanged.

---

## 3. Finding map — R1

`reviews/R1/REVIEW.md`, in R1's own order and numbering. Quotes are R1's own
titles/first clauses.

### 3.1 P1 — disqualifying

| # | Finding (R1's words) | Disposition | Justification |
|---|---|---|---|
| P1.1 | "**B1 physical provenance and capture are guessed.**" | not applicable to selected B2 | B1-only. B2 requires an authored binding: `bind_world` (`src/garns/storage.py:170`) loads it through `load_binding`, which refuses `STORAGE_BINDING_UNREADABLE` at `validate` when it cannot be read (`storage.py:140-144`). G10 asserts no `id`/`scope_id`/`_id` convention survives in generated physical names (`tools/check.py:603`). |
| P1.2 | "**B1 runtime identities are not qualified at public helpers/products.**" | not applicable to selected B2 | B1-only. B2 selects reads by qualified name only — `Engine._read` refuses `READ_UNKNOWN` with "reads are selected by qualified name" (`src/garns/engine.py:211`); G10 asserts that boundary in source (`tools/check.py:605`); the collision corpus proves distinct products for identical local names (`tools/check.py:298-302`, `corpus/metamorphic/collision/`). |
| P1.3 | "**B1 live correctness is not executable end-to-end.**" | not applicable to selected B2 | B1-only. B2's G7 runs one integrated engine: nested composition routing (`tools/check.py:442`), neutral batch (`:444`), cross-scope (`:452`), measured zero scans (`:453`), real rollback (`:465`), group move (`:479`), fold equivalence (`:491`). |
| P1.4 | "**B1 generated provenance is stale.**" | not applicable to selected B2 | B1-only. R1 itself reproduced B2 as byte-identical on delete/regenerate (173 files, `byte_identical True`); the standing assertion is `tools/check.py:544` plus `:547`. |
| P1.5 | "**B1 detection consumes filename/comment vocabulary.**" | not applicable to selected B2 | B1-only. B2 classifies from LALR parser state — `classify_decode` (`src/garns/parse.py:69`) over the value stack read by `_stack_of` (`parse.py:51-58`); G9 renames every fixture, strips comments and corrupts the manifest with unchanged outcomes (`tools/check.py:555-577`). |
| P1.6 | "**B1 Rust parity is circular Python/Python execution.**" | not applicable to selected B2 | B1-only. B2 compiles with a real `rustc` (`tools/check.py:624`) and compares typed rows for 7 reads across PRACTICE and SALES (`tools/check.py:633-635`, assertion at `:681`). |
| P1.7 | "**B3 physical mappings are optional guesses.**" | not applicable to selected B2 | B3-only. B2 has no canonical-storage constructor; the binding is an input, and a missing one refuses (`storage.py:140-144`). |
| P1.8 | "**B3 composed live questions cannot execute.**" | not applicable to selected B2 | B3-only. B2's composed inner/outer questions execute and route (`tools/check.py:442-444`). |
| P1.9 | "**B3 lacks transaction identity and transaction-coupled rollback.**" | not applicable to selected B2 | B3-only. B2 validates a typed transaction id before opening a transaction (`src/garns/engine.py:22`, `:94-95`, `:402`) and stores it in revision and ledger rows (`engine.py:220`, `:223`); rollback emits nothing (`tools/check.py:465`). |
| P1.10 | "**B3 detection consumes comments.**" | not applicable to selected B2 | B3-only; same B2 counter-evidence as P1.5. |

### 3.2 P2 — significant, bounded

| # | Finding (R1's words) | Disposition | Justification |
|---|---|---|---|
| P2.1 | "**B1 does not validate registered-call arity/type.**" | not applicable to selected B2 | B1-only; R1 records B2 refusing the same call as `CALL_ARITY`. Committed assertions: `corpus/mutants/CALL_ARITY-1.garns`, `CALL_ARGUMENT_TYPE-1.garns`, `CALL_ARITY`-family cases in `corpus/mutants/expected.json`, swept by G9 (`tools/check.py:549-552`). |
| P2.2 | "**B1 and B3 accept an undeclared writer class.**" | not applicable to selected B2 | B1/B3-only; R1 records B2 refusing `WRITER_CLASS_UNKNOWN`. `WRITER_CLASSES = frozenset({"governed", "external_captured"})` (`src/garns/resolve.py:25`). |
| P2.3 | "**B3's zero-scan/rollback evidence is not live instrumentation.**" | not applicable to selected B2 | B3-only. B2's `Registry.__iter__` increments the counter per visited instance (`src/garns/live.py:81-84`); G7 first forces a deliberate scan to prove the counter is live (`tools/check.py:437`) and only then measures zero (`:453`); G10 asserts the increment exists in source (`:607`). |
| **P2.4** | "**B2 admits an unavailable backend.** Reproduced with a complete deployment: `engine postgres` resolves to `ACCEPT [('D', 'postgres')]`…" | **repaired** | See §1. `LOWERED_ENGINES` (`resolve.py:28`) and the guard at `resolve.py:1292-1299` refuse `validate`/`ENGINE_LOWERING_ABSENT` at the `engine` item, before any `I.Deployment` is constructed and therefore before any store, schema, ledger, generation or migration effect. Regression: `tools/check.py:346-385` (six checks), `tests/test_repair_engine_lowering.py` (five cases), two corpus fixtures. |

### 3.3 P3 — non-blocking observations

| # | Finding (R1's words) | Disposition | Justification |
|---|---|---|---|
| P3.1 | "B2 honestly declares that verbs have no runtime, nested shows are limited to one inverse hop, cross-relation capture order is `(seq, carrier)`, and token cost is unverified… **the limits should remain explicit**." | already satisfied / no change | The limitations remain stated, and the repair *added* to them rather than removing anything: `README.md` §6 *Known limitations* (`README.md:428-456`), including the new postgres bullet at `README.md:436-441`; `REPORT.md` §8 *Limitations and honest non-claims* (`REPORT.md:236-255`), including the new bullet at `REPORT.md:241`. Verbs-no-runtime (`README.md:432`, `REPORT.md:240`), one-hop nested shows (`README.md:442`, `REPORT.md:242`), `(seq, carrier)` capture order (`README.md:449`, `REPORT.md:247`) and `token_bound` reported `unverified` (`REPORT.md:250`, emitted by `tools/check.py:625`) are all unchanged. |
| P3.2 | "B3's regeneration and native row-parity attacks did pass despite its other disqualifying defects." | not applicable to selected B2 | An observation about B3; no B2 action. |

### 3.4 R1's "Bounded repair for the selected build"

> "1. At validation or the earliest pre-effect deployment/ship boundary, refuse
> `engine postgres` with `ENGINE_LOWERING_ABSENT` until an actual PostgreSQL
> lowering exists. Add an executable regression using a renamed, otherwise
> complete deployment. Do not broaden this into a PostgreSQL implementation."

Every clause discharged: refusal at `validate`, the earliest boundary (§1.2);
code exactly `ENGINE_LOWERING_ABSENT`; executable regression on a **renamed**
(`ARCHIVE_STORE` on world `ARCHIVE`, names appearing nowhere else in the corpus),
**otherwise complete** deployment — `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns:22-29`
states `world`, `engine`, `at`, `ship`, `mode`, `snapshot` and `pool`; no
PostgreSQL lowering was written (§1.3).

### 3.5 R1's ratification rerun list

> "Ratification must rerun C0/C1, B2's entire G0-G11 checker, the 98-test suite,
> the fresh R1 rename, missing-binding/collision/comment probes, regeneration,
> live transactional sequence, capture coverage, and native parity against the
> repaired bytes."

| Rerun item | Where the evidence lives in the repaired B2 |
|---|---|
| C0 (grammar hashes) | `grammar/garns.lark` untouched; G0 check *"build grammar is byte-identical to the frozen grammar"* (`tools/check.py:135`) |
| C1 (frozen scaffold) | lane-root `tools/check_scaffold.py`, invoked as a subprocess by G0 (`tools/check.py:131`) |
| entire G0–G11 checker | `tools/check.py` — `12` gates, `128` checks, matrix at `tools/check.py:693-697`, report written to `gate-report.json` (`tools/check.py:713-722`) |
| the 98-test suite | `tests/` — now `103` tests including the five new `tests/test_repair_engine_lowering.py` cases (R1 measured 98 at its snapshot; `REPORT.md:295` recorded 103 at the builder's addendum) |
| fresh R1 rename | G5 metamorphic transform (`tools/check.py:221-232`, checks at `:227`, `:269-272`, `:277`); the name seed is a parameter at `tools/check.py:225`, which is exactly the substitution point R1 used for its private seed (C11) |
| missing-binding probe | `load_binding` refuses `STORAGE_BINDING_UNREADABLE` at `validate` (`src/garns/storage.py:140-144`); sibling binding refusals are committed as scenario mutants (`STORAGE_RELATION_MISSING`, `STORAGE_COLUMN_MISSING`, `STORAGE_COLUMN_COLLISION`, `STORAGE_TABLE_COLLISION`, `STORAGE_WORLD_MISMATCH` in `corpus/mutants/expected.json`) |
| collision probe | `corpus/metamorphic/collision/` with G5 checks at `tools/check.py:298`, `:301`, `:302`; runtime `READ_UNKNOWN` at `src/garns/engine.py:211` |
| comment probe | `classify_decode` from parser state (`src/garns/parse.py:69`, `:51-58`); G9 invariance under rename + comment strip + manifest corruption (`tools/check.py:555-577`) |
| regeneration | G9 (`tools/check.py:544`, `:547`); producer `tools/generate_all.py`; digests in `generated/INDEX.json` |
| live transactional sequence | G7 (`tools/check.py:437`, `:442-444`, `:448`, `:452-453`, `:465`, `:479`, `:491`, `:496`) |
| capture coverage | G8 (`tools/check.py:505`, `:511`, `:513`, `:515`, `:520`) |
| native parity | G11 (`tools/check.py:624`, 7 reads at `:633-635`, assertion at `:681`, measures at `:625`/`:682-683`) |

The repair touches none of these paths except G6, where
`engine_lowering_regression` was **added** ahead of the existing G6 body
(`tools/check.py:388-389`); no existing check was removed or weakened.

---

## 4. Finding map — R2

`reviews/R2/REVIEW.md`. R2's findings are unnumbered section headings; they are
listed here in R2's order. Every one is B1/B3-specific — R2 states so explicitly
("Similar failures in B1 and B3 are implementation-specific because B2
implements the same frozen grammar and contract without them") — so each row
records the B2 counter-evidence **R2 itself cited**, re-verified against the
repaired bytes.

| # | Finding (R2's words) | Disposition | Justification (B2 counter-evidence R2 cited) |
|---|---|---|---|
| P1-1 | "**B1 and B3 do not enforce `live bounded N`**" | not applicable to selected B2 | R2 cited "the only production `LIVE_BOUND_EXCEEDED` occurrence across the builds is B2". Verified at `src/garns/live.py:121-122` — `Instance._fetch` raises `LIVE_BOUND_EXCEEDED` at `runtime` when `len(result.rows) > self.read.live_bound`. Asserted by G7 check *"live bound is enforced at refresh (measured row count)"* (`tools/check.py:496`) and by the `LIVE_BOUND_EXCEEDED` scenario mutant (`tools/make_mutants.py:302-304`). |
| P1-2 | "**B1 and B3 decode results are comment-sensitive detectors**" | not applicable to selected B2 | R2 cited "B2 classifies from Lark parser state". Verified: `classify_decode` (`src/garns/parse.py:69`) driven by `_stack_of`, which reads `ip.parser_state.value_stack` (`parse.py:51-58`). Invariance asserted at `tools/check.py:577`. |
| P1-3 | "**B1 contains forbidden storage guesses and first-item selection**" | not applicable to selected B2 | R2 cited "B2's equivalent bind attempt refuses `validate/STORAGE_BINDING_UNREADABLE`". Verified at `src/garns/storage.py:140-144`. No first-item selection: G10 asserts qualified-name-only public boundaries (`tools/check.py:605`) and forbidden-token scans over `src/` (`tools/check.py:596-600`). |
| P1-4 | "**B3 has an implicit canonical storage adapter and bare runtime aliases**" | not applicable to selected B2 | B2 has no `canonical_storage` equivalent — the binding is an input to `bind_world` (`storage.py:170`) and an unreadable one refuses (`storage.py:144`). Bare aliases are impossible at the runtime boundary: `READ_UNKNOWN`, "reads are selected by qualified name" (`src/garns/engine.py:211`), with the collision suite at `tools/check.py:298-302`. |
| P1-5 | "**B1 and B3 omit typed transaction identity from the ledger**" | not applicable to selected B2 | R2 cited "B2 validates transaction IDs before opening a transaction and stores the ID in revision and ledger rows". Verified: `TRANSACTION_ID` pattern (`src/garns/engine.py:22`), `LEDGER_TRANSACTION_INVALID` pre-effect check (`engine.py:94-95`, called at `engine.py:402`), `Engine.transaction` (`engine.py:214-215`), `transaction_id` written to the revisions row (`engine.py:220`) and every ledger row (`engine.py:223`), carried on each `Delta` (`engine.py:493`, `:525`, `:542`). G8 assertion at `tools/check.py:515`. |
| P1-6 | "**B1's Rust parity claim executes Python twice**" | not applicable to selected B2 | R2 cited "B2 independently compiles generated Rust with `rustc`, runs seven reads, and compares typed row encodings". Verified: `tools/check.py:623-624` (toolchain), 4 PRACTICE + 3 SALES reads at `tools/check.py:634-635`, subprocess run at `:676`, assertion at `:681`. |
| P1-7 | "**B1's scan counter is constant evidence**" | not applicable to selected B2 | R2 cited "B2's `Registry.__iter__` increments the counter on each visited instance". Verified at `src/garns/live.py:81-84` (docstring at `live.py:66`: "Iterating it is a listener scan and is measured"). G7 forces a deliberate scan first (`tools/check.py:437`) then measures zero (`:453`); G10 asserts the increment in source (`:607`). |
| P2-1 | "**B1 and B3 do not provide executable coverage for all of G6**" | not applicable to selected B2 | R2 cited "B2 executes g1→g5 migration/reopen and the required identity, world, scope, exemption, capability, retirement, and move scenarios". Verified: `tools/check.py:410` (g1→g5 classify/migrate/reopen), `:411-412` (continuity, retire/restore), `:413` (renamed column keeps its data), `:423` (`move_home … data drop`), and the identity/module/scope/exemption/capability/trait mutants at `tools/check.py:390-393`. |
| P2-2 | "**B1's G9 checker omits mandatory mutant independence**" | not applicable to selected B2 | R2 cited B2's 166 mutants "spanning decode, validate, ship, load, and runtime", plus rename/comment-strip/manifest corruption. Verified at `tools/check.py:549-552` (now `168` cases), `:554` (stage coverage), `:555-577` (invariance). The repair adds two cases and removes none. |
| — | "**Required bounded repair: none found for G0–G11.** Preserve the reviewed B2 bytes; do not fold in B1/B3 parser, storage, ledger, live, or parity code." | already satisfied / no change | No R2-driven change was made. The only edit to `src/` is the four-line engine guard and two constants in `resolve.py`; nothing was folded in from B1 or B3, neither of which was opened during this pass. |
| — | "Documentation-only Rust naming warnings are non-gating and do not justify a semantic repair." | already satisfied / no change | No change. `src/garns_rust/sqlite.rs` and the generated Rust surfaces are untouched; the snake-case warnings noted at `REPORT.md:260` remain, and G11 continues to gate on row parity only (`tools/check.py:681`). |

**Disagreement between the reviewers, recorded not resolved:** R1 required one
bounded repair (P2.4); R2 found none. The repair satisfies R1 without violating
R2's preservation instruction — it adds a refusal and its regression, and
changes no behaviour R2 reproduced.

---

## 5. Frozen specification

**No frozen-specification contradiction was exposed by this repair.** The repair
is a refusal added inside the resolver over an engine name the *grammar already
admits as a plain identifier*; `grammar/garns.lark` is unchanged and still hashes
identical to the lane-root grammar (G0, `tools/check.py:135`). The frozen
positive corpus, `brief/`, `seed/`, `prompts/` and `FROZEN.json` were not
touched. Both reviewers independently reached the same conclusion on the
pre-repair bytes — R1: "No shared specification contradiction was reproduced";
R2: "No shared specification contradiction was found" — and nothing in this
repair disturbs that.

**The reviewers' initial findings are preserved unmodified.** `reviews/` was
opened read-only. `reviews/R1/REVIEW.md` and `reviews/R2/REVIEW.md` were not
edited, appended to, moved, or reformatted, and no file was created under
`reviews/`. R1's instruction — "Initial findings above must remain intact" — is
honoured; wave-4 ratification appends belong to the reviewers, per
`AGENTS.md` ("ratifying reviewers … append only to their own review").

---

## 6. Changed files

Implementation:

- `src/garns/resolve.py` — `LOWERED_ENGINES` (`:28`) and the pre-effect guard in `resolve_deployment` (`:1245`, `:1261`, `:1292-1299`)

Regression corpus and gate:

- `corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns` (new)
- `corpus/conformance/refusals/expected.json` (one case added)
- `tools/make_mutants.py` (`:88` single-file mutant; `:307-310` scenario)
- `corpus/mutants/ENGINE_LOWERING_ABSENT-1.garns` (new, generated)
- `corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT/` — `scenario.json`, `pg/world.garns`, `g1/world.garns`, `g1/storage-W.json` (new, generated)
- `corpus/mutants/expected.json` (two cases added)
- `tools/check.py` — `engine_lowering_regression` (`:346-385`), called from `g6` (`:389`)
- `tests/test_repair_engine_lowering.py` (new, five cases)

Corpus consequence of the repair (the migrated corpus must resolve):

- `tools/migrate_seed_corpus.py` (`:47-48`) — the declared edit and its reason
- `corpus/worlds/practice/deployments.garns` — `PROD` now `engine sqlite` (`:18`); `AUDIT` inherits it through `extends PROD` (`:26`)
- `corpus/worlds/MIGRATION.md` (`:17`) — the edit is logged with its justification
- `generated/PRACTICE/` and `generated/INDEX.json` — regenerated by `tools/generate_all.py`; `ir.json` embeds the deployment

Documents:

- `README.md` — §6 limitation bullet (`:436-441`) — *updated by the builder after this draft*
- `REPORT.md` — §8 bullet (`:241`) and §11 *Wave-3 repair* (`:302-304`) — *updated by the builder after this draft*
- `gate-report.json` — rewritten by the final `tools/check.py` run — *updated by the builder after this draft*
- `REPAIR.md` — this document (new)

No other file in `build/B2/` was modified, and no file outside `build/B2/` was
written.
