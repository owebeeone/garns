# Garns v9-5 — language reference

## How to read this reference

Garns source is one language with two read nouns, resolved once into a typed,
module-qualified IR. This document describes **what the frozen grammar admits and
what the implementation then enforces** — nothing else. Where a construct parses
but is not consumed downstream, that is stated at the point of use.

1. **The grammar is frozen and LALR.** `grammar/garns.lark` (sha256
   `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`) is the
   canonical input; `src/garns/parse.py::parser` builds one `Lark(grammar_text(),
   parser="lalr", propagate_positions=True, maybe_placeholders=False,
   keep_all_tokens=True)` over it. No construct outside that file exists.
2. **Grammar acceptance is never a corpus pass.** The grammar deliberately admits
   flexible item order and repetition; everything that must hold *exactly once*, or
   must not co-occur, is enforced by `resolve.py`, `resolve_read.py` and
   `storage.py::bind_world`, so a source that parses may still refuse at `validate`
   (`the historical v9-5 lane/brief/01-GrammarDecision.md`).
3. **Every rejection is a refusal** — one code, one stage, one position.
   `DIAGNOSTICS.md` (`## Catalogue`) is the canonical list of all 262 codes with
   raise site and evidence; this reference names the code for each rule.

Notation: `rule_name` refers to `grammar/garns.lark`; implementation anchors are
`src/garns/<file>.py::<symbol>`; "exactly one" is always a resolver rule.

See also `ARCHITECTURE.md` (`## Scope model`, `## Routing and live semantics`,
`## Transactions and ledger`, `## Worlds, deployments and engines`),
`COMPILER_PIPELINE.md` (`## Phases`), `LIMITATIONS.md` (`## Inventory`) for the
complete declared-but-unconsumed list, `INTEGRATION.md` (`## CLI`, `## Python API`),
`EXTENDING_GARNS.md` and `AI_DEVELOPER_GUIDE.md`.

---

## Lexical elements

| Terminal | Definition | Notes |
|---|---|---|
| `NAME` | `/[A-Za-z_][A-Za-z0-9_]*/` | every identifier |
| `INT` | `/[0-9]+/` | unsigned; no negative literal token (unary `-` exists in the static algebra only) |
| `STRING` | `/"([^"\\]\|\\.)*"/` | double-quoted, backslash escapes; decoded by `parse.py::_Builder.string` |
| `CTOR` | `/@[A-Za-z_][A-Za-z0-9_-]*/` | a closed-set member (`@open`); the `@` is stripped when stored |
| `COMMENT` | `/#[^\n]*/`, `%ignore`d | invisible to every stage, including decode classification |
| whitespace | `/[ \t\f\r\n]+/`, `%ignore`d | layout is never significant |

`literal: STRING | INT | CTOR | "true" | "false"`. There is no float literal: a
`Decimal`/`Money` value is written as an `INT` and retyped against the other
operand (`resolve_read.py::ReadResolver.retype_literal`).

**Keywords are contextual, not reserved**: every keyword is an anonymous string
terminal and the LALR contextual lexer resolves it against `NAME` by parser state, so
`intent use : Text "…"`, `resource query "…"` and `link optional -> A { … }` all
resolve. **Six terms are reserved by the resolver** instead
(`types.py::RESERVED_TERMS`): `identity`, `kind`, `rank`, `count`, `engine_clock`,
`ship_clock` — declaring an intent, carrier or member with one refuses `TERM_RESERVED`
(`resolve.py::Resolver.declare`), while they stay free as link, read, given and world
names.

---

## Files, modules and imports

`start: toplevel*` where
`toplevel: module | world_decl | deployment_decl | tighten_stmt | retype_stmt | restore_stmt | move_home_stmt`.
The unit the tools take is a *directory*: `parse.py::garns_files` globs `*.garns`
there, **non-recursively**, sorted. Any number of top-levels may share a file.

`module: "module" NAME STRING "{" import_stmt* decl* "}"`. The meaning `STRING` is
required (`MEANS_REQUIRED` at decode). A module name is declared **once**, in one
block (`MODULE_DUPLICATED`) — a module cannot be reopened in a second file. Every
declaration a module makes is importable; there is no private marker.

### Named imports only

`import_stmt: "import" NAME "(" import_item ("," import_item)* ")"` with
`import_item: NAME ["as" NAME]`. There is no whole-module import, no wildcard and no
implicit global namespace — `import a` alone is a decode `DECL_SHAPE_INVALID`
(mutant `WHOLE_MODULE_IMPORT-1.garns`).

The named module must be declared and must declare the item (`IMPORT_UNKNOWN`), and
must **own** it rather than re-export an import of its own (`IMPORT_NOT_OWNER`). A
module may not import itself (`IMPORT_SELF`); one local name may not be bound twice
(`IMPORT_AMBIGUOUS`) nor collide with a local declaration (`NAME_AMBIGUOUS`); the
import graph must be acyclic (`MODULE_CYCLE`); every import must be used
(`IMPORT_UNUSED`); and a bare name declared elsewhere but not imported refuses
`NAME_NOT_IMPORTED`.

`qname: NAME ["." NAME]` is used where a name must cross a module boundary explicitly:
`renamed_from`, `requires`/`exempt`, `call owner.function(…)`, and `within` in the
**static** algebra. A one-part `qname` where two are required refuses
`QNAME_REQUIRED`; an undeclared module part refuses `MODULE_UNKNOWN`. Internally every
identity is qualified (`module.Name`, `module.Carrier.link`, `module.Carrier.intent`),
which is why two modules may declare identical local names without interfering
(`corpus/metamorphic/collision/`).

---

## Types

`src/garns/types.py::BUILTIN_SCALARS` is the complete scalar set; source cannot add
one.

| Name | Class | SQL storage (`types.py::sql_storage_type`) | Ordered (`< <= > >=`) |
|---|---|---|---|
| `Text`, `DisplayName`, `Email`, `Id` | `text` | `TEXT` | yes |
| `Instant` | `instant` | `INTEGER` | yes |
| `Integer` | `integer` | `INTEGER` | yes |
| `Decimal`, `Money` | `decimal` | `REAL` | yes |
| `Boolean` | `boolean` | `INTEGER` | no |
| `Opaque`, `Vector` | `opaque`, `vector` | `BLOB` | no — presence only |

Comparability is by **class**, not name (`types.py::comparable`): the four `text`
scalars interoperate, and `integer` with `decimal` (`NUMERIC_CLASSES`). `Instant` is
stored as `INTEGER` — there is no date/time type. `Opaque`/`Vector`
(`PRESENCE_ONLY_CLASSES`) refuse comparison (`OPAQUE_COMPARED`) and the `key`/`order`
flags (`OPAQUE_POLICY`).

```
type_ref:  "optional" opt_inner | "list_of" NAME | NAME
opt_inner: "list_of" NAME | NAME
```

`T`, `optional T`, `list_of T` and `optional list_of T` are admitted;
`list_of optional T` is **not** (decode `DECL_SHAPE_INVALID`), and there is no
deeper nesting. `optional`/`list_of` belong to a *use* or a *given*, never to an
intent (`INTENT_TYPE_SHAPE`).

**Newtypes.** `newtype_decl: "newtype" NAME "of" type_ref STRING` declares a nominal
type over a **builtin scalar only**: a newtype of a newtype refuses `TYPE_UNKNOWN`,
and `optional`/`list_of` in the `of` clause refuses `NEWTYPE_SHAPE`. It keeps the
base class and storage but is nominally distinct.

