# W2 shared query-planning design

**Status:** design draft for independent Consistency/Safety review; not accepted
or implementation authority  
**Date:** 2026-10-03  
**Scope:** W2 design only

## 1. Decision and boundary

W2 will introduce one immutable, backend-neutral logical plan for both a
one-shot `query` and a `question`'s initial and refresh computations. The plan
contains qualified semantic identities and the existing resolved expression
classes, but no SQL, driver value, parser/AST node, source `Loc`, runtime
authority, secret, physical-name default, or scope claim. Only questions gain a
separate footprint derived from that same plan closure.

This design depends explicitly on accepted A2, not just transitively on W1.
A2 requires an immutable `Plan`/`ResultShape`, an opaque canonical root, full
type dimensions, pre-adapter validation, and no second expression IR
(`docs/adr/A2-backend-contract.md:3-25`). W1's accepted contract already fixes
`SemanticType`, `Parameter`, `ResultShape`, `PlanOrigin`, `FrozenPlanRoot`,
`Plan`, and binding-origin comparison
(`src/garns/backends/contracts/semantic.py:11-175`). W2 fills only the opaque
root's algebra and bridge.

The existing grammar remains byte-identical. The inherited resolved model is
the semantic source: its path terminals, operands, predicates, show terms and
`Read` dimensions are enumerated at `src/garns/ir.py:177-490`; `TypeRef` retains
base/class/optional/list/nominal/closed/carrier dimensions
(`src/garns/types.py:30-83`). The current SQLite plan is SQL-bearing and
therefore evidence, not the new shared plan (`src/garns/lower_sqlite.py:46-70`).

## 2. Proposed cohesive files and ownership

The future implementation uses only the W2-owned paths frozen by
`docs/PRODUCT_LAYOUT.md:10-20`:

| File | Cohesive responsibility |
|---|---|
| `src/garns/plan/nodes.py` | Frozen relational/result nodes and exact unions. |
| `src/garns/plan/codec.py` | Canonical encode/decode, format registry, digest, detached semantic-expression codec. |
| `src/garns/plan/validate.py` | Structural/type/capability validation and exhaustive visitor bases. |
| `src/garns/plan/footprint.py` | Question-only footprint derivation from logical plan closures. |
| `src/garns/plan/__init__.py` | Narrow exports; no compiler or backend imports. |
| `src/garns/compiler/plan_bridge/build.py` | `WorldIR` + resolved `Read` to W1 `Plan`; diagnostic sidecar. |
| `src/garns/compiler/plan_bridge/functions.py` | Snapshot/validate semantic function identities against the qualified registry. |
| `src/garns/backends/sqlite/lower/expressions.py` | Existing semantic expression classes to SQLite fragments. |
| `src/garns/backends/sqlite/lower/relations.py` | Logical relational nodes to bound SQL/select blocks. |
| `src/garns/backends/sqlite/lower/results.py` | Root/child statements and row assembly contract. |
| `src/garns/backends/sqlite/lower/__init__.py` | Validate then lower entry point. |
| `tests/plan/test_nodes_codec.py` | Algebra, attacks, exact exhaustive registries. |
| `tests/plan/test_bridge.py` | Complete inherited `Read` mapping and shape/type/default tests. |
| `tests/plan/test_footprint.py` | Question footprint/composition/scope parity and query refusal. |
| `tests/backends/sqlite/lower/test_lowering.py` | Differential SQL/results/refusals and hostile names/parameters. |
| `tests/architecture/test_plan_dependencies.py` | Import-direction and node-consumer completeness gates. |

This is a planned decomposition, not a relocation pass. The split-files
guidance favors cohesive files below the review trigger and warns against a
competing broad refactor. No existing file is automatically moved. Exact
legacy integration writes are separately gated in section 11.

## 3. Immutable logical algebra

All nodes are frozen, slotted dataclasses whose tuple fields are normalized at
construction. Strings are nonempty qualified identities where stated; booleans
are exact booleans; counts are exact positive integers; enums reject unknown
values. Every union below has a closed `typing.Union` registry. Visitors use
exact-class dispatch and an `assert_exhaustive` test analogous to the inherited
visitor gate (`src/garns/visit.py:15-56`). Unknown tags always refuse.

### 3.1 Shared leaf values

There is one path object model: decoded plans contain the existing frozen
`I.PathRef` class, never a `PlanPath` class. Canonical `PathRef` encodes
`root`, ordered `steps`, and `terminal`; it omits `text` and `loc`. Each
`LinkStep` encodes qualified `link`, `source`, `target`, exact booleans
`inverse`/`many`, and omits source `text`. Terminals use the existing four exact
classes and all their semantic fields, including `TypeRef`. Decode reconstructs
the same classes with `text=""` and one module-private frozen neutral `Loc`.
Those two reconstructed fields are forbidden to validation/lowering/equality;
the diagnostics sidecar alone preserves real spelling/location. A path begins
at its enclosing scan, has a continuous carrier chain, and is checked against
the authored program. `many` must equal the resolved edge property.

Expressions likewise remain exactly the existing `I.Operand` and `I.Expr`
classes listed at `src/garns/ir.py:249-390`; there is no translation expression
IR. Every semantic dataclass field except `loc`, path/step `text`, is encoded.
Decode supplies only the neutral values above. No AST class is admitted.

