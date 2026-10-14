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
| `await runtime.begin(identity, mutations, context=trusted_context)` | immutable ordered mutation batch fixed before acquire/effect; task-owned transaction |
| `await tx.apply()` | applies the prepared batch once, or returns its prior committed receipt; no arbitrary statement additions |
| `await tx.commit()` / `await tx.rollback()` | explicit terminal knowledge outcome; idempotent only for compatible terminal action |
| `await runtime.reconcile(identity, context=trusted_context)` | authoritative identity-bound commit knowledge, never retry-by-absence |
| `await runtime.aclose()` | typed close outcome, idempotent; unresolved ownership retained |
| `await Provisioner.open(prepared, host=privileged_host)` | separate schema privilege, no general raw SQL escape |
| `await provisioner.inspect(context=trusted_context)` | typed schema snapshot with structural digest |
| `await provisioner.ship(context=trusted_context)` | new or exactly matching owned deployment only |
| `await provisioner.migrate(request, context=trusted_context)` | locked classified migration, explicit expected generation |
| `await provisioner.recover_migration(request, attempt, context=trusted_context)` | privileged request-bound recovery, legal while execution remains fenced |
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
positive; reject booleans and NaN. The trusted-host field `operation_seconds`
defaults to 120s. At entry to execute, begin, ship, migrate or recover_migration,
capture `deadline = monotonic_now + operation_seconds`, before pool acquisition.
The begin deadline covers the complete explicit transaction, including caller
idle time, apply, commit and all retry attempts; no method renews it. A single
read/provision/recovery invocation has its own deadline. Every effect token and
phase deadline is bounded by that absolute deadline. Cleanup has its separate
finite budget. Cancellation requests interruption then bounded cleanup, retaining
the accepted distinction between nonquiescence and uncertain transaction truth.
Transaction retry defaults to one attempt; explicitly retry-safe transaction
functions may request up to three total attempts, bounded by the same operation
deadline. Only known-aborted serialization/deadlock failures qualify. Arbitrary
filesystem/network side effects in a retried body are not made atomic by GARNS.

At transaction expiry, a supervised runtime task revokes new effect/commit
authorization and starts bounded cleanup even if the caller is idle. Accepted
effects retain ownership until settled. Before commit request, rollback is
requested and only confirmed abort yields KNOWN_ABORTED; otherwise retain
INDETERMINATE. After commit request, expiry never converts uncertainty into
abort. A timeline with acquire at t=0..10, apply at t=20..40, idle to t=119 and
commit at t=119 is bounded by t=120, not t=149. Cleanup may run to t=130; only
authoritative evidence can retire its obligation after that budget expires.

No implicit finalizer, automatic success commit on context-manager exit, forced
rollback inference, or nested/savepoint public API is introduced. The first
surface is explicit begin/commit/rollback/close so uncertain outcomes remain
visible. Follow-up convenience syntax requires separate review.

## 4. Storage binding profile and codec decisions

Use a new explicit storage binding version `garns.storage/2`. The implementation
must retain the existing legacy reader separately: `schema` is the required
discriminator, and the legacy value remains `garns-v9-5/storage-binding/1`.
Missing or unknown `schema` refuses, matching the current reader; never silently
upgrade. Version 2 names engine, catalog/schema, every table,
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
Strings use literal UTF-8 for every admitted scalar except double quote,
backslash and U+0001..U+001F. Encode quote as `\"`, backslash as `\\`, and
backspace/tab/newline/form-feed/carriage-return as `\b`, `\t`, `\n`, `\f`, `\r`.
Other control characters use exactly lowercase `\u00xx`. U+0000 is refused,
as are surrogate scalars. Never escape solidus, non-ASCII, U+2028/U+2029 or a
valid non-BMP scalar. Object/array separators are comma and colon without spaces;
the canonical JSON document has no BOM, leading/trailing whitespace or final LF.
The identical serializer governs caller-input normalization and JSONB text
retrieval. Outer payload/binding encodings retain their separately specified
ASCII escaping and final LF. Reject values whose
canonical expansion exceeds the output bound before allocating that expansion.

Opaque remains presence-only in semantic queries. A JSON document binding does
not invent JSON path predicates, JSON indexing or a new expression algebra.
Unsupported operators refuse before lowering. Vector/list-valued storage is
refused in the initial PostgreSQL profile unless W2's element contract and an
explicit codec are implemented and independently verified.

Exact decimals use the tagged value encoding specified in section 6 at the
mutation/ledger boundary. An additive artifact/result contract amendment must
adopt that representation where the inherited format cannot carry Decimal; do not
pass Decimal through an existing float encoder or declare parity with legacy
SQLite REAL. A candidate cannot enable this profile until that amendment is
accepted. The existing W2 plan format is not modified by this design alone.

SQLite version-2 codecs must preserve the same input/output values (JSON stored
as validated canonical TEXT; decimal stored as canonical TEXT) or refuse the
profile. Decimal numeric predicates/order/aggregates refuse on SQLite until an
exact matching implementation exists. Legacy SQLite behavior is not renamed
as exact behavior. Capability negotiation precedes statement effects.