**Closed sets** are declared by an intent, by naming a fresh type and listing
members: `intent status : OrderStatus "…" { values @open, @closed }`.
`resolve.py::Resolver.resolve_type` registers `module.OrderStatus`, so another
intent may reuse it by name — but a different member list refuses
`CLOSED_SET_CONFLICT`. A closed set refines a **text** type only
(`CLOSED_SET_TYPE`); a repeated member refuses `CLOSED_SET_MEMBER_DUPLICATED`; an
unadmitted `@member` refuses `CLOSED_SET_MEMBER_UNKNOWN`. In DDL the column gets
`CHECK (col IN ('open', 'closed'))` — the `@` is not stored.

**Carrier-typed givens.** A `given` may be typed as a carrier or family member; its
value is that carrier's row identity. This is the only position resolved with
`allow_carrier=True` (`resolve_read.py::ReadResolver.resolve_given`) — a use or
intent typed as a carrier refuses `TYPE_UNKNOWN`. `by` and `is` consume such givens.

---

## Intents

`intent_decl: "intent" NAME ":" type_ref STRING intent_body?` — the only way a
carrier gets a scalar field. An intent no carrier uses refuses `INTENT_HOMELESS`
unless it is `retired`.

| Item | Grammar | Meaning | Enforced? |
|---|---|---|---|
| `alias NAME` | `"alias" NAME` | a second name in read paths | yes (`resolve_read.py::ReadResolver.resolve_path`) |
| `renamed_from qname` | | continuity with a previous generation | yes (`evolution.py::classify`) |
| `values @a, @b` | `ctor_list` | declares the closed set | yes |
| `pattern STRING` | | a text refinement | **carried only** — nothing consumes it |
| `length INT [".." INT]` | | a text length refinement | **carried only**; only `maximum < minimum` refuses (`LENGTH_RANGE_INVALID`) |
| `dimension INT` | | fixed vector width | positivity and `Vector`-ness only (`DIMENSION_NOT_POSITIVE`, `DIMENSION_NOT_VECTOR`, `DIMENSION_REQUIRED`); the width is not enforced |
| `retype NAME forward adapter backward adapter` | `retype_clause` | previous base type + adapters | yes (`evolution.py::_retype`) |
| `retired data quarantine\|drop` | `retire_clause` | retired, with a data disposition | yes |
| `restore` | `restore_clause` | bring a tombstoned intent back | yes (`evolution.py::_restore`) |

Each item kind appears **at most once** (`INTENT_ITEM_REPEATED`); `retired` with
`restore` refuses `INTENT_ITEM_CONFLICT`; `pattern`/`length` on a non-text type
refuses `INTENT_REFINEMENT_TYPE`; a `Vector` intent **must** state a `dimension`.
`adapter: "widen" | "validate"`; `disposition: "quarantine" | "drop"`.

---

## Carriers

| Kind | Storable? | Notes |
|---|---|---|
| `trait` | no | composed by `carry`; no `lifecycle` (`TRAIT_LIFECYCLE`); not a link target (`LINK_TO_TRAIT`), read subject (`READ_OF_TRAIT`) or verb receiver (`VERB_ON_TRAIT`) |
| `resource` | yes | the ordinary entity |
| `event` | yes | the only kind admitting `ordered_within`, and the only target of `append` |
| `association` | yes | needs at least two links (`ASSOCIATION_ARITY`) |
| `family` | yes | one identity space and one table shared with its members |
| `member` (only inside `family_decl`) | no — rows live in the family's table | inherits every use, link, trait, lifecycle and `scope_via` of its family |

`is_storable` is `kind not in ("trait", "member")` (`ir.py::Carrier`).

```
carrier_item: use_stmt | link_stmt | "lifecycle" lifecycle | "carry" name_list
            | "ordered_within" NAME | "history" "kept" | "breaking" STRING
            | "tighten" NAME "repair" repair_val | "invariant" expr | "scope_via" NAME
member_item: use_stmt | link_stmt | "invariant" expr | "breaking" STRING
           | "tighten" NAME "repair" repair_val
```

A member body is a strict subset: it may not restate `lifecycle`, `carry`,
`ordered_within`, `history kept` or `scope_via`.

### Uses

`use_stmt: "use" NAME use_body?`, `use_body: "{" use_flag* "}"`.

| Flag | Effect and rules |
|---|---|
| `key` | part of the carrier's key; `key` + `optional` refuses `USE_FLAG_CONFLICT`; on `Opaque`/`Vector` refuses `OPAQUE_POLICY` |
| `optional` | nullable column |
| `filter` | **carried only** — no index or check consumes it |
| `order` | consumed for **nested shows only** (a child orders by its `order` uses, then identity); on `Opaque`/`Vector` refuses `OPAQUE_POLICY` |
| `stamp on_mint\|on_change` | the engine writes it; requires an `Instant` intent (`STAMP_NOT_INSTANT`) and makes the use `engine_owned`, so supplying it refuses `VERB_INPUT_ENGINE_OWNED` |
| `default default_val` | typed against the intent (`DEFAULT_TYPE`); a literal becomes a SQL `DEFAULT` |
| `repair repair_val` | value for existing rows when the use becomes required (`REPAIR_TYPE`) |

`default_val: "ship_clock" | literal`; `repair_val: "ship_clock" | "quarantine" | literal`.
Repeating a flag kind refuses `USE_FLAG_REPEATED`; using one intent twice on one
carrier refuses `USE_DUPLICATED`.

### Links and enforcement

`link_stmt: "link" NAME "->" NAME link_body?`;
`link_flag: "end" end_kind | "unenforced" | "scopes" | "inverse" NAME | "optional" | "key" | "filter" | "order" | "default" default_val`;
`end_kind: "restrict" | "cascade" | "detach"`.

| Flag | Effect |
|---|---|
| `end restrict` | `FOREIGN KEY … ON DELETE RESTRICT` — **the default when no enforcement flag is given** |
| `end cascade` | `… ON DELETE CASCADE` |
| `end detach` | `… ON DELETE SET NULL`; requires `optional` (`DETACH_NOT_OPTIONAL`) |
| `unenforced` | **a standalone flag, never an `end` kind.** The link stays typed and participates in path resolution, inverses, storage mapping, lowering and footprints; only the `FOREIGN KEY` clause is omitted |
| `scopes` | the world's scope-root edge; only the world's declared scope link may carry it (`SCOPE_LINK_NOT_ROOT`) |
| `inverse NAME` | names the reverse traversal on the target |
| `optional` | nullable link column |
| `key` | part of the carrier's key; with `optional` refuses `LINK_FLAG_CONFLICT` |
| `filter`, `order` | **carried only** |
| `default default_val` | a literal identity default |

`unenforced` is a load-bearing v9-5 decision (`the historical v9-5 lane/brief/00-Constitution.md`):
`{ end unenforced }` is **not grammar** and refuses at **decode** with
`DECL_SHAPE_INVALID`; `{ unenforced end cascade }` parses and refuses
`LINK_ENFORCEMENT_CONFLICT`; repeating `unenforced`, or stating two `end` actions,
refuses `LINK_ENFORCEMENT_REPEATED`; repeating any other flag refuses
`LINK_FLAG_REPEATED`. Two links on one carrier may not share a name
(`LINK_DUPLICATED`), and a cycle of **required** links makes minting impossible
(`LINK_CYCLE_UNMINTABLE`).

**Inverses.** `inverse NAME` registers an `InverseEdge` on the target
(`resolve.py::Resolver.compute_inverses`), to-many unless the source link is `key`
*and* is the source carrier's sole key. Two links may not give one target the same
inverse name (`INVERSE_DUPLICATED`), and an inverse may not collide with a term of
the target (`NAME_AMBIGUOUS`). Members see their family's inverses. An inverse on a
**trait** link composes into every carrier of the trait and therefore usually
collides — the one seed edit recorded for `appflowy/embeddings.garns` in
`corpus/worlds/MIGRATION.md`.