The complete inline value registry is:

| Value | Exact fields / rules |
|---|---|
| `TypeRef` | `base`, `cls`: nonempty strings; exact booleans `optional`, `list_of`; `nominal`, `carrier`: null or qualified string; `closed`: ordered unique strings. |
| `LinkStep` and four terminals | Existing IR fields as above; exact class tag; no extra field. |
| `PathRef` | Existing semantic fields above; no canonical spelling/location. |
| `Order` | `key: I.Operand`, `direction: ASC|DESC`; ordered tuple position is significant. |
| `TieBreak` | exactly `NONE`, `SUBJECT_IDENTITY`, `GROUP_KEYS`; no payload. `NONE` covers inherited distinct and global aggregate behavior. |
| `ParameterDefault` | `name: str`, `value: I.Literal`; at most one per declared parameter, sorted by UTF-8 name, exact type equality with that parameter. |
| `AuthorityRequirement` | `kind: UNSCOPED_CAPABILITY`, `qualified_name: str`; zero or one, and only when the resolved read is unscoped by that capability. |
| `Subplan` | `read_qid: str`, `root_node_id: 64-lowercase-hex`; unique and sorted by read qid. |
| `FunctionUse` | fields and fingerprint below; one per used qid, sorted by qid. |

`TieBreak` records inherited lowering, not a new ordering promise: ordinary
non-distinct rows use subject identity, grouped rows use group keys only when
the inherited call site requests a tie break, while distinct/global aggregate
use `NONE` (`lower_sqlite.py:458-471`). `Order`, defaults, requirements,
subplans and function uses are inline canonical values, not DAG nodes.

`FunctionUse(qid, parameter_classes, result_rule, semantic_fingerprint)` has
no SQL. Its fingerprint is SHA-256 over canonical compact JSON plus newline of
`{"parameter_classes":[...],"purity":"pure","qid":...,"result_rule":...,
"semantic_schema":"garns.function-semantics/1"}`. Keys sort lexically;
strings use ASCII JSON escapes. A builtin result rule is
`{"base":NAME,"class":CLASS,"kind":"builtin"}`, where `CLASS` is
`BUILTIN_SCALARS[NAME]`. The inherited `same` rule is exactly
`{"argument":0,"kind":"same","list_of":false,"optional":false,
"projection":"scalar_base_and_class"}`: it preserves argument zero's scalar
base and class and strips optional/list dimensions, matching `result_type()`.
Current pure golden fingerprints are:

| qid | fingerprint |
|---|---|
| `text.normalize` | `1eba5a13d3f72d68d6d808c886dfc9df6c7419e7d99155e085bd7af3e73befc2` |
| `text.lower` | `d80efcd9ee66ae1badccf3ec39a2dfc526d4de907853a4d55142c73d49e90a53` |
| `text.upper` | `0bd651316c9cb046e5734bba58920b5e287c985b8494e7871b45ccbcb91a4970` |
| `text.length` | `f846ff93beb81412c312a638b1be1267695d42f018f6996923c258a8ade86d79` |
| `text.concat` | `4f90932ce4b6d80168b1d0a8bd01e57778389e168f2280aba6302c3c516d605c` |
| `math.abs` | `7621d62d15973211e1375112ac325fd58109449976962646223610715bd78585` |
| `math.round` | `8e452da30e4da17e10db09151dd79a5f2b2ab4c1f912907cba6dde45430a088d` |
| `money.round` | `4b30ba60dec684f8bd3385b57424e18d208db833316dfa4374b82007de68df9a` |
| `money.cents` | `e548dbfd4b7290e98be9c51aefa25ab91a8778b1e26ba16107afc2d1a3b81694` |

Changing qid, purity, arity/order/class, result rule or `same` behavior changes
the fingerprint and invalidates cached admission; volatile/effectful/unknown
entries refuse. Dialect SQL is excluded. Each dialect separately publishes
`(dialect_id, implementation_version, qid, semantic_fingerprint)` for every
implemented function. SQL-only changes increment `implementation_version` and
invalidate dialect SQL caches without changing plan bytes. A semantic-schema
shape change requires a new semantic schema and plan format; adding/changing a
function under the same schema changes only its per-function fingerprint.
Lowerers import only this contract metadata and their dialect table, not the
compiler registry. Contract-only imports from W1 semantic values and plan nodes
are permitted foundations; driver/runtime/compiler imports remain forbidden in
`plan/**` and driver/compiler imports remain forbidden in SQLite lowering.

### 3.2 Relational nodes

`RelNode` is exactly:

