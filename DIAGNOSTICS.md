# Diagnostics

Garns has exactly one failure channel: `Refusal`, defined in `src/garns/refuse.py`.
Every compile-time and runtime rejection in the implementation raises a `Refusal`
carrying a **code**, a **stage**, a **source position** and a human **detail**. No
part of the pipeline returns a warning, a partial result, or a repaired program:
the first refusal wins and nothing downstream runs.

This document is the canonical list of those codes. Other documents link here
rather than repeating rows: for what a code *means* in the language, see
`DSL_REFERENCE.md`; for when a stage runs, see `COMPILER_PIPELINE.md`
(`## Phases`, `## Earliest pre-effect validation boundary`); for what is not
implemented at all, see `LIMITATIONS.md` (`## Inventory`).

Scope note: refusal codes are **not** a stable public API surface in this build.
They are the codes the implementation raises, measured from the source at
`src/garns/`. Nothing in the frozen grammar names a code.

---

## Stages

`src/garns/refuse.py::STAGES` fixes seven stage names, in this order. `Refusal.__post_init__`
rejects any other stage, so a stage string outside this tuple is a programming
error, not a diagnostic.

| Stage | Meaning | Raised in | Distinct codes |
|---|---|---|---:|
| `decode` | the frozen grammar rejected the text; classified from LALR parser state | `parse.py::classify_decode`, and nowhere else | 6 |
| `validate` | names, types, worlds, storage binding, read algebra, verbs — everything the resolver and `bind_world` decide | `resolve.py`, `resolve_read.py`, `storage.py`, plus three source-shape checks in `lower_sqlite.py` and three in `footprint.py` | 216 |
| `lower` | relational / storage lowering | `lower_sqlite.py` (two internal guards) | 2 |
| `generate` | artifact generation | **nowhere** | **0** |
| `ship` | evolution classification and store shipping | `evolution.py` (`classify`, `_retype`, `_restore`, `migrate`) | 12 |
| `load` | opening an existing store | `evolution.py::open_store` / `check_window`, `capture.py::CaptureAdapter.check_coverage` | 5 |
| `runtime` | ledger, live and capture effects | `engine.py`, `live.py`, `capture.py` | 25 |

Two facts about this table matter to a caller:

- **`generate` is declared but never raised.** `grep -n '"generate"' src/garns`
  finds the `STAGES` entry, a `mutants.py` scenario step name and a `cli.py`
  subcommand name — no `Refusal`. `src/garns/generate.py::generate` refuses only
  by re-raising what `lower_read` and `derive_footprint` raise, at their own
  stages (`validate`, `lower`). A caller should not match on `stage == "generate"`.
- **`lower` is almost as thin.** Its two codes (`LOWER_INVERSE_OUTSIDE_QUANTIFIER`,
  `LOWER_QUANTIFIER_WITHOUT_MANY`) are internal guards; the resolver refuses the
  corresponding source shapes first (`TERM_TO_MANY_UNQUANTIFIED`,
  `QUANTIFIER_WITHOUT_TO_MANY`). Three codes raised *inside* `lower_sqlite.py` are
  deliberately reported at stage `validate`, because they are properties of the
  source rather than of the lowering: `GIVEN_NAME_RESERVED`, `NESTED_SHOW_PATH`,
  `QUANTIFIER_MULTIPLE_MANY`.

Four codes are raised at two different stages, because two different callers can
reach the same fault: `QUERY_NOT_LIVE`, `READ_UNKNOWN`, `VERB_INPUT_ENGINE_OWNED`
and `WRITER_CAPTURE_INCOMPLETE`. They appear once per stage in the catalogue.

---

## How diagnostics are produced

### The `Refusal` dataclass

`src/garns/refuse.py::Refusal` is a frozen dataclass that subclasses `Exception`:

| Field | Type | Meaning |
|---|---|---|
| `code` | `str` | the stable identifier in the catalogue below |
| `stage` | `str` | one of `STAGES`; validated in `__post_init__` |
| `file` | `str` | source file the position refers to; `""` when unknown |
| `line` | `int` | 1-based line; `1` when unknown |
| `column` | `int` | 1-based column; `1` when unknown |
| `detail` | `str` | prose naming the offending identity; never machine-parsed |

`__str__` renders `CODE [stage] at file:line:col: detail` (dropping `file:` when
empty); `as_dict()` returns the six fields for JSON. `src/garns/cli.py::main`
catches `Refusal`, prints `refused: <str(refusal)>` to stderr and exits **2**.

### Position semantics

`src/garns/refuse.py::refuse(code, stage, loc, detail)` accepts *anything* with
`file`/`line`/`column` attributes, and unwraps one level of `.loc` first. In
practice `loc` is an `ast.Name`, an `ast.*Item`/`*Stmt` node, or an IR node that
carries a `Loc`. Every identifier occurrence in the AST is its own
`ast.Name` with its own `Loc` (`src/garns/parse.py::_Builder.name`), so a refusal
can point at the exact token that is wrong rather than at the enclosing
declaration.

Three position conventions appear in the catalogue:

- **A source token.** Most `validate` codes. The `Location reported` column names
  which token.
- **The binding file at `1:1`.** All `STORAGE_*` codes and `WORLD_UNKNOWN` from
  `bind_world`: a binding is a JSON document, so the refusal carries the binding
  path with line/column `1:1` (`src/garns/storage.py::_fail`).
- **No position at all (`""`, `1`, `1`).** Every `runtime` and `load` code, and
  the two `lower` guards. `src/garns/engine.py::_runtime` and the `Refusal(...)`
  calls in `live.py`, `capture.py` and `evolution.py::open_store` construct the
  refusal with an empty file. A caller that needs to attribute a runtime refusal
  to source must use the qualified identity in `detail`, not the position.

Positions are therefore reliable for `decode` and `validate`, and absent for
`runtime`/`load`.

### Decode classification

`src/garns/parse.py::classify_decode(exc, file)` turns a Lark `UnexpectedInput`
into one of six codes using **only** parser state: the LALR value stack
(`_stack_of` reads `exc.interactive_parser.parser_state.value_stack`), the
expected-terminal set (`_expected_of`), and the failing token. No filename,
comment, marker or source regex participates. The decisions are taken in this
order — the first that matches wins:

| # | Code | Condition |
|---|---|---|
| 1 | `SOURCE_TRUNCATED` | the exception is `UnexpectedEOF`, or the offending token is `$END` |
| 2 | `MEANS_REQUIRED` | the expected set is exactly `{STRING}` **and** the last token after the innermost open `{` is not one of `PATTERN`, `BREAKING`, `PATH`, `DEFAULT` (the four keywords that take a non-meaning string) |
| 2′ | `DECL_SHAPE_INVALID` | the expected set is exactly `{STRING}` but the previous token *is* one of those four |
| 3 | `TYPE_SHAPE_INVALID` | the last token opens a type position (`COLON`, `OPTIONAL`, `LIST_OF`, `OF`) and the expected set is a subset of `{NAME, OPTIONAL, LIST_OF}` |
| 4 | `EXPR_NOT_ADMITTED` | brace depth > 0, and scanning the tail backwards an expression keyword (`WHERE`, `HAVING`, `INVARIANT`) is reached before any completed item tree (`q_item`, `query_item`, `carrier_item`, `member_item`, `intent_item`, `world_item`, `dep_item`) |
| 5 | `DECL_SHAPE_INVALID` | brace depth > 0 otherwise |
| 6 | `SOURCE_NOT_GARNS` | brace depth 0 and every entry left on the value stack is a completed `Tree` |
| 7 | `DECL_SHAPE_INVALID` | brace depth 0 with a partial declaration on the stack |

The value-stack rules are what make the classification stable: "the innermost
open body" is `stack[last LBRACE + 1:]`, and `depth` is the count of `LBRACE`
tokens still on the stack. Because a `Tree` on the stack means a *completed*
sub-parse, rule 6 fires exactly when nothing was started, which is how
non-Garns text (Python, SQL, YAML) is recognised without inspecting the text.

### Pre-effect guarantees

The `Before effects?` column in the catalogue records, per row:

- **`yes`** — no schema, store, ledger, generation, migration or generated-artifact
  effect had run when the refusal was raised. Every `decode`, `validate`, `lower`
  and `load` code is `yes`, because the only producer of a `WorldIR` is
  `src/garns/storage.py::bind_world`, which needs a resolved `Program`, and every
  effectful entry point (`Store.ship`, `Engine`, `generate`, `evolution.migrate`,
  `evolution.open_store`) takes a `WorldIR`. Most `runtime` codes are also `yes`:
  the typed ledger validation in `src/garns/engine.py::LedgerValidator` and the
  parameter binding in `Engine.bind_params` both run before any statement is
  issued.
- **`rolled back`** — a statement had been issued, and the code path executes
  `ROLLBACK` before raising, so the transaction leaves no revision, no ledger row
  and no batch (`Transaction.mint`, `Transaction.change`, `Transaction.delete`,
  `Transaction._check_invariants`; `evolution.migrate` wraps its whole run in
  `BEGIN`/`ROLLBACK`).
- **`read only`** — `LIVE_BOUND_EXCEEDED` is raised after a `SELECT` in
  `Instance._fetch`; nothing was written, and `LiveEngine.subscribe` registers an
  instance only after the initial fetch succeeds, so no partial registration
  survives.

`ENGINE_LOWERING_ABSENT` is the sharpest case of `yes`: see its row and
[PROVENANCE.md](PROVENANCE.md).

---

## Catalogue

262 distinct codes; 266 rows, because the four dual-stage codes appear once per
stage. Rows are grouped by stage in `STAGES` order, alphabetical within a stage.