### Lifecycle, traits, and the remaining items

`lifecycle: "mutable" | "retirable" | "archived_by" NAME`, stated at most once
(`LIFECYCLE_REPEATED`). `archived_by NAME` must name an **optional `Instant` use** of
the carrier (`ARCHIVED_BY_INVALID`); every read then appends
`<archived column> IS NULL` unless it says `including_archived`.
`carry name_list` composes each named trait's uses and links. The target must be a
trait (`CARRY_NOT_TRAIT`), carried once (`CARRY_REPEATED`), in an acyclic graph
(`TRAIT_CYCLE`). Composition (`resolve.py::Resolver._merge_use`): **restating a
trait's use narrows only** — dropping `key`, or adding `optional` where the trait
had none, refuses `TRAIT_WIDENED`, while adding `filter`/`order`/`key` is allowed; a
restated `stamp` or `default` that differs, two traits supplying one intent that
disagree on `(key, optional, stamp, default)`, and two traits supplying one link
name all refuse `TRAIT_POLICY_CONFLICT`.

| Item | Meaning | Enforced? |
|---|---|---|
| `ordered_within NAME` | this event's rows are ordered inside the named link | **carried only** — resolved into `Carrier.ordered_within`, consumed by nothing. Stated once (`ORDERED_WITHIN_REPEATED`), on an `event` only (`ORDERED_WITHIN_NOT_EVENT`), naming a link (`ORDERED_WITHIN_UNKNOWN`) |
| `history kept` | this carrier keeps history | **carried only**; twice refuses `PRESET_CONFLICT` |
| `breaking STRING` | acknowledges a breaking accessor change | consumed by `evolution.py::classify` (`ACCESSOR_BREAKING_UNACKNOWLEDGED`) |
| `tighten NAME repair repair_val` | repair for the named use when it tightens | consumed by `evolution.py::_repair_of`; unknown name refuses `TIGHTEN_UNKNOWN` |
| `invariant expr` | a **dynamic-algebra** predicate over the carrier | evaluated as SQL against the written row inside the transaction (`engine.py::Transaction._check_invariants`); violation refuses `INVARIANT_VIOLATED` and rolls back. May not compose reads (`INVARIANT_COMPOSES`) nor mention `engine_clock` (`INVARIANT_CLOCK`) |
| `scope_via NAME` | which link carries this carrier to the scope root | consumed by `compute_scope_paths`; once (`SCOPE_VIA_REPEATED`), naming a link (`SCOPE_VIA_UNKNOWN`) |

### Keys and families

`Carrier.key_columns` is every `key` use plus every `key` link, and `lower_ddl` emits
**one** `UNIQUE (…)` over all of them — several `key` flags form a *composite* key,
not several keys — counting only keys declared on the carrier itself.

A family and its members share one table: `storage.py::expected_relation_keys`
collects the family's own uses and links plus every member-only use and link under a
member-qualified storage key. A member-only column is **nullable regardless of its
`optional` flag**, and the family's `kind` discriminator carries
`CHECK (kind IN ('Letter', 'Form', …))`. `kind` is a read term on a family or member
only (`TERM_UNKNOWN` elsewhere), and a family may not be minted directly
(`FAMILY_MEMBER_MINT_ONLY`).

---

## Reads: queries and questions

Both nouns share the entity-first shape and lower through **one** entry point,
`lower_sqlite.py::lower_read`, producing one `Plan`.

```
query_decl:    "query"    NAME "of" NAME STRING "{" query_item* "}"
question_decl: "question" NAME "of" NAME STRING "{" q_item*     "}"
```

The subject must be a storable carrier or member; a trait refuses `READ_OF_TRAIT`.

| | `query` | `question` |
|---|---|---|
| nature | static, deterministic, fetch-only, **one-shot** | dynamic, closed algebra, **live** |
| live bound | none — the grammar admits no `live` item | **exactly one** `live bounded INT`, positive |
| footprint / binding / routing | never (`QUERY_NOT_LIVE`) | always |
| generated files | `queries/<qid>.sql` + surfaces | `questions/<qid>.sql` **plus** `.footprint.json`, `.binding.json`, `.routing.json` |
| algebra | the richer static algebra | the closed dynamic algebra |

### Items shared by both nouns

| Item | Meaning and rules |
|---|---|
| `given NAME : type_ref ["=" literal]` | a declared parameter. Every given must be used (`GIVEN_UNUSED`); duplicates refuse `GIVEN_DUPLICATED`; a name starting with `_` refuses `GIVEN_NAME_RESERVED` (the engine owns `:_scope`, `:_clock`, `:_parents`); a default is typed against it (`GIVEN_DEFAULT_TYPE`) |
| `where <expr>` | the predicate (`expr` for questions, `query_expr` for queries) |
| `show <list>` | result columns |
| `order <list>` | ordering terms, each optionally `ascending`/`descending` (`direction`) |
| `page NAME` / `limit NAME` | both or neither (`PAGE_LIMIT_PAIR`); each names an `integer` given (`PAGE_TYPE`) |
| `with_total` | a second `COUNT(*)`; requires `page` (`WITH_TOTAL_WITHOUT_PAGE`) |
| `including_archived` | drops the `archived_by` filter; requires that lifecycle (`INCLUDING_ARCHIVED_NOT_ARCHIVABLE`) |
| `unscoped NAME` | drops the scope predicate behind a capability |
| `by <path_expr>` | one row by identity; the path must be a single given typed as the subject (`BY_NOT_GIVEN`, `BY_TYPE`) |
| `one` | at most one row |
| `group by <path_list>` | grouping keys |
| `first INT` | a positive root bound (`FIRST_NOT_POSITIVE`) |

Repeating an item kind refuses `READ_ITEM_REPEATED` — except a repeated `live`
item, which refuses `QUESTION_LIVE_BOUND_DUPLICATED` (one ternary,
`resolve_read.py:529`).

### Static-only items (`query`)

`distinct` — `SELECT DISTINCT`; the *shown* columns become the result key. Exclusive
with `group by` (`SHAPE_CONFLICT`); a nested show inside it refuses
`NESTED_SHOW_WITH_DISTINCT`. `having <query_expr>` needs `group by` or an aggregate
show (`HAVING_WITHOUT_GROUP`). Plus the whole `query_expr` algebra: arithmetic,
`engine_clock`, aggregates and calls.
`query_aggregate: ("count"|"sum"|"average"|"minimum"|"maximum") "(" ["distinct"] [path_expr] ")"`
— `count()` with no path lowers to `COUNT(*)`, `count(distinct …)` needs a path, and
aggregates are admitted in `show`, `having` and `order` only (elsewhere
`AGGREGATE_MISUSED`) and do not nest. `query_call: "call" qname "(" [query_arg_list] ")"`
resolves **only** against `src/garns/calls.py::REGISTRY`:

| Function | Parameters | Result | SQL | Purity |
|---|---|---|---|---|
| `text.normalize` | `text` | `Text` | `LOWER(TRIM({0}))` | pure |
| `text.lower` / `text.upper` | `text` | `Text` | `LOWER({0})` / `UPPER({0})` | pure |
| `text.length` | `text` | `Integer` | `LENGTH({0})` | pure |
| `text.concat` | `text`, `text` | `Text` | `({0} \|\| {1})` | pure |
| `math.abs` | `numeric` | same as arg | `ABS({0})` | pure |
| `math.round` | `numeric`, `integer` | `Decimal` | `ROUND({0}, {1})` | pure |
| `money.round` | `numeric`, `integer` | `Money` | `ROUND({0}, {1})` | pure |
| `money.cents` | `numeric` | `Integer` | `CAST(ROUND({0} * 100) AS INTEGER)` | pure |
| `clock.now` | — | `Instant` | — | **volatile** → `CALL_VOLATILE` |
| `random.uniform` | — | `Decimal` | — | **volatile** → `CALL_VOLATILE` |
| `store.purge` | `text` | `Boolean` | — | **effectful** → `CALL_EFFECTFUL` |