| Node | Fields | Invariants / meaning |
|---|---|---|
| `Scan` | `carrier_qid` | One authored logical carrier relation. Member discrimination is explicit via `MemberOf`, not inferred from a physical table. |
| `MemberOf` | `input`, `family_qid`, `member_qid` | Input is the member scan; family/member relation is validated. |
| `ExcludeArchived` | `input`, `archived_use_qid` | Present only for an archival subject without `including archived`. |
| `ScopeFilter` | `input`, `scope_links` | Nonempty qualified scope path; binds the engine-reserved scope parameter at execution. Omitted for deployment scope or authorized unscoped reads. |
| `IdentityFilter` | `input`, `given_name` | Implements `by`; named given must identify the subject/family. |
| `Filter` | `input`, `predicate: I.Expr` | SQL three-valued predicate semantics preserved; optional-given guards remain in the existing expression. |
| `Project` | `input`, `items: tuple[ResultItem,...]` | Ordered visible projection. Empty inherited show is expanded by the bridge to subject uses in declaration order, preserving current behavior (`lower_sqlite.py:478-487`). |
| `Distinct` | `input` | Exact row distinctness after projection; no nested result allowed. |
| `Group` | `input`, `keys: tuple[PathRef,...]`, `having: I.Expr|None` | Group keys are nonempty for explicit grouping; the aggregate-without-keys case uses an empty tuple and yields one group even for empty input. |
| `Sort` | `input`, `terms: tuple[Order,...]`, `tie_break: TieBreak` | User order plus explicit deterministic tie policy; see section 7. |
| `Take` | `input`, `count` | Literal `first N`; positive. |
| `Page` | `input`, `page_given`, `limit_given` | Paired positive integer parameters; offset is `(page-1)*limit`. |
| `OptionalOne` | `input` | At most one row, preserving inherited `one`/`by` shape and deterministic prior sort if stated. |

Composition is represented inside existing `I.Within`, but canonical closure
also contains `Subplan(read_qid, root_node_id)` entries. Every `Within.inner`
must resolve to exactly one entry. This keeps one expression algebra while
making the root self-contained: validators and lowerers never call
`Program.read()` as today's SQLite lowerer does (`lower_sqlite.py:231-237`).
The registry is a DAG: no missing child, unused entry, duplicate qid, digest-id
collision or cycle. The bridge recursively interns identical canonical nodes.

Allowed relational order is validated rather than inferred: source decorators
(`MemberOf`, `ExcludeArchived`, `ScopeFilter`, `IdentityFilter`) precede
`Filter`; `Group` precedes grouped projection/having; `Project` precedes
`Distinct`; `Sort` precedes `Take`/`Page`/`OptionalOne`. Only `Subplan` edges
compose roots. Backend optimizers may transform this only with equivalence
tests; the canonical tree remains authoritative.

### 3.3 Result nodes

`ResultItem` is exactly:

| Node | Fields and output type |
|---|---|
| `PathField` | `qualified_name`, existing `PathRef`, exact `SemanticType`; maps `ShowPath`. |
| `IdentityField` | `qualified_name`, subject identity `SemanticType`; maps `ShowIdentity`. |
| `CountField` | `qualified_name`, nonoptional Integer; maps `ShowCount`. |
| `RankField` | `qualified_name`, nonoptional Integer; maps `ShowRank`. |
| `ScalarField` | `qualified_name`, existing `I.Operand`, exact `SemanticType`; maps `ShowScalar`. |
| `NestedField` | `qualified_name`, `NestedCollection`; maps `ShowNested`. |

`NestedCollection(path, items, last, order, parent_key)` requires a single
inverse to-many edge, recursively unique output names, an optional positive
`last`, and a stable parent correlation. Its child order is the child's
order-flagged uses followed by identity, exactly matching the inherited
lowering (`src/garns/lower_sqlite.py:383-435`). Nested collections may contain
all inherited nested show terms recursively, but may not smuggle filters,
givens, scope changes or an independent read.

`ResultSpec(cardinality, visible_fields, key, order, total)` is the root result
contract. `cardinality` is `COLLECTION`, `OPTIONAL_SINGLE`, `GROUPED`, or
`WINDOWED`. `key` is: subject identity for ordinary/optional/windowed rows;
group paths for grouped rows; all visible scalar fields for distinct rows; and
the empty tuple only for a single global aggregate. `order` names the complete
stable result order. `total` is `NONE` or `UNWINDOWED_COUNT`; the latter is
legal only with `Page` and counts the filtered/grouped result before page/limit.
Empty collections are valid; optional single is zero-or-one; a global aggregate
is one row; explicit groups may be empty.

The exact SQL/result assembly convention uses structural aliases distinct from
visible aliases. Ordinary/optional/windowed identity is `$key.identity` with
the subject identity `SemanticType`; grouped keys are `$key.group.0`,
`$key.group.1`, ... with each path's exact type; nested correlation is
`$key.parent` with the parent's identity type and child identity is
`$key.identity`. These reserved aliases cannot be authored as show aliases.
The assembler reads them into `Result.keys`/parent attachment and never inserts
them into visible row mappings. Distinct keys are the visible fields themselves
and add no hidden alias. A global aggregate has an empty key.

The accepted W1 `ResultShape` has `ResultField(qualified_name,type,key)` but no
visibility/structural role bit (`semantic.py:62-102`). Consequently it cannot
losslessly distinguish an ordinary hidden key from a user-visible key field.
W2 must not silently redefine every W1 field as conditionally hidden. Before
implementation can claim an executable W1 projection, a reviewed W1 ownership
amendment must add an exact visibility/role representation (recommended:
`ResultField.role` in `VISIBLE|STRUCTURAL_KEY|NESTED_OWNER`) or an equivalent
separate structural-key tuple. The same amendment must ratify the nested-owner
marker `SemanticType(base="NestedResult", storage_class="structured",
list_of=True)`, which is never a SQL scalar. Until then, W2 may prototype the
internal `ResultSpec` but must refuse construction of a W1 `Plan` requiring a
hidden key or nested owner; it may construct only distinct/global-aggregate
shapes whose keys are fully visible. This is an explicit launch prerequisite,
not a source change authorized by this design.