### 4.1 Closed binding-v2 document

The top-level object has exactly `schema`, `world`, `backend`, `namespace`,
`engine_tables`, `relations`; all are required. `schema` is `garns.storage/2`,
backend is postgres or sqlite, world is qualified, namespace has exactly
`catalog` and `schema` (nonempty strings). Every identifier is an authored plain
ASCII SQL identifier matching the legacy identifier rule, at most 63 UTF-8
bytes; quoting is still mandatory. No dot, NUL, SQL fragment or truncation.
SQLite retains the authored namespace in provenance but refuses a namespace
that its adapter cannot map explicitly; it never claims PostgreSQL catalogs.

`engine_tables` has exactly `generations`, `revisions`, `ledger`, `transactions`,
`publication`, `migration_attempts`, `activation`. Each value is a table-name
string; all names are distinct from relations. System columns/constraints are
the fixed engine format `garns.engine/1`, owned by the backend implementation,
not inferred from application names. A schema snapshot includes this format.
No author-defined SQL or renamed system column is permitted in version 2.

`relations` maps exact storable carrier qids (family, not its member aliases)
to objects with exactly `table`, `identity`, `kind`, `columns`, `links`,
`constraints`, `indexes`. All keys are required; empty collections are explicit.
Identity has exactly `column`, `codec` (bigint-v1). Kind is null outside families
or an authored discriminator column; all resolved family constructors have
closed TEXT values. Columns maps the legacy expected qualified use keys to
objects with exactly `column`, `codec`, `bounds`; links maps expected link keys
to `column`/`codec` objects (bigint-v1). Missing/extra mappings refuse.

Codec identifiers are exactly bigint-v1, bool-v1, text-v1, instant-v1,
decimal-v1, bytes-v1 and json-document-v1. Bounds is null except JSON, where it
has exactly max_bytes, max_depth, max_members, all required exact positive ints
within the section-4 ceilings. To request defaults, supply 16777216,128,100000;
there are no reader-invented missing keys. Schema version 2 admits nullable
columns only where resolved semantics is optional; nullability is not editable
as a physical override. Non-nullable family-member columns use their resolved
discriminator guard, not an unconditional NOT NULL that rejects other members.

Constraints is an array of objects with exactly name, kind, fields. Kind is
primary_key, unique, foreign_key or check. Fields is the ordered semantic field
identity list; identity uses the carrier qid plus `.identity`, discriminator
uses `.kind`. Resolver emits a closed required constraint inventory from the
IR: primary identity, one unique for the complete authored key group, a foreign
key for every enforced link, and one check per closed-set/range/discriminator
rule. Match by (kind,fields), never human label; duplicate matches refuse.
Foreign-key destination/action and check meaning come only from resolved IR,
not a binding SQL string. `unenforced` links require no foreign key. Composite
natural-key order is the authored source order. NOT NULL uses column metadata,
not a named constraint record. A semantic check with no implemented closed
rule (including arbitrary invariant expressions) refuses before ship.

Indexes is an array of exactly name, fields, method; method is btree. Fields
is a nonempty ordered list of mapped use/link identities. Constraint/index
names are unique within their PostgreSQL collision domain; primary/unique
backing index names share the index/table namespace. Other constraints share
the owning relation namespace. Validate the complete name inventory before DDL.

Normalization validates against resolved IR, converts no value types, sorts
constraints by (kind,fields,name), indexes by name, and recursively sorts object
keys; semantic fields within arrays retain order. The storage digest is SHA-256
of that normalized object encoded as ASCII compact JSON with ensure_ascii=True
and a final LF. Duplicate JSON keys and unknown fields refuse before normalization.
All namespace, names, codecs and bounds participate. No file path participates.

A complete minimal binding appears in the vector file: world demo.Store,
carrier demo.Document with mandatory payload:Opaque, no key fields or links.
The identity and payload fields, seven distinct engine tables, primary-key
constraint, null discriminator and empty indexes are all explicitly authored.
The input and normalized object are identical; the expected digest is recorded.
Changing whitespace/key order leaves digest unchanged; changing bounds or names
changes it. Version-1 input is dispatched to its reader only; missing/unknown
schema, any extra/missing field, colliding name, unsupported codec, missing
required constraint or excessive bound refuses before effect.

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

Every transaction, including one-attempt explicit transactions, uses
`garns.mutation-payload/1`. The complete immutable ordered batch is supplied at
begin before acquisition or effects. Arbitrary mutation append is not public;
build batches locally without I/O. The envelope is exactly
`{"schema":"garns.mutation-payload/1","mutations":[...]}`. Each mutation has
exact keys `kind`, `carrier`, `identity`, `values`; kind is insert/update/delete,
carrier is qualified, identity is an explicit bigint (including inserts), and
values maps qualified use/link identities to tagged atoms. Delete values is
empty. Unknown/missing keys refuse. Mutation order is significant; values keys
sort by Unicode code point. Omitted values are absent, not encoded as null.