The three non-pure entries exist so those calls refuse with a *specific* code
instead of `CALL_UNKNOWN`. Wrong arity refuses `CALL_ARITY`; a wrong argument
class, or a `@member` argument, refuses `CALL_ARGUMENT_TYPE`.

### Dynamic-only items (`question`)

- `live bounded INT` — **exactly one**, positive. Absent → `QUESTION_LIVE_BOUND_REQUIRED`;
  twice → `QUESTION_LIVE_BOUND_DUPLICATED`; `0` → `QUESTION_LIVE_BOUND_INVALID`. A
  `live` item in a *query* is not grammar at all, so it is a **decode**
  `DECL_SHAPE_INVALID`.
- `some` / `every <comparison>`; the dynamic aggregates `path count ( [expr] )`,
  `path max ( path )`, `path min ( path )` — to-many only (`AGG_NOT_TO_MANY`);
  `given_guard: "when" "given"`; and `within path_expr`.
- `count ( )` and `rank` as **show** terms. The static show list has neither: `rank`
  in a query resolves as a path (`TERM_UNKNOWN`), and `count()` is a static
  aggregate needing `as name`.

A question reaching any static-only construct refuses `QUESTION_NOT_FOOTPRINTABLE`
rather than being downgraded: `engine_clock` is caught in the resolver
(`resolve_read.py:657`), and `Arith`, `Negate`, `StaticAggregate`, `Call`, `Truth`,
`ShowScalar`, `having` and `distinct` while deriving the footprint
(`footprint.py::FootprintDeriver`). Most cannot be written in a question at all —
`q_item` and `show_value` do not admit them.

### Show lists

```
show_item:         show_value ["as" NAME]
?show_value:       path_expr ["[" show_list "]" ["last" INT]] | "identity" | "count" "(" ")" | "rank"
?query_show_value: path_expr "[" query_show_list "]" ["last" INT] | "identity" | query_scalar
```

| Term | Result |
|---|---|
| `path` | the value at the path; default column name is the path text (`customer.name`) |
| `path [ … ] [last N]` | a **nested show**: one child SELECT per parent, attached as a list |
| `identity` | the subject's identity column |
| `count()` | question only — `COUNT(*)`; its presence alone makes the shape `grouped` |
| `rank` | question only — `ROW_NUMBER() OVER (ORDER BY <order terms + tiebreak>)`; needs an `order` (`RANK_WITHOUT_ORDER`) |
| a static scalar | query only — arithmetic, aggregate or `call`; **must** be aliased (`SHOW_ALIAS_REQUIRED`), never a bare literal (`SHOW_LITERAL`) |

Two columns may not share a name (`SHOW_COLUMN_DUPLICATED`). **With no `show` item at
all**, the plan projects every use of the subject in declaration order, each column
named by the intent's local name. Nested shows: the path must be to-many
(`NESTED_SHOW_NOT_TO_MANY`) and — a limitation — must be **exactly one inverse step**,
longer chains refusing `NESTED_SHOW_PATH` (raised in `lower_sqlite.py::lower_nested`,
reported at stage `validate`); `last N` must be positive (`LAST_NOT_POSITIVE`) and
lowers to `ROW_NUMBER() OVER (PARTITION BY <parent> ORDER BY … DESC)` filtered by
`<= N`; children order by the child's `order`-flagged uses, then identity; and nested
shows are refused in grouped results (`AGGREGATE_MISUSED`).

### Shapes, keys and ordering

`Read.shape` is decided in this order (`resolve_read.py::ReadResolver.resolve_read`):

| Shape | When | Lowering |
|---|---|---|
| `optional_single` | `one` or `by` | `LIMIT 1` |
| `grouped` | `group by`, a static aggregate show, or a `count()` show | `GROUP BY`; key columns are the group keys |
| `windowed` | `first N`, or `page`+`limit` | `LIMIT N` / `LIMIT :limit OFFSET (:page - 1) * :limit` |
| `collection` | otherwise | no limit |

`one`, `by`, `first`, `page`/`limit` and `group by` are mutually exclusive
(`SHAPE_CONFLICT`), as are `distinct` and `group by`. In a grouped read every shown
path must be a group key or an aggregate and every path order key must be a group
key (`AGGREGATE_MISUSED`); `identity`, `rank` and nested shows are refused.

**Result keys are hidden**, in `$k`-prefixed columns absent from `Plan.columns`:
`$k0` is the subject identity for collections and windows; one `$k0…$kN` per group
key when grouped; for `distinct` the shown columns *are* the key. Nested children
add `$parent` and their own `$k0`.

**Deterministic tiebreak** (`lower_sqlite.py::order_clause`): after the declared
`order` terms the plan appends the **group keys ascending** for a grouped read,
**nothing** for a `distinct` read, and the **subject identity ascending** otherwise.
`rank` uses the same terms plus tiebreak inside its window. Ordering by a literal
refuses `ORDER_BY_LITERAL`; an order key must be ordered or a carrier identity
(`EXPR_TYPE`).

**Base predicates** (`lower_sqlite.py::base_predicates`), in order: the family-member
discriminator, `<archived column> IS NULL` unless `including_archived`, then the scope
predicate, which walks the carrier's resolved scope path (a tuple of link qids) to the
root against `:_scope`, nesting `IN (SELECT identity FROM parent WHERE …)` for
multi-hop paths. `unscoped NAME` drops it: the world must declare the capability
(`CAPABILITY_UNKNOWN`) and the caller must present it (`CAPABILITY_REQUIRED`); a scoped
plan executed without a scope refuses `SCOPE_REQUIRED`. See `ARCHITECTURE.md`
(`## Scope model`).

---

## Expressions

Two algebras, one expression IR (`src/garns/ir.py`), so lowering is shared and
footprint derivation can refuse the static-only nodes loudly.

### The dynamic (closed) algebra — `expr`

```
?expr: or_expr ; ?or_expr: and_expr ("or" and_expr)* ; ?and_expr: not_expr ("and" not_expr)*
?not_expr:  "not" not_expr | atom_expr
?atom_expr: "some" comparison | "every" comparison | comparison | "(" expr ")"
comparison: agg_expr cmp_op value_expr given_guard?
          | path_expr "contains"|"in"|"is" value_expr given_guard?
          | path_expr "present"|"absent" given_guard?
          | path_expr "within" path_expr
          | path_expr cmp_op value_expr given_guard?
?value_expr: path_expr | literal | clock ;  cmp_op: "=" | "!=" | "<" | "<=" | ">" | ">="
```

That is all of it: boolean combination, quantification, one comparison form per
operator, presence, composition, and the three dynamic aggregates. No arithmetic,
no `call`, no `distinct`, no `having`.