The five normative design vectors are:

| Vector | `ResultSpec` key / fields | Required amended W1 shape | Assembled user row / structural key |
|---|---|---|---|
| Ordinary collection showing only `customer` | key `subject.identity`; visible `customer` | visible `customer`; structural `$key.identity: Id(subject), key=True` | `{customer: ...}` / `(identity,)` |
| Optional or windowed showing only `total` | key `subject.identity`; cardinality `OPTIONAL_SINGLE` or `WINDOWED` | visible `total`; structural `$key.identity: Id(subject), key=True` | `{total: ...}` / `(identity,)`; optional enforces 0..1 |
| Grouped by hidden `status`, showing `count` | key `(status,)`; visible `count` | structural `$key.group.0: type(status), key=True`; visible `count` | `{count: ...}` / `(status,)` |
| Distinct showing `customer` | key visible `(customer,)` | visible `customer`, `key=True`; no structural field | `{customer: ...}` / `(customer,)` |
| Root `identity` plus nested `orders` | root identity key; visible identity and nested owner; child parent/id keys | visible root identity (also key); nested owner role and child shape with structural `$key.parent`/`$key.identity` | nested owner populated from child rows; child keys never exposed |

Codec/assembler golden vectors encode those exact aliases, types, roles,
cardinalities and ordering; decode/re-encode must preserve them. The first three
and fifth must refuse at the W1 projection boundary until the amendment exists,
rather than expose keys or mark an unrelated visible field.

## 4. Complete inherited mapping

| Inherited `Read` / expression form | Plan representation or refusal |
|---|---|
| `subject` / member | `Scan`, optionally `MemberOf`. |
| `givens` including defaults and every `TypeRef` dimension | W1 `Parameter`; defaults are canonical root metadata `ParameterDefault(name, Literal)` because W1 `Parameter` has no default field. Runtime binds caller value, else the typed default, else refuses missing. Unknown/extra/wrong-type values refuse before lowering. |
| `where` | `Filter` with the same `I.Expr`: all boolean forms, guards, quantifiers and truth retained. |
| path terminals/forward and inverse links | Existing `PathRef` semantic nodes; chain revalidated against logical identities. |
| literals/givens/clock/dynamic aggregate/arithmetic/negation/static aggregate/call | Same existing operand class, no translation IR. `ClockRef` is query-only and binds one execution clock value. |
| `show` path/identity/count/rank/scalar/nested | Corresponding result item above; omitted show expands declared subject uses. |
| `order` | `Sort`; non-path scalar keys remain legal. |
| `group by` / `having` | `Group`; aggregate and key constraints already resolved and revalidated. |
| `distinct` | `Distinct`; nested refusal preserved. |
| `one` / `by` | `OptionalOne`; `by` also adds `IdentityFilter`. |
| `first` | `Take`; positive literal. |
| `page` + `limit` + `with total` | `Page` plus `UNWINDOWED_COUNT`. Pairing/type/positivity checked before SQL. |
| `including archived` | Absence of `ExcludeArchived`; otherwise explicit decorator. |
| `unscoped capability` | Absence of `ScopeFilter` plus canonical `AuthorityRequirement(unscoped_capability)`. This states required authority, never that a caller possesses it; runtime authority must satisfy it. |
| `composes` / `Within` | Existing `Within` expression plus canonical `Subplan` closure; cycles and current restrictions refuse. |
| `live bounded N` | W1 `Plan.live_bound`; positive and question-only. Not a relational limit. |

There is no design refusal for an inherited form that currently resolves and
lowers. Question-only restrictions remain those already enforced by resolution
and footprintability: clock, static arithmetic/calls/aggregates, `having`,
`distinct`, static composition and windowed inner composition remain explicit
refusals. Those restrictions do not flow backwards onto queries. The resolver's
current shape and restriction logic is at `src/garns/resolve_read.py:590-789`;
W2 duplicates no grammar policy, but validates hostile decoded roots.

## 5. Canonical `FrozenPlanRoot`

`format_id` is exactly `garns.plan/1`. `canonical_payload` is UTF-8 canonical
JSON: sorted object keys; tagged closed-node objects; arrays preserve semantic
order; integers only where specified; no NaN/Infinity; strings in normalized
JSON escaping; no insignificant whitespace and one trailing newline. The top
object is:

```text
{format, profile, root, nodes, subplans, parameter_defaults, function_uses,
 authority_requirements, result}
```

`nodes` is an object keyed by `sha256(canonical-node-bytes)` and sorted by key;
children are ids, making a canonical DAG. `root` is one node id. Expression
objects use the existing IR class tag and its semantic fields, excluding `loc`,
path source text and all file data. `canonical_digest` is lowercase hex
SHA-256 of the exact payload bytes. Neither digest nor payload contains
`PlanOrigin`; W1 carries origin beside the root and binds the same logical plan
to one accepted world/storage/generation.

