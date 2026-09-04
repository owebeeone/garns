#!/usr/bin/env python3
"""Build the v9-5 mutant corpus: migrated seed mutants, new mutants, scenarios.

The expected manifest written here is an authored assertion (code and stage
per mutant); it is never an input to detection. Run from build/B2.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parents[1]
SEED = HERE.parents[1] / "seed" / "v9-4" / "c3-core" / "mutants"
OUT = HERE / "corpus" / "mutants"

# name -> (expected stage, expected code, optional text edits [(old, new)])
SEED_MUTANTS: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "MEANS_REQUIRED-1": ("decode", "MEANS_REQUIRED", []),
    "ESCAPE_BODY-1": ("decode", "DECL_SHAPE_INVALID", []),
    "HOST_EXPR-1": ("decode", "EXPR_NOT_ADMITTED", []),
    "SQL_ESCAPE-1": ("decode", "EXPR_NOT_ADMITTED", []),
    "KIND_NOT_ADMITTED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "STORAGE_KNOB-1": ("decode", "DECL_SHAPE_INVALID", []),
    "META_BLOCK-1": ("decode", "DECL_SHAPE_INVALID", []),
    "TYPE_INLINE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "DECL_SHAPE_INVALID-1": ("decode", "DECL_SHAPE_INVALID", []),
    "EXPR_NOT_ADMITTED-1": ("decode", "EXPR_NOT_ADMITTED", []),
    "WORLD_NOT_DATA-1": ("decode", "DECL_SHAPE_INVALID", []),
    "BODY_NOT_DATA-1": ("decode", "DECL_SHAPE_INVALID", []),
    "DJANGO_LOOKUP-1": ("decode", "EXPR_NOT_ADMITTED", []),
    "OVERRIDE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "PRECEDENCE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "NOW_CALL-1": ("decode", "EXPR_NOT_ADMITTED", []),
    "TABLENAME-1": ("decode", "DECL_SHAPE_INVALID", []),
    "COLUMN-1": ("decode", "DECL_SHAPE_INVALID", []),
    "SUPER-1": ("decode", "DECL_SHAPE_INVALID", []),
    "DEPENDS-1": ("decode", "DECL_SHAPE_INVALID", []),
    "U2_SHAPE-1": ("decode", "TYPE_SHAPE_INVALID", []),
    "U7_MAGNITUDE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "SYNC_SURFACE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "RAW_SQL_BLOCK-1": ("decode", "DECL_SHAPE_INVALID", []),
    "GENERATION_MISMATCH-1": ("decode", "SOURCE_NOT_GARNS", []),
    "FAMILY_LIFECYCLE_FIXED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "FAMILY_DEPTH-1": ("decode", "DECL_SHAPE_INVALID", []),
    "LIVE_BOUND_REQUIRED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "REPAIR_SLOT_REQUIRED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "RETYPE_ADAPTER_REQUIRED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "ERE4_DESTRUCTIVE-1": ("decode", "DECL_SHAPE_INVALID", []),
    "U12_INTERACT-1": ("decode", "DECL_SHAPE_INVALID", []),
    "TYPE_CONSTRUCTOR_NESTED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "TYPE_CONSTRUCTOR_NESTED-2": ("decode", "DECL_SHAPE_INVALID", []),
    "MEMBER_ITEM_NOT_ADMITTED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "WHOLE_MODULE_IMPORT-1": ("decode", "DECL_SHAPE_INVALID", []),
    "EXEMPT_ON_CARRIER-1": ("decode", "DECL_SHAPE_INVALID", []),
    "ENGINE_CLOCK_NOT_DEFAULT-1": ("decode", "DECL_SHAPE_INVALID", []),
    "MOVE_DISPOSITION_REQUIRED-1": ("decode", "DECL_SHAPE_INVALID", []),
    "MOVE_LEAVE_NOT_ADMITTED-1": ("decode", "DECL_SHAPE_INVALID", []),
    # validate
    "TRAIT_POLICY_CONFLICT-1": ("validate", "TRAIT_POLICY_CONFLICT", []),
    "TRAIT_WIDENED-1": ("validate", "TRAIT_WIDENED", []),
    "ID_DUPLICATED-1": ("validate", "ID_DUPLICATED", []),
    "ID_DUPLICATED-2": ("validate", "ID_DUPLICATED", []),
    "ID_RESERVED-1": ("validate", "ID_RESERVED", [("resource User \"u\" { lifecycle mutable }", "resource User \"u\" { use nickname lifecycle mutable }")]),
    "TERM_RENAMED-1": ("validate", "TERM_UNKNOWN", []),
    "QUESTION_INTENT_RETIRED-1": ("validate", "QUESTION_INTENT_RETIRED", [("    show nickname\n", "    show nickname\n    live bounded 10\n")]),
    "RETIRE_REASON_REQUIRED-1": ("validate", "RETIRE_REASON_REQUIRED", []),
    "ASSOCIATION_ARITY-1": ("validate", "ASSOCIATION_ARITY", []),
    "VERB_INPUT_ENGINE_OWNED-1": ("validate", "VERB_INPUT_ENGINE_OWNED", []),
    "BULK_NOT_DERIVED_VERB-1": ("validate", "BULK_NOT_DERIVED_VERB", [("question q of User \"q\" { show x }", "intent x : Text \"x\"\n  resource V \"v\" { use x }\n  question q of User \"q\" { show identity live bounded 10 }")]),
    "QUARANTINE_RETENTION_REQUIRED-1": ("validate", "QUARANTINE_RETENTION_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource R \"r\" { use nm { key } } trait Owned \"o\" { link owner -> R { end restrict scopes } } }\nworld W \"w\" {\n  modules m"), ("requires Owned\n  scope Owned.owner", "requires m.Owned exempt m.R\n  scope m.Owned.owner")]),
    "TRAIT_REQUIRED-1": ("validate", "TRAIT_REQUIRED", [("module m \"no owned\" {\n  resource Widget \"w\" { lifecycle mutable }\n}", "module m \"no owned\" {\n  intent nm : Text \"n\"\n  resource R \"r\" { use nm { key } }\n  trait Owned \"o\" { link owner -> R { end restrict scopes } }\n  resource Widget \"w\" { lifecycle mutable }\n}"), ("requires Owned\n  scope Owned.owner", "requires m.Owned exempt m.R\n  scope m.Owned.owner")]),
    "SCOPE_ROOT_NOT_SCOPED-1": ("validate", "SCOPE_ROOT_NOT_SCOPED", []),
    "SCOPE_LINK_NOT_ROOT-1": ("validate", "SCOPE_LINK_NOT_ROOT", []),
    "SCOPE_PATH_AMBIGUOUS-1": ("validate", "SCOPE_PATH_AMBIGUOUS", []),
    "MODULE_CYCLE-1": ("validate", "MODULE_CYCLE", []),
    "MODULE_NOT_LISTED-1": ("validate", "MODULE_NOT_LISTED", [("generated python\n  quarantine_retention 3", "generated python\n  scope deployment\n  quarantine_retention 3")]),
    "DETACH_NOT_OPTIONAL-1": ("validate", "DETACH_NOT_OPTIONAL", []),
    "OPTIONAL_PARAM_UNGUARDED-1": ("validate", "OPTIONAL_PARAM_UNGUARDED", [("    show n\n", "    show n\n    live bounded 10\n")]),
    "TERM_TO_MANY_UNQUANTIFIED-1": ("validate", "TERM_TO_MANY_UNQUANTIFIED", [("    where clients.n = \"a\"\n    show x\n", "    where clients.n = \"a\"\n    show identity\n    live bounded 10\n"), ("module m \"to-many\" {\n", "module m \"to-many\" {\n  intent n : Text \"n\"\n"), ("  resource Client \"c\" {\n", "  resource Client \"c\" {\n    use n\n")]),
    "EXPR_TYPE-1": ("validate", "EXPR_TYPE", [("    show n\n", "    show n\n    live bounded 10\n")]),
    "EXPR_TYPE-2": ("validate", "EXPR_TYPE", [("    where status = \"available\"\n", "    where status = \"available\"\n    live bounded 10\n")]),
    "TERM_UNKNOWN-1": ("validate", "TERM_UNKNOWN", [("    show nope\n", "    show nope\n    live bounded 10\n")]),
    "QUESTION_COMPOSE_PAGED-1": ("validate", "QUESTION_COMPOSE_PAGED", [("    with_total\n    show x\n", "    with_total\n    show identity\n    live bounded 10\n"), ("    where x within paged\n    show x\n", "    where identity within paged\n    show identity\n    live bounded 10\n")]),
    "QUESTION_COMPOSE_UNSCOPED-1": ("validate", "QUESTION_COMPOSE_UNSCOPED", [("    unscoped audit\n    show x\n", "    unscoped audit\n    show identity\n    live bounded 10\n"), ("    where x within uq\n    show x\n", "    where identity within uq\n    show identity\n    live bounded 10\n")]),
    "QUESTION_CLOCK_NOT_A_TERM-1": ("validate", "QUESTION_CLOCK_NOT_A_TERM", [("    show created_at\n", "    show created_at\n    live bounded 10\n")]),
    "ENGINE_LOWERING_ABSENT-1": ("validate", "ENGINE_LOWERING_ABSENT", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "ENGINE_REQUIRED-1": ("validate", "ENGINE_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "DEPLOYMENT_LOCATION_REQUIRED-1": ("validate", "DEPLOYMENT_LOCATION_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "SHIP_MODE_REQUIRED-1": ("validate", "SHIP_MODE_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "DEPLOYMENT_MODE_REQUIRED-1": ("validate", "DEPLOYMENT_MODE_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "DEPLOYMENT_SNAPSHOT_REQUIRED-1": ("validate", "DEPLOYMENT_SNAPSHOT_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m"), ("requires X\n  scope X.y", "scope deployment")]),
    "USE_DUPLICATED-1": ("validate", "USE_DUPLICATED", []),
    "STEP_NAME_DUPLICATED-1": ("validate", "STEP_NAME_DUPLICATED", []),
    "INTENT_HOMELESS-1": ("validate", "INTENT_HOMELESS", []),
    "LINK_CYCLE_UNMINTABLE-1": ("validate", "LINK_CYCLE_UNMINTABLE", []),
    "STEP_CYCLE-1": ("validate", "STEP_CYCLE", [("resource User \"u\" { lifecycle mutable }", "resource User \"u\" { lifecycle mutable link owner -> User { optional end detach } }")]),
    "STEP_REFERENCE_UNRESOLVED-1": ("validate", "STEP_REFERENCE_UNRESOLVED", [("resource User \"u\" { lifecycle mutable }", "resource User \"u\" { lifecycle mutable link owner -> User { optional end detach } }")]),
    "STEP_BIND_TYPE-1": ("validate", "STEP_BIND_TYPE", [("resource Client \"c\" { lifecycle mutable }", "resource Client \"c\" { lifecycle mutable link owner -> Client { optional end detach } }")]),
    "FAMILY_MEMBER_MINT_ONLY-1": ("validate", "FAMILY_MEMBER_MINT_ONLY", []),
    "PRESET_CONFLICT-1": ("validate", "PRESET_CONFLICT", []),
    "EL2_DEAD-1": ("validate", "INTENT_HOMELESS", []),
    "U16_ESCAPE-1": ("validate", "WORLD_UNKNOWN", []),
    "U17_INCOMPLETE-1": ("validate", "WORLD_SCOPE_REQUIRED", [("world W \"w\" {\n  modules m", "module m \"m\" { intent nm : Text \"n\" resource X \"x\" { use nm { key } } }\nworld W \"w\" {\n  modules m")]),
    "U18_COLLIDE-1": ("validate", "WORLD_MODULE_COLLISION", [("requires X\n  scope X.y", "scope deployment"), ("requires X\n  scope X.y", "scope deployment")]),
    "CLOSED_SET_MEMBER_UNKNOWN-1": ("validate", "CLOSED_SET_MEMBER_UNKNOWN", [("    where status = @availble\n", "    where status = @availble\n    live bounded 10\n")]),
    "BULK_PARAM_UNDECLARED-1": ("validate", "BULK_PARAM_UNDECLARED", [("question with_kind of A \"by kind\" { given k : DisplayName where kind = k }", "query with_kind of A \"by kind\" { given k : DisplayName where kind = k }"), ("@regex:\\bkind\\b", "sort")]),
    "ALIAS_NOT_DERIVED-1": ("validate", "ALIAS_NOT_DERIVED", [("question all_a of A \"all\" { }", "question all_a of A \"all\" { live bounded 10 }")]),
    "NAME_NOT_IMPORTED-1": ("validate", "NAME_NOT_IMPORTED", []),
    "NAME_NOT_IMPORTED-2": ("validate", "NAME_NOT_IMPORTED", [("generated python quarantine_retention 3", "generated python scope deployment quarantine_retention 3")]),
    "IMPORT_UNKNOWN-1": ("validate", "IMPORT_UNKNOWN", [("generated python quarantine_retention 3", "generated python scope deployment quarantine_retention 3")]),
    "IMPORT_NOT_OWNER-1": ("validate", "IMPORT_NOT_OWNER", [("generated python quarantine_retention 3", "generated python scope deployment quarantine_retention 3")]),
    "IMPORT_UNUSED-1": ("validate", "IMPORT_UNUSED", [("generated python quarantine_retention 3", "generated python scope deployment quarantine_retention 3"), ("intent email : Email \"an address\"\n}", "intent email : Email \"an address\"\n  resource A \"a\" { use email }\n}")]),
    "IMPORT_AMBIGUOUS-1": ("validate", "IMPORT_AMBIGUOUS", [("generated python quarantine_retention 3", "generated python scope deployment quarantine_retention 3")]),
    "CAPABILITY_UNKNOWN-1": ("validate", "CAPABILITY_UNKNOWN", [("{ unscoped practice_audit }", "{ show identity unscoped practice_audit live bounded 10 }")]),
    "SET_ABSENT_REQUIRED-1": ("validate", "SET_ABSENT_REQUIRED", [("question with_kind of A \"by kind\" { given k : DisplayName where kind = k }", "query with_kind of A \"by kind\" { given k : DisplayName where kind = k }"), ("@regex:\\bkind\\b", "sort")]),
    "OPAQUE_COMPARED-1": ("validate", "OPAQUE_COMPARED", [("    where blob = \"x\"\n", "    where blob = \"x\"\n    live bounded 10\n")]),
    "SCOPE_PATH_TO_EXEMPT-1": ("validate", "SCOPE_PATH_TO_EXEMPT", []),
}

NEW_MUTANTS: dict[str, tuple[str, str, str]] = {
    "CALL_UNKNOWN-1": ("validate", "CALL_UNKNOWN", 'module m "unknown function" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  query q of A "q" { show call text.reverse(n) as r }\n}\n'),
    "CALL_VOLATILE-1": ("validate", "CALL_VOLATILE", 'module m "volatile function" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  query q of A "q" { show n, call clock.now() as t }\n}\n'),
    "CALL_EFFECTFUL-1": ("validate", "CALL_EFFECTFUL", 'module m "effectful function" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  query q of A "q" { where call store.purge(n) show n }\n}\n'),
    "CALL_ARITY-1": ("validate", "CALL_ARITY", 'module m "wrong arity" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  query q of A "q" { show call text.length(n, n) as l }\n}\n'),
    "CALL_ARGUMENT_TYPE-1": ("validate", "CALL_ARGUMENT_TYPE", 'module m "wrong argument type" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { show call text.length(n) as l }\n}\n'),
    "AGGREGATE_MISUSED-1": ("validate", "AGGREGATE_MISUSED", 'module m "aggregate in where" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { where sum(n) > 3 show n }\n}\n'),
    "AGGREGATE_MISUSED-2": ("validate", "AGGREGATE_MISUSED", 'module m "ungrouped column beside an aggregate" {\n  intent n : Integer "n"\n  intent k : Text "k"\n  resource A "a" { use n use k }\n  query q of A "q" { show k, sum(n) as total }\n}\n'),
    "HAVING_WITHOUT_GROUP-1": ("validate", "HAVING_WITHOUT_GROUP", 'module m "having without grouping" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { show n having n > 3 }\n}\n'),
    "SHOW_ALIAS_REQUIRED-1": ("validate", "SHOW_ALIAS_REQUIRED", 'module m "expression column without a name" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { show n + 1 }\n}\n'),
    "DIMENSION_NOT_VECTOR-1": ("validate", "DIMENSION_NOT_VECTOR", 'module m "dimension on a text intent" {\n  intent n : Text "n" { dimension 3 }\n  resource A "a" { use n }\n}\n'),
    "DIMENSION_NOT_POSITIVE-1": ("validate", "DIMENSION_NOT_POSITIVE", 'module m "zero dimension" {\n  intent v : Vector "v" { dimension 0 }\n  resource A "a" { use v }\n}\n'),
    "COMPOSE_INNER_GIVENS-1": ("validate", "COMPOSE_INNER_GIVENS", 'module m "composed read with givens" {\n  intent n : Integer "n"\n  resource P "p" { use n }\n  resource C "c" { use n link p -> P { end cascade } }\n  question big of P "big" { given floor : Integer where n > floor show identity live bounded 10 }\n  question kids of C "kids" { where p within big show identity live bounded 10 }\n}\n'),
    "GIVEN_UNUSED-1": ("validate", "GIVEN_UNUSED", 'module m "unused given" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { given floor : Integer show n }\n}\n'),
    "INVERSE_DUPLICATED-1": ("validate", "INVERSE_DUPLICATED", 'module m "two links claim one inverse" {\n  intent n : Text "n"\n  resource T "t" { use n }\n  resource A "a" { use n link t -> T { end cascade inverse things } }\n  resource B "b" { use n link t -> T { end cascade inverse things } }\n}\n'),
    "EXEMPT_REDUNDANT-1": ("validate", "EXEMPT_REDUNDANT", 'module m "exempting a carrier that carries the trait" {\n  intent n : Text "n"\n  resource R "r" { use n { key } }\n  trait Owned "o" { link owner -> R { end restrict scopes } }\n  resource A "a" { use n carry Owned }\n}\nworld W "w" { modules m durability durable writers governed generated python requires m.Owned exempt m.R, m.A scope m.Owned.owner quarantine_retention 3 }\n'),
    "WRITER_SOURCE_REQUIRED-1": ("validate", "WRITER_SOURCE_REQUIRED", 'module m "captured world without a source" {\n  intent n : Text "n"\n  resource A "a" { use n }\n}\nworld W "w" { modules m durability durable writers external_captured generated python scope deployment quarantine_retention 3 }\n'),
    "TARGET_UNKNOWN-1": ("validate", "TARGET_UNKNOWN", 'module m "unsupported target" {\n  intent n : Text "n"\n  resource A "a" { use n }\n}\nworld W "w" { modules m durability durable writers governed generated python, cobol scope deployment quarantine_retention 3 }\n'),
    "SHAPE_CONFLICT-1": ("validate", "SHAPE_CONFLICT", 'module m "one and first together" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  question q of A "q" { show n one first 3 live bounded 10 }\n}\n'),
    "PAGE_LIMIT_PAIR-1": ("validate", "PAGE_LIMIT_PAIR", 'module m "page without limit" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  question q of A "q" { given p : Integer show n page p live bounded 10 }\n}\n'),
    "RANK_WITHOUT_ORDER-1": ("validate", "RANK_WITHOUT_ORDER", 'module m "rank without order" {\n  intent n : Text "n"\n  resource A "a" { use n }\n  question q of A "q" { show n, rank live bounded 10 }\n}\n'),
    "QUANTIFIER_WITHOUT_TO_MANY-1": ("validate", "QUANTIFIER_WITHOUT_TO_MANY", 'module m "some over a scalar" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  question q of A "q" { where some n > 3 show n live bounded 10 }\n}\n'),
    "IS_NOT_LINK-1": ("validate", "IS_NOT_LINK", 'module m "is on a scalar" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  question q of A "q" { given k : Integer where n is k show n live bounded 10 }\n}\n'),
    "IN_NOT_LIST-1": ("validate", "IN_NOT_LIST", 'module m "in with a scalar given" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  question q of A "q" { given k : Integer where n in k show n live bounded 10 }\n}\n'),
    "CONTAINS_NOT_TEXT-1": ("validate", "CONTAINS_NOT_TEXT", 'module m "contains on a number" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  question q of A "q" { given k : Text where n contains k show n live bounded 10 }\n}\n'),
    "TERM_RESERVED-1": ("validate", "TERM_RESERVED", 'module m "an intent named after a language term" {\n  intent identity : Text "i"\n  resource A "a" { use identity }\n}\n'),
    "GIVEN_NAME_RESERVED-1": ("validate", "GIVEN_NAME_RESERVED", 'module m "a given named like an engine parameter" {\n  intent n : Integer "n"\n  resource A "a" { use n }\n  query q of A "q" { given _scope : Integer where n = _scope show n }\n}\nworld W "w" { modules m durability durable writers governed generated python scope deployment quarantine_retention 3 }\n'),
    "USE_FLAG_CONFLICT-1": ("validate", "USE_FLAG_CONFLICT", 'module m "a key cannot be optional" {\n  intent n : Text "n"\n  resource A "a" { use n { key optional } }\n}\n'),
    "USE_FLAG_REPEATED-1": ("validate", "USE_FLAG_REPEATED", 'module m "a flag twice" {\n  intent n : Text "n"\n  resource A "a" { use n { filter filter } }\n}\n'),
    "STAMP_NOT_INSTANT-1": ("validate", "STAMP_NOT_INSTANT", 'module m "stamping a text" {\n  intent n : Text "n"\n  resource A "a" { use n { stamp on_mint } }\n}\n'),
    "ARCHIVED_BY_INVALID-1": ("validate", "ARCHIVED_BY_INVALID", 'module m "archived_by a required use" {\n  intent at : Instant "at"\n  resource A "a" { use at lifecycle archived_by at }\n}\n'),
    "NESTED_SHOW_WITH_DISTINCT-1": ("validate", "NESTED_SHOW_WITH_DISTINCT", 'module m "distinct rows carry no identity for nested rows" {\n  intent n : Text "n"\n  resource P "p" { use n }\n  resource C "c" { use n link p -> P { end cascade inverse kids } }\n  query q of P "q" { show n, kids [n] distinct }\n}\n'),
    "INCLUDING_ARCHIVED_NOT_ARCHIVABLE-1": ("validate", "INCLUDING_ARCHIVED_NOT_ARCHIVABLE", 'module m "including_archived on a mutable carrier" {\n  intent n : Text "n"\n  resource A "a" { use n lifecycle mutable }\n  query q of A "q" { show n including_archived }\n}\n'),
}

BASE_WORLD = """module w "a small scoped world for runtime scenarios" {
  intent code : Text "code"
  intent amount : Integer "amount"
  intent note : Text "note"
  intent seen_at : Instant "seen"
  resource Root "the scope root" { use code { key } }
  trait Held "held by a root" { link holder -> Root { end restrict scopes } }
  resource Item "an item" {
    use code { key }
    use amount { filter }
    use note { optional }
    use seen_at { optional stamp on_change }
    carry Held
    invariant amount >= 0
  }
  resource Detail "a detail scoped through its item" {
    use note
    link item -> Item { end cascade inverse details }
  }
  query items_once of Item "one-shot" { where amount > 0 show code, amount }
  question items_live of Item "live" { where amount > 0 show code, amount order amount descending live bounded 2 }
  query audit of Item "unscoped" { show code unscoped auditor }
}
world W "runtime world" {
  modules w
  durability durable
  writers governed
  generated python, rust
  requires w.Held exempt w.Root
  scope w.Held.holder
  capabilities auditor
  quarantine_retention 3
}
deployment D "explicit shipping" { world W engine sqlite at memory ship explicit mode readwrite snapshot none }
"""

BASE_BINDING = {
    "schema": "garns-v9-5/storage-binding/1", "world": "W",
    "engine": {"ledger": "w_journal", "generations": "w_epochs", "revisions": "w_ticks"},
    "relations": {
        "w.Root": {"table": "anchor", "identity": "anchor_key", "columns": {"w.Root.code": "code_v"}, "links": {}},
        "w.Item": {"table": "thing", "identity": "thing_key", "columns": {"w.Item.code": "code_v", "w.Item.amount": "qty", "w.Item.note": "memo", "w.Item.seen_at": "seen"}, "links": {"w.Item.holder": "held_by"}},
        "w.Detail": {"table": "particular", "identity": "particular_key", "columns": {"w.Detail.note": "memo"}, "links": {"w.Detail.item": "of_thing"}},
    },
}

G2_RETYPE_KEY = BASE_WORLD.replace('intent code : Text "code"', 'intent code : Integer "code" { retype Text forward validate backward widen }')
G2_RENAME_UNKNOWN = BASE_WORLD.replace('intent note : Text "note"', 'intent remark : Text "note" { renamed_from nothing }').replace("use note { optional }", "use remark { optional }").replace("resource Detail \"a detail scoped through its item\" {\n    use note", "resource Detail \"a detail scoped through its item\" {\n    use remark")
G2_NO_TOMBSTONE = BASE_WORLD.replace('  intent note : Text "note"\n', "").replace("    use note { optional }\n", "").replace("resource Detail \"a detail scoped through its item\" {\n    use note\n", "resource Detail \"a detail scoped through its item\" {\n    use code\n")
G2_LIFECYCLE = BASE_WORLD.replace("    carry Held\n    invariant amount >= 0\n  }", "    carry Held\n    invariant amount >= 0\n    lifecycle archived_by seen_at\n  }")
G2_TOMB_DROP = BASE_WORLD.replace('  intent note : Text "note"\n', '  tombstone note "dropped" { data drop }\n').replace("    use note { optional }\n", "").replace("resource Detail \"a detail scoped through its item\" {\n    use note\n", "resource Detail \"a detail scoped through its item\" {\n    use amount { optional }\n")
G3_RESTORE = BASE_WORLD.replace('  intent note : Text "note"\n', '  intent note : Text "note" { restore }\n')
G2_MOVE_HOME = BASE_WORLD.replace("resource Detail \"a detail scoped through its item\" {\n    use note\n", "resource Detail \"a detail scoped through its item\" {\n    use note\n    use amount\n").replace("  query items_once", "  move_home code of Detail into Item data drop\n  query items_once")


def scenario(name: str, stage: str, code: str, steps: list[dict], extra_files: dict[str, str] | None = None, bindings: dict[str, dict] | None = None) -> None:
    d = OUT / "scenarios" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "g1").mkdir(exist_ok=True)
    (d / "g1" / "world.garns").write_text(BASE_WORLD, encoding="utf-8")
    (d / "g1" / "storage-W.json").write_text(json.dumps(BASE_BINDING, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for rel, text in (extra_files or {}).items():
        path = d / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for rel, doc in (bindings or {}).items():
        path = d / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (d / "scenario.json").write_text(json.dumps({"steps": steps}, indent=1) + "\n", encoding="utf-8")
    EXPECTED.append({"mutant": f"scenarios/{name}", "stage": stage, "code": code})


EXPECTED: list[dict] = []


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for name, (stage, code, edits) in SEED_MUTANTS.items():
        text = (SEED / f"{name}.garns").read_text(encoding="utf-8")
        for old, new in edits:
            if old.startswith("@regex:"):
                import re as _re

                text = _re.sub(old[len("@regex:"):], new, text)
                continue
            if old not in text:
                raise SystemExit(f"{name}: edit target missing: {old!r}")
            text = text.replace(old, new, 1)
        (OUT / f"{name}.garns").write_text(text, encoding="utf-8")
        EXPECTED.append({"mutant": f"{name}.garns", "stage": stage, "code": code})
    for name, (stage, code, text) in NEW_MUTANTS.items():
        (OUT / f"{name}.garns").write_text(text, encoding="utf-8")
        EXPECTED.append({"mutant": f"{name}.garns", "stage": stage, "code": code})
    bind = {"do": "bind", "source": "g1", "world": "W", "binding": "g1/storage-W.json"}
    seed_rows = {"do": "write", "ops": [
        {"verb": "mint", "carrier": "w.Root", "values": {"w.Root.code": "R1"}, "as": "r1"},
        {"verb": "mint", "carrier": "w.Item", "values": {"w.Item.code": "I1", "w.Item.amount": 5, "w.Item.holder": "$r1"}, "as": "i1"},
    ]}
    # storage-stage mutants
    missing_col = json.loads(json.dumps(BASE_BINDING)); del missing_col["relations"]["w.Item"]["columns"]["w.Item.note"]
    scenario("STORAGE_COLUMN_MISSING", "validate", "STORAGE_COLUMN_MISSING", [{"do": "bind", "source": "g1", "world": "W", "binding": "bad.json"}], bindings={"bad.json": missing_col})
    collide = json.loads(json.dumps(BASE_BINDING)); collide["relations"]["w.Detail"]["table"] = "thing"
    scenario("STORAGE_TABLE_COLLISION", "validate", "STORAGE_TABLE_COLLISION", [{"do": "bind", "source": "g1", "world": "W", "binding": "bad.json"}], bindings={"bad.json": collide})
    missing_rel = json.loads(json.dumps(BASE_BINDING)); del missing_rel["relations"]["w.Detail"]
    scenario("STORAGE_RELATION_MISSING", "validate", "STORAGE_RELATION_MISSING", [{"do": "bind", "source": "g1", "world": "W", "binding": "bad.json"}], bindings={"bad.json": missing_rel})
    colcollide = json.loads(json.dumps(BASE_BINDING)); colcollide["relations"]["w.Item"]["columns"]["w.Item.note"] = "thing_key"
    scenario("STORAGE_COLUMN_COLLISION", "validate", "STORAGE_COLUMN_COLLISION", [{"do": "bind", "source": "g1", "world": "W", "binding": "bad.json"}], bindings={"bad.json": colcollide})
    wrong_world = json.loads(json.dumps(BASE_BINDING)); wrong_world["world"] = "X"
    scenario("STORAGE_WORLD_MISMATCH", "validate", "STORAGE_WORLD_MISMATCH", [{"do": "bind", "source": "g1", "world": "W", "binding": "bad.json"}], bindings={"bad.json": wrong_world})
    scenario("WORLD_UNKNOWN_SELECTION", "validate", "WORLD_UNKNOWN", [{"do": "bind", "source": "g1", "world": "NOPE", "binding": "g1/storage-W.json"}])
    captured = BASE_WORLD.replace("writers governed", "writers external_captured\n  writer_source outside")
    scenario("WRITER_CAPTURE_INCOMPLETE_BINDING", "validate", "WRITER_CAPTURE_INCOMPLETE", [{"do": "bind", "source": "cap", "world": "W", "binding": "g1/storage-W.json"}], extra_files={"cap/world.garns": captured})
    # ship / load stage
    scenario("STORE_BEHIND", "load", "STORE_BEHIND", [bind, {"do": "ship"}, {"do": "bind", "source": "g2", "world": "W", "binding": "g1/storage-W.json"}, {"do": "open", "deployment": "D"}],
             extra_files={"g2/world.garns": BASE_WORLD.replace('intent note : Text "note"', 'intent note : Text "a changed meaning"')})
    scenario("STORE_DRIFT", "load", "STORE_DRIFT", [bind, {"do": "ship"}, {"do": "sql", "statement": "ALTER TABLE thing ADD COLUMN stray TEXT"}, {"do": "open", "deployment": "D"}])
    scenario("STORE_UNSHIPPED", "load", "STORE_UNSHIPPED", [bind, {"do": "ship"}, {"do": "sql", "statement": "DROP TABLE w_epochs"}, {"do": "open", "deployment": "D"}])
    scenario("RETYPE_KEY_EQUALITY", "ship", "RETYPE_KEY_EQUALITY", [bind, {"do": "ship"}, {"do": "classify", "source": "g2"}], extra_files={"g2/world.garns": G2_RETYPE_KEY})
    scenario("RENAME_TARGET_UNKNOWN", "ship", "RENAME_TARGET_UNKNOWN", [bind, {"do": "ship"}, {"do": "classify", "source": "g2"}], extra_files={"g2/world.garns": G2_RENAME_UNKNOWN})
    scenario("RETIREMENT_POLICY_REQUIRED", "ship", "RETIREMENT_POLICY_REQUIRED", [bind, {"do": "ship"}, {"do": "classify", "source": "g2"}], extra_files={"g2/world.garns": G2_NO_TOMBSTONE})
    scenario("ACCESSOR_BREAKING_UNACKNOWLEDGED", "ship", "ACCESSOR_BREAKING_UNACKNOWLEDGED", [bind, {"do": "ship"}, {"do": "classify", "source": "g2"}], extra_files={"g2/world.garns": G2_LIFECYCLE})
    scenario("RESTORE_DATA_UNAVAILABLE", "ship", "RESTORE_DATA_UNAVAILABLE", [bind, {"do": "ship"}, {"do": "migrate", "source": "g2", "world": "W", "binding": "g2/storage-W.json"}, {"do": "classify", "source": "g3"}],
             extra_files={"g2/world.garns": G2_TOMB_DROP, "g3/world.garns": G3_RESTORE}, bindings={"g2/storage-W.json": {**json.loads(json.dumps(BASE_BINDING)), "relations": {**json.loads(json.dumps(BASE_BINDING))["relations"], "w.Item": {"table": "thing", "identity": "thing_key", "columns": {"w.Item.code": "code_v", "w.Item.amount": "qty", "w.Item.seen_at": "seen"}, "links": {"w.Item.holder": "held_by"}}, "w.Detail": {"table": "particular", "identity": "particular_key", "columns": {"w.Detail.amount": "qty"}, "links": {"w.Detail.item": "of_thing"}}}}})
    scenario("MOVE_HOME_INCONSISTENT", "ship", "MOVE_HOME_INCONSISTENT", [bind, {"do": "ship"}, {"do": "classify", "source": "g2"}], extra_files={"g2/world.garns": G2_MOVE_HOME})
    scenario("GENERATION_OUTSIDE_WINDOW", "load", "GENERATION_OUTSIDE_WINDOW", [bind, {"do": "ship"}] + [{"do": "migrate", "source": f"g{n}", "world": "W", "binding": "g1/storage-W.json"} for n in (2, 3, 4, 5)] + [{"do": "window"}],
             extra_files={f"g{n}/world.garns": BASE_WORLD.replace('intent note : Text "note"', f'intent note : Text "meaning {n}"') for n in (2, 3, 4, 5)})
    # runtime stage
    scenario("KEY_DUPLICATED", "runtime", "KEY_DUPLICATED", [bind, {"do": "ship"}, seed_rows, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Item", "values": {"w.Item.code": "I1", "w.Item.amount": 1, "w.Item.holder": 1}}]}])
    scenario("VERB_INPUT_REQUIRED", "runtime", "VERB_INPUT_REQUIRED", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Root", "values": {}}]}])
    scenario("VERB_INPUT_ENGINE_OWNED", "runtime", "VERB_INPUT_ENGINE_OWNED", [bind, {"do": "ship"}, seed_rows, {"do": "write", "ops": [{"verb": "change", "carrier": "w.Item", "identity": "$i1", "values": {"w.Item.seen_at": 5}}]}])
    scenario("LEDGER_WRITER_UNKNOWN", "runtime", "LEDGER_WRITER_UNKNOWN", [bind, {"do": "ship"}, {"do": "write", "writer": "stranger", "ops": []}])
    scenario("LEDGER_TRANSACTION_INVALID", "runtime", "LEDGER_TRANSACTION_INVALID", [bind, {"do": "ship"}, {"do": "write", "transaction": "", "ops": []}])
    scenario("LEDGER_FIELD_UNKNOWN", "runtime", "LEDGER_FIELD_UNKNOWN", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Root", "values": {"w.Root.colour": "red"}}]}])
    scenario("LEDGER_CARRIER_UNKNOWN", "runtime", "LEDGER_CARRIER_UNKNOWN", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Ghost", "values": {}}]}])
    scenario("LEDGER_SCOPE_UNKNOWN", "runtime", "LEDGER_SCOPE_UNKNOWN", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Item", "values": {"w.Item.code": "I9", "w.Item.amount": 1, "w.Item.holder": 999}}]}])
    scenario("LEDGER_VALUE_TYPE", "runtime", "LEDGER_VALUE_TYPE", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "mint", "carrier": "w.Root", "values": {"w.Root.code": 42}}]}])
    scenario("INVARIANT_VIOLATED", "runtime", "INVARIANT_VIOLATED", [bind, {"do": "ship"}, seed_rows, {"do": "write", "ops": [{"verb": "change", "carrier": "w.Item", "identity": "$i1", "values": {"w.Item.amount": -1}}]}])
    scenario("SCOPE_REQUIRED", "runtime", "SCOPE_REQUIRED", [bind, {"do": "ship"}, {"do": "execute", "read": "w.items_once"}])
    scenario("CAPABILITY_REQUIRED", "runtime", "CAPABILITY_REQUIRED", [bind, {"do": "ship"}, {"do": "execute", "read": "w.audit"}])
    scenario("PARAM_UNKNOWN", "runtime", "PARAM_UNKNOWN", [bind, {"do": "ship"}, seed_rows, {"do": "execute", "read": "w.items_once", "params": {"nope": 1}, "scope": "$r1"}])
    scenario("READ_UNKNOWN_SELECTION", "runtime", "READ_UNKNOWN", [bind, {"do": "ship"}, {"do": "execute", "read": "w.nothing"}])
    scenario("QUERY_NOT_LIVE", "runtime", "QUERY_NOT_LIVE", [bind, {"do": "ship"}, seed_rows, {"do": "subscribe", "read": "w.items_once", "scope": "$r1"}])
    scenario("LIVE_BOUND_EXCEEDED", "runtime", "LIVE_BOUND_EXCEEDED", [bind, {"do": "ship"}, seed_rows, {"do": "write", "ops": [
        {"verb": "mint", "carrier": "w.Item", "values": {"w.Item.code": "I2", "w.Item.amount": 6, "w.Item.holder": "$r1"}},
        {"verb": "mint", "carrier": "w.Item", "values": {"w.Item.code": "I3", "w.Item.amount": 7, "w.Item.holder": "$r1"}}]}, {"do": "subscribe", "read": "w.items_live", "scope": "$r1"}])
    scenario("CAPTURE_NOT_DECLARED", "runtime", "CAPTURE_NOT_DECLARED", [bind, {"do": "ship"}, {"do": "capture"}])
    scenario("IDENTITY_UNKNOWN", "runtime", "IDENTITY_UNKNOWN", [bind, {"do": "ship"}, {"do": "write", "ops": [{"verb": "delete", "carrier": "w.Root", "identity": 77}]}])
    # a recognised engine without a lowering refuses at bind (resolve), so ship/write never execute
    scenario("ENGINE_LOWERING_ABSENT", "validate", "ENGINE_LOWERING_ABSENT",
             [{"do": "bind", "source": "pg", "world": "W", "binding": "g1/storage-W.json"}, {"do": "ship"}, seed_rows],
             extra_files={"pg/world.garns": BASE_WORLD.replace("engine sqlite", "engine postgres")})
    # a scenario that must be accepted end to end (control)
    scenario("ACCEPTED_CONTROL", "accepted", "ACCEPTED", [bind, {"do": "lower"}, {"do": "generate"}, {"do": "ship"}, seed_rows, {"do": "execute", "read": "w.items_once", "scope": "$r1"}, {"do": "subscribe", "read": "w.items_live", "scope": "$r1"}, {"do": "open", "deployment": "D"}])
    (OUT / "expected.json").write_text(json.dumps({"schema": "garns-v9-5/mutant-expectations/1", "note": "authored assertions; never read by the runner", "cases": EXPECTED}, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(EXPECTED)} mutant expectations into {OUT}")


if __name__ == "__main__":
    main()