| Operator | Typing rule | Refusal |
|---|---|---|
| `=`, `!=` | both sides comparable (`types.py::comparable`) | `EXPR_TYPE` |
| `<`, `<=`, `>`, `>=` | additionally the left type must be ordered | `EXPR_TYPE` |
| `contains` | left `text`; right `text` and not a list | `CONTAINS_NOT_TEXT`, `EXPR_TYPE` |
| `in` | right **must** be a `list_of` given; elements comparable | `IN_NOT_LIST`, `EXPR_TYPE` |
| `is` | left ends at a link or `identity`; right identifies the same carrier or a member of the same family | `IS_NOT_LINK`, `IS_TYPE` |
| `present` / `absent` | any path | — |
| `within` | left ends at a link or `identity`; right names one read | `WITHIN_NOT_LINK`, `READ_UNKNOWN` |
| `some` / `every` | the body must mention a to-many path | `QUANTIFIER_WITHOUT_TO_MANY` |
| `count` / `max` / `min` | the path must be a to-many link; `max`/`min` need an ordered argument | `AGG_NOT_TO_MANY`, `EXPR_TYPE` |

### The static algebra — `query_expr`

Everything above (bar `some`/`every`, the dynamic aggregates and `when given`) plus
`+ - * / %` (`query_sum`, `query_product`), unary `+ -`, `query_aggregate`,
`query_call`, `engine_clock`, and a bare boolean scalar used as a predicate (`Truth`).
`%` needs two integers; `/` always yields a decimal (lowered as `CAST(x AS REAL) / y`);
any other numeric pair yields a decimal if either side is decimal, else an integer. In
the static algebra `within` takes a `qname`, so a query may compose across modules.

### Paths

`path_expr: NAME ("." NAME)*`, resolved segment by segment against *resolved edges
only* (`resolve_read.py::ReadResolver.resolve_path`): a **link** name → a forward
`LinkStep`; an **inverse** name → a reverse `LinkStep` (to-many unless the source
link is the carrier's sole key); a **use** name or intent **alias** → a
`UseTerminal`; `identity` → an `IdentityTerminal`; `kind` → a `KindTerminal`
(families only).

Continuing past a scalar refuses `PATH_THROUGH_SCALAR`; an unknown segment refuses
`TERM_UNKNOWN`, or `QUESTION_INTENT_RETIRED` when the module tombstoned that name;
`ship_clock` in a path refuses `QUESTION_CLOCK_NOT_A_TERM`. A path crossing a
to-many step outside `some`/`every`/an aggregate refuses
`TERM_TO_MANY_UNQUANTIFIED`; a quantified body mentioning **more than one distinct
to-many prefix** refuses `QUANTIFIER_MULTIPLE_MANY` (a lowering limitation reported
at stage `validate`).

### Literal retyping, closed sets, guards

A literal is parsed provisionally (`Integer`, `Text`, `Boolean`, or a `@ctor`
carrying a singleton set) and retyped against the other operand
(`resolve_read.py::ReadResolver.retype_literal`): an integer literal fits `integer`,
`decimal` **and** `instant`; a text literal fits `text`; an integer or text literal
fits a carrier identity. A `@member` requires the other side to be a closed set that
admits it (`CLOSED_SET_MEMBER_UNKNOWN`); a closed set compares only with a `@member`
or an un-nominal value of its base type; two literals may not be compared through a
closed set. `Opaque`/`Vector` admit `present`/`absent` only (`OPAQUE_COMPARED`).

`given_guard: "when" "given"` makes a predicate vacuous when its optional given is
absent, lowering to `(:g IS NULL OR <body>)`. It requires the right operand to be an
**optional** given (`GUARD_NOT_OPTIONAL_GIVEN`). An optional given used *without*
`when given` is guarded implicitly, but only in a top-level conjunct: inside `or` or
`not` the implicit guard would change meaning, so it refuses
`OPTIONAL_PARAM_UNGUARDED`. On the right of a predicate a given **shadows** a
same-named term; on the left the term wins (`operand(..., prefer_given=…)`).

---

## Verbs

**Verbs are resolved and validated only. Nothing executes them.** `alias`, `bulk`,
`restricted` and `compound` resolve into `ir.Alias` / `ir.Bulk` / `ir.Restricted` /
`ir.Compound` and are fully checked, but no consumer runs them and
`generate.py::generate` iterates `world.reads` only, so no verb surface is generated.
Writes go through `Engine.transaction(...)` and its `mint` / `change` / `delete`
(`ARCHITECTURE.md`, `## Transactions and ledger`). Treat a verb declaration as a
*checked specification*, not as callable code.

`dotted_verb: NAME "." NAME` names `Carrier.verb`, which must be in
`resolve.py::DERIVED_VERBS` = `mint, ensure, upsert, change, delete, archive,
restore, retire, append, apply, remove, by, list, count, page, history, kind`
(`ALIAS_NOT_DERIVED`). Traits have no verbs (`VERB_ON_TRAIT`); `append` is an event
verb (`VERB_NOT_ADMITTED`); a family is minted through a member
(`FAMILY_MEMBER_MINT_ONLY`).

| Form | What is checked |
|---|---|
| `alias NAME = Carrier.verb ["unscoped" NAME]` | the verb, and the capability if given |
| `bulk NAME STRING { given_item* Carrier.verb "over" NAME set_clause* }` | the verb must be in `BULKABLE` = `change, archive, delete, retire, restore, apply, remove` (`BULK_NOT_DERIVED_VERB`); the `over` read must exist (`READ_UNKNOWN`), share the subject (`BULK_OVER_MISMATCH`) and not be windowed (`BULK_OVER_PAGED`); each `set NAME = NAME` targets a non-engine-owned use (`BULK_SET_UNKNOWN`, `VERB_INPUT_ENGINE_OWNED`) from a declared given (`BULK_PARAM_UNDECLARED`) of a fitting type (`BULK_SET_TYPE`); `set NAME absent` needs an optional use (`SET_ABSENT_REQUIRED`) |
| `restricted NAME STRING { Carrier.verb "accepts" name_list ["unscoped" NAME] }` | each accepted name is a use or link of the carrier (`RESTRICTED_ACCEPTS_UNKNOWN`), not engine-owned |
| `compound NAME STRING { step_stmt* }` | step names unique (`STEP_NAME_DUPLICATED`); `bind <link> = <step>` names one link of the step's carrier (`STEP_BIND_PATH`, `STEP_BIND_UNKNOWN`) and an **earlier** step (`STEP_CYCLE`, `STEP_REFERENCE_UNRESOLVED`) whose carrier fits the link target (`STEP_BIND_TYPE`) |

---

## Worlds

`world_decl: "world" NAME STRING "{" world_item* "}"` — the modules that share one
store. Each item kind appears at most once (`WORLD_ITEM_REPEATED`).

| Item | Required? | Rules |
|---|---|---|
| `modules name_list` | **yes** (`WORLD_MODULES_REQUIRED`) | each module declared (`MODULE_UNKNOWN`), listed once (`WORLD_MODULE_REPEATED`), in no other world (`WORLD_MODULE_COLLISION`); every module a listed module imports must also be listed (`MODULE_NOT_LISTED`) |
| `durability NAME` | **yes** (`WORLD_DURABILITY_REQUIRED`) | `durable` \| `ephemeral` (`DURABILITY_UNKNOWN`) |
| `writers NAME` | **yes** (`WORLD_WRITERS_REQUIRED`) | `governed` \| `external_captured` (`WRITER_CLASS_UNKNOWN`) |
| `generated name_list` | **yes** (`WORLD_GENERATED_REQUIRED`) | `TARGETS` = `python`, `rust` (`TARGET_UNKNOWN`), no repeats (`WORLD_TARGET_REPEATED`). `typescript` is **not** a target in this build |
| `scope scope_target` | **yes** (`WORLD_SCOPE_REQUIRED`) | see below |
| `quarantine_retention INT` | **yes** (`QUARANTINE_RETENTION_REQUIRED`) | a positive generation count (`QUARANTINE_RETENTION_INVALID`) |
| `requires qname ["exempt" qname_list]` | when scoped | must be a trait inside the world's modules (`REQUIRES_NOT_TRAIT`, `TRAIT_UNKNOWN`); each exempt entry a storable carrier (`EXEMPT_NOT_CARRIER`, `EXEMPT_UNKNOWN`) that does not already carry the trait (`EXEMPT_REDUNDANT`), listed once (`EXEMPT_REPEATED`) |
| `capabilities name_list` | no | names for `unscoped` reads and verbs; no repeats (`CAPABILITY_REPEATED`) |
| `writer_source NAME` | for `external_captured` | required there (`WRITER_SOURCE_REQUIRED`), refused elsewhere (`WRITER_SOURCE_NOT_ADMITTED`); it is the writer identity the ledger records |

`scope_target: "deployment" | path_expr`.

- **`scope deployment`** — the whole store is one scope: `World.scope` is `None`, no
  scope predicate is emitted and no scope key is computed (`SALES`, `REPORTING`).
- **`scope module.Trait.link`** — exactly three segments (`SCOPE_PATH_INVALID`); the
  trait must be the world's `requires` trait (`SCOPE_ROOT_MISMATCH`,
  `WORLD_REQUIRES_REQUIRED`); the link must be one of its links (`SCOPE_LINK_UNKNOWN`)
  carrying the `scopes` flag (`SCOPE_ROOT_NOT_SCOPED`), and no other link in the world
  may carry `scopes` (`SCOPE_LINK_NOT_ROOT`).