Columns: **Raised by** lists every distinct `file::symbol` for that code and
stage, with the source line numbers in parentheses. **Trigger** is the
implementation's own `detail` text, with `<...>` marking runtime-interpolated
values; for codes raised from several places it is a summary of all of them.
**Location reported** names the token or object the position points at.
**Evidence** names one asserting fixture (`mutant …` = `corpus/mutants/`,
`refusal …` = `corpus/conformance/refusals/`) and/or unit-test module; `—` means
no fixture in this corpus asserts the code — the code is implemented and
reachable, but unasserted.

| Code | Stage | Raised by (file::symbol) | Trigger | Location reported | Before effects? | Evidence |
|---|---|---|---|---|---|---|
| `DECL_SHAPE_INVALID` | decode | `src/garns/parse.py::classify_decode` (93, 106, 110) | a declaration or body item whose shape the grammar does not admit (also: a string was required here) | the failing token | yes | mutant ESCAPE_BODY-1.garns; refusal END_UNENFORCED-1.garns |
| `EXPR_NOT_ADMITTED` | decode | `src/garns/parse.py::classify_decode` (105) | expression is outside the closed algebra | the failing token | yes | mutant HOST_EXPR-1.garns; tests/test_parse.py |
| `MEANS_REQUIRED` | decode | `src/garns/parse.py::classify_decode` (92) | a declaration states its meaning as a string | the failing token | yes | mutant MEANS_REQUIRED-1.garns; tests/test_parse.py |
| `SOURCE_NOT_GARNS` | decode | `src/garns/parse.py::classify_decode` (109) | text is not a Garns top-level declaration | the failing token | yes | mutant GENERATION_MISMATCH-1.garns; tests/test_parse.py |
| `SOURCE_TRUNCATED` | decode | `src/garns/parse.py::classify_decode` (77) | source ends inside an open construct | the failing token | yes | tests/test_parse.py |
| `TYPE_SHAPE_INVALID` | decode | `src/garns/parse.py::classify_decode` (96) | type reference is optional? list_of? NAME | the failing token | yes | mutant U2_SHAPE-1.garns |
| `AGGREGATE_MISUSED` | validate | `src/garns/resolve_read.py::ReadResolver.call`, `src/garns/resolve_read.py::ReadResolver.check_grouped`, `src/garns/resolve_read.py::ReadResolver.static_aggregate` (445, 447, 455, 458, 471, 693, 696, 698, 701) | an aggregate in a clause that admits none, a nested aggregate, count(distinct) without a path, a call inside an aggregate argument, or a grouped show/order that is neither a group key nor an aggregate | the offending node; the order term; the show term | yes | mutant AGGREGATE_MISUSED-1.garns |
| `AGG_NOT_TO_MANY` | validate | `src/garns/resolve_read.py::ReadResolver.agg` (344) | <node.path.text> is not a to-many link | the path | yes | — |
| `ALIAS_NOT_DERIVED` | validate | `src/garns/resolve.py::Resolver.verb_of` (878) | <verb> is not a derived verb | the verb name | yes | mutant ALIAS_NOT_DERIVED-1.garns |
| `ARCHIVED_BY_INVALID` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (643) | archived_by names an optional Instant use of the carrier | the archived_by name | yes | mutant ARCHIVED_BY_INVALID-1.garns |
| `ASSOCIATION_ARITY` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (617) | association <qid> needs at least two links | the declaration name | yes | mutant ASSOCIATION_ARITY-1.garns |
| `BULK_NOT_DERIVED_VERB` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (899) | bulk over <verb> is not admitted | the verb name | yes | mutant BULK_NOT_DERIVED_VERB-1.garns |
| `BULK_OVER_MISMATCH` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (904) | <over.qid> reads <over.subject>, not <carrier_qid> | the over read name | yes | — |
| `BULK_OVER_PAGED` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (906) | bulk over windowed read <over.qid> is refused | the over read name | yes | — |
| `BULK_PARAM_UNDECLARED` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (926) | <sc.value.text> is not a given of <entry.qid> | the set value | yes | mutant BULK_PARAM_UNDECLARED-1.garns |
| `BULK_SET_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (929) | <sc.value.text> is <gt.describe()>, <use.intent> is <use.type.describe()> | the set value | yes | — |
| `BULK_SET_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (915) | <sc.target.text> is not a use of <carrier_qid> | the set target | yes | — |
| `BY_NOT_GIVEN` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (574) | by names a given typed as the subject | the by path | yes | — |
| `BY_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (577) | by needs a given identifying <subject.qid> | the by path | yes | — |
| `CALL_ARGUMENT_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.call` (490, 496) | a closed-set member is not a function argument | the offending node | yes | mutant CALL_ARGUMENT_TYPE-1.garns |
| `CALL_ARITY` | validate | `src/garns/resolve_read.py::ReadResolver.call` (484) | <name> takes <len(sig.params)> arguments | the offending node | yes | mutant CALL_ARITY-1.garns |
| `CALL_EFFECTFUL` | validate | `src/garns/resolve_read.py::ReadResolver.call` (479) | <name> has side effects | the call name | yes | mutant CALL_EFFECTFUL-1.garns |
| `CALL_UNKNOWN` | validate | `src/garns/resolve_read.py::ReadResolver.call` (475) | <name> is not a registered function | the call name | yes | mutant CALL_UNKNOWN-1.garns |
| `CALL_VOLATILE` | validate | `src/garns/resolve_read.py::ReadResolver.call` (477) | <name> is not deterministic | the call name | yes | mutant CALL_VOLATILE-1.garns |
| `CAPABILITY_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1099) | capability <c.text> listed twice | the carrier | yes | — |
| `CAPABILITY_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.check_capabilities` (1226) | world <world_name> declares no capability <name.text> | the offending name | yes | mutant CAPABILITY_UNKNOWN-1.garns |
| `CARRIER_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_evolution_stmt -> lookup()`, `src/garns/resolve.py::Resolver.resolve_link -> lookup()`, `src/garns/resolve.py::Resolver.verb_of -> lookup()`, `src/garns/resolve_read.py::ReadResolver.resolve_read -> lookup()` (513, 517, 871, 993, 1014, 1016) | raised through src/garns/resolve.py:134 Resolver::lookup | the offending name | yes | — |
| `CARRY_NOT_TRAIT` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (587) | <t.text> is not a trait | the trait name | yes | — |
| `CARRY_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (589) | <qid> carries <t.text> twice | the trait name | yes | — |
| `CLOSED_SET_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_type` (279) | <closed_qid> is declared with different members | the offending name | yes | — |
| `CLOSED_SET_MEMBER_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (351) | <c.text> listed twice | the carrier | yes | — |
| `CLOSED_SET_MEMBER_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.literal_of_type`, `src/garns/resolve_read.py::ReadResolver.retype_literal` (189, 501) | a @member literal that the closed set does not admit | the flag or clause; the literal | yes | mutant CLOSED_SET_MEMBER_UNKNOWN-1.garns |
| `CLOSED_SET_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (385) | a closed set refines a text type | the type reference | yes | — |
| `COMPOSE_INNER_GIVENS` | validate | `src/garns/resolve_read.py::ReadResolver.check_compositions` (771) | <inner_qid> declares givens; a composed read is parameterless | the flag or clause | yes | mutant COMPOSE_INNER_GIVENS-1.garns |
| `COMPOSE_SUBJECT_MISMATCH` | validate | `src/garns/resolve_read.py::ReadResolver.check_compositions` (763) | <inner_qid> reads <inner.subject>; the path ends at <end> | the flag or clause | yes | — |
| `CONTAINS_NOT_TEXT` | validate | `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static` (270, 376) | contains applies to text | the offending node | yes | mutant CONTAINS_NOT_TEXT-1.garns |
| `DEFAULT_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_default -> literal_of_type()`, `src/garns/resolve.py::Resolver.resolve_default` (480, 483) | ship_clock defaults an Instant | the flag or clause; the offending name | yes | — |
| `DEPLOYMENT_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_worlds` (1032) | deployment <node.name.text> declared twice | the declaration name | yes | — |
| `DEPLOYMENT_EXTENDS_CYCLE` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1233) | extends cycle | the declaration name | yes | — |
| `DEPLOYMENT_EXTENDS_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1238) | deployment <node.extends.text> is not declared | the extends name | yes | — |
| `DEPLOYMENT_ITEM_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1248) | <item.kind> stated twice | the item | yes | — |
| `DEPLOYMENT_LOCATION_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no at | the declaration name | yes | mutant DEPLOYMENT_LOCATION_REQUIRED-1.garns |
| `DEPLOYMENT_MODE_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no mode | the declaration name | yes | mutant DEPLOYMENT_MODE_REQUIRED-1.garns |
| `DEPLOYMENT_MODE_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1273) | mode <item.name.text> is not admitted | the item's name | yes | — |
| `DEPLOYMENT_SNAPSHOT_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no snapshot | the declaration name | yes | mutant DEPLOYMENT_SNAPSHOT_REQUIRED-1.garns |
| `DEPLOYMENT_WORLD_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no world | the declaration name | yes | — |
| `DETACH_NOT_OPTIONAL` | validate | `src/garns/resolve.py::Resolver.resolve_link` (554) | link <node.name.text> detaches but is not optional | the offending node | yes | mutant DETACH_NOT_OPTIONAL-1.garns |
| `DIMENSION_NOT_POSITIVE` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (362) | dimension must be a positive integer | the item | yes | mutant DIMENSION_NOT_POSITIVE-1.garns |
| `DIMENSION_NOT_VECTOR` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (381) | dimension refines a Vector intent only | the type reference | yes | mutant DIMENSION_NOT_VECTOR-1.garns |
| `DIMENSION_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (383) | a Vector intent states its dimension | the type reference | yes | — |
| `DURABILITY_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1072) | durability <durability.text> is not admitted | the durability item | yes | — |
| `ENGINE_LOWERING_ABSENT` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1296) | deployment <node.name.text> uses engine <engine>, which this build recognises but cannot lower (lowered engines: <', '.join(sorted(LOWERED_ENGINES))>) | the deployment's `engine` item (or the deployment name if it had none) | yes | mutant ENGINE_LOWERING_ABSENT-1.garns; refusal ENGINE_LOWERING_ABSENT-1.garns; tests/test_repair_engine_lowering.py |
| `ENGINE_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no engine | the declaration name | yes | mutant ENGINE_REQUIRED-1.garns |
| `ENGINE_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1259) | engine <item.name.text> is not admitted | the item's name | yes | tests/test_repair_engine_lowering.py |
| `EVOLUTION_STATEMENT_HOMELESS` | validate | `src/garns/resolve.py::Resolver.resolve_verbs` (868) | evolution statements belong inside a module | the statement | yes | — |
| `EXEMPT_NOT_CARRIER` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1120) | <ex.text> cannot be exempted | the exempt name | yes | — |
| `EXEMPT_REDUNDANT` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1122) | <ex.text> carries <requires> and is also exempted | the exempt name | yes | mutant EXEMPT_REDUNDANT-1.garns |
| `EXEMPT_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1124) | <ex.text> exempted twice | the exempt name | yes | — |
| `EXEMPT_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_world -> lookup_qualified()` (1115) | raised through src/garns/resolve.py:149 Resolver::lookup_qualified | the offending name | yes | — |
| `EXPR_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.agg`, `src/garns/resolve_read.py::ReadResolver.arith`, `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.operand`, `src/garns/resolve_read.py::ReadResolver.resolve_read`, `src/garns/resolve_read.py::ReadResolver.retype_literal`, `src/garns/resolve_read.py::ReadResolver.static_aggregate`, `src/garns/resolve_read.py::ReadResolver.static`, `src/garns/resolve_read.py::ReadResolver.unify` (142, 187, 192, 202, 209, 219, 221, 265, 275, 284, 354, 380, 387, 400, 421, 433, 435, 462, 466, 595, 633) | an expression whose operand types do not fit (comparison, arithmetic, ordering, grouping, literal retyping, list misuse) | the aggregate argument; the flag or clause; the group key; the offending node; the order item | yes | mutant EXPR_TYPE-1.garns |
| `FAMILY_MEMBER_MINT_ONLY` | validate | `src/garns/resolve.py::Resolver.verb_of` (880) | a family is minted through one of its members | the verb name | yes | mutant FAMILY_MEMBER_MINT_ONLY-1.garns |
| `FIRST_NOT_POSITIVE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (654) | first N is positive | the first item | yes | — |
| `GIVEN_DEFAULT_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_given -> literal_of_type()` (53) | raised through src/garns/resolve.py:499 Resolver::literal_of_type | the offending name | yes | — |
| `GIVEN_DUPLICATED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (523) | given <item.name.text> declared twice | the item's name | yes | — |
| `GIVEN_NAME_RESERVED` | validate | `src/garns/lower_sqlite.py::lower_read`, `src/garns/resolve_read.py::ReadResolver.resolve_given` (49, 530) | a given whose name starts with _ (checked in the resolver and again in lower_read) | the declaration name; the given / target name | yes | mutant GIVEN_NAME_RESERVED-1.garns |
| `GIVEN_UNKNOWN` | validate | `src/garns/resolve_read.py::ReadResolver.given_ref` (670) | <name.text> is not a given | the offending name | yes | — |
| `GIVEN_UNUSED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (660) | given <g.name> is never used | the given / target name | yes | mutant GIVEN_UNUSED-1.garns |
| `GUARD_NOT_OPTIONAL_GIVEN` | validate | `src/garns/resolve_read.py::ReadResolver.guard_of` (228) | when given guards an optional given | the flag or clause | yes | — |
| `HAVING_WITHOUT_GROUP` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (618) | having needs group by or aggregates | the having item | yes | mutant HAVING_WITHOUT_GROUP-1.garns |
| `ID_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.declare` (109, 114) | a name declared twice in one module, or tombstoned twice | the offending name | yes | mutant ID_DUPLICATED-1.garns |
| `ID_RESERVED` | validate | `src/garns/resolve.py::Resolver.check_tombstones` (1326, 1328) | <t.qid> is tombstoned; redeclaring it requires restore | the intent declaration; the redeclaration | yes | mutant ID_RESERVED-1.garns |
| `IMPORT_AMBIGUOUS` | validate | `src/garns/resolve.py::Resolver.resolve_imports` (220) | <local.text> is imported twice into <module> | the local name | yes | mutant IMPORT_AMBIGUOUS-1.garns |
| `IMPORT_NOT_OWNER` | validate | `src/garns/resolve.py::Resolver.resolve_imports` (213) | <stmt.owner.text> imports <item.source.text>; it does not own it | the imported name | yes | mutant IMPORT_NOT_OWNER-1.garns |
| `IMPORT_SELF` | validate | `src/garns/resolve.py::Resolver.resolve_imports` (206) | <module> imports itself | the imported module name | yes | — |
| `IMPORT_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_imports` (204, 214) | the named module is not declared, or does not declare the named item | the imported module name; the imported name | yes | mutant IMPORT_UNKNOWN-1.garns |
| `IMPORT_UNUSED` | validate | `src/garns/resolve.py::Resolver.check_unused_imports` (246) | <scope.decl.name.text> imports <entry.local> and never uses it | the imported name | yes | mutant IMPORT_UNUSED-1.garns |
| `INCLUDING_ARCHIVED_NOT_ARCHIVABLE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (582) | <subject.qid> has no archived_by lifecycle | the including_archived item | yes | mutant INCLUDING_ARCHIVED_NOT_ARCHIVABLE-1.garns |
| `INTENT_HOMELESS` | validate | `src/garns/resolve.py::Resolver.check_homeless_intents` (1318) | intent <i.qid> is used by no carrier | the intent declaration | yes | mutant INTENT_HOMELESS-1.garns |
| `INTENT_ITEM_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (387) | retired and restore are exclusive | the declaration name | yes | — |
| `INTENT_ITEM_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (333) | <kind> stated twice on <entry.qid> | the item | yes | — |
| `INTENT_REFINEMENT_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (379) | pattern/length refine text types only | the type reference | yes | — |
| `INTENT_TYPE_SHAPE` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (375) | an intent is of a scalar type; optionality belongs to the use | the type reference | yes | — |
| `INVARIANT_CLOCK` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_invariant` (507) | an invariant is clock-free | the expression | yes | — |
| `INVARIANT_COMPOSES` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_invariant` (505) | an invariant does not compose reads | the expression | yes | — |
| `INVERSE_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.compute_inverses` (778) | <l.target> already has an inverse named <l.inverse> | the link | yes | mutant INVERSE_DUPLICATED-1.garns |
| `IN_NOT_LIST` | validate | `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static` (282, 385) | in takes a list_of given | the offending node | yes | mutant IN_NOT_LIST-1.garns |
| `IS_NOT_LINK` | validate | `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static` (289, 391) | is compares a link or identity with an identity | the offending node | yes | mutant IS_NOT_LINK-1.garns |
| `IS_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static` (296, 396) | <left.text> identifies <target>; the value identifies <rt.describe()> | the offending node | yes | — |
| `LAST_NOT_POSITIVE` | validate | `src/garns/resolve_read.py::ReadResolver.shows` (740) | last N is positive | the show value | yes | — |
| `LENGTH_RANGE_INVALID` | validate | `src/garns/resolve.py::Resolver.resolve_intent` (358) | maximum below minimum | the item | yes | — |
| `LIFECYCLE_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (580) | <qid> states lifecycle twice | the item | yes | — |
| `LINK_CYCLE_UNMINTABLE` | validate | `src/garns/resolve.py::Resolver.validate_link_targets.visit` (818) | ' -> '.join(path + [target]) | the first carrier of the cycle | yes | mutant LINK_CYCLE_UNMINTABLE-1.garns |
| `LINK_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier`, `src/garns/resolve.py::Resolver.resolve_member` (635, 744) | <qid> links <l.name> twice | the item; the link | yes | — |
| `LINK_ENFORCEMENT_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_link` (551) | link <node.name.text> combines unenforced with end <end> | the offending node | yes | refusal LINK_ENFORCEMENT_CONFLICT-1.garns |
| `LINK_ENFORCEMENT_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_link` (527) | <kind> repeated on link <name> | the flag | yes | refusal LINK_ENFORCEMENT_REPEATED-1.garns |
| `LINK_FLAG_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_link` (556) | a key link cannot be optional | the offending node | yes | — |
| `LINK_FLAG_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_link` (527) | <kind> repeated on link <name> | the flag | yes | — |
| `LINK_TO_TRAIT` | validate | `src/garns/resolve.py::Resolver.validate_link_targets` (803) | <l.qid> targets a trait | the link | yes | — |
| `MEMBER_OF_NON_FAMILY` | validate | `src/garns/resolve.py::Resolver.resolve_member` (728) | a member declared on a non-family carrier; unreachable from source, because member_decl appears only inside family_decl | the declaration name | yes | — |
| `MODULE_CYCLE` | validate | `src/garns/resolve.py::Resolver.resolve_imports.visit` (233) | ' -> '.join(cycle) | the module name of the cycle | yes | mutant MODULE_CYCLE-1.garns |
| `MODULE_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.collect` (159) | module <top.name.text> is declared twice | the module name | yes | — |
| `MODULE_NOT_LISTED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1069, 1109, 1117, 1136) | a module reached through an import, requires, exempt or scope path that the world does not list | the first path segment; the imported module name; the module of the exempt name; the module of the requires name | yes | mutant MODULE_NOT_LISTED-1.garns |
| `MODULE_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.lookup_qualified`, `src/garns/resolve.py::Resolver.resolve_world` (145, 1056, 1134) | a module name that no source declares | the first path segment; the module name | yes | — |
| `NAME_AMBIGUOUS` | validate | `src/garns/resolve.py::Resolver.compute_inverses`, `src/garns/resolve.py::Resolver.lookup`, `src/garns/resolve.py::Resolver.resolve_imports` (125, 222, 780) | a name is both declared and imported, or an inverse name collides with a term of its target | the link; the local name; the offending name | yes | — |
| `NAME_NOT_IMPORTED` | validate | `src/garns/resolve.py::Resolver.lookup` (133) | <name.text> is declared by <', '.join(owners)> and not imported into <module> | the offending name | yes | mutant NAME_NOT_IMPORTED-1.garns |
| `NESTED_SHOW_NOT_TO_MANY` | validate | `src/garns/resolve_read.py::ReadResolver.shows` (735) | <v.path.text> is not a to-many link | the nested show path | yes | — |
| `NESTED_SHOW_PATH` | validate | `src/garns/lower_sqlite.py::lower_nested` (478) | a nested show follows one inverse link | the offending node | yes | — |
| `NESTED_SHOW_WITH_DISTINCT` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (651) | a distinct result has no row identity to attach nested rows to | the distinct item | yes | mutant NESTED_SHOW_WITH_DISTINCT-1.garns |
| `NEWTYPE_SHAPE` | validate | `src/garns/resolve.py::Resolver.resolve_newtype` (295) | a newtype is of a scalar type | the newtype's of clause | yes | — |
| `OPAQUE_COMPARED` | validate | `src/garns/resolve_read.py::ReadResolver.unify` (212) | opaque and vector values admit presence only | the flag or clause | yes | mutant OPAQUE_COMPARED-1.garns |
| `OPAQUE_POLICY` | validate | `src/garns/resolve.py::Resolver.resolve_use` (474) | opaque and vector uses are neither keys nor order terms | the offending node | yes | — |
| `OPTIONAL_PARAM_UNGUARDED` | validate | `src/garns/resolve_read.py::ReadResolver.guard_of` (232) | optional given <given.name> is used inside or/not without when given | the flag or clause | yes | mutant OPTIONAL_PARAM_UNGUARDED-1.garns |
| `ORDERED_WITHIN_NOT_EVENT` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (596) | only events are ordered within a link | the item | yes | — |
| `ORDERED_WITHIN_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (594) | ordered_within stated twice | the item | yes | — |
| `ORDERED_WITHIN_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (650) | <ordered_within_name.text> is not a link of <qid> | the ordered_within name | yes | — |
| `ORDER_BY_LITERAL` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (631) | ordering by a literal is meaningless | the order item | yes | — |
| `PAGE_LIMIT_PAIR` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (557) | page and limit are stated together | the page or limit item | yes | mutant PAGE_LIMIT_PAIR-1.garns |
| `PAGE_TYPE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read -> given_ref()` (568, 569) | raised through src/garns/resolve_read.py:672 ReadResolver::given_ref | the offending name | yes | — |
| `PATH_THROUGH_SCALAR` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_path` (65) | <names[index - 1].text> is a scalar; <name.text> cannot follow it | the offending name | yes | — |
| `PRESET_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (600) | history kept stated twice | the item | yes | mutant PRESET_CONFLICT-1.garns |
| `QNAME_REQUIRED` | validate | `src/garns/resolve.py::Resolver.lookup_qualified` (141) | <qn.text> must be module-qualified | the qualified name | yes | — |
| `QUANTIFIER_MULTIPLE_MANY` | validate | `src/garns/lower_sqlite.py::_Lowerer.visit_Quantified` (245) | a quantified comparison follows one to-many path | the offending node | yes | — |
| `QUANTIFIER_WITHOUT_TO_MANY` | validate | `src/garns/resolve_read.py::ReadResolver.dyn` (255) | <node.kind> quantifies a to-many path; none is present | the offending node | yes | mutant QUANTIFIER_WITHOUT_TO_MANY-1.garns |
| `QUARANTINE_RETENTION_INVALID` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1094) | retention is a positive generation count | `seen['quarantine_retention']` | yes | — |
| `QUARANTINE_RETENTION_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no quarantine_retention | the declaration name | yes | mutant QUARANTINE_RETENTION_REQUIRED-1.garns |
| `QUERY_NOT_LIVE` | validate | `src/garns/footprint.py::derive_footprint` (219) | derive_footprint on a query (validate); LiveEngine.subscribe on a query (runtime) | the read declaration | yes | mutant scenarios/QUERY_NOT_LIVE; tests/test_static_dynamic.py |
| `QUESTION_CLOCK_NOT_A_TERM` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_path` (68) | ship_clock is a write-time default, not a read term | the offending name | yes | mutant QUESTION_CLOCK_NOT_A_TERM-1.garns |
| `QUESTION_COMPOSE_CYCLE` | validate | `src/garns/footprint.py::FootprintDeriver.visit_Within`, `src/garns/resolve_read.py::ReadResolver.check_compositions.visit` (149, 780) | within composition is cyclic (checked in the resolver and again while deriving the footprint) | the node's line/column, no file; the read at the head of the cycle | yes | — |
| `QUESTION_COMPOSE_PAGED` | validate | `src/garns/resolve_read.py::ReadResolver.check_compositions` (767) | <inner_qid> is windowed and cannot be composed | the flag or clause | yes | mutant QUESTION_COMPOSE_PAGED-1.garns |
| `QUESTION_COMPOSE_STATIC` | validate | `src/garns/resolve_read.py::ReadResolver.check_compositions` (765) | question <outer_qid> composes static query <inner_qid> | the flag or clause | yes | refusal QUESTION_COMPOSE_STATIC-1.garns |
| `QUESTION_COMPOSE_UNSCOPED` | validate | `src/garns/resolve_read.py::ReadResolver.check_compositions` (769) | <inner_qid> is unscoped; <outer_qid> is scoped | the flag or clause | yes | mutant QUESTION_COMPOSE_UNSCOPED-1.garns |
| `QUESTION_INTENT_RETIRED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_path` (110) | <text> is retired from <carrier.module> | the offending name | yes | mutant QUESTION_INTENT_RETIRED-1.garns |
| `QUESTION_LIVE_BOUND_DUPLICATED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (530) | <ItemClass> stated twice in <read qid> | the item | yes | refusal QUESTION_LIVE_BOUND_DUPLICATED-1.garns |
| `QUESTION_LIVE_BOUND_INVALID` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (554) | live bounded N is a positive literal | the live item | yes | refusal QUESTION_LIVE_BOUND_INVALID-1.garns |
| `QUESTION_LIVE_BOUND_REQUIRED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (549) | question <qid> states no live bounded N | the declaration name | yes | refusal QUESTION_LIVE_BOUND_REQUIRED-1.garns |
| `QUESTION_NOT_FOOTPRINTABLE` | validate | `src/garns/footprint.py::_static_only`, `src/garns/resolve_read.py::ReadResolver.resolve_read` (51, 657) | engine_clock in a question (resolver), or a static-only IR node reached while deriving the footprint (ClockRef, Arith, Negate, StaticAggregate, Call, Truth, ShowScalar, having, distinct) | the declaration name; the offending IR node | yes | refusal QUESTION_CLOCK-1.garns |
| `RANK_WITHOUT_ORDER` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (649) | rank needs an order | the show list | yes | mutant RANK_WITHOUT_ORDER-1.garns |
| `READ_ITEM_REPEATED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (530) | <ItemClass> stated twice in <read qid> | the item | yes | — |
| `READ_OF_TRAIT` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (517) | a read is of a storable carrier | the subject name | yes | — |
| `READ_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_bulk -> lookup()`, `src/garns/resolve_read.py::ReadResolver.dyn -> lookup()`, `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static -> lookup()`, `src/garns/resolve_read.py::ReadResolver.static -> lookup_qualified()` (306, 307, 410, 413, 900) | within names an unresolvable read, bulk names an unknown over read (validate); Engine/LiveEngine is given a read qid the world does not hold (runtime) | the `within` target, or the offending name | yes | mutant scenarios/READ_UNKNOWN_SELECTION |
| `REPAIR_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_repair -> literal_of_type()`, `src/garns/resolve.py::Resolver.resolve_repair` (488, 493) | ship_clock repairs an Instant | the flag or clause; the offending name | yes | — |
| `REQUIRES_NOT_TRAIT` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1112) | <item.qname.text> is not a trait | the requires qualified name | yes | — |
| `RESTRICTED_ACCEPTS_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_restricted` (950) | <a.text> is not a use or link of <carrier_qid> | the accepted name | yes | — |
| `RETIRE_REASON_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_verbs` (854) | a tombstone states why the intent retired | the declaration name | yes | mutant RETIRE_REASON_REQUIRED-1.garns |
| `SCOPE_LINK_NOT_ROOT` | validate | `src/garns/resolve.py::Resolver.compute_scope_paths` (1169) | <l.qid> is marked scopes but is not the world's scope root | the link | yes | mutant SCOPE_LINK_NOT_ROOT-1.garns |
| `SCOPE_LINK_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1148) | <names[2].text> is not a link of <tentry.qid> | the third path segment | yes | — |
| `SCOPE_PATH_AMBIGUOUS` | validate | `src/garns/resolve.py::Resolver.compute_scope_paths` (1212) | <c.qid> reaches the scope root through <', '.join((l.name for l in candidates))>; declare scope_via | the carrier | yes | mutant SCOPE_PATH_AMBIGUOUS-1.garns |
| `SCOPE_PATH_INVALID` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1132) | scope names module.Trait.link | the scope path | yes | — |
| `SCOPE_PATH_TO_EXEMPT` | validate | `src/garns/resolve.py::Resolver.compute_scope_paths` (1209) | <c.qid> is scoped via <link.qid>, whose target <link.target> carries no scope path | the link | yes | mutant SCOPE_PATH_TO_EXEMPT-1.garns |
| `SCOPE_ROOT_MISMATCH` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1145) | scope trait <tentry.qid> differs from required trait <requires> | the second path segment | yes | — |
| `SCOPE_ROOT_NOT_SCOPED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1151) | <link.qid> is not marked scopes | the third path segment | yes | mutant SCOPE_ROOT_NOT_SCOPED-1.garns |
| `SCOPE_VIA_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (610) | scope_via stated twice | the item | yes | — |
| `SCOPE_VIA_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (657) | <scope_via_name.text> is not a link of <qid> | the scope_via name | yes | — |
| `SET_ABSENT_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_bulk` (921) | <use.intent> is required and cannot be set absent | the set clause | yes | mutant SET_ABSENT_REQUIRED-1.garns |
| `SHAPE_CONFLICT` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (562, 564) | more than one of one / by / first / page+limit / group by, or distinct together with group by | the distinct item; the second shape item | yes | mutant SHAPE_CONFLICT-1.garns |
| `SHIP_MODE_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1291) | deployment <D> states no ship | the declaration name | yes | mutant SHIP_MODE_REQUIRED-1.garns |
| `SHIP_MODE_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1268) | ship <item.name.text> is not admitted | the item's name | yes | — |
| `SHOW_ALIAS_REQUIRED` | validate | `src/garns/resolve_read.py::ReadResolver.shows` (747) | an expression column needs `as name` | the show value | yes | mutant SHOW_ALIAS_REQUIRED-1.garns |
| `SHOW_COLUMN_DUPLICATED` | validate | `src/garns/resolve_read.py::ReadResolver.shows` (752) | column <term.column> shown twice | the item | yes | — |
| `SHOW_LITERAL` | validate | `src/garns/resolve_read.py::ReadResolver.shows` (745) | a literal is not a result column | the show value | yes | — |
| `SNAPSHOT_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment` (1278) | snapshot <item.name.text> is not admitted | the item's name | yes | — |
| `STAMP_NOT_INSTANT` | validate | `src/garns/resolve.py::Resolver.resolve_use` (463) | stamps are written to Instant uses only | the flag | yes | mutant STAMP_NOT_INSTANT-1.garns |
| `STEP_BIND_PATH` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (969) | a bind names one link of the step's carrier | the bind path | yes | — |
| `STEP_BIND_TYPE` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (982) | <link.qid> targets <link.target>; step <b.step.text> yields <bound_carrier> | the step reference | yes | mutant STEP_BIND_TYPE-1.garns |
| `STEP_BIND_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (972) | <b.path.text> is not a link of <carrier_qid> | the bind path | yes | — |
| `STEP_CYCLE` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (975, 978) | a step binds itself or a later step | the step reference | yes | mutant STEP_CYCLE-1.garns |
| `STEP_NAME_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (962) | step <st.name.text> declared twice | the step name | yes | mutant STEP_NAME_DUPLICATED-1.garns |
| `STEP_REFERENCE_UNRESOLVED` | validate | `src/garns/resolve.py::Resolver.resolve_compound` (979) | <b.step.text> is not a step of <entry.qid> | the step reference | yes | mutant STEP_REFERENCE_UNRESOLVED-1.garns |
| `STORAGE_BINDING_UNREADABLE` | validate | `src/garns/storage.py::load_binding` (144) | str(exc) | `str(path), 1, 1` | yes | — |
| `STORAGE_CAPTURE_NOT_ADMITTED` | validate | `src/garns/storage.py::bind_world` (202) | capture mappings belong to external_captured worlds | the binding file (1:1) | yes | — |
| `STORAGE_COLUMNS_MISSING` | validate | `src/garns/storage.py::bind_world` (217) | <qid> needs columns and links maps | the binding file (1:1) | yes | — |
| `STORAGE_COLUMN_COLLISION` | validate | `src/garns/storage.py::bind_world` (231, 240, 247, 267, 280, 289) | two mapped keys (or a key and the identity, kind or changelog metadata column) share one physical column name | the binding file (1:1) | yes | mutant scenarios/STORAGE_COLUMN_COLLISION |
| `STORAGE_COLUMN_MISSING` | validate | `src/garns/storage.py::bind_world` (228) | <qid> maps no column for use <key> | the binding file (1:1) | yes | mutant scenarios/STORAGE_COLUMN_MISSING |
| `STORAGE_COLUMN_UNKNOWN` | validate | `src/garns/storage.py::bind_world` (220, 294) | <qid> maps unknown use <key> | the binding file (1:1) | yes | — |
| `STORAGE_ENGINE_TABLES_MISSING` | validate | `src/garns/storage.py::bind_world` (182) | engine tables (ledger, generations, revisions) are required | the binding file (1:1) | yes | — |
| `STORAGE_KIND_NOT_ADMITTED` | validate | `src/garns/storage.py::bind_world` (249) | <qid> is not a family; kind has no meaning | the binding file (1:1) | yes | — |
| `STORAGE_LINK_MISSING` | validate | `src/garns/storage.py::bind_world` (237) | <qid> maps no column for link <key> | the binding file (1:1) | yes | — |
| `STORAGE_LINK_UNKNOWN` | validate | `src/garns/storage.py::bind_world` (223, 297) | <qid> maps unknown link <key> | the binding file (1:1) | yes | — |
| `STORAGE_NAME_INVALID` | validate | `src/garns/storage.py::_ident` (136) | a physical name that is not a plain identifier | the binding file (1:1) | yes | — |
| `STORAGE_RELATIONS_MISSING` | validate | `src/garns/storage.py::bind_world` (190) | relations are required | the binding file (1:1) | yes | — |
| `STORAGE_RELATION_MISSING` | validate | `src/garns/storage.py::bind_world` (207) | no relation mapping for <qid> | the binding file (1:1) | yes | mutant scenarios/STORAGE_RELATION_MISSING |
| `STORAGE_RELATION_UNKNOWN` | validate | `src/garns/storage.py::bind_world` (194) | <qid> is not a storable carrier of world <world_name> | the binding file (1:1) | yes | — |
| `STORAGE_SCHEMA_UNKNOWN` | validate | `src/garns/storage.py::load_binding` (146) | expected schema <SCHEMA> | the binding file (1:1) | yes | — |
| `STORAGE_TABLE_COLLISION` | validate | `src/garns/storage.py::bind_world` (197, 210, 257) | two relations, or a relation and an engine or changelog table, map to one physical table name | the binding file (1:1) | yes | mutant scenarios/STORAGE_TABLE_COLLISION |
| `STORAGE_WORLD_MISMATCH` | validate | `src/garns/storage.py::bind_world` (179) | binding is for world <data.get('world')>, not <world_name> | the binding file (1:1) | yes | mutant scenarios/STORAGE_WORLD_MISMATCH |
| `TARGET_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1079) | generated target <g.text> has no surface in this build | the given / target name | yes | mutant TARGET_UNKNOWN-1.garns |
| `TERM_RESERVED` | validate | `src/garns/resolve.py::Resolver.declare` (105) | <name.text> is a language term and cannot be declared | the offending name | yes | mutant TERM_RESERVED-1.garns |
| `TERM_TO_MANY_UNQUANTIFIED` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_path` (115) | <node.text> traverses a to-many link without some/every | the offending node | yes | mutant TERM_TO_MANY_UNQUANTIFIED-1.garns |
| `TERM_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_evolution_stmt -> lookup()`, `src/garns/resolve.py::Resolver.resolve_use -> lookup()`, `src/garns/resolve_read.py::ReadResolver.resolve_path` (74, 111, 443, 1002, 1008, 1012) | a path segment that is not a use, link, inverse or alias of the carrier at that point; kind on a non-family; an unknown intent name on a use | the offending name | yes | mutant TERM_RENAMED-1.garns |
| `TIGHTEN_PATH_INVALID` | validate | `src/garns/resolve.py::Resolver.resolve_evolution_stmt` (992) | tighten names Carrier.intent | the tighten path | yes | — |
| `TIGHTEN_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_carrier`, `src/garns/resolve.py::Resolver.resolve_evolution_stmt`, `src/garns/resolve.py::Resolver.resolve_member` (664, 751, 998) | tighten names something that is not a use of the carrier | the intent name; the tighten name; the tighten term | yes | — |
| `TRAIT_CYCLE` | validate | `src/garns/resolve.py::Resolver._trait_order.visit` (431) | ' -> '.join(path + [d]) | the declaration name | yes | — |
| `TRAIT_LIFECYCLE` | validate | `src/garns/resolve.py::Resolver.resolve_carrier` (615) | a trait has no lifecycle | the declaration name | yes | — |
| `TRAIT_POLICY_CONFLICT` | validate | `src/garns/resolve.py::Resolver._merge_use`, `src/garns/resolve.py::Resolver.resolve_carrier` (627, 684, 686, 697) | two traits compose the same intent or link with different policies, or a restated use changes the trait's stamp/default | the carrier name; the declaration name; the restated use | yes | mutant TRAIT_POLICY_CONFLICT-1.garns |
| `TRAIT_REQUIRED` | validate | `src/garns/resolve.py::Resolver.compute_scope_paths` (1213) | <c.qid> neither carries <world.scope.trait>, is exempt, nor is scoped through a link | the carrier | yes | mutant TRAIT_REQUIRED-1.garns |
| `TRAIT_UNKNOWN` | validate | `src/garns/resolve.py::Resolver._trait_order -> lookup()`, `src/garns/resolve.py::Resolver.resolve_carrier -> lookup()`, `src/garns/resolve.py::Resolver.resolve_world -> lookup_qualified()`, `src/garns/resolve.py::Resolver.resolve_world` (420, 585, 1107, 1140) | <names[0].text>.<names[1].text> is not a trait | the offending name; the second path segment | yes | — |
| `TRAIT_WIDENED` | validate | `src/garns/resolve.py::Resolver._merge_use` (682) | <new.intent> restated wider than its trait | the restated use | yes | mutant TRAIT_WIDENED-1.garns |
| `TYPE_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_evolution_stmt`, `src/garns/resolve.py::Resolver.resolve_intent`, `src/garns/resolve.py::Resolver.resolve_newtype`, `src/garns/resolve.py::Resolver.resolve_type` (288, 289, 297, 366, 1005) | a type name that is not a builtin scalar, newtype or declared closed set | the newtype's base type; the offending name; the renamed_from target; the retype target | yes | — |
| `USE_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_carrier`, `src/garns/resolve.py::Resolver.resolve_member` (631, 739) | <qid> uses <u.intent> twice | the item; the use | yes | mutant USE_DUPLICATED-1.garns |
| `USE_FLAG_CONFLICT` | validate | `src/garns/resolve.py::Resolver.resolve_use` (472) | a key use cannot be optional | the offending node | yes | mutant USE_FLAG_CONFLICT-1.garns |
| `USE_FLAG_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_use` (451) | <flag.kind> repeated on use <node.intent.text> | the flag | yes | mutant USE_FLAG_REPEATED-1.garns |
| `VERB_INPUT_ENGINE_OWNED` | validate | `src/garns/resolve.py::Resolver.resolve_bulk`, `src/garns/resolve.py::Resolver.resolve_restricted` (918, 943) | a bulk set or restricted accepts naming a stamped use (validate); a write supplying a stamped use (runtime) | the accepted name; the set target | yes | mutant VERB_INPUT_ENGINE_OWNED-1.garns |
| `VERB_NOT_ADMITTED` | validate | `src/garns/resolve.py::Resolver.verb_of` (882) | append is an event verb | the verb name | yes | — |
| `VERB_ON_TRAIT` | validate | `src/garns/resolve.py::Resolver.verb_of` (875) | traits have no verbs | the carrier name | yes | — |
| `WITHIN_NOT_LINK` | validate | `src/garns/resolve_read.py::ReadResolver.dyn`, `src/garns/resolve_read.py::ReadResolver.static` (304, 408) | within composes a link or identity with a read | the offending node | yes | — |
| `WITH_TOTAL_WITHOUT_PAGE` | validate | `src/garns/resolve_read.py::ReadResolver.resolve_read` (559) | with_total accompanies page/limit | the with_total item | yes | — |
| `WORLD_DUPLICATED` | validate | `src/garns/resolve.py::Resolver.resolve_worlds` (1026) | world <node.name.text> declared twice | the declaration name | yes | — |
| `WORLD_DURABILITY_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no durability | the declaration name | yes | — |
| `WORLD_GENERATED_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no generated | the declaration name | yes | — |
| `WORLD_ITEM_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1041) | <item.kind> stated twice in world <node.name.text> | the item | yes | — |
| `WORLD_MODULES_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no modules | the declaration name | yes | — |
| `WORLD_MODULE_COLLISION` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1060) | module <m.text> already belongs to world <self.world_of_module[m.text]> | the module name | yes | mutant U18_COLLIDE-1.garns |
| `WORLD_MODULE_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1058) | module <m.text> listed twice | the module name | yes | — |
| `WORLD_REQUIRES_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1143) | a scoped world requires its scope trait | the scope item | yes | — |
| `WORLD_SCOPE_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no scope | the declaration name | yes | mutant U17_INCOMPLETE-1.garns |
| `WORLD_TARGET_REPEATED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1081) | target <g.text> listed twice | the given / target name | yes | — |
| `WORLD_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_deployment`, `src/garns/storage.py::bind_world` (174, 1253) | world <item.name.text> is not declared | `str(binding_path), 1, 1`; the item's name | yes | mutant U16_ESCAPE-1.garns; tests/test_generate.py |
| `WORLD_WRITERS_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1052) | world <W> states no writers | the declaration name | yes | — |
| `WRITER_CAPTURE_INCOMPLETE` | validate | `src/garns/storage.py::bind_world` (200, 254, 261, 273, 277, 286) | the binding does not map a changelog for every relation and every one of its fields (validate), or the real changelog table lacks a declared field (load) | the binding file (1:1) | yes | mutant scenarios/WRITER_CAPTURE_INCOMPLETE_BINDING; tests/test_capture_ledger.py |
| `WRITER_CLASS_UNKNOWN` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1075) | writers <writers.text> is not admitted | the writers item | yes | — |
| `WRITER_SOURCE_NOT_ADMITTED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1086) | writer_source belongs to external_captured worlds | `seen['writer_source']` | yes | — |
| `WRITER_SOURCE_REQUIRED` | validate | `src/garns/resolve.py::Resolver.resolve_world` (1090) | an external_captured world names its writer_source | the writers item | yes | mutant WRITER_SOURCE_REQUIRED-1.garns |
| `LOWER_INVERSE_OUTSIDE_QUANTIFIER` | lower | `src/garns/lower_sqlite.py::_Frame.alias_for` (100) | an inverse (to-many) step reached _Frame.alias_for, which only joins forward steps; the resolver normally refuses first (internal guard) | none (1:1) | yes | — |
| `LOWER_QUANTIFIER_WITHOUT_MANY` | lower | `src/garns/lower_sqlite.py::_Lowerer.visit_Quantified` (242) | a Quantified node whose body mentions no to-many path reached lowering; the resolver normally refuses first (internal guard) | the node's line/column, no file | yes | — |
| `ACCESSOR_BREAKING_UNACKNOWLEDGED` | ship | `src/garns/evolution.py::classify` (131) | <qid> changes lifecycle <prev.lifecycle> -> <c.lifecycle>; the carrier must state breaking "..." | the carrier | yes | mutant scenarios/ACCESSOR_BREAKING_UNACKNOWLEDGED; tests/test_evolution.py |
| `MIGRATION_UNSUPPORTED` | ship | `src/garns/evolution.py::migrate` (311) | column <pcol> of <rel.table> disappears without a classified disposition | none (1:1) | rolled back | — |
| `MOVE_HOME_INCONSISTENT` | ship | `src/garns/evolution.py::classify` (115, 118) | <mh.source> did not use <mh.intent> in the previous generation | the move_home statement | yes | mutant scenarios/MOVE_HOME_INCONSISTENT; tests/test_evolution.py |
| `RENAME_TARGET_UNKNOWN` | ship | `src/garns/evolution.py::classify` (70) | <qid> is renamed_from <it.renamed_from>, which the previous generation does not declare | the intent declaration | yes | mutant scenarios/RENAME_TARGET_UNKNOWN; tests/test_evolution.py |
| `RESTORE_DATA_UNAVAILABLE` | ship | `src/garns/evolution.py::_restore` (195) | <it.qid> was retired with data drop; nothing to restore | the intent declaration | yes | mutant scenarios/RESTORE_DATA_UNAVAILABLE; tests/test_evolution.py |
| `RESTORE_OUTSIDE_RETENTION` | ship | `src/garns/evolution.py::_restore` (197) | <it.qid> was tombstoned <age> generations ago; retention is <retention> | the intent declaration | yes | — |
| `RESTORE_TARGET_UNKNOWN` | ship | `src/garns/evolution.py::_restore` (193) | <it.qid> restores an intent no earlier generation tombstoned | the intent declaration | yes | — |
| `RETIREMENT_POLICY_REQUIRED` | ship | `src/garns/evolution.py::classify` (96, 108) | an intent disappears, or moves module without renamed_from, and no tombstone states its data disposition | the intent declaration; the previous intent | yes | mutant scenarios/RETIREMENT_POLICY_REQUIRED; tests/test_evolution.py |
| `RETYPE_ADAPTER_REQUIRED` | ship | `src/garns/evolution.py::_retype` (175) | <it.qid> changes type <prev.type.base> -> <it.type.base> without retype adapters | the intent declaration | yes | — |
| `RETYPE_INCONSISTENT` | ship | `src/garns/evolution.py::_retype`, `src/garns/evolution.py::classify` (86, 177) | retype declares a previous base type that is not the previous generation's | the intent declaration | yes | — |
| `RETYPE_KEY_EQUALITY` | ship | `src/garns/evolution.py::_retype` (179) | <it.qid> is a key; <prev.type.base> -> <it.type.base> does not preserve equality | the intent declaration | yes | mutant scenarios/RETYPE_KEY_EQUALITY; tests/test_evolution.py |
| `TIGHTEN_REPAIR_REQUIRED` | ship | `src/garns/evolution.py::classify`, `src/garns/evolution.py::migrate` (143, 148, 266) | a use becomes required (added or tightened) with no default, stamp or repair for existing rows | none (1:1); the use | rolled back | — |
| `GENERATION_OUTSIDE_WINDOW` | load | `src/garns/evolution.py::check_window` (355) | generation <min(generations)> lies outside the retention window of <retention> generations | none (1:1) | yes | mutant scenarios/GENERATION_OUTSIDE_WINDOW |
| `STORE_BEHIND` | load | `src/garns/evolution.py::open_store` (340, 341) | the recorded IR/storage digests differ from the source | none (1:1) | yes | mutant scenarios/STORE_BEHIND |
| `STORE_DRIFT` | load | `src/garns/evolution.py::open_store` (347, 349) | a mapped table lacks a declared column, or carries an undeclared one | none (1:1) | yes | mutant scenarios/STORE_DRIFT |
| `STORE_UNSHIPPED` | load | `src/garns/evolution.py::open_store` (333, 335) | the store has no generation table, or the table records no generation | none (1:1) | yes | mutant scenarios/STORE_UNSHIPPED |
| `WRITER_CAPTURE_INCOMPLETE` | load | `src/garns/capture.py::CaptureAdapter.check_coverage` (41, 43) | the binding does not map a changelog for every relation and every one of its fields (validate), or the real changelog table lacks a declared field (load) | none (1:1) | yes | mutant scenarios/WRITER_CAPTURE_INCOMPLETE_BINDING; tests/test_capture_ledger.py |
| `CAPABILITY_REQUIRED` | runtime | `src/garns/engine.py::Engine.bind_params` (329) | <read.qid> is unscoped behind capability <read.unscoped> | none (1:1) | yes | mutant scenarios/CAPABILITY_REQUIRED |
| `CAPTURE_NOT_DECLARED` | runtime | `src/garns/capture.py::CaptureAdapter.__init__` (28) | world <self.world.world.name> declares writers <self.world.world.writers>; capture needs external_captured | none (1:1) | yes | mutant scenarios/CAPTURE_NOT_DECLARED; tests/test_capture_ledger.py |
| `CAPTURE_OP_UNKNOWN` | runtime | `src/garns/capture.py::CaptureAdapter.acquire` (96) | changelog op <op> | none (1:1) | yes | — |
| `CAPTURE_SEQUENCE_INVALID` | runtime | `src/garns/capture.py::CaptureAdapter.acquire` (89) | update of <carrier> <identity> without its before image | none (1:1) | yes | — |
| `CONSTRAINT_VIOLATED` | runtime | `src/garns/engine.py::Transaction.change`, `src/garns/engine.py::Transaction.mint` (489, 522) | sqlite3.IntegrityError on insert or update whose text does not mention UNIQUE (NOT NULL, CHECK, foreign key) | none (1:1) | rolled back | — |
| `IDENTITY_UNKNOWN` | runtime | `src/garns/engine.py::Transaction.change`, `src/garns/engine.py::Transaction.delete` (502, 505, 533) | change/delete names a row identity the relation does not hold, or the row is not of the named member | none (1:1) | yes | mutant scenarios/IDENTITY_UNKNOWN |
| `INVARIANT_VIOLATED` | runtime | `src/garns/engine.py::Transaction._check_invariants` (564) | <carrier> row <identity> violates an invariant | none (1:1) | rolled back | mutant scenarios/INVARIANT_VIOLATED |
| `KEY_DUPLICATED` | runtime | `src/garns/engine.py::Transaction.change`, `src/garns/engine.py::Transaction.mint` (489, 522) | sqlite3.IntegrityError on insert or update whose text mentions UNIQUE | none (1:1) | rolled back | mutant scenarios/KEY_DUPLICATED |
| `LEDGER_CARRIER_ABSTRACT` | runtime | `src/garns/engine.py::LedgerValidator.check_carrier` (101) | <carrier> is a family; write through one of its members | none (1:1) | yes | — |
| `LEDGER_CARRIER_UNKNOWN` | runtime | `src/garns/engine.py::LedgerValidator.check_carrier` (99) | <carrier> is not a storable carrier of world <self.world.world.name> | none (1:1) | yes | mutant scenarios/LEDGER_CARRIER_UNKNOWN; tests/test_capture_ledger.py |
| `LEDGER_FIELD_UNKNOWN` | runtime | `src/garns/engine.py::LedgerValidator.check_field` (114) | <field_qid> is not a use or link of <carrier> | none (1:1) | yes | mutant scenarios/LEDGER_FIELD_UNKNOWN; tests/test_capture_ledger.py |
| `LEDGER_SCOPE_UNKNOWN` | runtime | `src/garns/engine.py::LedgerValidator.check_scope` (158) | scope <scope> is not an identity of <root.root> | none (1:1) | yes | mutant scenarios/LEDGER_SCOPE_UNKNOWN; tests/test_capture_ledger.py |
| `LEDGER_TRANSACTION_INVALID` | runtime | `src/garns/engine.py::LedgerValidator.check_transaction` (95) | transaction id <txid> is not a typed identity | none (1:1) | yes | mutant scenarios/LEDGER_TRANSACTION_INVALID; tests/test_capture_ledger.py |
| `LEDGER_VALUE_TYPE` | runtime | `src/garns/engine.py::LedgerValidator.check_value` (127, 129, 133, 146, 148) | a written value of the wrong type class, a missing required value, or a non-member of a closed set | none (1:1) | yes | mutant scenarios/LEDGER_VALUE_TYPE; tests/test_capture_ledger.py |
| `LEDGER_WRITER_UNKNOWN` | runtime | `src/garns/engine.py::LedgerValidator.check_writer` (91) | writer <writer> is not declared by world <self.world.world.name> (declared: <sorted(self.writers)>) | none (1:1) | yes | mutant scenarios/LEDGER_WRITER_UNKNOWN; tests/test_capture_ledger.py |
| `LINK_RESTRICTED` | runtime | `src/garns/engine.py::Transaction.delete` (540) | sqlite3.IntegrityError on delete: a FOREIGN KEY ... ON DELETE RESTRICT still references the row | none (1:1) | rolled back | — |
| `LIVE_BOUND_EXCEEDED` | runtime | `src/garns/live.py::Instance._fetch` (122) | <self.read.qid> holds <len(result.rows)> rows; live bounded <self.read.live_bound> | none (1:1) | read only | mutant scenarios/LIVE_BOUND_EXCEEDED |
| `PARAM_REQUIRED` | runtime | `src/garns/engine.py::Engine.bind_params` (317) | <read.qid> needs given <name> | none (1:1) | yes | — |
| `PARAM_TYPE` | runtime | `src/garns/engine.py::Engine._check_param` (339, 343, 346, 348, 351, 354) | a bound parameter of the wrong type class, or a closed-set value that is not a member | none (1:1) | yes | — |
| `PARAM_UNKNOWN` | runtime | `src/garns/engine.py::Engine.bind_params` (309) | <read.qid> declares no given <name> | none (1:1) | yes | mutant scenarios/PARAM_UNKNOWN |
| `QUERY_NOT_LIVE` | runtime | `src/garns/live.py::LiveEngine.subscribe` (187) | derive_footprint on a query (validate); LiveEngine.subscribe on a query (runtime) | none (1:1) | yes | mutant scenarios/QUERY_NOT_LIVE; tests/test_static_dynamic.py |
| `READ_UNKNOWN` | runtime | `src/garns/engine.py::Engine._read` (211) | within names an unresolvable read, bulk names an unknown over read (validate); Engine/LiveEngine is given a read qid the world does not hold (runtime) | none (1:1) | yes | mutant scenarios/READ_UNKNOWN_SELECTION |
| `SCOPE_REQUIRED` | runtime | `src/garns/engine.py::Engine.bind_params` (325) | <read.qid> is scoped; a scope identity is required | none (1:1) | yes | mutant scenarios/SCOPE_REQUIRED |
| `VERB_INPUT_ENGINE_OWNED` | runtime | `src/garns/engine.py::Transaction._prepare` (429) | a bulk set or restricted accepts naming a stamped use (validate); a write supplying a stamped use (runtime) | none (1:1) | yes | mutant VERB_INPUT_ENGINE_OWNED-1.garns |
| `VERB_INPUT_REQUIRED` | runtime | `src/garns/engine.py::Transaction.mint` (468, 475) | mint <carrier> requires <key> | none (1:1) | yes | mutant scenarios/VERB_INPUT_REQUIRED |

### Counting the codes

The catalogue is derived by scanning `src/garns/**/*.py` for every refusal
construction. Two forms exist:

- **Literal first argument** — `refuse("CODE", …)`, `Refusal("CODE", …)`,
  `_runtime("CODE", …)` (`engine.py:68`), `_ship("CODE", …)` (`evolution.py:51`),
  `_fail("CODE", …)` (`storage.py:130`): **241 distinct codes at 347 raise sites**
  (`resolve.py` 120, `resolve_read.py` 56, `engine.py` 19, `storage.py` 19,
  `evolution.py` 16, `parse.py` 6, `lower_sqlite.py` 5, `capture.py` 4,
  `footprint.py` 3, `live.py` 2).
- **Code chosen through a variable** — **21 further codes** that a literal-argument
  scan misses:
  - a ternary at the raise site: `LINK_ENFORCEMENT_REPEATED` / `LINK_FLAG_REPEATED`
    (`resolve.py:526-527`), `QUESTION_LIVE_BOUND_DUPLICATED` / `READ_ITEM_REPEATED`
    (`resolve_read.py:529-530`), `KEY_DUPLICATED` / `CONSTRAINT_VIOLATED`
    (`engine.py:489,522` — `KEY_DUPLICATED` is also a literal, so only
    `CONSTRAINT_VIOLATED` is new here);
  - a required-item loop that iterates `(key, code)` pairs:
    `WORLD_MODULES_REQUIRED`, `WORLD_DURABILITY_REQUIRED`, `WORLD_WRITERS_REQUIRED`,
    `WORLD_GENERATED_REQUIRED`, `WORLD_SCOPE_REQUIRED`,
    `QUARANTINE_RETENTION_REQUIRED` (`resolve.py:1043-1052`) and
    `DEPLOYMENT_WORLD_REQUIRED`, `ENGINE_REQUIRED`, `DEPLOYMENT_LOCATION_REQUIRED`,
    `SHIP_MODE_REQUIRED`, `DEPLOYMENT_MODE_REQUIRED`, `DEPLOYMENT_SNAPSHOT_REQUIRED`
    (`resolve.py:1282-1291`);
  - a code passed to a helper that raises it: `lookup` / `lookup_qualified`
    take a `missing_code` (`resolve.py:119-151`), `literal_of_type` takes a `code`
    (`resolve.py:495`), `given_ref` takes a `code` (`resolve_read.py:667`). Only
    `CARRIER_UNKNOWN`, `EXEMPT_UNKNOWN`, `GIVEN_DEFAULT_TYPE` and `PAGE_TYPE` are
    *only* reachable this way; `TRAIT_UNKNOWN`, `TERM_UNKNOWN`, `READ_UNKNOWN`,
    `DEFAULT_TYPE` and `REPAIR_TYPE` are also raised literally elsewhere.

**241 + 21 = 262.** Because the helper form takes a code as data, the scan must
follow call sites; a future call site passing a new string would add a code
without touching a `refuse("…")` literal.

---

## Guaranteed diagnostics versus incidental exceptions

A `Refusal` is the guarantee. Everything below is a code path where a **non-`Refusal`
Python exception can escape to the caller** — reproduced by reading the code and,
where cheap, by provoking it. These are limitations, not contracts: an integrator
must be prepared for them, and none of them should be relied on as a signal.

| Escaping exception | Where | How it was observed | Note |
|---|---|---|---|
| `KeyError` | `src/garns/ir.py::Program.carrier` / `.intent` / `.read` / `.world` / `.link` / `.module` (`ir.py:713-748`), and through them `WorldIR.carrier`, `WorldIR.relation_of`, `StorageMapping.relation` (`storage.py:59-96`) | called each helper with an unknown qualified id: `KeyError: 'nope.Nope'` etc. | These are the public lookup helpers of the IR. The *engine* boundary is guarded (`Engine._read` refuses `READ_UNKNOWN`), but the IR helpers are not. The v9-5 R1 review records a probe wrapper that "assumed a `Refusal` instead of the actual `KeyError`"; see [PROVENANCE.md](PROVENANCE.md). |
| `sqlite3.OperationalError` | `src/garns/engine.py::Engine._last_revision` (`engine.py:196-199`) | constructed `Engine(store)` on a store that was never shipped: `no such table: sd_revisions` | The guarded path for an unshipped store is `src/garns/evolution.py::open_store`, which refuses `STORE_UNSHIPPED` at stage `load`. Constructing an `Engine` directly skips that check. |
| `sqlite3.OperationalError` | `src/garns/engine.py::Store.ship` (`engine.py:171-177`) | called `ship()` twice on one store: `table "tenant" already exists` | Shipping is not idempotent and there is no re-ship refusal. |
| `TypeError` | `src/garns/engine.py::Engine._check_param` (`engine.py:334-338`) | executed a read with a `list_of` given bound to `5`: `TypeError: 'int' object is not iterable` | Ordering defect: `items = list(value) if g.type.list_of else [value]` runs **before** the `isinstance(value, (list, tuple))` guard that would refuse `PARAM_TYPE`. A string or dict does refuse `PARAM_TYPE`; a non-iterable scalar raises. |
| `TypeError` | `src/garns/visit.py::Visitor.visit` (`visit.py:37-41`) | dispatched a subclass of an IR node through `FootprintDeriver`: `FootprintDeriver has no handler for IR node Phantom` | Deliberate: this is the exhaustiveness guard that makes adding an IR node fail loudly in every consumer (`check_exhaustive` / `assert_exhaustive`). It is a build-time signal for compiler authors, not a user diagnostic. |
| `json.JSONDecodeError` | `src/garns/cli.py::cmd_execute` (`cli.py:63-65`) | `garns execute … --param 'floor=notjson'`: traceback, **exit 1** | `main` catches only `Refusal`. A malformed `--param` value is not a refusal, so the CLI's documented "exit 2 on refusal" contract does not cover it. |
| `AssertionError` | the AST builder, `src/garns/parse.py` (35 sites: `parse.py:183, 199, 208, 216, 223, 242, 272, 306, 345, 346, 366, 377, 379, 388, 403, 405, 413, 447, 459, 502, 506, 525, 529, 536, 562, 575, 579, 581, 647, 678, 686, 703, 713, 748, 785`) and the resolver's exhaustiveness guards (`resolve.py:194, 290, 373, 470, 482, 492, 514, 549, 613, 640, 757, 785, 1020, 1092, 1106, 1129, 1176, 1191, 1208, 1251, 1257, 1263, 1266, 1271, 1276`; `resolve_read.py:88, 112, 150, 181, 203, 313, 351, 547, 552, 567, 572, 585, 591, 601, 609, 616, 626, 750`) | not provoked from admitted source | These assert grammar shapes the builder does not expect. Two are provably unreachable from source: `resolve_read.py:547` (`"grammar admits no live item in a query"` — a `live` item in a `query` is a **decode** `DECL_SHAPE_INVALID`, observed) and `MEMBER_OF_NON_FAMILY` (`resolve.py:728` — `member_decl` appears only inside `family_decl`). Because Python's `-O` strips `assert`, the bare `assert` forms are not a runtime guarantee at all. |
| `RecursionError` | `resolve.py` cycle walks (`resolve_imports::visit`, `_trait_order::visit`, `validate_link_targets::visit`), `resolve_read.py::check_compositions::visit`, `lower_sqlite.py::_Frame.alias_for`, `evolution`/`footprint` recursion | not provoked | Every graph walk is plain recursion with no depth bound. Cyclic input refuses (`MODULE_CYCLE`, `TRAIT_CYCLE`, `LINK_CYCLE_UNMINTABLE`, `QUESTION_COMPOSE_CYCLE`, `DEPLOYMENT_EXTENDS_CYCLE`), but a very deep acyclic graph is unguarded. |
| `sqlite3.*` (general) | `src/garns/engine.py`, `capture.py`, `evolution.py` | — | Only `sqlite3.IntegrityError` is mapped (`KEY_DUPLICATED` / `CONSTRAINT_VIOLATED` on write, `LINK_RESTRICTED` on delete). `OperationalError`, `DatabaseError` and `ProgrammingError` propagate unchanged; `evolution.migrate` rolls back and re-raises whatever `conn.execute` raised. |
| `ValueError` | `src/garns/mutants.py::observe_scenario` (`mutants.py:140`) | — | An unknown scenario step name. Test-harness only; not part of the compiler. |
| `AssertionError` | `src/garns/metamorphic.py:72` | — | Reference-map mismatch during a rename. Test-harness only. |

Rule of thumb for an integrator: **catch `Refusal` for everything the language
decides, and catch `Exception` at the process boundary anyway.** See
`INTEGRATION.md` (`## Python API`) for the call shapes that are guarded.

