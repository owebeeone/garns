# Python PostgreSQL database design

**Status:** draft for dual review and separate Surface review; design only.
**Date:** 2026-10-11
**Owner:** GARNS lane owner

## 1. Scope and authority

Complete the generic Python database-definition and governed execution design.
This is not an application schema, a new reconciliation engine, or authority to
start a database, change credentials, activate a deployment, or implement code.
Rust, live delivery implementation, external capture, and application-specific
catalog policies are outside this checkpoint. Existing question semantics are
retained: a backend cannot claim question support without its snapshot contract.

Accepted W1 architecture is controlled by `W1-ACCEPTANCE.md`, not draft headers
in A1-A15. W2 is the composed `W2-QueryPlanningDesign.md` plus
`W2-AdmissionLifetimeRedesign.md`, accepted by its acceptance record. Preserve
that composition; neither the stopped base alone nor a new parallel planner is
an implementation input. Worker-exit acceptance controls internal reference
models only. No reviewed source, grammar, ADR, or historical report is edited.

This document adds concrete W3/W4 design choices; it does not supersede accepted
contracts. New binding codecs require the additive versioned binding extension
in section 4, reviewed here before implementation. Any conflict with accepted
contracts is a blocking finding, not implicit permission to change them.

## 2. Current evidence and remaining work

| Area | Actual state | Next deliverable |
|---|---|---|
| Compiler, binding, SQLite DDL and reads | implemented legacy semantic reference | bridge into accepted W2 plan |
| W2 planning | accepted composed design, no production planner | exhaustive codec, validator, bridge and dialect visitors |
| Lifetime/authority | accepted reference models, including worker exit | real async integration and deployment activation proof |
| PostgreSQL | recognised engine, refuses `ENGINE_LOWERING_ABSENT` | dialect, codecs, async adapter, schema inspection |
| Public async Python API | provisional names in existing ADRs | section 3 and the separate user-facing walkthrough |
| JSON document storage | no named storage codec | versioned codec/binding profile below |

The lane owner ran the existing unittest suite on Python 3.12: 293 passed.
That is baseline evidence only, not PostgreSQL, crash, or release evidence.

## 3. Public Python runtime and execution ownership

`compile_database(sources, binding)` is synchronous, pure and driver-free. It
returns an immutable prepared database artifact with program, binding, schema
and plan-format digests. Compilation never grants admission. Runtime open
revalidates the artifact against the installed generation, capabilities and
trusted-host configuration. No source file lookup, registry mutation or driver
import occurs in `plan/**`.

Proposed public names, to be frozen only after Surface review:

| API | Contract |
|---|---|
| `await Runtime.open(prepared, host=host_config)` | opens owned pool; no implicit schema creation; all configuration validated |
| `await runtime.execute(read_qid, parameters, context=trusted_context)` | qualified admitted read, detached typed result, whole-operation lease |
| `await runtime.begin(identity, context=trusted_context)` | task-owned transaction; nesting/child-task/concurrent use refuse |
| `await tx.mutate(mutation)` | typed governed mutation, with original trusted context retained privately |
| `await tx.commit()` / `await tx.rollback()` | explicit terminal knowledge outcome; idempotent only for compatible terminal action |
| `await runtime.reconcile(identity, context=trusted_context)` | authoritative identity-bound commit knowledge, never retry-by-absence |
| `await runtime.aclose()` | typed close outcome, idempotent; unresolved ownership retained |
| `await Provisioner.open(prepared, host=privileged_host)` | separate schema privilege, no general raw SQL escape |
| `await provisioner.inspect(context=trusted_context)` | typed schema snapshot with structural digest |
| `await provisioner.ship(context=trusted_context)` | new or exactly matching owned deployment only |
| `await provisioner.migrate(request, context=trusted_context)` | locked classified migration, explicit expected generation |
| `await provisioner.aclose()` | same close knowledge contract as runtime |

The trusted host constructs contexts through the accepted runtime registry;
callers cannot manufacture a principal/capability dictionary. `host_config` is
deployment-owned, not request data. The public API never returns a driver,
connection, verifier, private worker key or mutable admission registry.