`resolve.py::Resolver.compute_scope_paths` derives, per storable carrier, the tuple
of link qids reaching the root: directly for carriers that carry the trait, then to a
fixpoint through `scope_via` or a *unique* link whose target already has a path.
More than one such link demands `scope_via` (`SCOPE_PATH_AMBIGUOUS`); a `scope_via`
target with no path refuses `SCOPE_PATH_TO_EXEMPT`; a carrier that neither carries the
trait, nor is exempt, nor is reachable refuses `TRAIT_REQUIRED`.

---

## Deployments

`deployment_decl: "deployment" NAME STRING ["extends" NAME] "{" dep_item* "}"` binds
one world to one engine and location. Names are unique (`DEPLOYMENT_DUPLICATED`);
each item kind appears once (`DEPLOYMENT_ITEM_REPEATED`). `extends NAME` inherits
every value item by item and the child's own items override; the base must exist
(`DEPLOYMENT_EXTENDS_UNKNOWN`) and the chain must be acyclic
(`DEPLOYMENT_EXTENDS_CYCLE`).

| Item | Required (after inheritance) | Values |
|---|---|---|
| `world NAME` | `DEPLOYMENT_WORLD_REQUIRED` | a declared world (`WORLD_UNKNOWN`) |
| `engine NAME` | `ENGINE_REQUIRED` | `sqlite`, `postgres` (`ENGINE_UNKNOWN` otherwise) — see below |
| `at location` | `DEPLOYMENT_LOCATION_REQUIRED` | `env NAME ["default" STRING]`, `path STRING`, `memory` |
| `ship NAME` | `SHIP_MODE_REQUIRED` | `on_open`, `explicit` (`SHIP_MODE_UNKNOWN`) |
| `mode NAME` | `DEPLOYMENT_MODE_REQUIRED` | `readwrite`, `readonly` (`DEPLOYMENT_MODE_UNKNOWN`) |
| `snapshot NAME` | `DEPLOYMENT_SNAPSHOT_REQUIRED` | `none`, `before_ship` (`SNAPSHOT_UNKNOWN`) |
| `pool INT` | optional | carried in the IR; no consumer reads it |

**PostgreSQL is recognised, not lowered.** `resolve.py::ENGINES = {"sqlite",
"postgres"}` but `resolve.py::LOWERED_ENGINES = {"sqlite"}`. Any deployment
resolving to an engine outside `LOWERED_ENGINES` refuses **`ENGINE_LOWERING_ABSENT`
at stage `validate`**, positioned at that deployment's `engine` item, **before any
effect** — no schema, store, ledger, generation, migration or generated artifact
(`resolve.py::Resolver.resolve_deployment`, `:1292-1299`). An unrecognised engine
still refuses `ENGINE_UNKNOWN` at the same item, keeping the two cases
distinguishable. See `../evidence/v9-5-b2/REPAIR.md` and `LIMITATIONS.md` (`## Inventory`).

Observed positions: a base declaring `engine postgres` refuses at its **own** `engine`
item even when only a child is reachable first, and a child overriding a SQLite base
refuses at the child's item — so the implementation's fallback of positioning at the
deployment name when no `engine` item exists is unreachable from source.

---

## Storage binding

**Not part of the grammar.** Every world needs one JSON document mapping every
qualified relation, use, link, family discriminator, engine table and changelog
field to a physical name. `storage.py::bind_world` is the only producer of a
`WorldIR` and therefore the gate in front of every effect. Nothing is guessed: no
pluralisation, no `id` identity, no `<link>_id` convention and no `scope_id` column
exists in the implementation.

Schema `garns-v9-5/storage-binding/1`:

```json
{"schema": "garns-v9-5/storage-binding/1", "world": "LEDGERHOUSE",
 "engine": {"ledger": "lh_journal", "generations": "lh_epochs", "revisions": "lh_ticks"},
 "relations": {"pantry.Jar": {"table": "jar", "identity": "jar_no",
    "columns": {"pantry.Jar.jar_label": "lbl", "pantry.Jar.grams": "mass_g"},
    "links": {"pantry.Jar.shelf": "on_shelf"},
    "kind": "<family discriminator column; families only>"}},
 "capture": {"pantry.Jar": {"table": "jar_trail", "fields": {
    "seq": "trail_seq", "op": "verb", "revision": "tick", "identity": "jar_ref",
    "columns": {"pantry.Jar.grams": "mass_v"}, "links": {"pantry.Jar.shelf": "on_shelf_v"}}}}}
```

`bind_world` checks the document exhaustively before anything is lowered: the world
exists; the file reads as JSON with the right `schema` and `world`; `engine` gives
three distinct tables; every storable carrier is mapped and nothing else is; every use
and link key — including the member-qualified keys a family member adds — has a column
and no unknown key is mapped; every physical name is a plain identifier
`[A-Za-z_][A-Za-z0-9_]*` and collides with nothing, the identity, `kind` column and
engine tables included; `kind` is admitted only for families; and `capture` is required
exactly when the world declares `writers external_captured`. The seventeen `STORAGE_*`
codes plus `WORLD_UNKNOWN` and `WRITER_CAPTURE_INCOMPLETE` are catalogued in
`DIAGNOSTICS.md`, each with its exact trigger.

`tools/storage_template.py WORLD DIR` is an **authoring aid** printing a complete
binding (`--fresh SEED` emits opaque hashed names so they cannot be mistaken for a
convention). It calls `storage.py::binding_document`, which the compiler never calls —
`bind_world` only ever reads a document from disk.

---

## Evolution

Continuity is by qualified identity across one generation of a world.
`evolution.py::classify(before, after, history, retention)` compares two resolved
programs and returns `Event`s plus a `compat` verdict; `evolution.py::migrate`
applies a classification to a real store.

