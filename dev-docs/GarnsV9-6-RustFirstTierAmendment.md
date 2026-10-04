# Garns v9-6 Rust first-tier amendment

**Operator decision:** binding, D9 — Rust is a first-tier product language alongside
Python ("rust is first tier, along with python", 2026-10-04)  
**Architecture status:** draft for review; not independently reviewed  
**Decision date:** 2026-10-04  
**Recorded by:** operator's drafting session, for manager integration

Garns v9-6 ships two first-tier runtime languages with equal standing. This
amendment states what that changes in the accepted plan, which decisions it
requires, and the work packages that deliver it. It is a draft: under the lane's
own rules it binds W2 and later packages only after peer-blind review and
acceptance. The operator decision itself is binding now.

## Governing documents and precedence

This is an additive amendment. It does not alter any reviewed historical
document or acceptance record.

| Historical document | SHA-256 |
|---|---|
| `GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |
| `GarnsV9-6-GovernedWritesScopeAmendment.md` | `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe` |
| `GarnsV9-6-OperatorDecisions-D6a-D7-D8.md` | `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f` |
| `GarnsV9-6-OperatorDecisions-D4-D6b.md` | `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce` |

It supersedes only the plan's implicit Python-only scope: the single-language
public API, packaging and release evidence. Every other requirement remains
binding, including the frozen grammar, the direction invariants, PostgreSQL
primary with SQLite secondary, the async-only public API, governed writes only,
and the review discipline.

## 1. What "first tier" means

- **Both languages ship a public async database API** over PostgreSQL (primary,
  15–18 per D4/D6b) and SQLite (secondary, supported), with the same semantics,
  the same refusal codes and the same API style. The requirement for one client
  API across engines applies within each language, and the API style matches
  across languages.
- **Both are release-gated.** No v9-6 release ships with only one of them, and
  every compatibility claim names real executable evidence in both.
- **Both use the sdax family** for lifecycle orchestration, carrying forward the
  operator decision of 2026-09-12: Python `sdax` (PyPI, 0.7.2, Python 3.11+, no
  dependencies) and `sdax-rs` (`sdax` core with no dependencies, plus the
  `sdax-tokio` adapter). Until now this decision was absent from the v9-6 record.
  `sdax-rs` is published once Garns, its first use case, is using it (D9c).

## 2. How this composes with accepted decisions

**D8 (one convergent implementation)** forbids competing whole-product builds. A
Rust runtime implementing the same frozen interfaces, under its own single-writer
ownership, is a component, not a competing build, so D8 holds. D8's root table
names exactly one product root, now `/Volumes/projects/limbo/garns-wz/garns` (see
`GarnsV9-6-Relocation.md`). The Rust code therefore lives inside it (D9a).

**Direction invariant 1** (source resolves once into the qualified IR) and plan
§6 ("a backend never imports the parser/resolver, and the compiler never imports a
database driver") hold unchanged. **The Python compiler remains the only
compiler.** Rust never parses or resolves Garns source.

**A2** already makes the plan root "opaque canonical bytes plus format/digest",
with plan origin recording world, IR digest, authored-storage digest and
generation. This amendment turns that encoding from opaque into a **published,
versioned, language-neutral format**. It becomes the language boundary, consumed
by both runtimes.

**A16** admits a plan only after "deterministic canonical rebuild-and-compare".
That presumes an in-process compiler. A Rust runtime has none, so Rust admission
must instead verify the artifact's provenance digests against the bound world.
This needs an A16 amendment (§5), designed so that neither runtime admits an
artifact it cannot authenticate.

**A1, A3, A7, A8 and A11** are Python-shaped. Each needs a Rust counterpart with
the same observable semantics (§5).

## 3. Architecture: one compiler, two runtimes

```text
source + grammar ─► Python compiler ─► qualified IR ─► WorldIR ─► Plan (A2)
                                                                    │
                     published, versioned, language-neutral artifacts:
                     plan encoding · ResultShape · typed values · parameters ·
                     refusal envelope · revision/ledger/batch envelopes
                                   │                          │
                          Python runtime (sdax)       Rust runtime (sdax-rs, tokio)
                          ├─ SQLite adapter (A8)      ├─ SQLite adapter (A20)
                          └─ PostgreSQL (A1)          └─ PostgreSQL (A19)
