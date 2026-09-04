"""Query and question resolution: paths, typed expressions, shapes.

The dynamic (question) algebra is the closed subset produced from ``ast``
dynamic nodes; the static (query) algebra is the superset. Both resolve to
the same expression IR so that lowering is shared, while footprint derivation
refuses anything outside the closed subset loudly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union

from . import ast as A
from . import ir as I
from .calls import REGISTRY, accepts, result_type
from .refuse import refuse
from .types import BUILTIN_SCALARS, TypeRef, comparable, ordered

if TYPE_CHECKING:
    from .resolve import Resolver


@dataclass
class Ctx:
    module: str
    read_qid: str
    root: str  # carrier qid
    givens: dict[str, I.Given]
    used_givens: set[str] = field(default_factory=set)
    static: bool = False
    in_quantifier: bool = False
    top_conjunct: bool = True
    allow_aggregates: bool = False
    grouped: bool = False
    composes: list[str] = field(default_factory=list)
    has_clock: bool = False
    in_aggregate_arg: bool = False


class ReadResolver:
    def __init__(self, r: "Resolver") -> None:
        self.r = r
        self._pending_composition_checks: list[tuple[str, str, str, object]] = []

    # ------------------------------------------------------------- givens
    def resolve_given(self, module: str, node: A.GivenItem) -> I.Given:
        if node.name.text.startswith("_"):
            refuse("GIVEN_NAME_RESERVED", "validate", node.name, "given names beginning with _ are reserved for engine parameters")
        t = self.r.resolve_type(module, node.type_ref, allow_carrier=True)
        default = None
        if node.default is not None:
            default = self.r.literal_of_type(node.default, t, "GIVEN_DEFAULT_TYPE")
        return I.Given(node.name.text, t, default, node.loc)

    # -------------------------------------------------------------- paths
    def resolve_path(self, ctx: Ctx, node: A.PathNode, *, allow_many: bool) -> I.PathRef:
        carrier = self.r.carriers[ctx.root]
        steps: list[I.LinkStep] = []
        terminal: I.Terminal | None = None
        names = node.names
        for index, name in enumerate(names):
            last = index == len(names) - 1
            if terminal is not None:
                refuse("PATH_THROUGH_SCALAR", "validate", name, f"{names[index - 1].text} is a scalar; {name.text} cannot follow it")
            text = name.text
            if text == "ship_clock":
                refuse("QUESTION_CLOCK_NOT_A_TERM", "validate", name, "ship_clock is a write-time default, not a read term")
            if text == "identity":
                terminal = I.IdentityTerminal(carrier.qid)
                continue
            if text == "kind":
                if carrier.kind not in ("family", "member"):
                    refuse("TERM_UNKNOWN", "validate", name, f"{carrier.qid} is not a family; kind is undefined")
                terminal = I.KindTerminal(carrier.family or carrier.qid)
                continue
            link = carrier.link_named(text)
            if link is not None:
                self.r.ref(name, self.r.link_identity(link), "link")
                steps.append(I.LinkStep(link.qid, carrier.qid, link.target, False, False, text))
                if last:
                    terminal = I.LinkTerminal(carrier.qid, link.qid, link.target, link.optional)
                carrier = self.r.carriers[link.target]
                continue
            edge = carrier.inverse_named(text)
            if edge is not None:
                source_link = self.r.carriers[edge.source].link_named(edge.link.rsplit(".", 1)[-1])
                assert source_link is not None
                self.r.ref(name, f"{self.r.link_identity(source_link)}#inverse", "inverse")
                steps.append(I.LinkStep(edge.link, carrier.qid, edge.source, True, edge.many, text))
                if last:
                    terminal = I.LinkTerminal(carrier.qid, edge.link, edge.source, True)
                carrier = self.r.carriers[edge.source]
                continue
            use = carrier.use_named(text)
            if use is None:
                # intent alias?
                for u in carrier.uses:
                    intent = self.r.intents[u.intent]
                    if intent.alias == text:
                        use = u
                        break
            if use is not None:
                via_alias = use.intent.rsplit(".", 1)[-1] != text
                self.r.ref(name, f"{use.intent}#alias" if via_alias else use.intent, "intent-alias" if via_alias else "intent")
                terminal = I.UseTerminal(carrier.qid, use.qid, use.intent, use.type)
                continue
            tomb = self.r.scopes[carrier.module].tombstones.get(text)
            if tomb is not None:
                refuse("QUESTION_INTENT_RETIRED", "validate", name, f"{text} is retired from {carrier.module}")
            refuse("TERM_UNKNOWN", "validate", name, f"{text} is not a use, link, or inverse of {carrier.qid}")
        assert terminal is not None
        path = I.PathRef(ctx.root, tuple(steps), terminal, node.text, node.loc)
        if path.many and not allow_many:
            refuse("TERM_TO_MANY_UNQUANTIFIED", "validate", node, f"{node.text} traverses a to-many link without some/every")
        return path

    # ----------------------------------------------------------- operands
    def operand(self, ctx: Ctx, node: object, *, prefer_given: bool = True) -> I.Operand:
        """Resolve a value position. Givens shadow terms on the right of a
        predicate (``prefer_given``); terms shadow givens on the left."""
        if isinstance(node, A.PathNode):
            single = len(node.names) == 1
            is_given = single and node.names[0].text in ctx.givens
            if is_given and (prefer_given or not self._is_term(ctx, node.names[0].text)):
                given = ctx.givens[node.names[0].text]
                ctx.used_givens.add(given.name)
                self.r.ref(node.names[0], f"{ctx.read_qid}#{given.name}", "given")
                return I.GivenRef(given.name, given.type, node.loc)
            return self.resolve_path(ctx, node, allow_many=ctx.in_quantifier)
        if isinstance(node, A.LiteralNode):
            return self.provisional_literal(node)
        if isinstance(node, A.ClockNode):
            ctx.has_clock = True
            return I.ClockRef(node.loc)
        if isinstance(node, A.SBinaryNode):
            return self.arith(ctx, node)
        if isinstance(node, A.SUnaryNode):
            item = self.operand(ctx, node.item)
            t = self.type_of(item)
            if t.scalar().cls not in ("integer", "decimal"):
                refuse("EXPR_TYPE", "validate", node, "unary sign applies to numbers")
            if node.op == "+":
                return item
            return I.Negate(item, t.scalar(), node.loc)
        if isinstance(node, A.SAggregateNode):
            return self.static_aggregate(ctx, node)
        if isinstance(node, A.SCallNode):
            return self.call(ctx, node)
        raise TypeError(node)

    def _is_term(self, ctx: Ctx, text: str) -> bool:
        carrier = self.r.carriers[ctx.root]
        if text in ("identity", "kind"):
            return True
        return carrier.link_named(text) is not None or carrier.inverse_named(text) is not None or carrier.use_named(text) is not None

    @staticmethod
    def provisional_literal(node: A.LiteralNode) -> I.Literal:
        if node.kind == "int":
            return I.Literal(TypeRef("Integer", "integer"), node.value)
        if node.kind == "string":
            return I.Literal(TypeRef("Text", "text"), node.value)
        if node.kind == "bool":
            return I.Literal(TypeRef("Boolean", "boolean"), node.value)
        # constructor literal: typed against the other operand later
        return I.Literal(TypeRef("Text", "text", nominal="@ctor", closed=(str(node.value),)), node.value)

    @staticmethod
    def type_of(op: I.Operand) -> TypeRef:
        if isinstance(op, I.PathRef):
            return op.type
        if isinstance(op, I.Literal):
            return op.type
        if isinstance(op, I.GivenRef):
            return op.type
        if isinstance(op, I.ClockRef):
            return TypeRef("Instant", "instant")
        if isinstance(op, (I.AggRef, I.Arith, I.Negate, I.StaticAggregate, I.Call)):
            return op.type
        raise TypeError(op)

    def retype_literal(self, lit: I.Literal, against: TypeRef, at: object, node: A.LiteralNode | None = None) -> I.Literal:
        s = against.scalar()
        if lit.type.nominal == "@ctor":
            if not s.is_closed:
                refuse("EXPR_TYPE", "validate", at, f"{lit.value} is a closed-set member; the other side is {s.describe()}")
            if lit.value not in s.closed:
                refuse("CLOSED_SET_MEMBER_UNKNOWN", "validate", at, f"{lit.value} is not a member of {s.describe()}")
            return I.Literal(s, str(lit.value)[1:])
        if s.is_closed:
            refuse("EXPR_TYPE", "validate", at, f"a closed set compares with a @member, not a {lit.type.cls} literal")
        cls = lit.type.cls
        if cls == "text" and s.cls == "text":
            return I.Literal(s, lit.value)
        if cls == "integer" and s.cls in ("integer", "decimal", "instant"):
            return I.Literal(s, lit.value)
        if cls == "boolean" and s.cls == "boolean":
            return I.Literal(s, lit.value)
        if s.carrier and cls in ("integer", "text"):
            return I.Literal(s, lit.value)
        refuse("EXPR_TYPE", "validate", at, f"{cls} literal does not fit {s.describe()}")
        raise AssertionError

    def unify(self, ctx: Ctx, left: I.Operand, right: I.Operand, at: object) -> tuple[I.Operand, I.Operand]:
        """Type both sides of a comparison; retype literals against the other side."""
        if isinstance(left, I.Literal) and isinstance(right, I.Literal):
            if left.type.nominal == "@ctor" or right.type.nominal == "@ctor":
                refuse("EXPR_TYPE", "validate", at, "two literals cannot be compared through a closed set")
            return left, right
        if self.type_of(left).scalar().cls in ("opaque", "vector") or self.type_of(right).scalar().cls in ("opaque", "vector"):
            refuse("OPAQUE_COMPARED", "validate", at, "opaque and vector values admit presence only")
        if isinstance(left, I.Literal):
            left = self.retype_literal(left, self.type_of(right), at)
        if isinstance(right, I.Literal):
            right = self.retype_literal(right, self.type_of(left), at)
        lt, rt = self.type_of(left), self.type_of(right)
        if lt.list_of or rt.list_of:
            refuse("EXPR_TYPE", "validate", at, "a list is used with in, not compared")
        if not comparable(lt, rt):
            refuse("EXPR_TYPE", "validate", at, f"{lt.describe()} is not comparable with {rt.describe()}")
        return left, right

    def guard_of(self, ctx: Ctx, right: I.Operand, guard: bool, at: object) -> I.GivenRef | None:
        given = right if isinstance(right, I.GivenRef) else None
        if guard:
            if given is None or not given.type.optional:
                refuse("GUARD_NOT_OPTIONAL_GIVEN", "validate", at, "when given guards an optional given")
            return given
        if given is not None and given.type.optional:
            if not ctx.top_conjunct:
                refuse("OPTIONAL_PARAM_UNGUARDED", "validate", at, f"optional given {given.name} is used inside or/not without when given")
            return given
        return None

    # --------------------------------------------------- dynamic expressions
    def dyn(self, ctx: Ctx, node: A.DynExpr) -> I.Expr:
        if isinstance(node, A.AndNode):
            return I.And(tuple(self.dyn(ctx, i) for i in node.items), node.loc)
        if isinstance(node, A.OrNode):
            inner = Ctx(**{**ctx.__dict__, "top_conjunct": False})
            items = tuple(self.dyn(inner, i) for i in node.items)
            self._merge(ctx, inner)
            return I.Or(items, node.loc)
        if isinstance(node, A.NotNode):
            inner = Ctx(**{**ctx.__dict__, "top_conjunct": False})
            item = self.dyn(inner, node.item)
            self._merge(ctx, inner)
            return I.Not(item, node.loc)
        if isinstance(node, A.QuantNode):
            inner = Ctx(**{**ctx.__dict__, "in_quantifier": True})
            item = self.dyn(inner, node.item)
            self._merge(ctx, inner)
            if not self._mentions_many(item):
                refuse("QUANTIFIER_WITHOUT_TO_MANY", "validate", node, f"{node.kind} quantifies a to-many path; none is present")
            return I.Quantified(node.kind, item, node.loc)
        if isinstance(node, A.CmpNode):
            if isinstance(node.left, A.AggNode):
                left: I.Operand = self.agg(ctx, node.left)
            else:
                left = self.resolve_path(ctx, node.left, allow_many=ctx.in_quantifier)
            right = self.operand(ctx, node.right)
            left, right = self.unify(ctx, left, right, node)
            if node.op in ("<", "<=", ">", ">=") and not ordered(self.type_of(left)):
                refuse("EXPR_TYPE", "validate", node, f"{node.op} needs an ordered type")
            return I.Compare(left, node.op, right, self.guard_of(ctx, right, node.guard, node), node.loc)
        if isinstance(node, A.ContainsNode):
            left = self.resolve_path(ctx, node.path, allow_many=ctx.in_quantifier)
            if self.type_of(left).scalar().cls != "text":
                refuse("CONTAINS_NOT_TEXT", "validate", node, "contains applies to text")
            right = self.operand(ctx, node.value)
            if isinstance(right, I.Literal):
                right = self.retype_literal(right, self.type_of(left), node)
            elif self.type_of(right).scalar().cls != "text" or self.type_of(right).list_of:
                refuse("EXPR_TYPE", "validate", node, "contains takes a text value")
            return I.Contains(left, right, self.guard_of(ctx, right, node.guard, node), node.loc)
        if isinstance(node, A.InNode):
            left = self.resolve_path(ctx, node.path, allow_many=ctx.in_quantifier)
            right = self.operand(ctx, node.value)
            rt = self.type_of(right)
            if not isinstance(right, I.GivenRef) or not rt.list_of:
                refuse("IN_NOT_LIST", "validate", node, "in takes a list_of given")
            if not comparable(self.type_of(left), rt):
                refuse("EXPR_TYPE", "validate", node, f"{self.type_of(left).describe()} is not comparable with {rt.describe()}")
            return I.In(left, right, self.guard_of(ctx, right, node.guard, node), node.loc)
        if isinstance(node, A.IsNode):
            left = self.resolve_path(ctx, node.path, allow_many=ctx.in_quantifier)
            if not isinstance(left.terminal, (I.LinkTerminal, I.IdentityTerminal)):
                refuse("IS_NOT_LINK", "validate", node, "is compares a link or identity with an identity")
            right = self.operand(ctx, node.value)
            rt = self.type_of(right)
            target = left.terminal.target if isinstance(left.terminal, I.LinkTerminal) else left.terminal.carrier
            if isinstance(right, I.Literal):
                right = self.retype_literal(right, TypeRef("Id", "text", carrier=target), node)
            elif rt.carrier != target and not self._same_family(rt.carrier, target):
                refuse("IS_TYPE", "validate", node, f"{left.text} identifies {target}; the value identifies {rt.describe()}")
            return I.Is(left, right, self.guard_of(ctx, right, node.guard, node), node.loc)
        if isinstance(node, A.PresenceNode):
            path = self.resolve_path(ctx, node.path, allow_many=ctx.in_quantifier)
            return I.Presence(path, node.present, None, node.loc)
        if isinstance(node, A.WithinNode):
            path = self.resolve_path(ctx, node.path, allow_many=ctx.in_quantifier)
            if not isinstance(path.terminal, (I.LinkTerminal, I.IdentityTerminal)):
                refuse("WITHIN_NOT_LINK", "validate", node, "within composes a link or identity with a read")
            if len(node.target.names) != 1:
                refuse("READ_UNKNOWN", "validate", node.target, "within names a read declared in this module or imported")
            entry = self.r.lookup(ctx.module, node.target.names[0], ("read",), "READ_UNKNOWN")
            self.r.ref(node.target.names[0], entry.qid, "read")
            end = path.terminal.target if isinstance(path.terminal, I.LinkTerminal) else path.terminal.carrier
            ctx.composes.append(entry.qid)
            self._pending_composition_checks.append((ctx.read_qid, entry.qid, end, node))
            return I.Within(path, entry.qid, node.loc)
        raise TypeError(node)

    def _same_family(self, a: str | None, b: str | None) -> bool:
        if a is None or b is None:
            return False
        ca, cb = self.r.carriers.get(a), self.r.carriers.get(b)
        return bool(ca and cb and (ca.family == b or cb.family == a))

    @staticmethod
    def _merge(outer: Ctx, inner: Ctx) -> None:
        outer.used_givens |= inner.used_givens
        outer.composes.extend(c for c in inner.composes if c not in outer.composes)
        outer.has_clock = outer.has_clock or inner.has_clock

    def _mentions_many(self, expr: object) -> bool:
        if isinstance(expr, I.PathRef):
            return expr.many
        if hasattr(expr, "__dataclass_fields__"):
            for name in expr.__dataclass_fields__:  # type: ignore[attr-defined]
                if name == "loc":
                    continue
                if self._mentions_many(getattr(expr, name)):
                    return True
            return False
        if isinstance(expr, (list, tuple)):
            return any(self._mentions_many(x) for x in expr)
        return False

    def agg(self, ctx: Ctx, node: A.AggNode) -> I.AggRef:
        path = self.resolve_path(ctx, node.path, allow_many=True)
        if not isinstance(path.terminal, I.LinkTerminal) or not path.many:
            refuse("AGG_NOT_TO_MANY", "validate", node.path, f"{node.path.text} is not a to-many link")
        end = path.terminal.target
        inner_ctx = Ctx(ctx.module, ctx.read_qid, end, ctx.givens, ctx.used_givens, ctx.static, False, True, False, False, ctx.composes, ctx.has_clock)
        if node.fn == "count":
            filt = self.dyn(inner_ctx, node.arg) if node.arg is not None else None  # type: ignore[arg-type]
            ctx.has_clock = ctx.has_clock or inner_ctx.has_clock
            return I.AggRef(path, "count", filt, None, TypeRef("Integer", "integer"), node.loc)
        assert isinstance(node.arg, A.PathNode)
        arg = self.resolve_path(inner_ctx, node.arg, allow_many=False)
        if not ordered(arg.type):
            refuse("EXPR_TYPE", "validate", node.arg, f"{node.fn} needs an ordered type")
        return I.AggRef(path, node.fn, None, arg, arg.type.scalar(), node.loc)

    # ---------------------------------------------------- static expressions
    def static(self, ctx: Ctx, node: A.StaticExpr) -> I.Expr:
        if isinstance(node, A.SAndNode):
            return I.And(tuple(self.static(ctx, i) for i in node.items), node.loc)
        if isinstance(node, A.SOrNode):
            inner = Ctx(**{**ctx.__dict__, "top_conjunct": False})
            items = tuple(self.static(inner, i) for i in node.items)
            self._merge(ctx, inner)
            return I.Or(items, node.loc)
        if isinstance(node, A.SNotNode):
            inner = Ctx(**{**ctx.__dict__, "top_conjunct": False})
            item = self.static(inner, node.item)
            self._merge(ctx, inner)
            return I.Not(item, node.loc)
        if isinstance(node, A.SCmpNode):
            left = self.operand(ctx, node.left, prefer_given=False)
            right = self.operand(ctx, node.right)
            if node.op == "contains":
                if self.type_of(left).scalar().cls != "text":
                    refuse("CONTAINS_NOT_TEXT", "validate", node, "contains applies to text")
                if isinstance(right, I.Literal):
                    right = self.retype_literal(right, self.type_of(left), node)
                elif self.type_of(right).scalar().cls != "text":
                    refuse("EXPR_TYPE", "validate", node, "contains takes a text value")
                return I.Contains(left, right, self.guard_of(ctx, right, False, node), node.loc)
            if node.op == "in":
                rt = self.type_of(right)
                if not isinstance(right, I.GivenRef) or not rt.list_of:
                    refuse("IN_NOT_LIST", "validate", node, "in takes a list_of given")
                if not comparable(self.type_of(left), rt):
                    refuse("EXPR_TYPE", "validate", node, "in list element type mismatch")
                return I.In(left, right, self.guard_of(ctx, right, False, node), node.loc)
            if node.op == "is":
                if not isinstance(left, I.PathRef) or not isinstance(left.terminal, (I.LinkTerminal, I.IdentityTerminal)):
                    refuse("IS_NOT_LINK", "validate", node, "is compares a link or identity with an identity")
                target = left.terminal.target if isinstance(left.terminal, I.LinkTerminal) else left.terminal.carrier
                if isinstance(right, I.Literal):
                    right = self.retype_literal(right, TypeRef("Id", "text", carrier=target), node)
                elif self.type_of(right).carrier != target:
                    refuse("IS_TYPE", "validate", node, f"{left.text} identifies {target}")
                return I.Is(left, right, self.guard_of(ctx, right, False, node), node.loc)
            left, right = self.unify(ctx, left, right, node)
            if node.op in ("<", "<=", ">", ">=") and not ordered(self.type_of(left)):
                refuse("EXPR_TYPE", "validate", node, f"{node.op} needs an ordered type")
            return I.Compare(left, node.op, right, self.guard_of(ctx, right, False, node), node.loc)
        if isinstance(node, A.SPresenceNode):
            path = self.resolve_path(ctx, node.path, allow_many=False)
            return I.Presence(path, node.present, None, node.loc)
        if isinstance(node, A.SWithinNode):
            path = self.resolve_path(ctx, node.path, allow_many=False)
            if not isinstance(path.terminal, (I.LinkTerminal, I.IdentityTerminal)):
                refuse("WITHIN_NOT_LINK", "validate", node, "within composes a link or identity with a read")
            if len(node.target.parts) == 1:
                entry = self.r.lookup(ctx.module, node.target.parts[0], ("read",), "READ_UNKNOWN")
                self.r.ref(node.target.parts[0], entry.qid, "read")
            else:
                entry = self.r.lookup_qualified(node.target, ("read",), "READ_UNKNOWN", "read")
            end = path.terminal.target if isinstance(path.terminal, I.LinkTerminal) else path.terminal.carrier
            ctx.composes.append(entry.qid)
            self._pending_composition_checks.append((ctx.read_qid, entry.qid, end, node))
            return I.Within(path, entry.qid, node.loc)
        # boolean scalar as predicate
        op = self.operand(ctx, node)
        if self.type_of(op).scalar().cls != "boolean":
            refuse("EXPR_TYPE", "validate", node, "a predicate must be boolean")
        return I.Truth(op, node.loc)

    def arith(self, ctx: Ctx, node: A.SBinaryNode) -> I.Arith:
        left = self.operand(ctx, node.left)
        right = self.operand(ctx, node.right)
        if isinstance(left, I.Literal) and not isinstance(right, I.Literal):
            left = self.retype_literal(left, self.type_of(right), node)
        if isinstance(right, I.Literal) and not isinstance(left, I.Literal):
            right = self.retype_literal(right, self.type_of(left), node)
        lt, rt = self.type_of(left).scalar(), self.type_of(right).scalar()
        if lt.cls not in ("integer", "decimal") or rt.cls not in ("integer", "decimal"):
            refuse("EXPR_TYPE", "validate", node, f"arithmetic needs numbers, got {lt.describe()} and {rt.describe()}")
        if node.op == "%" and (lt.cls != "integer" or rt.cls != "integer"):
            refuse("EXPR_TYPE", "validate", node, "% needs integers")
        if node.op == "/" or "decimal" in (lt.cls, rt.cls):
            base = lt.base if lt.cls == "decimal" else (rt.base if rt.cls == "decimal" else "Decimal")
            t = TypeRef(base, "decimal")
        else:
            t = TypeRef("Integer", "integer")
        return I.Arith(node.op, left, right, t, node.loc)

    def static_aggregate(self, ctx: Ctx, node: A.SAggregateNode) -> I.StaticAggregate:
        if not ctx.allow_aggregates:
            refuse("AGGREGATE_MISUSED", "validate", node, f"{node.fn}() is not admitted in this clause")
        if ctx.in_aggregate_arg:
            refuse("AGGREGATE_MISUSED", "validate", node, "aggregates do not nest")
        path = None
        if node.path is not None:
            inner = Ctx(**{**ctx.__dict__, "in_aggregate_arg": True})
            path = self.resolve_path(inner, node.path, allow_many=False)
            self._merge(ctx, inner)
        if node.fn == "count":
            if node.distinct and path is None:
                refuse("AGGREGATE_MISUSED", "validate", node, "count(distinct) needs a path")
            return I.StaticAggregate("count", node.distinct, path, TypeRef("Integer", "integer"), node.loc)
        if path is None:
            refuse("AGGREGATE_MISUSED", "validate", node, f"{node.fn}() needs a path")
        t = path.type.scalar()
        if node.fn in ("sum", "average"):
            if t.cls not in ("integer", "decimal"):
                refuse("EXPR_TYPE", "validate", node, f"{node.fn} needs a number")
            rt = TypeRef(t.base, t.cls) if node.fn == "sum" else (TypeRef(t.base, "decimal") if t.cls == "decimal" else TypeRef("Decimal", "decimal"))
            return I.StaticAggregate(node.fn, node.distinct, path, rt, node.loc)
        if not ordered(t):
            refuse("EXPR_TYPE", "validate", node, f"{node.fn} needs an ordered type")
        return I.StaticAggregate(node.fn, node.distinct, path, t, node.loc)

    def call(self, ctx: Ctx, node: A.SCallNode) -> I.Call:
        if ctx.in_aggregate_arg:
            refuse("AGGREGATE_MISUSED", "validate", node, "calls do not appear inside aggregate arguments")
        name = node.function.text
        sig = REGISTRY.get(name)
        if sig is None:
            refuse("CALL_UNKNOWN", "validate", node.function, f"{name} is not a registered function")
        if sig.purity == "volatile":
            refuse("CALL_VOLATILE", "validate", node.function, f"{name} is not deterministic")
        if sig.purity == "effectful":
            refuse("CALL_EFFECTFUL", "validate", node.function, f"{name} has side effects")
        for part in node.function.parts:
            self.r.ref(part, name, "call")
        args = tuple(self.operand(ctx, a) for a in node.args)
        if len(args) != len(sig.params):
            refuse("CALL_ARITY", "validate", node, f"{name} takes {len(sig.params)} arguments")
        typed: list[I.Operand] = []
        for param, arg in zip(sig.params, args):
            if isinstance(arg, I.Literal):
                want = {"text": "Text", "numeric": "Decimal", "integer": "Integer", "instant": "Instant", "boolean": "Boolean"}[param]
                if arg.type.nominal == "@ctor":
                    refuse("CALL_ARGUMENT_TYPE", "validate", node, "a closed-set member is not a function argument")
                if param == "numeric" and arg.type.cls == "integer":
                    typed.append(arg)
                    continue
                arg = self.retype_literal(arg, TypeRef(want, BUILTIN_SCALARS[want]), node)
            if not accepts(param, self.type_of(arg)):
                refuse("CALL_ARGUMENT_TYPE", "validate", node, f"{name} expects {param}, got {self.type_of(arg).describe()}")
            typed.append(arg)
        return I.Call(name, tuple(typed), result_type(sig, tuple(self.type_of(a) for a in typed)), node.loc)

    # ------------------------------------------------------------ invariants
    def resolve_invariant(self, carrier: I.Carrier, expr: A.DynExpr) -> I.Expr:
        ctx = Ctx(carrier.module, carrier.qid, carrier.qid, {})
        result = self.dyn(ctx, expr)
        if ctx.composes:
            refuse("INVARIANT_COMPOSES", "validate", expr, "an invariant does not compose reads")
        if ctx.has_clock:
            refuse("INVARIANT_CLOCK", "validate", expr, "an invariant is clock-free")
        return result

    # ----------------------------------------------------------------- reads
    def resolve_read(self, module: str, qid: str, node: A.ReadDecl) -> I.Read:
        static = node.noun == "query"
        sentry = self.r.lookup(module, node.subject, ("carrier", "member"), "CARRIER_UNKNOWN")
        self.r.ref(node.subject, sentry.qid, sentry.kind)
        subject = self.r.carriers[sentry.qid]
        if subject.kind == "trait":
            refuse("READ_OF_TRAIT", "validate", node.subject, "a read is of a storable carrier")
        givens: dict[str, I.Given] = {}
        items: dict[str, A.ReadItem] = {}
        for item in node.items:
            if isinstance(item, A.GivenItem):
                if item.name.text in givens:
                    refuse("GIVEN_DUPLICATED", "validate", item.name, f"given {item.name.text} declared twice")
                self.r.ref(item.name, f"{qid}#{item.name.text}", "given")
                givens[item.name.text] = self.resolve_given(module, item)
                continue
            kind = type(item).__name__
            if kind in items:
                code = "QUESTION_LIVE_BOUND_DUPLICATED" if isinstance(item, A.LiveItem) else "READ_ITEM_REPEATED"
                refuse(code, "validate", item, f"{kind} stated twice in {qid}")
            items[kind] = item
        ctx = Ctx(module, qid, subject.qid, givens, static=static)
        # window / shape items
        first = items.get("FirstItem")
        one = items.get("OneItem")
        by = items.get("ByItem")
        page = items.get("PageItem")
        limit = items.get("LimitItem")
        group = items.get("GroupByItem")
        distinct = items.get("DistinctItem")
        with_total = items.get("WithTotalItem")
        live = items.get("LiveItem")
        including = items.get("IncludingArchivedItem")
        unscoped = items.get("UnscopedItem")
        having = items.get("HavingItem")
        if static and live is not None:
            raise AssertionError("grammar admits no live item in a query")
        if not static and live is None:
            refuse("QUESTION_LIVE_BOUND_REQUIRED", "validate", node.name, f"question {qid} states no live bounded N")
        live_bound = None
        if live is not None:
            assert isinstance(live, A.LiveItem)
            if live.bound <= 0:
                refuse("QUESTION_LIVE_BOUND_INVALID", "validate", live, "live bounded N is a positive literal")
            live_bound = live.bound
        if (page is None) != (limit is None):
            refuse("PAGE_LIMIT_PAIR", "validate", page or limit, "page and limit are stated together")
        if with_total is not None and page is None:
            refuse("WITH_TOTAL_WITHOUT_PAGE", "validate", with_total, "with_total accompanies page/limit")
        shape_items = [x for x in (first, one, by, page, group) if x is not None]
        if len(shape_items) > 1:
            refuse("SHAPE_CONFLICT", "validate", shape_items[1], "one, by, first, page/limit, and group by are exclusive")
        if distinct is not None and group is not None:
            refuse("SHAPE_CONFLICT", "validate", distinct, "distinct and group by are exclusive")
        page_ref = limit_ref = None
        if page is not None:
            assert isinstance(page, A.PageItem) and isinstance(limit, A.LimitItem)
            page_ref = self.given_ref(ctx, page.name, "PAGE_TYPE", "integer")
            limit_ref = self.given_ref(ctx, limit.name, "PAGE_TYPE", "integer")
        by_ref = None
        if by is not None:
            assert isinstance(by, A.ByItem)
            if len(by.path.names) != 1 or by.path.names[0].text not in givens:
                refuse("BY_NOT_GIVEN", "validate", by.path, "by names a given typed as the subject")
            g = givens[by.path.names[0].text]
            if g.type.carrier != subject.qid and g.type.carrier != subject.family:
                refuse("BY_TYPE", "validate", by.path, f"by needs a given identifying {subject.qid}")
            ctx.used_givens.add(g.name)
            self.r.ref(by.path.names[0], f"{qid}#{g.name}", "given")
            by_ref = I.GivenRef(g.name, g.type, by.loc)
        if including is not None and subject.lifecycle != "archived_by":
            refuse("INCLUDING_ARCHIVED_NOT_ARCHIVABLE", "validate", including, f"{subject.qid} has no archived_by lifecycle")
        unscoped_name = None
        if unscoped is not None:
            assert isinstance(unscoped, A.UnscopedItem)
            unscoped_name = unscoped.capability.text
            self.r._capability_refs.append((module, unscoped.capability))
        # group by
        group_paths: tuple[I.PathRef, ...] = ()
        if group is not None:
            assert isinstance(group, A.GroupByItem)
            group_paths = tuple(self.resolve_path(ctx, p, allow_many=False) for p in group.paths)
            for gp in group_paths:
                if gp.type.scalar().cls in ("opaque", "vector"):
                    refuse("EXPR_TYPE", "validate", gp, "cannot group by an opaque value")
        ctx.grouped = group is not None
        # predicate
        predicate = None
        where = items.get("WhereItem")
        if where is not None:
            assert isinstance(where, A.WhereItem)
            wctx = Ctx(**{**ctx.__dict__, "allow_aggregates": False, "in_aggregate_arg": False})
            predicate = self.static(wctx, where.expr) if static else self.dyn(wctx, where.expr)  # type: ignore[arg-type]
            self._merge(ctx, wctx)
        # shows
        shows: tuple[I.ShowTerm, ...] = ()
        show = items.get("ShowListItem")
        if show is not None:
            assert isinstance(show, A.ShowListItem)
            sctx = Ctx(**{**ctx.__dict__, "allow_aggregates": static, "in_aggregate_arg": False})
            shows = self.shows(sctx, show.items, subject)
            self._merge(ctx, sctx)
        # having
        having_expr = None
        if having is not None:
            assert isinstance(having, A.HavingItem)
            if group is None and not any(isinstance(s, I.ShowScalar) and self._has_aggregate(s.expr) for s in shows):
                refuse("HAVING_WITHOUT_GROUP", "validate", having, "having needs group by or aggregates")
            hctx = Ctx(**{**ctx.__dict__, "allow_aggregates": True, "in_aggregate_arg": False})
            having_expr = self.static(hctx, having.expr)
            self._merge(ctx, hctx)
        # orders
        orders: list[I.OrderTerm] = []
        order = items.get("OrderListItem")
        if order is not None:
            assert isinstance(order, A.OrderListItem)
            octx = Ctx(**{**ctx.__dict__, "allow_aggregates": static, "in_aggregate_arg": False})
            for oi in order.items:
                key = self.operand(octx, oi.key)
                if isinstance(key, I.Literal):
                    refuse("ORDER_BY_LITERAL", "validate", oi, "ordering by a literal is meaningless")
                if not ordered(self.type_of(key)) and self.type_of(key).carrier is None:
                    refuse("EXPR_TYPE", "validate", oi, "order key must be ordered")
                orders.append(I.OrderTerm(key, oi.direction == "descending", oi.loc))
            self._merge(ctx, octx)
        # shape
        shape = "collection"
        if one is not None or by is not None:
            shape = "optional_single"
        elif group is not None or (static and any(isinstance(s, I.ShowScalar) and self._has_aggregate(s.expr) for s in shows)):
            shape = "grouped"
        elif first is not None or page is not None:
            shape = "windowed"
        if shape == "grouped":
            self.check_grouped(group_paths, shows, orders, having_expr, static, show or node)
        elif any(isinstance(s, I.ShowCount) for s in shows):
            shape = "grouped"
        if any(isinstance(s, I.ShowRank) for s in shows) and not orders:
            refuse("RANK_WITHOUT_ORDER", "validate", show, "rank needs an order")
        if distinct is not None and any(isinstance(s, I.ShowNested) for s in shows):
            refuse("NESTED_SHOW_WITH_DISTINCT", "validate", distinct, "a distinct result has no row identity to attach nested rows to")
        first_n = first.count if isinstance(first, A.FirstItem) else None
        if first_n is not None and first_n <= 0:
            refuse("FIRST_NOT_POSITIVE", "validate", first, "first N is positive")
        # closed-algebra checks for questions
        if not static and ctx.has_clock:
            refuse("QUESTION_NOT_FOOTPRINTABLE", "validate", node.name, "engine_clock has no write footprint; a question refreshes on writes only")
        for g in givens.values():
            if g.name not in ctx.used_givens:
                refuse("GIVEN_UNUSED", "validate", g, f"given {g.name} is never used")
        return I.Read(
            node.noun, qid, module, node.name.text, subject.qid, node.meaning, tuple(givens.values()), predicate,
            shows, tuple(orders), group_paths, having_expr, distinct is not None, shape, first_n, page_ref, limit_ref,
            with_total is not None, including is not None, unscoped_name, by_ref, live_bound, tuple(ctx.composes), node.loc,
        )

    def given_ref(self, ctx: Ctx, name: A.Name, code: str, cls: str) -> I.GivenRef:
        g = ctx.givens.get(name.text)
        if g is None:
            refuse("GIVEN_UNKNOWN", "validate", name, f"{name.text} is not a given")
        if g.type.scalar().cls != cls or g.type.list_of:
            refuse(code, "validate", name, f"{name.text} must be {cls}")
        ctx.used_givens.add(g.name)
        self.r.ref(name, f"{ctx.read_qid}#{g.name}", "given")
        return I.GivenRef(g.name, g.type, name.loc)

    def _has_aggregate(self, op: object) -> bool:
        if isinstance(op, (I.StaticAggregate, I.AggRef)):
            return True
        if isinstance(op, (I.Arith,)):
            return self._has_aggregate(op.left) or self._has_aggregate(op.right)
        if isinstance(op, I.Negate):
            return self._has_aggregate(op.item)
        if isinstance(op, I.Call):
            return any(self._has_aggregate(a) for a in op.args)
        return False

    def check_grouped(self, keys: tuple[I.PathRef, ...], shows: tuple[I.ShowTerm, ...], orders: list[I.OrderTerm], having: I.Expr | None, static: bool, at: object) -> None:
        key_texts = {k.text for k in keys}
        for s in shows:
            if isinstance(s, I.ShowPath):
                if s.path.text not in key_texts:
                    refuse("AGGREGATE_MISUSED", "validate", s, f"{s.path.text} is neither a group key nor aggregated")
            elif isinstance(s, I.ShowScalar):
                if not self._has_aggregate(s.expr) and not self._only_keys(s.expr, key_texts):
                    refuse("AGGREGATE_MISUSED", "validate", s, "a grouped show is a key or an aggregate")
            elif isinstance(s, (I.ShowIdentity, I.ShowRank, I.ShowNested)):
                refuse("AGGREGATE_MISUSED", "validate", s, "identity, rank, and nested shows do not appear in grouped results")
        for o in orders:
            if isinstance(o.key, I.PathRef) and o.key.text not in key_texts:
                refuse("AGGREGATE_MISUSED", "validate", o, f"order key {o.key.text} is not a group key")

    def _only_keys(self, op: object, keys: set[str]) -> bool:
        if isinstance(op, I.PathRef):
            return op.text in keys
        if isinstance(op, (I.Literal, I.GivenRef, I.ClockRef)):
            return True
        if isinstance(op, I.Arith):
            return self._only_keys(op.left, keys) and self._only_keys(op.right, keys)
        if isinstance(op, I.Negate):
            return self._only_keys(op.item, keys)
        if isinstance(op, I.Call):
            return all(self._only_keys(a, keys) for a in op.args)
        return False

    def shows(self, ctx: Ctx, items: tuple[A.ShowItemNode, ...], subject: I.Carrier) -> tuple[I.ShowTerm, ...]:
        out: list[I.ShowTerm] = []
        columns: set[str] = set()
        for item in items:
            column = item.alias.text if item.alias is not None else None
            v = item.value
            term: I.ShowTerm
            if isinstance(v, A.IdentityShow):
                term = I.ShowIdentity(column or "identity", item.loc)
            elif isinstance(v, A.CountShow):
                term = I.ShowCount(column or "count", item.loc)
            elif isinstance(v, A.RankShow):
                term = I.ShowRank(column or "rank", item.loc)
            elif isinstance(v, A.PathShow):
                path = self.resolve_path(ctx, v.path, allow_many=False)
                term = I.ShowPath(path, column or v.path.text, item.loc)
            elif isinstance(v, A.NestedShow):
                path = self.resolve_path(ctx, v.path, allow_many=True)
                if not isinstance(path.terminal, I.LinkTerminal) or not path.many:
                    refuse("NESTED_SHOW_NOT_TO_MANY", "validate", v.path, f"{v.path.text} is not a to-many link")
                end = self.r.carriers[path.terminal.target]
                inner_ctx = Ctx(ctx.module, ctx.read_qid, end.qid, ctx.givens, ctx.used_givens, ctx.static, False, True, False, False, ctx.composes, ctx.has_clock)
                inner = self.shows(inner_ctx, v.items, end)
                if v.last is not None and v.last <= 0:
                    refuse("LAST_NOT_POSITIVE", "validate", v, "last N is positive")
                term = I.ShowNested(path, inner, v.last, column or v.path.text, item.loc)
            elif isinstance(v, A.ScalarShow):
                expr = self.operand(ctx, v.scalar)
                if isinstance(expr, I.Literal):
                    refuse("SHOW_LITERAL", "validate", v, "a literal is not a result column")
                if column is None:
                    refuse("SHOW_ALIAS_REQUIRED", "validate", v, "an expression column needs `as name`")
                term = I.ShowScalar(expr, column, item.loc)
            else:
                raise TypeError(v)
            if term.column in columns:
                refuse("SHOW_COLUMN_DUPLICATED", "validate", item, f"column {term.column} shown twice")
            columns.add(term.column)
            out.append(term)
        return tuple(out)

    # ----------------------------------------------------------- compositions
    def check_compositions(self, reads: dict[str, I.Read]) -> None:
        for outer_qid, inner_qid, end, at in self._pending_composition_checks:
            outer = reads[outer_qid]
            inner = reads[inner_qid]
            if inner.subject != end and self.r.carriers[inner.subject].family != end and self.r.carriers[end].family != inner.subject:
                refuse("COMPOSE_SUBJECT_MISMATCH", "validate", at, f"{inner_qid} reads {inner.subject}; the path ends at {end}")
            if outer.is_question and not inner.is_question:
                refuse("QUESTION_COMPOSE_STATIC", "validate", at, f"question {outer_qid} composes static query {inner_qid}")
            if inner.windowed:
                refuse("QUESTION_COMPOSE_PAGED", "validate", at, f"{inner_qid} is windowed and cannot be composed")
            if inner.unscoped is not None and outer.unscoped is None:
                refuse("QUESTION_COMPOSE_UNSCOPED", "validate", at, f"{inner_qid} is unscoped; {outer_qid} is scoped")
            if inner.givens:
                refuse("COMPOSE_INNER_GIVENS", "validate", at, f"{inner_qid} declares givens; a composed read is parameterless")
        # cycles
        graph = {q.qid: set(q.composes) for q in reads.values()}
        state: dict[str, int] = {}

        def visit(q: str, path: list[str]) -> None:
            state[q] = 1
            for nxt in sorted(graph.get(q, ())):
                if state.get(nxt) == 1:
                    refuse("QUESTION_COMPOSE_CYCLE", "validate", reads[q], " -> ".join(path + [nxt]))
                if state.get(nxt) is None:
                    visit(nxt, path + [nxt])
            state[q] = 2

        for q in sorted(graph):
            if state.get(q) is None:
                visit(q, [q])
        self._pending_composition_checks = []