| Construct | Meaning and refusals |
|---|---|
| `renamed_from qname` (intent item) | this intent *is* the previous identity: same module → `intent_renamed`, different module → `intent_relocated`. Unknown target → `RENAME_TARGET_UNKNOWN` |
| `tombstone NAME STRING { data quarantine\|drop }` | records why an intent retired and what happens to its data. Empty meaning → `RETIRE_REASON_REQUIRED`; redeclaring a tombstoned name without `restore` → `ID_RESERVED` |
| `retype NAME retype_clause` / `retype` in an intent | a base-type change with `forward`/`backward` adapters. Missing → `RETYPE_ADAPTER_REQUIRED`; wrong "previous" type → `RETYPE_INCONSISTENT`; a **key** across type classes → `RETYPE_KEY_EQUALITY` |
| `restore NAME` / `restore` in an intent | bring a tombstoned intent back. No tombstone → `RESTORE_TARGET_UNKNOWN`; tombstoned `drop` → `RESTORE_DATA_UNAVAILABLE`; older than `quarantine_retention` → `RESTORE_OUTSIDE_RETENTION` |
| `tighten path_expr repair repair_val` / `tighten NAME repair …` | the repair for existing rows when a use becomes required. Path must be `Carrier.intent` (`TIGHTEN_PATH_INVALID`, `TIGHTEN_UNKNOWN`) |
| `move_home NAME of NAME into NAME data quarantine\|drop` | a real event: the intent's home carrier changes, with a disposition for the old column. Inconsistent with either generation → `MOVE_HOME_INCONSISTENT` |

Evolution statements may appear at top level in the grammar but must live **inside a
module** (`EVOLUTION_STATEMENT_HOMELESS`).

`classify` produces eighteen event kinds — `intent_renamed`, `intent_relocated`,
`meaning_delta`, `retype`, `add_intent`, `retire_intent`, `restore_intent`,
`move_home`, `add_carrier`, `retire_carrier`, `lifecycle`, `carry_added`,
`use_added`, `use_removed`, `tighten`, `link_added`, `link_policy`, `link_removed` —
and a `compat` of `breaking` / `deprecating` / `additive`. An **undeclared** move
(same local name, different module, no `renamed_from`) is a retirement plus a mint
and demands a tombstone (`RETIREMENT_POLICY_REQUIRED`). Adding or tightening a use
to *required* without a default, stamp or repair refuses `TIGHTEN_REPAIR_REQUIRED`.

Migration is **column- and table-level only**: `ALTER TABLE … RENAME COLUMN` for
continued identities, `ADD COLUMN` plus a repair `UPDATE` for new required uses,
`CREATE TABLE … __quarantine_<generation>` for quarantined retirements, then
`DROP COLUMN`, and `CREATE TABLE` for a new relation. A column that disappears with no
classified disposition refuses `MIGRATION_UNSUPPORTED`; no in-place type change is
performed. `open_store` refuses `STORE_UNSHIPPED`, `STORE_BEHIND`, `STORE_DRIFT` at
stage `load`; `check_window` refuses `GENERATION_OUTSIDE_WINDOW`. Worked
five-generation example: `corpus/worlds/evolution/g1..g5`.

---

## Live behaviour

A `question` derives three artifacts from the same resolved IR; a `query` derives
none.

**Footprint** (`footprint.py::derive_footprint`) — a set of `Atom(carrier, field)`
where `field` is a use qid, a link qid, or `"*"` for structural change, covering the
subject's structure, the `archived_by` use, both ends of every predicate path step,
projections including nested shows and the child's `order`-flagged uses, order keys,
group keys, the scope-path links, and — recursively through `within` — the whole inner
question. On a query it refuses `QUERY_NOT_LIVE`. **Binding descriptor**
(`generate.py::binding_descriptor`) — subject, shape, `live_bound`, parameters,
`scoped`, capability, writer class and source, retention, composed reads. **Routing
keys** (`generate.py::routing_descriptor`, `live.py::LiveEngine.routing_keys`) — one
`(partition, carrier, field)` per atom; the partition is the instance's scope when the
atom's carrier has a scope path in a scoped world, `global` otherwise.

At runtime `LiveEngine.subscribe` fetches once and registers only on success;
`match(deltas)` probes only the keys a delta can touch. A refresh whose row count
exceeds `live bounded N` refuses `LIVE_BOUND_EXCEEDED` at stage `runtime`
(`live.py::Instance._fetch`) — the bound is enforced, not descriptive — and a refresh
that changes nothing emits no batch. Composition rules: the inner read must be a
question (`QUESTION_COMPOSE_STATIC`), not windowed (`QUESTION_COMPOSE_PAGED`), not
unscoped under a scoped outer (`QUESTION_COMPOSE_UNSCOPED`), parameterless
(`COMPOSE_INNER_GIVENS`), subject-compatible (`COMPOSE_SUBJECT_MISMATCH`) and acyclic
(`QUESTION_COMPOSE_CYCLE`). Full semantics: `ARCHITECTURE.md`
(`## Routing and live semantics`).

---

## Capture

A world declaring `writers external_captured` (with its `writer_source`) is written
by an outside process; Garns reads the changes back.

**Declared triggers.** `lower_sqlite.py::lower_capture_ddl` emits, per relation, one
changelog table plus three triggers `<changelog table>__insert`, `__update`,
`__delete`, using the **mapped** physical names; the update trigger writes a `before`
row from `OLD` and then an `update` row from `NEW`, so every update carries its
before-image.

**Coverage is checked twice.** At bind time the binding must map a changelog and every
field of every relation (`WRITER_CAPTURE_INCOMPLETE`, stage `validate`); at load time
`capture.py::CaptureAdapter.check_coverage` reads `PRAGMA table_info` on the real
changelog tables and refuses the same code at stage `load`, before any effect — those
`PRAGMA` counts are the measured coverage denominators.

**`acquire(transaction_id)`** reads rows whose revision column is still null, orders
each relation by its own `seq`, merges by `seq`, builds typed deltas validated by the
same `LedgerValidator` as a governed write, writes one revision plus its ledger rows,
stamps the consumed rows, and notifies live listeners. An `update` with no buffered
before-image refuses `CAPTURE_SEQUENCE_INVALID`, an unknown op refuses
`CAPTURE_OP_UNKNOWN`, and constructing the adapter on a `governed` world refuses
`CAPTURE_NOT_DECLARED`. **Ordering limitation:** each relation's changelog has its own
`AUTOINCREMENT` sequence, so interleaving inside one acquisition is
`(seq, carrier qid)`, not a true global order — see example 3, where a `Depot`
inserted *before* a `Crate` is recorded *after* it.

Worked example: `corpus/conformance/worlds/ledgerhouse/`.

---

## Minimal valid examples

Three complete sources — the first two printed in full, the third described against
the second — each written into a fresh temporary directory with its storage binding and
then parsed, resolved, bound, shipped and executed with **this build** (nothing was
written inside `build/B2`); the observed output is quoted. All three ran
from `build/B2` as
`PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -c '<script>'` with
`sys.path.insert(0, "src")`, `EX` the temporary directory, and the script doing
`resolve_files(parse_paths(garns_files(EX)))` → `bind_world(p, "<WORLD>", EX / "storage-<WORLD>.json")`
→ `lower_read` / `Store(...).ship()` / `Engine(...)`.

### 1 — A static world with a query

```garns
module inventory "one stockroom and the reads over it" {
  intent sku : Id "stock keeping unit"
  intent item_name : Text "what the item is called"
  intent quantity : Integer "units on hand"
  resource Item "one stocked item" {
    use sku { key } use item_name use quantity { filter order } lifecycle mutable
  }
  query low_stock of Item "items at or below a threshold, scarcest first" {
    given threshold : Integer
    where quantity <= threshold
    show sku, item_name, quantity order quantity ascending
  }
}
world INVENTORY "the stockroom store" {
  modules inventory durability durable writers governed
  generated python, rust scope deployment quarantine_retention 3
}
deployment INVENTORY_DEV "in memory" {
  world INVENTORY engine sqlite at memory ship on_open mode readwrite snapshot none
}
```