`authority_requirements` may contain only a qualified named capability required
by resolved `unscoped`; it contains no context, granted capability, effective
scope, principal or writer. It is a semantic precondition, not an authority
claim. Only the runtime can decide whether a genuine context satisfies it.

Construction is encode -> decode/validate -> re-encode equality. Consumption
requires, in order: resource-profile preparse; exact contract classes; known
format/profile; UTF-8/JSON with duplicate-key rejection; canonical byte
equality; digest recomputation using constant-time comparison; exact node and
expression tags/fields; DAG reachability/acyclicity; structural/type/function/
result validation; `Plan.read_qid`/noun/parameters/result/live-bound agreement
with payload; then `BindingIdentity.validate_plan` for world/IR/storage/
generation. Forged digest, noncanonical equivalent JSON, unknown fields/tags,
digest-id mismatch, orphan nodes, recursive/deep bombs, mismatched outer plan,
IR/storage binding mismatch and stale/future generation all refuse before a
dialect or adapter is invoked.

`PlanOrigin.ir_digest` is the qualified resolved program digest;
`storage_digest` is a canonical digest of the authored storage mapping, not a
file path; generation comes from the shipped binding. Existing `WorldIR.digest`
currently combines program/world/storage (`storage.py:126-127`), so the bridge
must calculate and test the two W1 components separately, not reuse it
ambiguously. Diagnostics sidecars are keyed to the verified payload digest and
are discarded on mismatch; their absence changes only source positioning, not
the refusal code or meaning.

### 5.1 Closed schema and completeness

`garns.plan/1` admits only JSON null/boolean/integer/string; the exact enums
named here; registered inline values from section 3.1; existing registered
semantic `Literal`, `Operand`, `Expr`, terminal and type forms; registered
`ResultItem`/`ResultSpec` forms; and registered `RelNode` DAG nodes. Floats are
not an envelope primitive: decimal/float literals use a type-tagged
deterministic decimal string with decode range/type validation. Objects reject
duplicate and unknown keys. UTF-8 identity bytes are significant; there is no
Unicode normalization.

Named registries are `REL_NODE_TAGS`, `RESULT_TAGS`, `SEMANTIC_EXPR_TAGS`,
`SEMANTIC_VALUE_TAGS`, `PLAN_INLINE_TAGS`, and `TOP_LEVEL_FIELDS`. Encoder,
decoder and validator each have an exact handler for every member. A schema
closure test starts at the top object's annotations and recursively requires
every reachable annotation to end in a primitive, exact enum, a registered
inline/expression/result form, or `RelNodeId`; no `Any`, fallback object or
unregistered union is allowed. Only `nodes` is content-addressed; all other
forms are inline. A reachable field/tag addition or rename fails all three
completeness checks and requires a new format absent an explicit future-format
extension rule.

Golden path vectors prove source `text` or `Loc` changes leave bytes unchanged,
while changing root/link/source/target/inverse/many/terminal/type,
order/direction/tie, default value/type, or authority requirement changes the
digest or refuses. Decode always reconstructs existing semantic classes with
neutral spelling/location, establishing one object model.

### 5.2 Resource profile `garns.plan-limits/1`

The profile id is mandatory and fixed by `garns.plan/1`; processes claiming
serialized-plan interoperability may not silently vary it.

| Dimension | Inclusive maximum / counting rule |
|---|---|
| payload | 8,388,608 bytes before UTF-8 decode |
| JSON nesting | 128 open object/array levels in streaming preparse |
| string | 16,384 UTF-8 bytes each; 4,194,304 total decoded string bytes |
| qualified identifier/name | 1,024 UTF-8 bytes each, also charged as string |
| relational DAG | 10,000 unique nodes; a shared node counts once |
| relational/subplan edges | 200,000 references; every occurrence counts |
| semantic expressions | 50,000 dataclass occurrences, including repeats |
| expression depth | 64 nested semantic forms |
| subplans | 256 entries; recursive subplan depth 32 |
| results | 4,096 `ResultItem` occurrences; 1,024 per collection; nesting 32 |
| functions | 256 unique `FunctionUse` entries |
| parameters/defaults | 1,024 each; defaults are a unique-name subset |
| combined semantic depth | 128 across subplan, relation, expression and result recursion |
| total validation work | 1,000,000 units: one per JSON token, object/array member, DAG edge visit, semantic value/expression, result item, metadata entry and provenance-comparison field |

A byte-counting streaming preparse enforces payload, UTF-8 validity, nesting,
per/total strings and token work before materializing JSON and tracks keys to
reject duplicates as each object closes. Precedence is payload overflow
`PLAN_RESOURCE_LIMIT`; otherwise malformed UTF-8/JSON/duplicate key
`PLAN_ENCODING_INVALID`; otherwise the first exceeded profile counter in table
order `PLAN_RESOURCE_LIMIT`; if one token crosses several counters, table order
selects the diagnostic. Scanning stops on that winner rather than seeking a
later error. After parse, canonical-byte/digest failures precede
schema/semantic errors; provenance failure precedes capability/lowering.
Validators use explicit stacks, not Python recursion. Shared DAG nodes count
once for node capacity, but every edge and comparison consumes work.