---

## Diagnostics asserted by the corpus

`corpus/mutants/expected.json` (schema `garns-v9-5/mutant-expectations/1`) holds
**168 cases** — 131 single-file `.garns` mutants plus 37 scenario directories —
covering **124 distinct outcomes** (123 refusal codes plus one `ACCEPTED`
control). By stage: validate 99, decode 40, runtime 18, ship 6, load 4,
accepted 1.

**The manifest is an assertion, never an input to detection.** The observation is
produced by `src/garns/mutants.py`:

- `observe_single(path)` parses and resolves the file through the production
  pipeline (`parse_text` → `resolve_files`) and returns
  `Observation(stage, code, line, column, detail)` from the raised `Refusal`, or
  the `ACCEPTED` sentinel.
- `observe_scenario(directory)` reads `scenario.json` and *executes* its steps —
  `resolve`, `bind`, `lower`, `generate`, `ship`, `sql`, `open`, `migrate`,
  `classify`, `window`, `write`, `capture`, `execute`, `subscribe` — against real
  SQLite stores, and returns the first refusal. That is how `ship`, `load` and
  `runtime` codes are reached: a scenario really ships a schema, really runs an
  external `ALTER TABLE`, really writes through a `Transaction`, really subscribes.
- Neither function opens `expected.json`. The file is read only by the test suite
  and by `tools/check.py` **after** the observation exists, to compare.

The independence property is executable, not asserted in prose: gate G9
re-identifies all 168 cases after renaming every mutant to `mNNN.garns`, stripping
every comment, renaming every scenario directory to a hash, and overwriting
`expected.json` with `{"corrupted": true}` — 168/168 unchanged (recorded in
`gate-report.json` and independently reproduced by both v9-5 reviewers; see
[PROVENANCE.md](PROVENANCE.md)).

`corpus/conformance/refusals/expected.json` (schema
`garns-v9-5/refusal-expectations/1`, 12 cases, 9 distinct codes) works the same
way and carries the same note: *"assertions only: the runner never reads this file
to decide an outcome."* Its cases are the language's load-bearing separations —
`end unenforced` (decode), the two enforcement conflicts, the four live-bound
rules, the static-call and clock refusals in a question, and
`ENGINE_LOWERING_ABSENT`.

### Coverage, stated honestly

Of the 262 implemented codes, **132 carry a named mutant, refusal fixture or unit
test**; **130 do not**. An unasserted code is not a dead code — the `Evidence`
column simply records that this corpus contains no case pinning it. Codes whose
only evidence is a unit test are marked with the test module rather than a
fixture. See `TESTING.md` (`## Commands`) for how to run the mutant sweep and the
unit suite.