Plain SDAX orchestrates acquire, admitted work, settlement and cleanup. The
transaction itself is the sole retry owner (A7): SDAX must not retry mutation,
commit or migration nodes independently. Each invocation has isolated state.
The trusted issuer owns effect tokens; graph completion is not commit evidence.
YIDL Lifecycle and TAUT are not new GARNS dependencies: GARNS must not depend on
TAUT, and its accepted reference-model boundary remains the source of lifecycle
semantics. External adapters may project this API into other contracts later.

Configuration defaults are pool min 1/max 10, acquire 10s, statement 30s,
commit 30s, cleanup 10s, shutdown 30s, migration lock 30s. Values are finite and
positive; reject booleans and NaN. An operation absolute monotonic deadline
bounds all attempts; per-phase limits cannot extend it. Cleanup has its separate
finite budget. Cancellation requests interruption then bounded cleanup, retaining
the accepted distinction between nonquiescence and uncertain transaction truth.
Transaction retry defaults to one attempt; explicitly retry-safe transaction
functions may request up to three total attempts, bounded by the same operation
deadline. Only known-aborted serialization/deadlock failures qualify. Arbitrary
filesystem/network side effects in a retried body are not made atomic by GARNS.

No implicit finalizer, automatic success commit on context-manager exit, forced
rollback inference, or nested/savepoint public API is introduced. The first
surface is explicit begin/commit/rollback/close so uncertain outcomes remain
visible. Follow-up convenience syntax requires separate review.

## 4. Storage binding profile and codec decisions

Use a new explicit storage binding version `garns.storage/2`. The implementation
must retain the existing legacy reader separately; absent version means legacy,
never silently upgraded. Version 2 names engine, catalog/schema, every table,
column, constraint/index object, and per-column codec. Unknown keys and codecs
refuse. New physical mapping participates in storage digest, admission and
generation identity; the same resolved program does not imply the same storage.
Each codec has a fixed semantic input/output contract and version. No arbitrary
callable, executable import path or SQL fragment is allowed in the binding.

| Semantic value | PostgreSQL type/profile | Python boundary |
|---|---|---|
| Integer and carrier identity | `bigint` | exact int, not bool; signed 64-bit range |
| Boolean | `boolean` | exact bool |
| Text and text newtypes/closed sets | `text` | exact str, UTF-8, reject NUL; constraints enforce closed values |
| Instant | `bigint` initially | preserve inherited integer instant units; do not invent timezone conversion |
| Decimal/Money | `numeric`, exact decimal profile | finite Decimal or exact int; never float conversion |
| Opaque, `bytes-v1` | `bytea` | immutable bytes |
| Opaque, `json-document-v1` | `jsonb` | validated JSON UTF-8 bytes in, canonical JSON UTF-8 bytes out |

`json-document-v1` preserves semantic JSON including ordered arrays, nested
null and exact finite decimals, not original whitespace/object-key order/number
spelling. Original bytes must use a separate `bytes-v1` field when required.
Reject duplicate keys, nonfinite numbers, invalid UTF-8, unpaired surrogates,
NUL, excess bounds and PostgreSQL JSONB numeric-range violations before DML.
Parse JSON numbers without binary float. Encode numbers exactly and retrieve
JSONB through text plus exact parsing, not the driver's default float decoder.
JSON `null` is non-null bytes `b"null"`; optional-field Python `None` is SQL NULL.
Omitted fields follow mutation semantics, not JSON null or an invented value.

Codec defaults: at most 16 MiB input/canonical output, depth 128, and 100,000
JSON object/array members in total. Binding may lower bounds, never silently
raise them. Bound input scanning, parsing and output building; size rejection
must not first allocate an unbounded canonical output. Numeric limits are the
documented server numeric/JSONB limits, independently tested at boundary values.
Canonical JSON is versioned: keys sort by Unicode code point, no Unicode
normalization, arrays retain order, decimals use exact non-exponent spelling
with fractional trailing zeroes removed and negative zero encoded as zero;
strings use UTF-8 with standard JSON quote/control escapes. Reject values whose
canonical expansion exceeds the output bound before allocating that expansion.

Opaque remains presence-only in semantic queries. A JSON document binding does
not invent JSON path predicates, JSON indexing or a new expression algebra.
Unsupported operators refuse before lowering. Vector/list-valued storage is
refused in the initial PostgreSQL profile unless W2's element contract and an
explicit codec are implemented and independently verified.