Vectors accept every exact maximum with a valid witness inside all other
limits, and refuse maximum+1 while all other dimensions remain valid; cover
broad/shallow, deep/narrow, combined-depth/work bombs, 200,000 versus 200,001
edges to one shared node, malformed UTF-8, duplicate keys, payload overflow and
unknown profile. Readers claiming format/profile 1 must agree on admission.

### 5.3 Trusted semantic provenance

Canonical integrity does not prove that a root belongs to a named read. W2
chooses deterministic rebuild-and-compare. The trusted runtime admission owner
(future W3, outside this write scope) retains the exact resolved `Program` and
authored `WorldIR` used to open a binding. Before capability validation or
lowering it calls the synchronous pure W2 bridge to rebuild the complete
expected W1 envelope for `read_qid`: noun, parameters/defaults, result, live
bound, authority requirements, function fingerprints, root DAG and every
recursive subplan. Admission requires byte-for-byte canonical payload, digest,
outer W1 values and `PlanOrigin` equality after binding validation.

`admit_plan(candidate, resolved_program, world_ir, binding_identity) ->
AdmittedPlan` is runtime-internal. `AdmittedPlan` is opaque, process-local,
nonserializable and not publicly constructible. It is neither a W1 protocol
type nor an authority token: after admission, the runtime unwraps its exact W1
`Plan` and passes that to the existing Plan-consuming backend protocol. The
pure bridge owns deterministic rebuilding but issues no trust; runtime owns the
admission decision/cache; backend owns neither.
The cache key is `(read_qid, world, ir_digest, storage_digest, generation,
format_id, profile_id, full_function_fingerprint_set, canonical_digest)`.
Changing any component, reopening/migrating the binding, changing a function
fingerprint, or closing the runtime evicts it. Reachable subplans compare as a
closure, never by qid alone; relabeling changes outer equality and refuses.

This future runtime integration requires an explicit ownership amendment; it
does not authorize W1/W3 edits here. Until integrated, serialized or
caller-constructed `Plan` values must not execute. Exact bridge roots succeed;
canonical correctly digested same-origin mutants that change/remove scope or
authority, archive/member/identity filters, predicate/result expressions or a
subplan refuse `PLAN_PROVENANCE_MISMATCH` before lowering/adapter. Another
read/storage/generation cannot be relabeled.

## 6. Validation, capability, binding and authority order

The pure pipeline is:

```text
resolved IR + authored WorldIR
  -> bridge semantic validation
  -> detached root encode/decode validation
  -> W1 Plan + diagnostics
  -> opened BindingIdentity/origin validation
  -> trusted rebuild-and-compare admission
  -> backend static capability validation
  -> runtime trusted-context authority/scope validation
  -> parameter/default type binding
  -> dialect lowering
  -> adapter execution
```

Static capabilities are a closed set such as relational node tags, scalar
types, expression tags, function qids, nested depth, window functions, JSON
list expansion, and total count. The SQLite capability table must cover the
whole inherited supported set. A PostgreSQL table is a future W4 consumer, not
SQLite SQL rewriting. Static unsupported nodes/functions/types refuse before
SQL construction. Dynamic backend capabilities (`QUERY`; additionally `LIVE`
for a question subscription), server/version and namespace state refuse before
adapter invocation/effect.

The compiler can derive `RequiredAuthority` (scope required; named unscoped
capability), but cannot issue or validate caller authority. W1 runtime remains
the authority owner. The root never stores a claimed scope, capability, writer,
trusted context or secret. Parameter values likewise remain outside the root.
Even a perfectly valid plan cannot bypass effect/delivery checks; question
subscription revalidates authority at W1/W3 entry and delivery barriers.

## 7. SQLite lowering and result semantics

The SQLite lowerer accepts only a decoded validated plan and a separately
validated `WorldIR`. Logical carrier/use/link identities resolve through
`RelationMapping`; no name is synthesized. Authored mapping completeness and
collisions already refuse in `storage.py:170-302`. Every physical identifier is
quoted by doubling `"`; every caller/default/scope/clock/parent value is bound,
never rendered as SQL. Literals embedded in trusted plan bytes may be bound too;
they are never identifier text. Given names map to generated positional slots,
so hostile names cannot become SQLite parameter syntax. The current `q()` and
literal rendering are baseline evidence only (`lower_sqlite.py:28-43`).

Lowering is root-first and deterministic: create a select frame for `Scan`;
apply member/archive/scope/identity/filter; establish joins by full logical path
keys; group/having; ordered projection; distinct; total-count sibling from the
pre-window relation; stable sort; then optional/take/page. Forward optional
links remain left joins. Inverse quantifiers lower to correlated EXISTS/NOT
EXISTS. Dynamic aggregate count/min/max remains correlated. `Within` lowers its
embedded subplan root, not a compiler lookup.

Ordering preserves inherited behavior exactly. User terms lead. Where the
current lowerer requests a tie break, ordinary non-distinct rows append subject
identity and grouped rows append group keys; distinct rows append nothing
(`lower_sqlite.py:458-471`). Rank uses that same inherited call path. This
design does not newly sort unordered distinct results or refuse them for lack
of a total order; paging and distinct are already mutually exclusive in the
resolved shape. Nested children order by parent, declared child order fields,
then child identity. `last N` ranks descending per parent and emits retained
children in original ascending order, matching `lower_sqlite.py:499-523`.