```json
{"schema": "garns-v9-5/storage-binding/1", "world": "INVENTORY",
 "engine": {"ledger": "inv_ledger", "generations": "inv_generations", "revisions": "inv_revisions"},
 "relations": {"inventory.Item": {"table": "stock_item", "identity": "item_no",
   "columns": {"inventory.Item.sku": "sku_txt", "inventory.Item.item_name": "label",
               "inventory.Item.quantity": "on_hand"}, "links": {}}}}
```

Observed (exit 0): shape `collection`, params `('threshold',)`, keys `('$k0',)`,
`scoped False`; two rows minted through `Engine.transaction("governed", "tx1")`;
`e.execute("inventory.low_stock", {"threshold": 10})` → `[{'sku': 'A-1', 'item_name': 'bolt', 'quantity': 3}]`.

```sql
SELECT s0."item_no" AS "$k0", s0."sku_txt" AS "sku", s0."label" AS "item_name", s0."on_hand" AS "quantity"
FROM "stock_item" AS s0 WHERE (s0."on_hand" <= :threshold) ORDER BY s0."on_hand" ASC, s0."item_no" ASC
```

### 2 — A dynamic world with a question (scoped)

```garns
module tenants "tenants and the trait that scopes a row to one of them" {
  intent tenant_code : Text "the tenant's code"
  resource Tenant "the scope root" { use tenant_code { key } lifecycle mutable }
  trait Owned "belongs to exactly one tenant" { link tenant -> Tenant { end restrict scopes } }
}
module tickets "support tickets, scoped through the tenant they belong to" {
  import tenants (Owned)
  intent ticket_ref : Id "ticket reference"
  intent state : TicketState "where the ticket stands" { values @open, @closed }
  intent opened_at : Instant "when the ticket was opened"
  resource Ticket "one support ticket" {
    use ticket_ref { key } use state { filter } use opened_at { order }
    carry Owned lifecycle mutable
  }
  question open_tickets of Ticket "the tenant's open tickets, newest first" {
    where state = @open
    show identity, ticket_ref, opened_at
    order opened_at descending first 50 live bounded 50
  }
}
world SUPPORT "the support desk store" {
  modules tenants, tickets durability durable writers governed generated python, rust
  requires tenants.Owned exempt tenants.Tenant scope tenants.Owned.tenant quarantine_retention 3
}
deployment SUPPORT_DEV "in memory" {
  world SUPPORT engine sqlite at memory ship on_open mode readwrite snapshot none
}
```

The binding maps `tenants.Tenant` → `tenant(tenant_no, code_txt)` and
`tickets.Ticket` → `ticket(ticket_no, ref_txt, state_txt, opened, held_by)`, with
`tickets.Ticket.tenant` → `held_by`.

Observed (exit 0): `scope_paths` `{'SUPPORT': {'tickets.Ticket': ('tickets.Ticket.tenant',), 'tenants.Tenant': ()}}`;
`plan.scoped True`, `plan.live_bound 50`; footprint atoms `(tickets.Ticket, *)`,
`.opened_at`, `.state`, `.tenant`, `.ticket_ref` with
`scope_links ('tickets.Ticket.tenant',)`; SQL

```sql
SELECT s0."ticket_no" AS "$k0", s0."ticket_no" AS "identity", s0."ref_txt" AS "ticket_ref", s0."opened" AS "opened_at"
FROM "ticket" AS s0 WHERE s0."held_by" = :_scope AND (s0."state_txt" = 'open')
ORDER BY s0."opened" DESC, s0."ticket_no" ASC LIMIT 50
```

After `live.subscribe("tickets.open_tickets", {}, scope=t1)`, a write into tenant
`t2` routed **nothing** (`last_batches {}`, `candidates 0`) and a write into `t1`
produced one batch with a single `upsert`. `listener_scans` stayed `0` throughout.

### 3 — A captured world

Example 2's shape with `writers external_captured`, `writer_source depot_daemon`,
`quarantine_retention 2`, carriers `Depot`/`Crate` (trait `Stored`, link
`depot -> Depot { end restrict scopes }`), one question
`heavy_crates of Crate "…" { where mass_g > 500 show crate_label, mass_g order mass_g descending live bounded 200 }`,
and a `capture` section mapping `depot.Depot` → `depot_log`, `depot.Crate` →
`crate_log` (fields `log_seq`, `verb`, `tick`, `<x>_ref`, plus one `_v` column per
use and link).

Observed (exit 0): shipping emitted the six triggers `crate_log__insert/update/delete`
and `depot_log__insert/update/delete` with the mapped names, and `check_coverage()`
returned `{'depot.Crate': 7, 'depot.Depot': 5}`. Two `INSERT`s were then run against
the store **outside** Garns (a depot, then a 900 g crate in it), and
`CaptureAdapter(e).acquire("ext-1")` produced revision 1 with two typed deltas — the
`Crate` insert (`scope_after 1`, through `kept_in`) *before* the `Depot` insert, the
`(seq, carrier qid)` ordering limitation in action — both stamped
`writer depot_daemon`, `transaction ext-1`, both written to the ledger. A later
external `UPDATE crate SET mass = 400` was acquired as an `update` delta carrying
`old 900, new 400` from the before-image, and routed one batch containing a `delete`
for the now-too-light crate.

---

## Refusal examples

Every row was produced by running parse + resolve on the snippet with this build;
stage, code and position are observed, not authored. Codes link to
`DIAGNOSTICS.md` (`## Catalogue`).

| Snippet (inside an otherwise valid module) | Stage | Code |
|---|---|---|
| `link parent -> Parent { end unenforced }` | decode | `DECL_SHAPE_INVALID` |
| `link parent -> Parent { unenforced end cascade }` | validate | `LINK_ENFORCEMENT_CONFLICT` |
| `link parent -> Parent { unenforced unenforced }` | validate | `LINK_ENFORCEMENT_REPEATED` |
| `question q of Thing "…" { show identity }` (no live bound) | validate | `QUESTION_LIVE_BOUND_REQUIRED` |
| `… { show identity live bounded 10 live bounded 20 }` | validate | `QUESTION_LIVE_BOUND_DUPLICATED` |
| `… { show identity live bounded 0 }` | validate | `QUESTION_LIVE_BOUND_INVALID` |
| `query q of Thing "…" { show identity live bounded 10 }` | decode | `DECL_SHAPE_INVALID` |
| `question … { show call text.length(code) as n live bounded 10 }` | decode | `DECL_SHAPE_INVALID` |
| `question … { where seen_at < engine_clock … live bounded 10 }` | validate | `QUESTION_NOT_FOOTPRINTABLE` |
| `deployment D "…" { world W engine postgres at memory ship on_open mode readwrite snapshot none }` | validate | `ENGINE_LOWERING_ABSENT` (at the `engine` item) |
| the same with `engine oracle` | validate | `ENGINE_UNKNOWN` |
| `where things.amount > 1` (to-many, unquantified) | validate | `TERM_TO_MANY_UNQUANTIFIED` |
| `show call text.slugify(code) as s` / `clock.now() as n` / `store.purge(code) as p` | validate | `CALL_UNKNOWN` / `CALL_VOLATILE` / `CALL_EFFECTFUL` |
| `module m { … }` (no meaning string) | decode | `MEANS_REQUIRED` |
| `CREATE TABLE thing (id INTEGER);` | decode | `SOURCE_NOT_GARNS` |
| `use blob { key }` / `where blob = "x"`, `blob : Opaque` | validate | `OPAQUE_POLICY` / `OPAQUE_COMPARED` |