Exact decimals require a versioned value encoding at the W2/W1 artifact/result
boundary where the inherited format cannot carry Decimal. Implementation must
first produce a focused additive contract amendment with golden vectors; do not
pass Decimal through an existing float encoder or declare parity with legacy
SQLite REAL. A candidate cannot enable this profile until that amendment is
accepted. The existing W2 plan format is not modified by this design alone.

SQLite version-2 codecs must preserve the same input/output values (JSON stored
as validated canonical TEXT; decimal stored as canonical TEXT) or refuse the
profile. Decimal numeric predicates/order/aggregates refuse on SQLite until an
exact matching implementation exists. Legacy SQLite behavior is not renamed
as exact behavior. Capability negotiation precedes statement effects.

## 5. Schema, constraints and lowering

Retain the semantic model's single integer carrier identity and authored
logical keys. Multiple key fields form a unique constraint; this is not native
composite primary-key support. Links reference carrier identity, with authored
restrict/cascade/detach policy. Composite natural keys can identify records
through static queries without changing identity representation. Native UUID
identity and arbitrary composite foreign keys are not claimed in this profile.

DDL derives from resolved IR and explicit binding: identity primary key,
NOT NULL for mandatory fields, closed-set and range checks, unique authored
keys, typed links and known scope invariants. Nullable keys retain legacy SQL
NULL uniqueness semantics. Defaults/stamps are applied under the same governed
mutation rules as the semantic reference; no ambient NOW or driver inference.
Expose no general trigger/check-expression SQL. Cascades require complete
effect accounting: if the dialect cannot enumerate and ledger every resulting
mutation atomically, refuse the operation before effect (A12/A14).

Index declarations are a separate binding-version-2 physical optimization:
explicit name, ordered authored field identities, method `btree` only, no SQL
expressions, predicates, INCLUDE, concurrent build or inferred index names.
They cannot add a uniqueness rule absent from semantic keys. Validate types
and collations; text uses explicit PostgreSQL `C` collation for deterministic
ordering. Inspection compares definitions, not backend-generated names.

W2 exhaustively maps the inherited relational/result node registry into
PostgreSQL visitors, with parameter placeholders generated independently of
authored names. Values are always parameters; identifier components are quoted
separately. Nested reads share one consistent transaction snapshot, preserve
owner/key/order/result-role semantics, and do not return a driver row object.
Functions use audited dialect entries with matching semantic fingerprints;
unimplemented functions fail before invocation, never fallback to Python.

## 6. Durable transactions and retry

Use Psycopg 3 async and AsyncConnectionPool as accepted A1 prescribes. Open and
close explicitly, no driver import from the compiler. Validate/reset sessions
on every borrow/release; a poisoned, busy, nonquiescent or unreset connection is
discarded, not lent. Fully qualified namespace and safe search_path follow A13.

A4 is unchanged: data, typed ledger effects, transaction identity/payload
digest and revision commit in one transaction. Lock the durable scope
publication row before assigning the next revision; keep it until commit.
Identity/digest uniqueness returns the original committed outcome; another
payload under that identity refuses. Durable identity records outlive generation
changes and ledger retention. Missing reconciliation row is not proof of abort.

A callback-based retry API, when implemented, retains the original identity and
requires deterministic effective mutation payload across known-aborted retries.
A payload mismatch refuses rather than writing under a reused identity. Planned
mutation payload and actual recorded effects must be distinguished so stamped
or backend-induced values do not silently change the idempotency comparison.
The future execution brief must specify that canonical encoding before enabling
callback retries; default one-attempt explicit transactions are not affected.

Cancellation/lost acknowledgement after commit request preserves INDETERMINATE.
Reconcile on an independently acquired connection after original ownership is
contained; runtime shutdown never deletes the reconciliation obligation.
No blanket retry decorators, statement retries or retry after uncertain commit.

## 7. Provisioning, privileges and migration

Database/login creation is an external administrator operation, not runtime
open, ship or migration. Provisioner ships inside an already existing, explicitly
bound database/schema; compare connected database with configured catalog.
Fresh install requires empty owned namespace or a matching verified deployment,
not an empty-looking table probe. Advisory locking serializes ship/migration.
All owned names and generation metadata are validated before any effect.