Row assembly checks exact returned aliases/types, builds root keys and nested
parent associations, preserves visible order, represents optional as zero or
one, and returns total separately from rows. Duplicate keys, child without
parent, unexpected/missing column, too many optional rows, or result type
decode failure are backend faults/refusals, not silent overwrite. A question's
`live_bound` is checked on fully assembled root rows, not SQL child rows or
`LIMIT`; it remains independent from query windows.

## 8. Questions, footprints and live coupling

`derive_footprint(plan)` is legal only for `noun == question`; queries refuse
`QUERY_NOT_LIVE`. It exhaustively walks the verified root, all expression paths,
result items, order/group/having nodes, source decorators and every reachable
subplan. It emits the inherited `(carrier, field)` atoms, structural `*`,
composition qids and scope links. Scope paths and authored member/family
relations come from the bridge's validated logical metadata, never physical
names. The current rules are the compatibility oracle
(`src/garns/footprint.py:45-223`).

One admitted `Plan` object is cached by the full provenance key in section 5.3.
One-shot execution,
question initialization and every refresh pass that same object to the same
SQLite lowerer/result assembler. A live instance stores the verified plan
digest, bound parameters, runtime scope and derived footprint. Routing and
deltas remain separate consumers of footprint atoms and committed ledger
deltas; they do not re-read query syntax or rebuild relational semantics.
Recursive composition routing follows the same embedded subplan edges used by
lowering. Refresh enforces `live_bound`, computes keyed changes, suppresses
result-neutral batches and preserves fold equivalence. Existing behavior and
measurements are visible in `live.py:95-165` and `live.py:192-254`.

This design does not claim the current live engine already consumes the plan;
it currently stores `I.Read` and calls synchronous `Engine.execute`. Wiring it
is outside W2 ownership and gated below.

## 9. Exhaustiveness and refusal catalog

There are the six exact registries named in section 5.1. Validator, codec encoder, codec
decoder, footprint deriver, SQLite relational lowerer, SQLite result lowerer
and diagnostic walker declare which registries they consume. Tests compare
each visitor's exact handler set to its registry; adding, removing or renaming a
node fails every affected consumer. Dialect function tables are checked against
the plan's `FunctionUse` set. No default visitor, duck-typed fallback,
`else: str(node)`, or unknown-field ignore path is permitted.

Refusals distinguish malformed encoding/root, plan invariant/type/result
mismatch, function semantic mismatch, static capability unsupported, binding
mismatch, generation mismatch, authority/scope invalid, parameter missing/
unknown/type invalid, and backend fault. Stable source attribution comes from
the sidecar if its digest matches; otherwise it points to the qualified read and
canonical JSON pointer. A forged sidecar cannot change validation.

## 10. Ordered future implementation and verification

1. Implement nodes/registries/codec and hostile decode tests. Prove round-trip
   byte identity and closed exhaustive handlers before adding the bridge.
2. Implement the bridge for every inherited form and W1 shape/origin adapter.
   Golden structural tests enumerate every `Operand`, `Expr`, `ShowTerm`, shape,
   default and type dimension; mutation of any field must change or refuse the
   digest as appropriate. Exercise all five exact result vectors in section
   3.3; hidden-key/nested W1 projection remains blocked until its contract
   amendment is accepted.
3. Implement plan validation/capability tables and dependency checks. Import
   graph must be compiler -> plan <- backend lowerer: `plan/**` imports neither
   compiler nor backend; SQLite lower imports plan/storage/contracts but not
   AST/parser/resolver/plan_bridge; compiler bridge imports no backend.
4. Implement plan footprint derivation. Differentially compare exact atoms,
   composes and scope links with the inherited deriver for every corpus
   question, plus nested/group/scope/composition mutants; queries must refuse.
5. Implement SQLite expression, relation and result lowering. Differentially
   execute old and new paths over all inherited worlds and generated fixtures,
   comparing ordered rows, root keys, nested rows, cardinality, totals, SQL
   parameter sets and refusal code/stage. Old SQL/results are a baseline, never
   fixture dispatch or the only oracle; independent hand-computed seeded rows
   remain required (current examples: `tests/test_static_dynamic.py:58-89`).
6. Exercise identity-preserving semantic renames and arbitrary hostile physical
   renames, quotes/reserved words where storage syntax admits them, duplicate
   logical local names, hostile parameter names/values, list values and literal
   payloads. No source/schema/case dispatch or synthesized name may appear.
7. Reproduce every function golden fingerprint; mutate qid, purity, arity,
   parameter class/order, builtin result and `same` projection. SQL-only
   mutation must preserve plan bytes and fail the dialect-version cache gate.
8. Attack format id/digest/payload, duplicate JSON keys, noncanonical numbers,
   unknown/missing fields, all node ids, cycles/orphans/depth/size, expression
   tags/types, outer `Plan` mismatches, forged origins, IR/storage/generation
   mismatch, function fingerprints and diagnostics sidecar. Run every exact/
   plus-one resource vector, combined bomb, shared-DAG fanout and mixed-profile
   case from section 5.2.
