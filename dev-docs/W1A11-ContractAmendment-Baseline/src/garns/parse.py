"""Parsing: frozen grammar -> located source nodes.

Decode refusals are classified from the parser state at the point of failure
(open declaration bodies, expression context, expected terminals). No text
pattern, filename, comment, or marker takes part in classification.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from lark import Lark, Token, Tree
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedInput, UnexpectedToken

from . import ast as A
from .refuse import Refusal

BUILD_ROOT = Path(__file__).resolve().parents[2]
GRAMMAR_PATH = BUILD_ROOT / "grammar" / "garns.lark"

_PARSER: Lark | None = None


def grammar_text() -> str:
    return GRAMMAR_PATH.read_text(encoding="utf-8")


def parser() -> Lark:
    global _PARSER
    if _PARSER is None:
        _PARSER = Lark(
            grammar_text(),
            parser="lalr",
            propagate_positions=True,
            maybe_placeholders=False,
            keep_all_tokens=True,
        )
    return _PARSER


# --- decode classification ---------------------------------------------------

_EXPR_KEYWORDS = {"WHERE", "HAVING", "INVARIANT"}
_ITEM_TREES = {"q_item", "query_item", "carrier_item", "member_item", "intent_item", "world_item", "dep_item"}
_STRING_NOT_MEANING = {"PATTERN", "BREAKING", "PATH", "DEFAULT"}
_TYPE_LEAD = {"COLON", "OPTIONAL", "LIST_OF", "OF"}


def _stack_of(exc: UnexpectedInput) -> list[object]:
    ip = getattr(exc, "interactive_parser", None)
    if ip is None:
        return []
    try:
        return list(ip.parser_state.value_stack)
    except Exception:  # pragma: no cover - defensive
        return []


def _expected_of(exc: UnexpectedInput) -> set[str]:
    for attr in ("expected", "allowed"):
        got = getattr(exc, attr, None)
        if got:
            return set(got)
    return set()


def classify_decode(exc: UnexpectedInput, file: str) -> Refusal:
    line = int(getattr(exc, "line", 1) or 1)
    column = int(getattr(exc, "column", 1) or 1)
    stack = _stack_of(exc)
    expected = _expected_of(exc)
    token = getattr(exc, "token", None)

    if isinstance(exc, UnexpectedEOF) or (isinstance(token, Token) and token.type == "$END"):
        return Refusal("SOURCE_TRUNCATED", "decode", file, line, column, "source ends inside an open construct")

    # Tokens after the innermost open body brace describe the current item.
    last_brace = -1
    for index, item in enumerate(stack):
        if isinstance(item, Token) and item.type == "LBRACE":
            last_brace = index
    tail = stack[last_brace + 1 :]
    tail_tokens = [t for t in tail if isinstance(t, Token)]
    tail_types = [t.type for t in tail_tokens]
    depth = sum(1 for item in stack if isinstance(item, Token) and item.type == "LBRACE")

    if expected == {"STRING"}:
        previous = tail_types[-1] if tail_types else ""
        if previous not in _STRING_NOT_MEANING:
            return Refusal("MEANS_REQUIRED", "decode", file, line, column, "a declaration states its meaning as a string")
        return Refusal("DECL_SHAPE_INVALID", "decode", file, line, column, "string required here")

    if tail_types and tail_types[-1] in _TYPE_LEAD and expected <= {"NAME", "OPTIONAL", "LIST_OF"}:
        return Refusal("TYPE_SHAPE_INVALID", "decode", file, line, column, "type reference is optional? list_of? NAME")

    if depth > 0:
        # Expression context: an expression keyword opened the current item and no
        # later item has been completed.
        for item in reversed(tail):
            if isinstance(item, Tree) and item.data in _ITEM_TREES:
                break
            if isinstance(item, Token) and item.type in _EXPR_KEYWORDS:
                return Refusal("EXPR_NOT_ADMITTED", "decode", file, line, column, "expression is outside the closed algebra")
        return Refusal("DECL_SHAPE_INVALID", "decode", file, line, column, "declaration shape is not admitted by the grammar")

    if all(isinstance(item, Tree) for item in stack):
        return Refusal("SOURCE_NOT_GARNS", "decode", file, line, column, "text is not a Garns top-level declaration")
    return Refusal("DECL_SHAPE_INVALID", "decode", file, line, column, "top-level declaration shape is not admitted")


# --- AST construction --------------------------------------------------------


def _loc(node: Tree | Token, file: str) -> A.Loc:
    if isinstance(node, Token):
        return A.Loc(file, int(node.line or 1), int(node.column or 1))
    meta = node.meta
    if getattr(meta, "empty", False) or getattr(meta, "line", None) is None:
        return A.Loc(file, 1, 1)
    return A.Loc(file, int(meta.line), int(meta.column))


class _Builder:
    def __init__(self, file: str, text: str) -> None:
        self.file = file
        self.text = text
        self.names: list[A.Name] = []

    # -- helpers
    def L(self, node: Tree | Token) -> A.Loc:
        return _loc(node, self.file)

    def name(self, tok: Token) -> A.Name:
        n = A.Name(str(tok.value), self.L(tok))
        self.names.append(n)
        return n

    @staticmethod
    def toks(tree: Tree) -> list[Token]:
        return [c for c in tree.children if isinstance(c, Token)]

    @staticmethod
    def trees(tree: Tree) -> list[Tree]:
        return [c for c in tree.children if isinstance(c, Tree)]

    @staticmethod
    def tree(tree: Tree, data: str) -> Tree | None:
        for c in tree.children:
            if isinstance(c, Tree) and c.data == data:
                return c
        return None

    @staticmethod
    def has(tree: Tree, ttype: str) -> bool:
        return any(isinstance(c, Token) and c.type == ttype for c in tree.children)

    @staticmethod
    def tok(tree: Tree, ttype: str) -> Token | None:
        for c in tree.children:
            if isinstance(c, Token) and c.type == ttype:
                return c
        return None

    def string(self, tok: Token) -> str:
        raw = str(tok.value)
        return bytes(raw[1:-1], "utf-8").decode("unicode_escape")

    def qname(self, tree: Tree) -> A.QName:
        parts = tuple(self.name(t) for t in self.toks(tree) if t.type == "NAME")
        return A.QName(parts, self.L(tree))

    def path(self, tree: Tree) -> A.PathNode:
        return A.PathNode(tuple(self.name(t) for t in self.toks(tree) if t.type == "NAME"), self.L(tree))

    def type_ref(self, tree: Tree) -> A.TypeRefNode:
        optional = self.has(tree, "OPTIONAL")
        inner = self.tree(tree, "opt_inner")
        source = inner if inner is not None else tree
        list_of = self.has(source, "LIST_OF")
        nm = self.tok(source, "NAME")
        assert nm is not None
        return A.TypeRefNode(self.name(nm), optional, list_of, self.L(tree))

    def literal(self, tree: Tree) -> A.LiteralNode:
        tok = self.toks(tree)[0]
        loc = self.L(tok)
        if tok.type == "STRING":
            return A.LiteralNode("string", self.string(tok), loc)
        if tok.type == "INT":
            return A.LiteralNode("int", int(tok.value), loc)
        if tok.type == "CTOR":
            return A.LiteralNode("ctor", str(tok.value), loc)
        if tok.type == "TRUE":
            return A.LiteralNode("bool", True, loc)
        if tok.type == "FALSE":
            return A.LiteralNode("bool", False, loc)
        raise AssertionError(f"literal token {tok.type}")

    def value(self, node: Tree) -> A.DynValue:
        if node.data == "path_expr":
            return self.path(node)
        if node.data == "literal":
            return self.literal(node)
        if node.data == "clock":
            return A.ClockNode(self.L(node))
        raise AssertionError(f"value {node.data}")

    def repair_val(self, tree: Tree) -> object:
        if self.has(tree, "SHIP_CLOCK"):
            return "ship_clock"
        if self.has(tree, "QUARANTINE"):
            return "quarantine"
        lit = self.tree(tree, "literal")
        assert lit is not None
        return self.literal(lit)

    def default_val(self, tree: Tree) -> object:
        if self.has(tree, "SHIP_CLOCK"):
            return "ship_clock"
        lit = self.tree(tree, "literal")
        assert lit is not None
        return self.literal(lit)

    # -- dynamic expressions
    def dyn(self, node: Tree) -> A.DynExpr:
        d = node.data
        if d == "or_expr":
            return A.OrNode(tuple(self.dyn(c) for c in self.trees(node)), self.L(node))
        if d == "and_expr":
            return A.AndNode(tuple(self.dyn(c) for c in self.trees(node)), self.L(node))
        if d == "not_expr":
            return A.NotNode(self.dyn(self.trees(node)[0]), self.L(node))
        if d == "atom_expr":
            if self.has(node, "SOME") or self.has(node, "EVERY"):
                kind = "some" if self.has(node, "SOME") else "every"
                return A.QuantNode(kind, self.dyn(self.trees(node)[0]), self.L(node))
            return self.dyn(self.trees(node)[0])  # parenthesised
        if d == "comparison":
            return self.comparison(node)
        raise AssertionError(f"dyn {d}")

    def agg(self, node: Tree) -> A.AggNode:
        subtrees = self.trees(node)
        path = self.path(subtrees[0])
        fn = "count" if self.has(node, "COUNT") else ("max" if self.has(node, "MAX") else "min")
        arg: A.DynExpr | A.PathNode | None = None
        if len(subtrees) > 1:
            inner = subtrees[1]
            arg = self.path(inner) if (fn != "count" and inner.data == "path_expr") else self.dyn(inner)
        return A.AggNode(path, fn, arg, self.L(node))

    def comparison(self, node: Tree) -> A.DynExpr:
        loc = self.L(node)
        guard = self.tree(node, "given_guard") is not None
        subtrees = [c for c in self.trees(node) if c.data != "given_guard"]
        if self.has(node, "WITHIN"):
            return A.WithinNode(self.path(subtrees[0]), self.path(subtrees[1]), loc)
        if self.has(node, "PRESENT"):
            return A.PresenceNode(self.path(subtrees[0]), True, guard, loc)
        if self.has(node, "ABSENT"):
            return A.PresenceNode(self.path(subtrees[0]), False, guard, loc)
        if self.has(node, "CONTAINS"):
            return A.ContainsNode(self.path(subtrees[0]), self.value(subtrees[1]), guard, loc)
        if self.has(node, "IN"):
            return A.InNode(self.path(subtrees[0]), self.value(subtrees[1]), guard, loc)
        if self.has(node, "IS"):
            return A.IsNode(self.path(subtrees[0]), self.value(subtrees[1]), guard, loc)
        first = subtrees[0]
        op_tree = self.tree(node, "cmp_op")
        assert op_tree is not None
        op = str(self.toks(op_tree)[0].value)
        left: A.PathNode | A.AggNode = self.agg(first) if first.data == "agg_expr" else self.path(first)
        right_tree = [c for c in subtrees if c is not first and c.data != "cmp_op"][0]
        return A.CmpNode(left, op, self.value(right_tree), guard, loc)

    # -- static expressions
    def static(self, node: Tree) -> A.StaticExpr:
        d = node.data
        if d == "query_or":
            return A.SOrNode(tuple(self.static(c) for c in self.trees(node)), self.L(node))
        if d == "query_and":
            return A.SAndNode(tuple(self.static(c) for c in self.trees(node)), self.L(node))
        if d == "query_not":
            if self.has(node, "NOT"):
                return A.SNotNode(self.static(self.trees(node)[0]), self.L(node))
            return self.static(self.trees(node)[0])
        if d == "query_predicate":
            return self.static_predicate(node)
        return self.scalar(node)

    def static_predicate(self, node: Tree) -> A.StaticExpr:
        loc = self.L(node)
        subtrees = self.trees(node)
        if self.has(node, "PRESENT"):
            return A.SPresenceNode(self.path(subtrees[0]), True, loc)
        if self.has(node, "ABSENT"):
            return A.SPresenceNode(self.path(subtrees[0]), False, loc)
        if self.has(node, "WITHIN"):
            return A.SWithinNode(self.path(subtrees[0]), self.qname(subtrees[1]), loc)
        for kw, op in (("CONTAINS", "contains"), ("IN", "in"), ("IS", "is")):
            if self.has(node, kw):
                return A.SCmpNode(self.scalar(subtrees[0]), op, self.scalar(subtrees[1]), loc)
        op_tree = self.tree(node, "cmp_op")
        assert op_tree is not None
        operands = [c for c in subtrees if c.data != "cmp_op"]
        return A.SCmpNode(self.scalar(operands[0]), str(self.toks(op_tree)[0].value), self.scalar(operands[1]), loc)

    def scalar(self, node: Tree) -> A.StaticScalar:
        d = node.data
        loc = self.L(node)
        if d == "path_expr":
            return self.path(node)
        if d == "literal":
            return self.literal(node)
        if d == "clock":
            return A.ClockNode(loc)
        if d in ("query_sum", "query_product"):
            children = list(node.children)
            result = self.scalar(children[0])
            index = 1
            while index < len(children):
                op = str(children[index].value)
                rhs = self.scalar(children[index + 1])
                result = A.SBinaryNode(op, result, rhs, self.L(children[index]))
                index += 2
            return result
        if d == "query_unary":
            op = str(self.toks(node)[0].value)
            return A.SUnaryNode(op, self.scalar(self.trees(node)[0]), loc)
        if d == "query_primary":
            return self.scalar(self.trees(node)[0])  # parenthesised scalar
        if d == "query_aggregate":
            fn = str(self.toks(node)[0].value)
            distinct = self.has(node, "DISTINCT")
            path_tree = self.tree(node, "path_expr")
            return A.SAggregateNode(fn, distinct, self.path(path_tree) if path_tree is not None else None, loc)
        if d == "query_call":
            qn = self.qname(self.tree(node, "qname"))  # type: ignore[arg-type]
            args_tree = self.tree(node, "query_arg_list")
            args = tuple(self.scalar(c) for c in self.trees(args_tree)) if args_tree is not None else ()
            return A.SCallNode(qn, args, loc)
        if d in ("query_predicate", "query_or", "query_and", "query_not"):
            raise AssertionError("predicate where scalar expected")
        raise AssertionError(f"scalar {d}")

    # -- shows / orders
    def show_list(self, tree: Tree, static: bool) -> tuple[A.ShowItemNode, ...]:
        return tuple(self.show_item(c, static) for c in self.trees(tree))

    def show_item(self, item: Tree, static: bool) -> A.ShowItemNode:
        loc = self.L(item)
        alias: A.Name | None = None
        toks = self.toks(item)
        if any(t.type == "AS" for t in toks):
            alias = self.name([t for t in toks if t.type == "NAME"][-1])
        value: A.ShowValue
        first = item.children[0]
        if isinstance(first, Token):
            if first.type == "IDENTITY":
                value = A.IdentityShow(self.L(first))
            elif first.type == "RANK":
                value = A.RankShow(self.L(first))
            else:
                raise AssertionError(f"show token {first.type}")
        else:
            value = self.show_value(first, static)
        return A.ShowItemNode(value, alias, loc)

    def show_value(self, node: Tree, static: bool) -> A.ShowValue:
        loc = self.L(node)
        if node.data in ("show_value", "query_show_value"):
            if self.has(node, "COUNT"):
                return A.CountShow(loc)
            path_tree = self.tree(node, "path_expr")
            assert path_tree is not None
            inner = self.tree(node, "show_list") or self.tree(node, "query_show_list")
            assert inner is not None
            last = None
            if self.has(node, "LAST"):
                last = int(self.tok(node, "INT").value)  # type: ignore[union-attr]
            return A.NestedShow(self.path(path_tree), self.show_list(inner, static), last, loc)
        if node.data == "path_expr":
            return A.PathShow(self.path(node), loc)
        if static:
            return A.ScalarShow(self.scalar(node), loc)
        raise AssertionError(f"show value {node.data}")

    def order_list(self, tree: Tree, static: bool) -> tuple[A.OrderItemNode, ...]:
        out = []
        for item in self.trees(tree):
            direction_tree = self.tree(item, "direction")
            direction = str(self.toks(direction_tree)[0].value) if direction_tree is not None else None
            key_tree = [c for c in self.trees(item) if c.data != "direction"][0]
            key: A.PathNode | A.StaticScalar = self.scalar(key_tree) if static else self.path(key_tree)
            out.append(A.OrderItemNode(key, direction, self.L(item)))
        return tuple(out)

    # -- read declarations
    def given(self, tree: Tree) -> A.GivenItem:
        nm = self.tok(tree, "NAME")
        assert nm is not None
        tr = self.tree(tree, "type_ref")
        assert tr is not None
        lit = self.tree(tree, "literal")
        return A.GivenItem(self.name(nm), self.type_ref(tr), self.literal(lit) if lit is not None else None, self.L(tree))

    def read_item(self, item: Tree, static: bool) -> A.ReadItem:
        loc = self.L(item)
        first = item.children[0]
        if isinstance(first, Tree):
            assert first.data == "given_item"
            return self.given(first)
        kw = first.type
        subtrees = self.trees(item)
        if kw == "WHERE":
            return A.WhereItem(self.static(subtrees[0]) if static else self.dyn(subtrees[0]), loc)
        if kw == "SHOW":
            return A.ShowListItem(self.show_list(subtrees[0], static), loc)
        if kw == "ORDER":
            return A.OrderListItem(self.order_list(subtrees[0], static), loc)
        if kw == "PAGE":
            return A.PageItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        if kw == "LIMIT":
            return A.LimitItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        if kw == "WITH_TOTAL":
            return A.WithTotalItem(loc)
        if kw == "LIVE":
            return A.LiveItem(int(self.tok(item, "INT").value), loc)  # type: ignore[union-attr]
        if kw == "INCLUDING_ARCHIVED":
            return A.IncludingArchivedItem(loc)
        if kw == "UNSCOPED":
            return A.UnscopedItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        if kw == "BY":
            return A.ByItem(self.path(subtrees[0]), loc)
        if kw == "ONE":
            return A.OneItem(loc)
        if kw == "DISTINCT":
            return A.DistinctItem(loc)
        if kw == "GROUP":
            return A.GroupByItem(tuple(self.path(p) for p in self.trees(subtrees[0])), loc)
        if kw == "HAVING":
            return A.HavingItem(self.static(subtrees[0]), loc)
        if kw == "FIRST":
            return A.FirstItem(int(self.tok(item, "INT").value), loc)  # type: ignore[union-attr]
        raise AssertionError(f"read item {kw}")

    def read_decl(self, node: Tree, noun: str) -> A.ReadDecl:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        static = noun == "query"
        items = tuple(self.read_item(c, static) for c in self.trees(node))
        return A.ReadDecl(noun, self.name(names[0]), self.name(names[1]), meaning, items, self.L(node))

    # -- carriers
    def use_stmt(self, node: Tree) -> A.UseStmt:
        nm = self.tok(node, "NAME")
        assert nm is not None
        flags: list[A.UseFlag] = []
        body = self.tree(node, "use_body")
        if body is not None:
            for flag in self.trees(body):
                loc = self.L(flag)
                if self.has(flag, "STAMP"):
                    when = str(self.toks(self.tree(flag, "stamp_when"))[0].value)  # type: ignore[arg-type]
                    flags.append(A.UseFlag("stamp", when, loc))
                elif self.has(flag, "DEFAULT"):
                    flags.append(A.UseFlag("default", self.default_val(self.tree(flag, "default_val")), loc))  # type: ignore[arg-type]
                elif self.has(flag, "REPAIR"):
                    flags.append(A.UseFlag("repair", self.repair_val(self.tree(flag, "repair_val")), loc))  # type: ignore[arg-type]
                else:
                    flags.append(A.UseFlag(str(self.toks(flag)[0].value), None, loc))
        return A.UseStmt(self.name(nm), tuple(flags), self.L(node))

    def link_stmt(self, node: Tree) -> A.LinkStmt:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        flags: list[A.LinkFlag] = []
        body = self.tree(node, "link_body")
        if body is not None:
            for flag in self.trees(body):
                loc = self.L(flag)
                if self.has(flag, "END"):
                    end_tree = self.tree(flag, "end_kind")
                    flags.append(A.LinkFlag("end", str(self.toks(end_tree)[0].value), loc))  # type: ignore[arg-type]
                elif self.has(flag, "INVERSE"):
                    flags.append(A.LinkFlag("inverse", self.name(self.tok(flag, "NAME")), loc))  # type: ignore[arg-type]
                elif self.has(flag, "DEFAULT"):
                    flags.append(A.LinkFlag("default", self.default_val(self.tree(flag, "default_val")), loc))  # type: ignore[arg-type]
                else:
                    flags.append(A.LinkFlag(str(self.toks(flag)[0].value), None, loc))
        return A.LinkStmt(self.name(names[0]), self.name(names[1]), tuple(flags), self.L(node))

    def carrier_item(self, item: Tree) -> A.CarrierItem:
        loc = self.L(item)
        first = item.children[0]
        if isinstance(first, Tree):
            if first.data == "use_stmt":
                return self.use_stmt(first)
            if first.data == "link_stmt":
                return self.link_stmt(first)
            raise AssertionError(first.data)
        kw = first.type
        if kw == "LIFECYCLE":
            lc = self.tree(item, "lifecycle")
            assert lc is not None
            if self.has(lc, "ARCHIVED_BY"):
                return A.LifecycleItem("archived_by", self.name(self.tok(lc, "NAME")), loc)  # type: ignore[arg-type]
            return A.LifecycleItem(str(self.toks(lc)[0].value), None, loc)
        if kw == "CARRY":
            nl = self.tree(item, "name_list")
            return A.CarryItem(tuple(self.name(t) for t in self.toks(nl) if t.type == "NAME"), loc)  # type: ignore[arg-type]
        if kw == "ORDERED_WITHIN":
            return A.OrderedWithinItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        if kw == "HISTORY":
            return A.HistoryKeptItem(loc)
        if kw == "BREAKING":
            return A.BreakingItem(self.string(self.tok(item, "STRING")), loc)  # type: ignore[arg-type]
        if kw == "TIGHTEN":
            return A.TightenItem(self.name(self.tok(item, "NAME")), self.repair_val(self.tree(item, "repair_val")), loc)  # type: ignore[arg-type]
        if kw == "INVARIANT":
            return A.InvariantItem(self.dyn(self.trees(item)[0]), loc)
        if kw == "SCOPE_VIA":
            return A.ScopeViaItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        raise AssertionError(f"carrier item {kw}")

    def carrier_decl(self, node: Tree, kind: str) -> A.CarrierDecl:
        nm = self.tok(node, "NAME")
        assert nm is not None
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        items = tuple(self.carrier_item(c) for c in self.trees(node) if c.data in ("carrier_item",))
        members = []
        for m in self.trees(node):
            if m.data == "member_decl":
                mn = self.tok(m, "NAME")
                assert mn is not None
                mitems = tuple(self.carrier_item(c) for c in self.trees(m) if c.data == "member_item")
                members.append(A.MemberDecl(self.name(mn), self.string(self.tok(m, "STRING")), mitems, self.L(m)))  # type: ignore[arg-type]
        return A.CarrierDecl(kind, self.name(nm), meaning, items, tuple(members), self.L(node))

    # -- intents
    def intent_item(self, item: Tree) -> A.IntentItem:
        loc = self.L(item)
        first = item.children[0]
        if isinstance(first, Tree):
            return self.intent_clause(first)
        kw = first.type
        if kw == "ALIAS":
            return A.AliasItem(self.name(self.tok(item, "NAME")), loc)  # type: ignore[arg-type]
        if kw == "RENAMED_FROM":
            return A.RenamedFromItem(self.qname(self.tree(item, "qname")), loc)  # type: ignore[arg-type]
        if kw == "VALUES":
            cl = self.tree(item, "ctor_list")
            return A.ValuesItem(tuple(A.Ctor(str(t.value), self.L(t)) for t in self.toks(cl) if t.type == "CTOR"), loc)  # type: ignore[arg-type]
        if kw == "PATTERN":
            return A.PatternItem(self.string(self.tok(item, "STRING")), loc)  # type: ignore[arg-type]
        if kw == "LENGTH":
            ints = [int(t.value) for t in self.toks(item) if t.type == "INT"]
            return A.LengthItem(ints[0], ints[1] if len(ints) > 1 else None, loc)
        if kw == "DIMENSION":
            return A.DimensionItem(int(self.tok(item, "INT").value), loc)  # type: ignore[union-attr]
        raise AssertionError(f"intent item {kw}")

    def intent_clause(self, tree: Tree) -> A.IntentItem:
        loc = self.L(tree)
        if tree.data == "retype_clause":
            nm = self.tok(tree, "NAME")
            adapters = [str(self.toks(a)[0].value) for a in self.trees(tree) if a.data == "adapter"]
            return A.RetypeClauseNode(self.name(nm), adapters[0], adapters[1], loc)  # type: ignore[arg-type]
        if tree.data == "retire_clause":
            disp = self.tree(tree, "disposition")
            return A.RetireClauseNode(str(self.toks(disp)[0].value), loc)  # type: ignore[arg-type]
        if tree.data == "restore_clause":
            return A.RestoreClauseNode(loc)
        raise AssertionError(tree.data)

    def intent_decl(self, node: Tree) -> A.IntentDecl:
        nm = self.tok(node, "NAME")
        assert nm is not None
        tr = self.tree(node, "type_ref")
        assert tr is not None
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        body = self.tree(node, "intent_body")
        items = tuple(self.intent_item(c) for c in self.trees(body)) if body is not None else ()
        return A.IntentDecl(self.name(nm), self.type_ref(tr), meaning, items, self.L(node))

    # -- verbs
    def dotted_verb(self, tree: Tree) -> A.DottedVerb:
        names = [t for t in self.toks(tree) if t.type == "NAME"]
        return A.DottedVerb(self.name(names[0]), self.name(names[1]), self.L(tree))

    def alias_decl(self, node: Tree) -> A.AliasDecl:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        unscoped = self.name(names[1]) if self.has(node, "UNSCOPED") else None
        return A.AliasDecl(self.name(names[0]), self.dotted_verb(self.tree(node, "dotted_verb")), unscoped, self.L(node))  # type: ignore[arg-type]

    def bulk_decl(self, node: Tree) -> A.BulkDecl:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        givens = tuple(self.given(c) for c in self.trees(node) if c.data == "given_item")
        verb = self.dotted_verb(self.tree(node, "dotted_verb"))  # type: ignore[arg-type]
        sets = []
        for sc in self.trees(node):
            if sc.data == "set_clause":
                sc_names = [t for t in self.toks(sc) if t.type == "NAME"]
                value = self.name(sc_names[1]) if len(sc_names) > 1 else None
                sets.append(A.SetClause(self.name(sc_names[0]), value, self.L(sc)))
        return A.BulkDecl(self.name(names[0]), meaning, givens, verb, self.name(names[1]), tuple(sets), self.L(node))

    def restricted_decl(self, node: Tree) -> A.RestrictedDecl:
        nm = self.tok(node, "NAME")
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        verb = self.dotted_verb(self.tree(node, "dotted_verb"))  # type: ignore[arg-type]
        nl = self.tree(node, "name_list")
        accepts = tuple(self.name(t) for t in self.toks(nl) if t.type == "NAME")  # type: ignore[arg-type]
        uc = self.tree(node, "unscoped_clause")
        unscoped = self.name(self.tok(uc, "NAME")) if uc is not None else None  # type: ignore[arg-type]
        return A.RestrictedDecl(self.name(nm), meaning, verb, accepts, unscoped, self.L(node))  # type: ignore[arg-type]

    def compound_decl(self, node: Tree) -> A.CompoundDecl:
        nm = self.tok(node, "NAME")
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        steps = []
        for st in self.trees(node):
            if st.data != "step_stmt":
                continue
            st_names = [t for t in self.toks(st) if t.type == "NAME"]
            each = self.name(st_names[1]) if self.has(st, "EACH") else None
            binds = []
            bl = self.tree(st, "bind_list")
            if bl is not None:
                for bi in self.trees(bl):
                    binds.append(A.BindItem(self.path(self.tree(bi, "path_expr")), self.name(self.tok(bi, "NAME")), self.L(bi)))  # type: ignore[arg-type]
            steps.append(A.StepStmt(self.name(st_names[0]), self.dotted_verb(self.tree(st, "dotted_verb")), each, tuple(binds), self.L(st)))  # type: ignore[arg-type]
        return A.CompoundDecl(self.name(nm), meaning, tuple(steps), self.L(node))  # type: ignore[arg-type]

    # -- evolution
    def tombstone_decl(self, node: Tree) -> A.TombstoneDecl:
        disp = self.tree(node, "disposition")
        return A.TombstoneDecl(self.name(self.tok(node, "NAME")), self.string(self.tok(node, "STRING")), str(self.toks(disp)[0].value), self.L(node))  # type: ignore[arg-type]

    def tighten_stmt(self, node: Tree) -> A.TightenStmt:
        return A.TightenStmt(self.path(self.tree(node, "path_expr")), self.repair_val(self.tree(node, "repair_val")), self.L(node))  # type: ignore[arg-type]

    def retype_stmt(self, node: Tree) -> A.RetypeStmt:
        clause = self.intent_clause(self.tree(node, "retype_clause"))  # type: ignore[arg-type]
        assert isinstance(clause, A.RetypeClauseNode)
        return A.RetypeStmt(self.name(self.tok(node, "NAME")), clause, self.L(node))  # type: ignore[arg-type]

    def restore_stmt(self, node: Tree) -> A.RestoreStmt:
        return A.RestoreStmt(self.name(self.tok(node, "NAME")), self.L(node))  # type: ignore[arg-type]

    def move_home_stmt(self, node: Tree) -> A.MoveHomeStmt:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        disp = self.tree(node, "disposition")
        return A.MoveHomeStmt(self.name(names[0]), self.name(names[1]), self.name(names[2]), str(self.toks(disp)[0].value), self.L(node))  # type: ignore[arg-type]

    # -- world / deployment
    def world_decl(self, node: Tree) -> A.WorldDecl:
        nm = self.tok(node, "NAME")
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        items = []
        for it in self.trees(node):
            kw = it.children[0].type  # type: ignore[union-attr]
            loc = self.L(it)
            if kw in ("MODULES", "GENERATED", "CAPABILITIES"):
                nl = self.tree(it, "name_list")
                items.append(A.WorldItem(kw.lower(), names=tuple(self.name(t) for t in self.toks(nl) if t.type == "NAME"), loc=loc))  # type: ignore[arg-type]
            elif kw in ("DURABILITY", "WRITERS", "WRITER_SOURCE"):
                items.append(A.WorldItem(kw.lower(), names=(self.name(self.tok(it, "NAME")),), loc=loc))  # type: ignore[arg-type]
            elif kw == "REQUIRES":
                qn = self.qname(self.tree(it, "qname"))  # type: ignore[arg-type]
                ql = self.tree(it, "qname_list")
                exempt = tuple(self.qname(c) for c in self.trees(ql)) if ql is not None else ()
                items.append(A.WorldItem("requires", qname=qn, exempt=exempt, loc=loc))
            elif kw == "SCOPE":
                st = self.tree(it, "scope_target")
                assert st is not None
                if self.has(st, "DEPLOYMENT"):
                    items.append(A.WorldItem("scope", deployment_scope=True, loc=loc))
                else:
                    items.append(A.WorldItem("scope", path=self.path(self.tree(st, "path_expr")), loc=loc))  # type: ignore[arg-type]
            elif kw == "QUARANTINE_RETENTION":
                items.append(A.WorldItem("quarantine_retention", integer=int(self.tok(it, "INT").value), loc=loc))  # type: ignore[union-attr]
            else:
                raise AssertionError(f"world item {kw}")
        return A.WorldDecl(self.name(nm), meaning, tuple(items), self.L(node))  # type: ignore[arg-type]

    def deployment_decl(self, node: Tree) -> A.DeploymentDecl:
        names = [t for t in self.toks(node) if t.type == "NAME"]
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        extends = self.name(names[1]) if self.has(node, "EXTENDS") else None
        items = []
        for it in self.trees(node):
            kw = it.children[0].type  # type: ignore[union-attr]
            loc = self.L(it)
            if kw in ("WORLD", "ENGINE", "SHIP", "MODE", "SNAPSHOT"):
                items.append(A.DepItem(kw.lower(), name=self.name(self.tok(it, "NAME")), loc=loc))  # type: ignore[arg-type]
            elif kw == "POOL":
                items.append(A.DepItem("pool", integer=int(self.tok(it, "INT").value), loc=loc))  # type: ignore[union-attr]
            elif kw == "AT":
                lt = self.tree(it, "location")
                assert lt is not None
                if self.has(lt, "ENV"):
                    s = self.tok(lt, "STRING")
                    location = A.LocationNode("env", self.name(self.tok(lt, "NAME")), self.string(s) if s is not None else None, self.L(lt))  # type: ignore[arg-type]
                elif self.has(lt, "PATH"):
                    location = A.LocationNode("path", None, self.string(self.tok(lt, "STRING")), self.L(lt))  # type: ignore[arg-type]
                else:
                    location = A.LocationNode("memory", None, None, self.L(lt))
                items.append(A.DepItem("at", location=location, loc=loc))
            else:
                raise AssertionError(f"dep item {kw}")
        return A.DeploymentDecl(self.name(names[0]), meaning, extends, tuple(items), self.L(node))

    # -- module / toplevel
    def decl(self, node: Tree) -> A.Decl:
        d = node.data
        if d == "intent_decl":
            return self.intent_decl(node)
        if d == "newtype_decl":
            nm = self.tok(node, "NAME")
            return A.NewtypeDecl(self.name(nm), self.type_ref(self.tree(node, "type_ref")), self.string(self.tok(node, "STRING")), self.L(node))  # type: ignore[arg-type]
        if d in ("trait_decl", "resource_decl", "event_decl", "association_decl", "family_decl"):
            return self.carrier_decl(node, d[: -len("_decl")])
        if d == "query_decl":
            return self.read_decl(node, "query")
        if d == "question_decl":
            return self.read_decl(node, "question")
        if d == "alias_decl":
            return self.alias_decl(node)
        if d == "bulk_decl":
            return self.bulk_decl(node)
        if d == "restricted_decl":
            return self.restricted_decl(node)
        if d == "compound_decl":
            return self.compound_decl(node)
        if d == "tombstone_decl":
            return self.tombstone_decl(node)
        if d == "tighten_stmt":
            return self.tighten_stmt(node)
        if d == "retype_stmt":
            return self.retype_stmt(node)
        if d == "restore_stmt":
            return self.restore_stmt(node)
        if d == "move_home_stmt":
            return self.move_home_stmt(node)
        raise AssertionError(f"decl {d}")

    def module(self, node: Tree) -> A.ModuleDecl:
        nm = self.tok(node, "NAME")
        meaning = self.string(self.tok(node, "STRING"))  # type: ignore[arg-type]
        imports = []
        decls = []
        for c in self.trees(node):
            if c.data == "import_stmt":
                owner = self.name(self.tok(c, "NAME"))  # type: ignore[arg-type]
                items = []
                for ii in self.trees(c):
                    ii_names = [t for t in self.toks(ii) if t.type == "NAME"]
                    local = self.name(ii_names[1]) if len(ii_names) > 1 else None
                    items.append(A.ImportItem(self.name(ii_names[0]), local, self.L(ii)))
                imports.append(A.ImportStmt(owner, tuple(items), self.L(c)))
            elif c.data == "decl":
                decls.append(self.decl(self.trees(c)[0]))
        return A.ModuleDecl(self.name(nm), meaning, tuple(imports), tuple(decls), self.L(node))  # type: ignore[arg-type]

    def toplevel(self, node: Tree) -> A.TopLevel:
        inner = self.trees(node)[0]
        d = inner.data
        if d == "module":
            return self.module(inner)
        if d == "world_decl":
            return self.world_decl(inner)
        if d == "deployment_decl":
            return self.deployment_decl(inner)
        if d == "tighten_stmt":
            return self.tighten_stmt(inner)
        if d == "retype_stmt":
            return self.retype_stmt(inner)
        if d == "restore_stmt":
            return self.restore_stmt(inner)
        if d == "move_home_stmt":
            return self.move_home_stmt(inner)
        raise AssertionError(f"toplevel {d}")

    def build(self, tree: Tree) -> A.SourceFile:
        tops = tuple(self.toplevel(c) for c in self.trees(tree))
        return A.SourceFile(self.file, self.text, tops, tuple(self.names))


# --- public API --------------------------------------------------------------


def parse_text(text: str, file: str = "<text>") -> A.SourceFile:
    """Parse ``text`` or raise a decode ``Refusal``."""
    try:
        tree = parser().parse(text)
    except UnexpectedInput as exc:
        raise classify_decode(exc, file) from None
    return _Builder(file, text).build(tree)


def parse_path(path: Path) -> A.SourceFile:
    return parse_text(path.read_text(encoding="utf-8"), str(path))


def parse_paths(paths: Iterable[Path]) -> list[A.SourceFile]:
    return [parse_path(p) for p in paths]


def garns_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.glob("*.garns") if p.is_file())
