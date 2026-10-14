"""Shared relational / SQLite lowering.

One lowering serves both nouns: ``execute`` (static query) and live refresh
(dynamic question) obtain their SQL from ``lower_read``. Every table and column
name comes from the world's storage binding; every join comes from a resolved
link edge. There is no schema-name branch anywhere in this module.

Reserved parameter names begin with an underscore (``:_scope``, ``:_clock``,
``:_parents``); given names may not.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import ir as I
from .refuse import Refusal, refuse
from .storage import WorldIR
from .types import sql_storage_type
from .visit import Visitor

SCOPE_PARAM = "_scope"
CLOCK_PARAM = "_clock"
PARENTS_PARAM = "_parents"
KEY_PREFIX = "$k"


def q(name: str) -> str:
    """Quote a physical identifier."""
    return '"' + name.replace('"', '""') + '"'


def sql_literal(lit: I.Literal) -> str:
    v = lit.value
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


@dataclass(frozen=True)
class ChildPlan:
    column: str
    sql: str
    params: tuple[str, ...]
    parent_column: str  # hidden column in child rows carrying the parent key
    key_columns: tuple[str, ...]
    columns: tuple[str, ...]
    children: tuple["ChildPlan", ...]


@dataclass(frozen=True)
class Plan:
    read: str
    noun: str
    sql: str
    params: tuple[str, ...]  # given names
    key_columns: tuple[str, ...]
    columns: tuple[str, ...]  # shown columns in order
    children: tuple[ChildPlan, ...]
    total_sql: str | None
    scoped: bool
    uses_clock: bool
    shape: str
    live_bound: int | None


@dataclass
class _Frame:
    """Join registry for one SELECT block rooted at a carrier alias."""

    world: WorldIR
    root_carrier: str
    root_alias: str
    joins: list[str] = field(default_factory=list)
    aliases: dict[tuple[str, ...], str] = field(default_factory=dict)
    counter: list[int] = field(default_factory=lambda: [0])
    params: set[str] = field(default_factory=set)
    uses_clock: bool = False

    def new_alias(self) -> str:
        self.counter[0] += 1
        return f"j{self.counter[0]}"

    def alias_for(self, steps: tuple[I.LinkStep, ...]) -> str:
        """Alias of the carrier reached by forward ``steps`` from the root (LEFT JOINs)."""
        if not steps:
            return self.root_alias
        key = tuple(s.link for s in steps)
        if key in self.aliases:
            return self.aliases[key]
        prev = self.alias_for(steps[:-1])
        step = steps[-1]
        if step.inverse:
            raise Refusal("LOWER_INVERSE_OUTSIDE_QUANTIFIER", "lower", "", 1, 1, f"{step.text} is to-many outside a quantifier")
        link = self.world.program.link(step.link)
        source_rel = self.world.relation_of(step.source)
        target_rel = self.world.relation_of(step.target)
        alias = self.new_alias()
        link_col = self.world.link_column_of(step.source, link)
        self.joins.append(f'LEFT JOIN {q(target_rel.table)} AS {alias} ON {alias}.{q(target_rel.identity)} = {prev}.{q(link_col)}')
        self.aliases[key] = alias
        return alias


class _Lowerer(Visitor):
    """Lower expressions and operands to SQL text within a frame."""

    def __init__(self, world: WorldIR, frame: _Frame, params_of_read: set[str]) -> None:
        self.world = world
        self.frame = frame
        self.read_params = params_of_read

    # ---------------------------------------------------------------- paths
    def column(self, path: I.PathRef, frame: _Frame | None = None) -> str:
        fr = frame or self.frame
        t = path.terminal
        if isinstance(t, I.UseTerminal):
            alias = fr.alias_for(path.steps)
            carrier = self.world.carrier(t.carrier)
            use = next(u for u in carrier.uses if u.qid == t.use)
            return f"{alias}.{q(self.world.column_of(t.carrier, use))}"
        if isinstance(t, I.LinkTerminal):
            last = path.steps[-1]
            if last.inverse:
                # the identity of the reached row (only meaningful inside a quantifier frame)
                alias = fr.alias_for(path.steps)
                return f"{alias}.{q(self.world.relation_of(t.target).identity)}"
            alias = fr.alias_for(path.steps[:-1])
            link = self.world.program.link(t.link)
            return f"{alias}.{q(self.world.link_column_of(t.carrier, link))}"
        if isinstance(t, I.IdentityTerminal):
            alias = fr.alias_for(path.steps)
            return f"{alias}.{q(self.world.relation_of(t.carrier).identity)}"
        if isinstance(t, I.KindTerminal):
            alias = fr.alias_for(path.steps)
            rel = self.world.relation_of(t.family)
            assert rel.kind is not None
            return f"{alias}.{q(rel.kind)}"
        raise TypeError(t)

    # ------------------------------------------------------------- operands
    def visit_PathRef(self, node: I.PathRef) -> str:
        return self.column(node)

    def visit_Literal(self, node: I.Literal) -> str:
        return sql_literal(node)

    def visit_GivenRef(self, node: I.GivenRef) -> str:
        self.frame.params.add(node.name)
        return f":{node.name}"

    def visit_ClockRef(self, node: I.ClockRef) -> str:
        self.frame.uses_clock = True
        return f":{CLOCK_PARAM}"

    def visit_Arith(self, node: I.Arith) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == "/":
            return f"(CAST({left} AS REAL) / {right})"
        return f"({left} {node.op} {right})"

    def visit_Negate(self, node: I.Negate) -> str:
        return f"(-{self.visit(node.item)})"

    def visit_StaticAggregate(self, node: I.StaticAggregate) -> str:
        fn = {"count": "COUNT", "sum": "SUM", "average": "AVG", "minimum": "MIN", "maximum": "MAX"}[node.fn]
        if node.path is None:
            return "COUNT(*)"
        inner = self.column(node.path)
        return f"{fn}({'DISTINCT ' if node.distinct else ''}{inner})"

    def visit_Call(self, node: I.Call) -> str:
        from .calls import REGISTRY

        sig = REGISTRY[node.function]
        args = [self.visit(a) for a in node.args]
        return sig.sql.format(*args)

    def visit_AggRef(self, node: I.AggRef) -> str:
        sub, alias = self.many_subquery(node.path)
        if node.fn == "count":
            where = ""
            if node.filter is not None:
                where = " AND " + sub.lowerer.visit(node.filter)
            return f"(SELECT COUNT(*) {sub.from_clause} WHERE {sub.correlation}{where})"
        assert node.arg is not None
        target = sub.lowerer.column(node.arg)
        fn = "MAX" if node.fn == "max" else "MIN"
        return f"(SELECT {fn}({target}) {sub.from_clause} WHERE {sub.correlation})"

    # ------------------------------------------------------------ predicates
    def guarded(self, guard: I.GivenRef | None, body: str) -> str:
        if guard is None:
            return body
        self.frame.params.add(guard.name)
        return f"(:{guard.name} IS NULL OR {body})"

    def visit_And(self, node: I.And) -> str:
        return "(" + " AND ".join(self.visit(i) for i in node.items) + ")"

    def visit_Or(self, node: I.Or) -> str:
        return "(" + " OR ".join(self.visit(i) for i in node.items) + ")"

    def visit_Not(self, node: I.Not) -> str:
        return f"(NOT {self.visit(node.item)})"

    def visit_Compare(self, node: I.Compare) -> str:
        op = {"=": "=", "!=": "<>", "<": "<", "<=": "<=", ">": ">", ">=": ">="}[node.op]
        return self.guarded(node.guard, f"({self.visit(node.left)} {op} {self.visit(node.right)})")

    def visit_Contains(self, node: I.Contains) -> str:
        return self.guarded(node.guard, f"(instr({self.visit(node.left)}, {self.visit(node.right)}) > 0)")

    def visit_In(self, node: I.In) -> str:
        right = self.visit(node.right)
        return self.guarded(node.guard, f"({self.visit(node.left)} IN (SELECT value FROM json_each({right})))")

    def visit_Is(self, node: I.Is) -> str:
        return self.guarded(node.guard, f"({self.column(node.left)} = {self.visit(node.right)})")

    def visit_Presence(self, node: I.Presence) -> str:
        return f"({self.column(node.path)} IS {'NOT ' if node.present else ''}NULL)"

    def visit_Within(self, node: I.Within) -> str:
        inner = self.world.program.read(node.inner)
        inner_sql = key_select(self.world, inner, self.frame.counter)
        self.frame.params |= set(g.name for g in inner.givens)
        if inner.unscoped is None and self.world.scope_path(inner.subject) and not self.world.world.deployment_scoped:
            self.frame.params.add(SCOPE_PARAM)
        return f"({self.column(node.path)} IN ({inner_sql}))"

    def visit_Quantified(self, node: I.Quantified) -> str:
        many_paths = collect_many_paths(node.item)
        if not many_paths:
            raise Refusal("LOWER_QUANTIFIER_WITHOUT_MANY", "lower", "", node.loc.line, node.loc.column, "quantifier without a to-many path")
        prefixes = {many_prefix(p) for p in many_paths}
        if len(prefixes) != 1:
            refuse("QUANTIFIER_MULTIPLE_MANY", "validate", node, "a quantified comparison follows one to-many path")
        prefix = next(iter(prefixes))
        sub, alias = self.many_subquery_from_prefix(prefix)
        rebased = rebase(node.item, len(prefix))
        body = sub.lowerer.visit(rebased)
        if node.kind == "some":
            return f"EXISTS (SELECT 1 {sub.from_clause} WHERE {sub.correlation} AND {body})"
        return f"NOT EXISTS (SELECT 1 {sub.from_clause} WHERE {sub.correlation} AND NOT {body})"

    def visit_Truth(self, node: I.Truth) -> str:
        return f"({self.visit(node.item)} = 1)"

    # ------------------------------------------------------------ subqueries
    def many_subquery(self, path: I.PathRef) -> tuple["_Sub", str]:
        return self.many_subquery_from_prefix(path.steps)

    def many_subquery_from_prefix(self, prefix: tuple[I.LinkStep, ...]) -> tuple["_Sub", str]:
        """A subquery FROM clause following ``prefix`` from the current frame's root.

        Forward steps before the first inverse step are taken in the outer frame
        (joins); the first inverse step starts the subquery; later steps join
        inside the subquery.
        """
        first_inverse = next(i for i, s in enumerate(prefix) if s.inverse)
        outer_alias = self.frame.alias_for(prefix[:first_inverse])
        step = prefix[first_inverse]
        link = self.world.program.link(step.link)
        source_rel = self.world.relation_of(step.target)  # carrier owning the link (reached row)
        alias = self.frame.new_alias()
        link_col = self.world.link_column_of(step.target, link)
        outer_rel = self.world.relation_of(step.source)
        correlation = f"{alias}.{q(link_col)} = {outer_alias}.{q(outer_rel.identity)}"
        sub_frame = _Frame(self.world, step.target, alias, [], {}, self.frame.counter, self.frame.params, False)
        member_pred = member_predicate(self.world, step.target, alias)
        rest = prefix[first_inverse + 1 :]
        current_alias = alias
        current_carrier = step.target
        rest_key: tuple[str, ...] = ()
        for s in rest:
            rest_key = rest_key + (s.link,)
            link2 = self.world.program.link(s.link)
            nxt = self.frame.new_alias()
            if s.inverse:
                rel2 = self.world.relation_of(s.target)
                col2 = self.world.link_column_of(s.target, link2)
                sub_frame.joins.append(f"JOIN {q(rel2.table)} AS {nxt} ON {nxt}.{q(col2)} = {current_alias}.{q(self.world.relation_of(current_carrier).identity)}")
            else:
                rel2 = self.world.relation_of(s.target)
                col2 = self.world.link_column_of(s.source, link2)
                sub_frame.joins.append(f"JOIN {q(rel2.table)} AS {nxt} ON {nxt}.{q(rel2.identity)} = {current_alias}.{q(col2)}")
            sub_frame.aliases[rest_key] = nxt
            current_alias = nxt
            current_carrier = s.target
        sub = _Sub(sub_frame, source_rel.table, alias, correlation + (f" AND {member_pred}" if member_pred else ""), _Lowerer(self.world, sub_frame, self.read_params))
        return sub, current_alias


@dataclass
class _Sub:
    frame: _Frame
    table: str
    alias: str
    correlation: str
    lowerer: "_Lowerer"

    @property
    def from_clause(self) -> str:
        return f"FROM {q(self.table)} AS {self.alias}" + ("".join(" " + j for j in self.frame.joins))


def member_predicate(world: WorldIR, carrier_qid: str, alias: str) -> str:
    c = world.carrier(carrier_qid)
    if c.kind != "member":
        return ""
    rel = world.relation_of(carrier_qid)
    assert rel.kind is not None
    return f"{alias}.{q(rel.kind)} = '{c.name}'"


def collect_many_paths(expr: object) -> list[I.PathRef]:
    out: list[I.PathRef] = []
    if isinstance(expr, I.PathRef):
        if expr.many:
            out.append(expr)
        return out
    if hasattr(expr, "__dataclass_fields__"):
        for name in expr.__dataclass_fields__:  # type: ignore[attr-defined]
            if name == "loc":
                continue
            out.extend(collect_many_paths(getattr(expr, name)))
    elif isinstance(expr, (list, tuple)):
        for x in expr:
            out.extend(collect_many_paths(x))
    return out


def many_prefix(path: I.PathRef) -> tuple[I.LinkStep, ...]:
    last_inverse = max(i for i, s in enumerate(path.steps) if s.inverse)
    return path.steps[: last_inverse + 1]


def rebase(expr: object, drop: int) -> object:
    """Re-root every path by dropping ``drop`` leading steps (inside a subquery)."""
    if isinstance(expr, I.PathRef):
        if not expr.steps[:drop] or len(expr.steps) < drop:
            return expr
        steps = expr.steps[drop:]
        root = expr.steps[drop - 1].target
        return I.PathRef(root, steps, expr.terminal, expr.text, expr.loc)
    if hasattr(expr, "__dataclass_fields__"):
        values = {}
        for name in expr.__dataclass_fields__:  # type: ignore[attr-defined]
            value = getattr(expr, name)
            values[name] = value if name == "loc" else rebase(value, drop)
        return type(expr)(**values)
    if isinstance(expr, tuple):
        return tuple(rebase(x, drop) for x in expr)
    if isinstance(expr, list):
        return [rebase(x, drop) for x in expr]
    return expr


# ------------------------------------------------------------------ scoping


def scope_predicate(world: WorldIR, alias: str, carrier_qid: str, path: tuple[str, ...], counter: list[int]) -> str:
    """``alias`` row belongs to scope ``:_scope`` by following ``path`` (link qids)."""
    link_qid = path[0]
    link = world.program.link(link_qid)
    col = world.link_column_of(carrier_qid, link)
    if len(path) == 1:
        return f"{alias}.{q(col)} = :{SCOPE_PARAM}"
    target_rel = world.relation_of(link.target)
    counter[0] += 1
    inner_alias = f"p{counter[0]}"
    inner = scope_predicate(world, inner_alias, link.target, path[1:], counter)
    return f"{alias}.{q(col)} IN (SELECT {inner_alias}.{q(target_rel.identity)} FROM {q(target_rel.table)} AS {inner_alias} WHERE {inner})"


def base_predicates(world: WorldIR, read: I.Read, alias: str, counter: list[int], params: set[str]) -> list[str]:
    """Member discriminator, archived filter, and scope weaving for the subject."""
    subject = world.carrier(read.subject)
    out: list[str] = []
    mp = member_predicate(world, read.subject, alias)
    if mp:
        out.append(mp)
    if subject.lifecycle == "archived_by" and not read.including_archived:
        assert subject.archived_by is not None
        use = subject.use_named(subject.archived_by.rsplit(".", 1)[-1])
        assert use is not None
        out.append(f"{alias}.{q(world.column_of(read.subject, use))} IS NULL")
    path = world.scope_path(read.subject)
    if read.unscoped is None and path and not world.world.deployment_scoped:
        out.append(scope_predicate(world, alias, read.subject, path, counter))
        params.add(SCOPE_PARAM)
    return out


# ------------------------------------------------------------ read lowering


def key_select(world: WorldIR, read: I.Read, counter: list[int]) -> str:
    """``SELECT identity FROM ...`` of a read, for composition (within)."""
    rel = world.relation_of(read.subject)
    alias = f"c{counter[0] + 1}"
    counter[0] += 1
    frame = _Frame(world, read.subject, alias, [], {}, counter, set(), False)
    low = _Lowerer(world, frame, set(g.name for g in read.givens))
    preds = base_predicates(world, read, alias, counter, frame.params)
    if read.predicate is not None:
        preds.append(low.visit(read.predicate))
    where = f" WHERE {' AND '.join(preds)}" if preds else ""
    joins = "".join(" " + j for j in frame.joins)
    return f"SELECT {alias}.{q(rel.identity)} FROM {q(rel.table)} AS {alias}{joins}{where}"


class _ShowLowerer(Visitor):
    def __init__(self, low: _Lowerer, world: WorldIR, read: I.Read, alias: str) -> None:
        self.low = low
        self.world = world
        self.read = read
        self.alias = alias
        self.children: list[ChildPlan] = []
        self.columns: list[str] = []

    def visit_ShowPath(self, node: I.ShowPath) -> str | None:
        self.columns.append(node.column)
        return f"{self.low.column(node.path)} AS {q(node.column)}"

    def visit_ShowIdentity(self, node: I.ShowIdentity) -> str | None:
        self.columns.append(node.column)
        rel = self.world.relation_of(self.read.subject)
        return f"{self.alias}.{q(rel.identity)} AS {q(node.column)}"

    def visit_ShowCount(self, node: I.ShowCount) -> str | None:
        self.columns.append(node.column)
        return f"COUNT(*) AS {q(node.column)}"

    def visit_ShowRank(self, node: I.ShowRank) -> str | None:
        self.columns.append(node.column)
        order = order_clause(self.low, self.world, self.read, self.alias, with_tiebreak=True)
        return f"ROW_NUMBER() OVER (ORDER BY {order}) AS {q(node.column)}"

    def visit_ShowScalar(self, node: I.ShowScalar) -> str | None:
        self.columns.append(node.column)
        return f"{self.low.visit(node.expr)} AS {q(node.column)}"

    def visit_ShowNested(self, node: I.ShowNested) -> str | None:
        self.columns.append(node.column)
        self.children.append(lower_nested(self.world, self.read, node, self.low.frame.counter))
        return None


def order_clause(low: _Lowerer, world: WorldIR, read: I.Read, alias: str, *, with_tiebreak: bool) -> str:
    parts = []
    for o in read.orders:
        parts.append(f"{low.visit(o.key)} {'DESC' if o.descending else 'ASC'}")
    if with_tiebreak:
        if read.shape == "grouped":
            for g in read.group_by:
                parts.append(f"{low.column(g)} ASC")
        elif read.distinct:
            pass
        else:
            rel = world.relation_of(read.subject)
            parts.append(f"{alias}.{q(rel.identity)} ASC")
    return ", ".join(parts)


def lower_nested(world: WorldIR, read: I.Read, node: I.ShowNested, counter: list[int]) -> ChildPlan:
    """A child SELECT returning rows of the to-many path for a set of parent identities."""
    prefix = many_prefix(node.path)
    if len(prefix) != 1 or node.path.steps != prefix:
        refuse("NESTED_SHOW_PATH", "validate", node, "a nested show follows one inverse link")
    step = prefix[0]
    child_qid = step.target
    link = world.program.link(step.link)
    child_rel = world.relation_of(child_qid)
    parent_col = world.link_column_of(child_qid, link)
    counter[0] += 1
    alias = f"n{counter[0]}"
    frame = _Frame(world, child_qid, alias, [], {}, counter, set(), False)
    low = _Lowerer(world, frame, set(g.name for g in read.givens))
    child = world.carrier(child_qid)
    inner_read = I.Read(
        read.noun, f"{read.qid}[{node.column}]", read.module, read.name, child_qid, "", read.givens, None, node.items, (), (),
        None, False, "collection", None, None, None, False, True, read.unscoped, None, None, (), node.loc,
    )
    shows = _ShowLowerer(low, world, inner_read, alias)
    select_parts = [f"{alias}.{q(parent_col)} AS {q('$parent')}", f"{alias}.{q(child_rel.identity)} AS {q('$k0')}"]
    for item in node.items:
        part = shows.visit(item)
        if part is not None:
            select_parts.append(part)
    # ordering: the child's order-flagged uses, then identity
    order_parts = []
    for u in child.uses:
        if u.order:
            order_parts.append(f"{alias}.{q(world.column_of(child_qid, u))}")
    order_parts.append(f"{alias}.{q(child_rel.identity)}")
    preds = [f"{alias}.{q(parent_col)} IN (SELECT value FROM json_each(:{PARENTS_PARAM}))"]
    mp = member_predicate(world, child_qid, alias)
    if mp:
        preds.append(mp)
    joins = "".join(" " + j for j in frame.joins)
    cols = ", ".join(select_parts)
    asc = ", ".join(f"{p} ASC" for p in order_parts)
    if node.last is not None:
        desc = ", ".join(f"{p} DESC" for p in order_parts)
        inner = (
            f"SELECT {cols}, ROW_NUMBER() OVER (PARTITION BY {alias}.{q(parent_col)} ORDER BY {desc}) AS {q('$rn')} "
            f"FROM {q(child_rel.table)} AS {alias}{joins} WHERE {' AND '.join(preds)}"
        )
        outer_cols = ", ".join(q(c) for c in ["$parent", "$k0"] + shows.columns)
        order_outer = ", ".join(f"{q(c)} ASC" for c in ["$parent"]) + ", " + q("$rn") + " DESC"
        sql = f"SELECT {outer_cols} FROM ({inner}) WHERE {q('$rn')} <= {node.last} ORDER BY {order_outer}"
    else:
        sql = f"SELECT {cols} FROM {q(child_rel.table)} AS {alias}{joins} WHERE {' AND '.join(preds)} ORDER BY {alias}.{q(parent_col)} ASC, {asc}"
    return ChildPlan(node.column, sql, tuple(sorted(frame.params)), "$parent", ("$k0",), tuple(shows.columns), tuple(shows.children))


def lower_read(world: WorldIR, read: I.Read) -> Plan:
    """Lower a query or question to its execution plan (shared by both nouns)."""
    for g in read.givens:
        if g.name.startswith("_"):
            refuse("GIVEN_NAME_RESERVED", "validate", g, "given names beginning with _ are reserved for engine parameters")
    rel = world.relation_of(read.subject)
    alias = "s0"
    counter = [0]
    frame = _Frame(world, read.subject, alias, [], {}, counter, set(), False)
    low = _Lowerer(world, frame, set(g.name for g in read.givens))
    preds = base_predicates(world, read, alias, counter, frame.params)
    if read.by is not None:
        preds.append(f"{alias}.{q(rel.identity)} = :{read.by.name}")
        frame.params.add(read.by.name)
    if read.predicate is not None:
        preds.append(low.visit(read.predicate))
    # keys
    key_columns: list[str] = []
    select_parts: list[str] = []
    if read.shape == "grouped":
        for index, g in enumerate(read.group_by):
            name = f"{KEY_PREFIX}{index}"
            key_columns.append(name)
            select_parts.append(f"{low.column(g)} AS {q(name)}")
    elif read.distinct:
        pass
    else:
        key_columns.append(f"{KEY_PREFIX}0")
        select_parts.append(f"{alias}.{q(rel.identity)} AS {q(KEY_PREFIX + '0')}")
    shows = _ShowLowerer(low, world, read, alias)
    if read.shows:
        for item in read.shows:
            part = shows.visit(item)
            if part is not None:
                select_parts.append(part)
    else:
        # no show list: every use of the subject, in declaration order
        subject = world.carrier(read.subject)
        for u in subject.uses:
            col = u.intent.rsplit(".", 1)[-1]
            shows.columns.append(col)
            select_parts.append(f"{alias}.{q(world.column_of(read.subject, u))} AS {q(col)}")
    if read.distinct:
        key_columns = list(shows.columns)
    group = ""
    if read.shape == "grouped" and read.group_by:
        group = " GROUP BY " + ", ".join(low.column(g) for g in read.group_by)
    having = ""
    if read.having is not None:
        having = " HAVING " + low.visit(read.having)
    order = order_clause(low, world, read, alias, with_tiebreak=not (read.shape == "grouped" and not read.group_by))
    order_sql = f" ORDER BY {order}" if order else ""
    limit = ""
    if read.shape == "optional_single":
        limit = " LIMIT 1"
    elif read.first is not None:
        limit = f" LIMIT {read.first}"
    elif read.page is not None and read.limit is not None:
        limit = f" LIMIT :{read.limit.name} OFFSET (:{read.page.name} - 1) * :{read.limit.name}"
        frame.params.add(read.page.name)
        frame.params.add(read.limit.name)
    joins = "".join(" " + j for j in frame.joins)
    where = f" WHERE {' AND '.join(preds)}" if preds else ""
    distinct = "DISTINCT " if read.distinct else ""
    sql = f"SELECT {distinct}{', '.join(select_parts)} FROM {q(rel.table)} AS {alias}{joins}{where}{group}{having}{order_sql}{limit}"
    total_sql = None
    if read.with_total:
        if read.shape == "grouped":
            total_sql = f"SELECT COUNT(*) FROM (SELECT 1 FROM {q(rel.table)} AS {alias}{joins}{where}{group}{having})"
        else:
            total_sql = f"SELECT COUNT(*) FROM {q(rel.table)} AS {alias}{joins}{where}"
    params = tuple(sorted(p for p in frame.params if not p.startswith("_")))
    scoped = SCOPE_PARAM in frame.params
    return Plan(read.qid, read.noun, sql, params, tuple(key_columns), tuple(shows.columns), tuple(shows.children), total_sql, scoped, frame.uses_clock, read.shape, read.live_bound)


# ------------------------------------------------------------------- DDL


def lower_ddl(world: WorldIR) -> str:
    """Schema DDL: tables, keys, checks, enforced foreign keys, engine tables, capture triggers."""
    program = world.program
    statements: list[str] = []
    for c in world.relations:
        rel = world.storage.relation(c.qid)
        cols = [f"{q(rel.identity)} INTEGER PRIMARY KEY"]
        checks: list[str] = []
        fks: list[str] = []
        uniques: list[str] = []
        from .storage import expected_relation_keys

        uses, links = expected_relation_keys(program, c)
        key_cols: list[str] = []
        for key, u in uses.items():
            col = rel.columns[key]
            optional = u.optional or key.rsplit(".", 1)[0] != c.qid  # member-only uses are nullable at the family table
            spec = f"{q(col)} {sql_storage_type(u.type)}"
            if not optional:
                spec += " NOT NULL"
            if isinstance(u.default, I.Literal):
                spec += f" DEFAULT {sql_literal(u.default)}"
            cols.append(spec)
            if u.type.is_closed:
                members = ", ".join("'" + m[1:].replace("'", "''") + "'" for m in u.type.closed)
                checks.append(f"CHECK ({q(col)} IN ({members}))")
            if u.key and key.rsplit(".", 1)[0] == c.qid:
                key_cols.append(col)
        for key, l in links.items():
            col = rel.links[key]
            optional = l.optional or key.rsplit(".", 1)[0] != c.qid
            spec = f"{q(col)} INTEGER"
            if not optional:
                spec += " NOT NULL"
            cols.append(spec)
            if l.enforcement != "unenforced":
                target_rel = world.relation_of(l.target)
                action = {"restrict": "RESTRICT", "cascade": "CASCADE", "detach": "SET NULL"}[l.enforcement]
                fks.append(f"FOREIGN KEY ({q(col)}) REFERENCES {q(target_rel.table)}({q(target_rel.identity)}) ON DELETE {action}")
            if l.key and key.rsplit(".", 1)[0] == c.qid:
                key_cols.append(col)
        if rel.kind is not None:
            members = ", ".join("'" + program.carrier(m).name + "'" for m in c.members)
            cols.append(f"{q(rel.kind)} TEXT NOT NULL CHECK ({q(rel.kind)} IN ({members}))")
        if key_cols:
            uniques.append("UNIQUE (" + ", ".join(q(k) for k in key_cols) + ")")
        body = ",\n  ".join(cols + checks + uniques + fks)
        statements.append(f"CREATE TABLE {q(rel.table)} (\n  {body}\n);")
    eng = world.storage.engine
    statements.append(
        f"CREATE TABLE {q(eng.generations)} (\n  ordinal INTEGER PRIMARY KEY,\n  ir_digest TEXT NOT NULL,\n  storage_digest TEXT NOT NULL,\n  shipped_at_revision INTEGER NOT NULL\n);"
    )
    statements.append(f"CREATE TABLE {q(eng.revisions)} (\n  revision INTEGER PRIMARY KEY,\n  writer TEXT NOT NULL,\n  transaction_id TEXT NOT NULL\n);")
    statements.append(
        f"CREATE TABLE {q(eng.ledger)} (\n  revision INTEGER NOT NULL,\n  ordinal INTEGER NOT NULL,\n  carrier TEXT NOT NULL,\n  identity INTEGER NOT NULL,\n  operation TEXT NOT NULL CHECK (operation IN ('insert', 'update', 'delete')),\n  changes TEXT NOT NULL,\n  scope_before TEXT,\n  scope_after TEXT,\n  writer TEXT NOT NULL,\n  transaction_id TEXT NOT NULL,\n  PRIMARY KEY (revision, ordinal)\n);"
    )
    if world.world.writers == "external_captured":
        statements.extend(lower_capture_ddl(world))
    return "\n\n".join(statements) + "\n"


def lower_capture_ddl(world: WorldIR) -> list[str]:
    """Changelog tables and the declared triggers that fill them."""
    from .storage import expected_relation_keys

    out: list[str] = []
    for c in world.relations:
        rel = world.storage.relation(c.qid)
        cap = rel.capture
        assert cap is not None
        uses, links = expected_relation_keys(world.program, c)
        cols = [f"{q(cap.seq)} INTEGER PRIMARY KEY AUTOINCREMENT", f"{q(cap.op)} TEXT NOT NULL", f"{q(cap.revision)} INTEGER", f"{q(cap.identity)} INTEGER NOT NULL"]
        pairs: list[tuple[str, str]] = []  # (table column, changelog column)
        for key, u in uses.items():
            cols.append(f"{q(cap.columns[key])} {sql_storage_type(u.type)}")
            pairs.append((rel.columns[key], cap.columns[key]))
        for key in links:
            cols.append(f"{q(cap.links[key])} INTEGER")
            pairs.append((rel.links[key], cap.links[key]))
        out.append(f"CREATE TABLE {q(cap.table)} (\n  " + ",\n  ".join(cols) + "\n);")
        log_cols = ", ".join([q(cap.op), q(cap.identity)] + [q(p[1]) for p in pairs])

        def values_of(op: str, row: str) -> str:
            return ", ".join([f"'{op}'", f"{row}.{q(rel.identity)}"] + [f"{row}.{q(p[0])}" for p in pairs])

        for op in ("insert", "update", "delete"):
            trigger = f"{cap.table}__{op}"
            if op == "update":
                body = (
                    f"  INSERT INTO {q(cap.table)} ({log_cols}) VALUES ({values_of('before', 'OLD')});\n"
                    f"  INSERT INTO {q(cap.table)} ({log_cols}) VALUES ({values_of('update', 'NEW')});"
                )
            else:
                body = f"  INSERT INTO {q(cap.table)} ({log_cols}) VALUES ({values_of(op, 'NEW' if op == 'insert' else 'OLD')});"
            out.append(f"CREATE TRIGGER {q(trigger)} AFTER {op.upper()} ON {q(rel.table)}\nBEGIN\n{body}\nEND;")
    return out
