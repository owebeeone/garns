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

`PlanPath(root, steps, terminal)` is a detached use of the existing semantic
path meaning: each step carries qualified link/source/target plus inverse/many;
the terminal is exactly one existing `UseTerminal`, `LinkTerminal`,
`IdentityTerminal`, or `KindTerminal`. It excludes source spelling and `Loc`.
It must start at the enclosing scan carrier, have a continuous carrier chain,
and agree with the authored `Program` and `WorldIR` when bridged and again when
lowered. `many` is derived, never caller supplied.

Expressions are not new plan nodes. Fields typed `I.Operand` or `I.Expr` hold
the existing qualified `ir.py` variants: `PathRef`, `Literal`, `GivenRef`,
`ClockRef`, `AggRef`, `Arith`, `Negate`, `StaticAggregate`, `Call`; and `And`,
`Or`, `Not`, `Compare`, `Contains`, `In`, `Is`, `Presence`, `Within`,
`Quantified`, `Truth` (`src/garns/ir.py:249-390`). Codec detachment reconstructs
those same classes with a private neutral location, dropping `PathRef.text` and
all `Loc` values from canonical meaning. No AST class is admitted. Diagnostics
use a noncanonical `PlanDiagnostics` sidecar keyed by canonical node/expression
JSON pointer; it may contain file/line/column and source spelling, but cannot
affect digest, equality, lowering or authority.

`FunctionUse(qid, parameter_classes, result_type, semantic_revision)` records
only the qualified semantic registry identity needed to validate an existing
`I.Call`; it is metadata in the root, not another call node and contains no SQL
template. Bridge validation requires exact qid, purity=`pure`, arity, accepted
classes and result type from `calls.REGISTRY` (current registry and purity are
at `src/garns/calls.py:1-57`). A dialect owns its independently exhaustive
function implementation table. Unknown or revision-mismatched functions refuse
before lowering; lowerers never import the compiler registry or interpolate a
registry SQL template.

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

The bridge projects this richer spec losslessly onto W1 `ResultShape`: one
`ResultField` per visible field in order, `key=True` exactly for key fields, and
one `NestedResult` whose owner is its `NestedField` for every nested collection.
Because W1 requires nested owners to be fields
(`semantic.py:86-102`), the owner is a non-value marker field with the fixed
type `SemanticType(base="NestedResult", storage_class="structured",
list_of=True)`. It is never sent to a scalar codec or expected as a SQL column;
its `NestedResult.shape` is the complete child schema. W1 admits that exact
immutable semantic type and A2 assigns the nested shape to its named owner.
Review must reject this convention if W1 intended every owner field to be a
database scalar; that requires a reviewed W1 contract amendment before
implementation, never flattening or a false scalar.

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
{format, root, nodes, subplans, parameter_defaults, function_uses,
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
requires, in order: exact contract classes; known format; byte length/depth/
node-count limits; UTF-8/JSON with duplicate-key rejection; canonical byte
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

## 6. Validation, capability, binding and authority order

The pure pipeline is:

```text
resolved IR + authored WorldIR
  -> bridge semantic validation
  -> detached root encode/decode validation
  -> W1 Plan + diagnostics
  -> backend static capability validation
  -> opened BindingIdentity/origin validation
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

Stable ordering is semantic output, not an SQLite accident. User terms lead;
ordinary rows append subject identity; grouped rows append group keys;
distinct rows append all projected comparable fields when not already total;
global aggregate needs no tie; rank uses the same complete order. If a distinct
projected type cannot be deterministically ordered, explicit order must make
the result total or validation refuses paging/windowing/rank; an unwindowed
unordered distinct query may remain unordered. Nested children order by parent,
declared child order fields, then child identity. `last N` ranks descending per
parent and emits retained children in original ascending order, matching the
current window implementation (`lower_sqlite.py:409-433`).

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

One `Plan` object is cached per read/binding/generation. One-shot execution,
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

There are four registries: relational nodes, result items, existing semantic
operands/expressions, and canonical tags. Validator, codec encoder, codec
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
   digest as appropriate.
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
7. Attack format id/digest/payload, duplicate JSON keys, noncanonical numbers,
   unknown/missing fields, all node ids, cycles/orphans/depth/size, expression
   tags/types, outer `Plan` mismatches, forged origins, IR/storage/generation
   mismatch, registry revision and diagnostics sidecar.
8. Under an accepted ownership amendment, wire legacy consumers and repeat
   shared-plan equivalence: exact same object/digest for query execution,
   question initial and refresh; bounded overflow refusal; scoped/unscoped and
   nested/grouped/windowed/composed cases; old/new group movement; neutral
   suppression; every-revision delta fold equals recomputation; zero routing
   listener scans. Existing live tests describe these baselines
   (`tests/README.md:32-39`).
9. Run all source-manifest checks, the complete unit/product/evidence suite on
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
| Confirm the fixed nested-owner marker is consistent with W1's intent. | W1 permits the exact `SemanticType` value but has no explicit structural enum (`semantic.py:11-35`); A2 requires a named nested owner. | Consistency review must reject it if owner fields were intended to be scalar-only; rejection requires a W1 contract amendment, never a W2 workaround. |
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