```

- **The Python reference models stay the executable specification.** Rust
  conformance is proven against **language-neutral conformance vectors** generated
  from them — inputs, expected results, expected refusals, expected state
  transitions — not by porting the reference models as a second specification.
- **Both runtimes can serve the same PostgreSQL store.** Revision allocation, the
  ledger, replay and commit publication (A4, A7) are database protocols, so they
  must be specified at the wire level and implemented identically. A writer in one
  language and a subscriber in the other must interoperate on PostgreSQL. On
  SQLite, cross-process sharing is not claimed.

## 4. Operator decisions D9a–D9d

Ruled 2026-10-04. D9c and D9d were set by the operator; the proposed defaults
for D9a and D9b stood.

| # | Decision | Ruling |
|---|---|---|
| **D9a** | Where Rust code lives | **In-tree**, under `crates/**` in the one product root, as a Cargo workspace beside `src/`. D8's root table needs no change. The `garns-wz/garns-rust` member — 133 lines: contract-ID constants and the stage enum — is superseded; its crates may seed `crates/`, and the member itself is left as it is. The alternative, keeping Rust in `garns-rust`, puts product code outside the only product root and needs a D8 amendment. |
| **D9b** | Rust support range (the D6a analogue) | MSRV **1.75**, matching what `garns-rust` and `sdax-rs` declare, plus current stable. Neither repository has ever measured 1.75, so the MSRV is claimed only after a real build on that toolchain, exactly as D6a requires real interpreters. A missing toolchain is a provisioning task, not authority to narrow the range. |
| **D9c** | `sdax-rs` publication | **Publish `sdax-rs` once Garns — its first use case — is using it.** In practice that is when R3's lifecycle runs on it, so it is published before W7's crates.io release. This replaces the earlier keep-private posture. |
| **D9d** | Which runtime ships and migrates stores | **Both runtimes ship and migrate.** Planning stays single-sourced: the Python compiler produces each ship or migration request — its A12 class, the expected previous generation and digests, the next binding, per-dialect statements, typed effects and the request digest — as a versioned A17 artifact. Each runtime applies it under the A12 deployment lock, refuses on drift, accounts effects atomically under `migration:<request-digest>`, and publishes the new generation. A2 already makes migration application a method every backend retains. Ship is the first-generation case of the same mechanism. |

## 5. W1 additions — new and amended decision records

All are reviewed before W2 freezes its plan encoding.

| Record | Content |
|---|---|
| **A17 — cross-language artifacts** | The published formats for the plan encoding, ResultShape, parameters (incl. list givens), the refusal envelope (`code`, `stage`, `file`, `line`, `column` contractual; `detail` advisory), the revision/ledger/batch envelopes, ship and migration requests (D9d), and typed value codecs — including the `Instant` domain (unit, epoch, width, no timezone), `Boolean` and `Decimal`/`Money` normalisation, so that both languages and both engines return the same types. Versioning: exact identifiers, unknown versions refused, never guessed. The conformance-vector format. |
| **A18 — Rust async runtime and lifecycle** | tokio plus `sdax-rs`; the A3 open/close and one-owner transaction semantics in Rust; cancellation without async `Drop` (consuming `commit`/`rollback`, or discard of the connection), with no future dropped between ledger write and `COMMIT` able to leave an open transaction; the A7 retry contract; A11's trusted context. |
| **A19 — Rust PostgreSQL driver** (A1 analogue) | Driver and pool selection, e.g. `tokio-postgres` with an sdax-managed or `deadpool` pool; SQLSTATE-based refusal mapping; real-server verification on 15–18 per D4/D6b. |
| **A20 — Rust SQLite adapter** (A8 analogue) | `rusqlite` on one dedicated thread per connection with a serialised command queue; nothing blocking on the async executor. Garns crates keep `unsafe_code = "forbid"`; driver crates are exempt. |
| **A3 amendment** | Lifecycle orchestration in both runtimes uses the sdax family. Python `sdax`'s task model must preserve A3's rule that the runtime task captured at creation owns the transaction handle and is compared by identity. Note that `sdax.task_sync_func` runs blocking work inline, so it is not an executor bridge; A8's worker thread remains the bridge. |
| **A2 amendment** | The plan root encoding is published and versioned under A17. |
| **A12 amendment** | Ship and migration requests are compiler-planned A17 artifacts, applied by either runtime through one executor contract (D9d). A12's compatibility check ("mixed binaries outside an explicit window refuse") becomes language-neutral: it compares digests, not binaries, so it holds across a Python and a Rust runtime serving one store. |
| **A16 amendment** | Admission without an in-process compiler: provenance-digest verification of the artifact against the bound world, IR, storage and generation, giving the same refusal outcomes as rebuild-and-compare. |

## 6. Design question for review

**Where dialect lowering lives.**

- **(a) Each runtime lowers the SQL-free plan itself.** Plans stay dialect-free
  end to end, but every dialect gets two lowerers, one per language, plus a parity
  burden between them.
- **(b) Lowering happens once, in Python, and lowered dialect statements travel in
  the artifact.** One lowerer per dialect; Rust executes, binds and shapes results.
  This is close to what v9-5's generated tree already did, and G11 already shows
  Rust reading generated SQL with identical row encoding.

**Tentative recommendation: (b)** for v9-6. It single-sources lowering, which is
the riskiest semantic code, and it matches D9d, which already splits ship and migration
the same way: plan once in Python, apply in either runtime. Note that A2 rejected "portable SQL"
*as the plan*; lowered per-dialect statements carried *alongside* a SQL-free plan
are a different thing, and reviewers should confirm that distinction holds.

## 7. Work packages

The R packages run in parallel with their W counterparts, with disjoint write
paths (`crates/**` versus `src/**`). Each R package is a milestone. Steps are
goals with an aspirational budget of 500 LOC; larger runtime steps are split
during package planning.

### Product layout additions *(a boundary change, reviewed with this amendment)*

| Surface | Path |
|---|---|
| language-neutral schemas and conformance vectors | `contracts/**` |
| artifact decoding | `crates/garns-artifact/**` |
| Rust runtime and lifecycle | `crates/garns-runtime/**` |
| Rust SQLite adapter | `crates/garns-sqlite/**` |
| Rust PostgreSQL execution and live | `crates/garns-postgres/**` |
| Rust tests | matching `crates/**/tests` and `tests/rust/**` |

### R1 — cross-language contracts *(with W1, before W2 freezes)*

| Step | Goal |
|---|---|
| R1.1 | Record D9a–D9d as operator decisions. |
| R1.2 | A17: artifact formats, value codecs, versioning, conformance-vector format. |
| R1.3 | A18–A20, plus the A2, A3 and A16 amendments. |
| R1.4 | The conformance-vector generator, specified over the W1 Python reference models. |

**Exit:** A17–A20 and the amendments accepted GO/GO; the vector format frozen.

### W2 — additions

The plan algebra's canonical encoding satisfies A17. W2's exit adds the published
encoding specification, its golden vectors and a Python emitter whose output a
second implementation can decode. The compiler also emits ship and migration
requests as A17 artifacts (D9d), and the Python runtime (W3/W4) applies them
through the same executor contract as Rust, so both executors face the same vectors.

### R2 — artifact pipeline *(with W2)*

| Step | Goal |
|---|---|
| R2.1 | `garns-artifact`: decode every A17 artifact and refuse unknown versions; seeded from the existing `garns-rust` crates. |
| R2.2 | Typed value codecs matching A17, proven against the vectors. |
| R2.3 | The refusal envelope and the Rust error type. |

**Exit:** Rust decodes every golden vector byte-for-byte and refuses every
malformed or unknown-version vector.

### W3 — additions

The W3 Surface review becomes a **two-language surface review**: the Python API
and the Rust API freeze together, one semantic specification with two bindings.
The A16 note that names stay provisional until W3 Surface review applies to both.

### R3 — Rust runtime with SQLite *(parallel to W3)*

| Step | Goal |
|---|---|
| R3.1 | Runtime open/close lifecycle on tokio and `sdax-rs`; idempotent close. |
| R3.2 | Execute and result retrieval from artifacts; parameter, scope and capability binding identical to Python's refusals. |
| R3.3 | Transactions, ledger and commit publication; cancellation-safe rollback under A18. |
| R3.4 | The SQLite adapter on a dedicated thread (A20). |
| R3.5 | The subscription resource, close and resource release. |
| R3.6 | Apply ship and migration requests on SQLite through the D9d executor contract. |

**Exit:** the W3 exit criteria hold in Rust, and the shared conformance vectors
pass in both languages.

### R4 — Rust PostgreSQL *(parallel to W4)*

| Step | Goal |
|---|---|
| R4.1 | Driver and pool per A19; session sanitation before reuse. |
| R4.2 | Execution and refusal mapping by SQLSTATE; serialisation/deadlock retry per A7. |
| R4.3 | Apply ship and migration requests under the A12 deployment lock: verify the expected previous generation and digests, account effects atomically, publish the generation, refuse on drift or outside the compatibility window. |

**Exit:** the W4 exit criteria hold in Rust against real PostgreSQL 15–18.

### R5 — Rust live *(parallel to W5)*

| Step | Goal |
|---|---|
| R5.1 | Revision, replay and subscription delivery per A4 and A6. |
| R5.2 | Overflow surfaces as a refusal, never a dropped batch (`live bounded N`). |
| R5.3 | Cross-language interoperation on PostgreSQL: Python writer to Rust subscriber, and the reverse. |

**Exit:** the W5 exit criteria hold in Rust, and cross-language delivery is
demonstrated on PostgreSQL.

### W7 — additions

- A cross-language differential suite: both languages, both engines, the same
  vectors, rows, refusals and revisions.
- A Rust toolchain matrix (MSRV and stable) per D9b.
- Packaging for PyPI and crates.io; `sdax-rs` is published first (D9c).
- Documentation and executable examples in both languages.
- The v9-5 raw-FFI parity runner (`src/garns_rust/sqlite.rs`, gate G11) retires
  into historical evidence once R3 provides real runtime parity.

W6 (capture) stays deferred, with no Rust counterpart.

## 8. Sequencing

```
R1 contracts ─► W2 + R2 (encoding, emitter, decoder) ─┬─► W3 (Python runtime) ─┐
                                                      └─► R3 (Rust runtime) ───┴─► joint Surface review
                                                                                          │
                                       W7 release ◄─ W5 ∥ R5 (live) ◄─ W4 ∥ R4 (PostgreSQL) ◄─┘
```

## 9. Effect on current work

- **The parked W1A11 review is unaffected.** It judges Python contract bytes, and
  no file in its tuple changes. It proceeds as the relocation record says.
- **W2 must not freeze its plan encoding before A17 is accepted**, because the
  encoding is now a cross-language contract.

## 10. Not changed

The grammar (frozen); the Python-only compiler; direction invariants 1–12;
PostgreSQL primary and SQLite secondary; the async-only public API; governed writes
only, with capture deferred; one product root; and the review-loop discipline.