Migration uses accepted A12 classes and expected previous generation/digests.
No destructive rebuild fallback, silent column drop, online concurrent DDL,
protocol retirement, or credential changes. Migration drains all deployment
leases including buffered/active work per the accepted lifetime overlay; local
runtime close does not perform a deployment-wide drain. New-generation admission
starts only after atomic generation publication. Unsupported migration classes
refuse before execution. Transactional PostgreSQL DDL can be supported only
with the required effect accounting; no success receipt merely from DDL return.

Runtime/migration credentials stay in the trusted host; request principals
cannot read or borrow them. Read-only researcher roles may inspect designated
views only, not bound-data DML. Writer authority is checked through the accepted
context registry before every effect. Privilege inspection includes grants,
ownership, role inheritance and RLS; unsupported states fail closed. Database
superusers/trusted-host compromise remain outside the threat model. An external
SQL editing gateway must call governed operations, not bypass them with raw DML.

Deployment activation is operator-owned stop-the-world fencing, not runtime
automatic upgrade. Reuse the accepted epoch/legacy-access protocol. In the first
implementation, refuse the pending `CURRENT x NONE -> RETIRED` binding operation;
do not depend on its safety or claim the open operator issue is decided. Reopening
that capability requires its separately reviewed decision/contract.

## 8. Cohesion and implementation order

| Package | Owned responsibility and prerequisite |
|---|---|
| W2 | accepted node/codec/validator/bridge/SQLite lowering; no driver or runtime |
| W3 | public runtime, trusted-host API, SDAX ownership/cleanup, SQLite async adapter; consume W2 and amended W1 |
| W4 codecs/binding | binding-v2 reader and codec registry; focused value-artifact amendment before exact-value activation |
| W4 PostgreSQL | `backends/postgres/` dialect, pool, codecs, schema inspection, governed writes and provisioning |
| A10 sub-lane | owned isolated PostgreSQL 15-18 services and secret-redacted evidence |
| W5 | snapshot/live/replay integration, remains a separate subsequent package |

Use existing `docs/PRODUCT_LAYOUT.md` write boundaries. No builder gets authority
to edit a neighbor's frozen interface incidentally. An integration brief must
enumerate any legacy wiring changes before implementation. W4 follows W2/W3;
codec research/service tooling may proceed independently, not a second runtime.

## 9. Proof gates and release boundaries

| Gate | Required independent observation |
|---|---|
| G1 planning | exhaustive node visitors, malformed formats, old-artifact rejection, admitted lifetime over fetch/assembly |
| G2 values | JSON duplicate titles/keys distinctions, null/absence, deep/oversize payloads, exact numeric boundaries, archive bytes |
| G3 schema | ship, matching re-open, drift refusal, poisoned namespace, metamorphic names, keys/links/index definitions |
| G4 transactions | two writers, stale revision predicate, atomic ledger/data, rollback no revision, deadlock and serializable abort |
| G5 uncertainty | cancel acquire/read/write/rollback/commit; kill before/after durability; restart reconcile same identity/digest |
| G6 privilege | read-only versus writer/migrator, hostile role/RLS and session mutation, secret redaction |
| G7 evolution | lock contention, held read lease, mixed generation, unsupported cascade/backfill pre-effect refusal |
| G8 surface | cold first-day walkthrough, explicit close/rollback/reconcile, defaults, no driver's object escape |

Execute G2-G7 on fresh isolated real servers 15,16,17,18 with recorded driver,
server and artifact versions, not the shared local server. Native async tests
must show another coroutine progresses during blocked I/O. Byte/digest golden
vectors and independent SQL reads are evidence, not detector inputs. Record each
capability as implemented/verified/refused separately, with no blanket parity.

Initial usable database slice: compile authored schema, provision, inspect,
execute a static read, write and rollback, restart and reconcile, then migrate
an explicitly metadata-only supported change. JSON/exact-value profile enables
only after its contract amendment and G2. A subset milestone does not declare
W4/W5 or a v9-6 release complete; question/live refusal is explicit until proved.

Review this design with two peer-blind Consistency/Safety reviewers. Separately
review `PythonPostgresApiWalkthrough.md` as a cold Surface step. At most two
remediation rounds; a third architectural root triggers STOP. Final acceptance
must name exact design/input tuple and reports. No implementation launch or
PostgreSQL support claim follows from documentation approval alone.