9. Rebuild expected roots and attack provenance with correctly digested
   same-origin mutants for scope/authority/archive/member/identity/predicate/
   result/subplan, plus relabeling. Assert refusal before capability/lowering/
   adapter and exact trusted-root success.
10. Under accepted W1 result-shape and runtime ownership amendments, wire legacy consumers and repeat
   shared-plan equivalence: exact same object/digest for query execution,
   question initial and refresh; bounded overflow refusal; scoped/unscoped and
   nested/grouped/windowed/composed cases; old/new group movement; neutral
   suppression; every-revision delta fold equals recomputation; zero routing
   listener scans. Existing live tests describe these baselines
   (`tests/README.md:32-39`).
11. Run all source-manifest checks, the complete unit/product/evidence suite on
   supported Python minors, and deterministic regeneration. No PostgreSQL or
   async runtime claim follows.

Tests cannot prove SQL semantics on all SQLite versions, PostgreSQL behavior,
driver codec safety, event-loop nonblocking behavior, runtime authority
issuance, crash/restart/replay continuity, concurrency, or real delivery
barriers. Those remain W3/W4/W5 gates. Differential equality can preserve a
shared old bug; independent expected rows, metamorphisms, mutant refusals and
structural attacks reduce but do not eliminate that risk.

## 11. Exact legacy wiring and ownership gaps

The current call graph is not within W2's frozen paths:

| Required future integration | Current evidence | Owner/gate |
|---|---|---|
| Replace `Engine`'s SQL `Plan` import/cache and `lower_read(WorldIR, Read)` with W1 `Plan` creation/consumption. | `src/garns/engine.py:18`, `:194`, `:201-205`; execution still accepts both plan and `Read` at `:281-285`. | `src/garns/engine.py` is outside W2; reviewed ownership amendment, naturally W3 runtime/integration owner. |
| Replace footprint derivation from `WorldIR, Read` and live instances storing `Read` with plan-root derivation/storage. | `src/garns/footprint.py:217-223`; `src/garns/live.py:95-116`, `:192-212`. | Existing files are outside W2 (and future `src/garns/live/**` is W5-owned); amendment plus W3/W5 coordination. |
| Move/replace the legacy `src/garns/lower_sqlite.py` read lowerer and imports without disturbing its DDL consumers. | SQL-bearing `Plan` and `lower_read` at `lower_sqlite.py:46-70`, `:439-525`; DDL shares the file from `:528`. | W2 may create only new `backends/sqlite/lower/**`; edits/deletion/re-export in legacy file need explicit amendment. Keep DDL outside the move. |
| Export or invoke the compiler bridge from compile/generate paths. | Current generation calls inherited lowerer and footprint products; product layout assigns only new `compiler/plan_bridge/**`. | Any edits to `generate.py`, CLI, package exports or test harness need a named integration owner/amendment. |
| Add explicit hidden-key/visibility and nested-owner roles to W1 result shape. | W1 `ResultField` has only name/type/key and cannot encode hidden structural identity/group keys (`semantic.py:62-102`). | Reviewed W1 ownership amendment is a prerequisite to executable W1 plans for ordinary/grouped/nested shapes; section 3.3 gives the required semantics. |
| Admit only rebuilt-equivalent plans at runtime. | W1 plan values are directly constructible; digest integrity is not provenance. | W3/runtime-owned `AdmittedPlan` integration and exact legacy protocol/call paths require a reviewed ownership amendment; caller plans remain non-executable until then. |
| Separate IR digest and authored storage digest from the current combined `WorldIR.digest`. | `storage.py:126-127`. | Bridge may calculate them in its owned path; changing storage API requires amendment. |

No diagram or this design authorizes those writes. An implementation brief must
name exact paths, ownership, migration ordering and compatibility window. Until
then, new W2 packages can be built and tested through owned adapters/harnesses,
but cannot claim production call-site integration.

## 12. Evidence read and nonclaims

This design was prepared against the exact 48-file read-only source manifest
`dev-docs/W2-DesignSourceInputs.sha256` (manifest SHA-256
`b24732fba66b3b649927ef94fc9704abc82641572a90e9374f0bc4990ba981b5`),
the unchanged grammar SHA-256
`3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`,
accepted W1 complete-manifest SHA-256
`95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`,
accepted A2 SHA-256
`cf92142270bc706dbac320cfc448ab3b16e847b3ec3a2771cd711a0b0df3dac2`,
and frozen layout SHA-256
`b4211c5902e47f403fa8bccd15006b14a0737a8d4ac8c0e7691a7f52d7f6d971`.
The accepted parent plan, provider-neutral amendment and acceptance, operator
decisions, governed-write amendment/acceptance, W1 acceptance, checkpoint and
W2 execution brief remain controlling.

This draft changes no grammar, source, test, contract, database, dependency,
service or Git state. It does not accept itself, launch implementation, freeze
a public API, implement PostgreSQL, claim async/runtime behavior, or close W3
Surface/P12. External capture and cryptographic/provider integration remain
deferred; pure compilation remains synchronous.

The corrected design is not fully implementation-ready under the current W1
bytes. Its next action, if reviewers accept the architecture, is a manager-
scoped and independently reviewed W1 result-shape amendment for structural
field roles, followed by an execution brief that assigns runtime admission and
legacy wiring paths. Neither prerequisite is authorized or self-accepted here.