Atoms are closed arrays: `["null"]`, `["bool",true|false]`,
`["int",SIGNED_DECIMAL_STRING]`, `["text",STRING]`,
`["decimal",CANONICAL_EXACT_DECIMAL_STRING]`, `["bytes",PADDED_BASE64]`.
Integers use no leading zero or plus; zero has no minus. Decimal spelling uses
the exact non-exponent rule in section 4. Bytes use RFC 4648 standard padded
base64 with no whitespace. Semantic type/binding validation selects the tag:
Instant/link identities use int, closed sets/newtypes their base tag. Unknown
tags, float, nonfinite Decimal, mutable bytearray, tuple/list/map values and
unsupported scalar types refuse for this initial scalar profile. JSON documents
are opaque bytes canonicalized by their codec before the bytes atom is created.

Payload bytes are ASCII JSON: sorted object keys, compact separators, Python
`ensure_ascii=True` escaping (surrogate-pair escapes for valid non-BMP scalars),
no slash escape, lowercase hexadecimal control escapes, plus one final LF.
SHA-256 of exactly these bytes is the payload digest. The durable identity row
stores encoding version, digest and normalized payload bytes plus original
artifact provenance. Exact byte comparison protects against digest mismatch or
unknown encodings; unsupported historical encoding remains reconcilable via its
durable outcome but cannot be replay-executed through a new encoder.

Generated default/stamp values and induced cascade effects are excluded from
the caller-intent payload; they are fully recorded in typed ledger effects.
User-supplied overrides, including explicit NULL, remain in the intent. A
duplicate same identity resolves against retained original payload/provenance
before evaluating new defaults/stamps or performing DML. It returns the original
outcome; different intent refuses. No implicit identity allocation is offered,
so a retry cannot generate a new insert identity. New-generation validation does
not erase or reinterpret retained identity records.

At begin, validate/normalize the batch and retain it; database-side serialization
of a qualified identity prevents simultaneous owners. Before any batch effect,
look up durable identity; compare original intent, return prior outcome or
refuse conflict. If no final record but the original operation might still be
active, containment/reconciliation takes precedence; it does not authorize
another owner. Apply cannot partially authorize a different batch. Commit seals
the already fixed digest alongside effects. A retry-safe callback, if later
enabled, must produce this batch before effects on every attempt and compare
bytes to the first batch; mismatch refuses. The first slice does not expose that
callback API, even though A7's whole-transaction retry ownership remains fixed.

Exact vectors and expected digests are filed in
`PythonPostgresDatabaseDesign-Vectors.json`. They cover empty batch, omitted
versus NULL, numeric/opaque atoms, ordering, and exact storage binding bytes.

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

Migration recovery is a privileged control-plane operation, not ordinary
runtime admission. Before effects, persist a migration attempt descriptor in
the engine's migration_attempts table: request digest, expected old and exact
requested new binding digests, attempt serial and deployment/activation epoch.
The descriptor is written under the deployment advisory lock and validated
against the coordinator's sealed attempt; it grants no caller authority.
Request/attempt references are returned or recoverable by privileged inspect
even if the initial migrate await was cancelled. Identifiers are references,
never caller-supplied evidence proofs or serialized worker keys.

`recover_migration` opens an independently owned privileged connection under
the same finite lock, authenticates current recovery capability and restores
coordinator state from durable request/attempt evidence plus authoritative
participant inventory. It is legal while ordinary execute/begin/open admission
is fenced. It does not repeat migration SQL. Close/restart retains the durable
descriptor and fence; an unverified participant stop never counts as drain.
The backend/coordinator privately constructs exact phase/serial/successor-bound
proofs; the caller cannot submit a proof digest to reopen a deployment.

Its result is exactly SUCCESSOR_CONFIRMED (requested binding and generation
publication durably proven), NO_EFFECT_CONFIRMED (old binding fully restored,
all effects authoritatively aborted and original workers quiescent, new admission
epoch), or INDETERMINATE (retain fence/ownership and reference). Invalid authority,
wrong request/attempt, unknown phase or stale epoch yields a typed refusal and
no state change. Table absence or schema inspection alone is not abort proof.
No binding-non-reuse/retirement resolution is enabled in this initial profile.
Transaction reconciliation alone cannot settle migration coordination.

Metadata-only recovery reads its atomic generation/proof record, not a data
revision that A12 forbids. Accounted migration recovery requires exact generation,
transaction identity/payload digest and complete effects. After effects but
without authoritative commit/abort evidence it stays INDETERMINATE. A before-
effects cancellation can reopen only with the accepted no-effect phase proof
and barrier acknowledgements. Ack loss after atomic publication returns
SUCCESSOR_CONFIRMED after matching the exact descriptor; never executes twice.

There is no public migration rollback method: cancelling migrate requests
bounded interruption/rollback internally, without claiming it succeeded.
The host must then recover_migration, not call runtime rollback or start a new
attempt. Closing the Provisioner preserves recovery references for a newly
opened recovery Provisioner; normal provisioner open does not require ordinary
data admission or accidentally clear an indeterminate fence.

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
