"""Footprints: what writes can change a question's result.

Derived recursively from the resolved question IR through an exhaustive
visitor. An atom is (carrier, field) where field is a use qid, a link qid, or
"*" for structural changes (insert/delete). Composition includes the inner
question's atoms; scope paths are included because a scope move changes
membership.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import ir as I
from .refuse import Refusal
from .storage import WorldIR
from .visit import Visitor

STRUCTURE = "*"


@dataclass(frozen=True)
class Atom:
    carrier: str
    field: str

    def as_dict(self) -> dict[str, str]:
        return {"carrier": self.carrier, "field": self.field}


@dataclass(frozen=True)
class Footprint:
    read: str
    subject: str
    atoms: tuple[Atom, ...]
    composes: tuple[str, ...]
    scope_links: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "read": self.read,
            "subject": self.subject,
            "atoms": [a.as_dict() for a in self.atoms],
            "composes": list(self.composes),
            "scope_links": list(self.scope_links),
        }


def _static_only(node: object) -> Refusal:
    loc = getattr(node, "loc", None)
    return Refusal("QUESTION_NOT_FOOTPRINTABLE", "validate", getattr(loc, "file", ""), getattr(loc, "line", 1), getattr(loc, "column", 1), f"{type(node).__name__} is a static-only construct")


class FootprintDeriver(Visitor):
    def __init__(self, world: WorldIR) -> None:
        self.world = world
        self.atoms: set[Atom] = set()
        self.composes: list[str] = []
        self._stack: list[str] = []

    # ---------------------------------------------------------------- paths
    def path(self, p: I.PathRef) -> None:
        for step in p.steps:
            owner = step.target if step.inverse else step.source
            self.atoms.add(Atom(owner, step.link))
            self.atoms.add(Atom(step.target, STRUCTURE))
        t = p.terminal
        if isinstance(t, I.UseTerminal):
            self.atoms.add(Atom(t.carrier, t.use))
        elif isinstance(t, I.LinkTerminal):
            if p.steps and p.steps[-1].inverse:
                self.atoms.add(Atom(t.target, STRUCTURE))
            else:
                self.atoms.add(Atom(t.carrier, t.link))
        elif isinstance(t, I.IdentityTerminal):
            self.atoms.add(Atom(t.carrier, STRUCTURE))
        elif isinstance(t, I.KindTerminal):
            pass
        else:
            raise TypeError(t)

    # ------------------------------------------------------------- operands
    def visit_PathRef(self, node: I.PathRef) -> None:
        self.path(node)

    def visit_Literal(self, node: I.Literal) -> None:
        pass

    def visit_GivenRef(self, node: I.GivenRef) -> None:
        pass

    def visit_ClockRef(self, node: I.ClockRef) -> None:
        raise _static_only(node)

    def visit_AggRef(self, node: I.AggRef) -> None:
        self.path(node.path)
        if node.filter is not None:
            self.visit(node.filter)
        if node.arg is not None:
            self.path(node.arg)

    def visit_Arith(self, node: I.Arith) -> None:
        raise _static_only(node)

    def visit_Negate(self, node: I.Negate) -> None:
        raise _static_only(node)

    def visit_StaticAggregate(self, node: I.StaticAggregate) -> None:
        raise _static_only(node)

    def visit_Call(self, node: I.Call) -> None:
        raise _static_only(node)

    # ----------------------------------------------------------- predicates
    def visit_And(self, node: I.And) -> None:
        for i in node.items:
            self.visit(i)

    def visit_Or(self, node: I.Or) -> None:
        for i in node.items:
            self.visit(i)

    def visit_Not(self, node: I.Not) -> None:
        self.visit(node.item)

    def visit_Compare(self, node: I.Compare) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_Contains(self, node: I.Contains) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_In(self, node: I.In) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_Is(self, node: I.Is) -> None:
        self.path(node.left)
        self.visit(node.right)

    def visit_Presence(self, node: I.Presence) -> None:
        self.path(node.path)

    def visit_Within(self, node: I.Within) -> None:
        self.path(node.path)
        inner = self.world.program.read(node.inner)
        if node.inner in self._stack:
            raise Refusal("QUESTION_COMPOSE_CYCLE", "validate", "", node.loc.line, node.loc.column, " -> ".join(self._stack + [node.inner]))
        self.composes.append(node.inner)
        self.derive_into(inner)

    def visit_Quantified(self, node: I.Quantified) -> None:
        self.visit(node.item)

    def visit_Truth(self, node: I.Truth) -> None:
        raise _static_only(node)

    # ----------------------------------------------------------------- shows
    def visit_ShowPath(self, node: I.ShowPath) -> None:
        self.path(node.path)

    def visit_ShowIdentity(self, node: I.ShowIdentity) -> None:
        pass

    def visit_ShowCount(self, node: I.ShowCount) -> None:
        pass

    def visit_ShowRank(self, node: I.ShowRank) -> None:
        pass

    def visit_ShowScalar(self, node: I.ShowScalar) -> None:
        raise _static_only(node)

    def visit_ShowNested(self, node: I.ShowNested) -> None:
        self.path(node.path)
        for item in node.items:
            self.visit(item)
        child = self.world.carrier(node.path.terminal.target)  # type: ignore[union-attr]
        for u in child.uses:
            if u.order:
                self.atoms.add(Atom(child.qid, u.qid))

    # ----------------------------------------------------------------- reads
    def derive_into(self, read: I.Read) -> None:
        self._stack.append(read.qid)
        subject = self.world.carrier(read.subject)
        self.atoms.add(Atom(read.subject, STRUCTURE))
        if subject.kind == "member" and subject.family:
            self.atoms.add(Atom(subject.family, STRUCTURE))
        if subject.lifecycle == "archived_by" and subject.archived_by:
            use = subject.use_named(subject.archived_by.rsplit(".", 1)[-1])
            assert use is not None
            self.atoms.add(Atom(read.subject, use.qid))
        if read.predicate is not None:
            self.visit(read.predicate)
        for s in read.shows:
            self.visit(s)
        for o in read.orders:
            self.visit(o.key)
        for g in read.group_by:
            self.path(g)
        if read.having is not None:
            raise _static_only(read.having)
        if read.distinct:
            raise _static_only(read)
        for link_qid in self.scope_links_of(read):
            self.atoms.add(Atom(link_qid.rsplit(".", 1)[0], link_qid))
        self._stack.pop()

    def scope_links_of(self, read: I.Read) -> tuple[str, ...]:
        if read.unscoped is not None or self.world.world.deployment_scoped:
            return ()
        return self.world.scope_path(read.subject)


def derive_footprint(world: WorldIR, read: I.Read) -> Footprint:
    if not read.is_question:
        raise Refusal("QUERY_NOT_LIVE", "validate", read.loc.file, read.loc.line, read.loc.column, f"{read.qid} is a static query; it derives no footprint")
    d = FootprintDeriver(world)
    d.derive_into(read)
    atoms = tuple(sorted(d.atoms, key=lambda a: (a.carrier, a.field)))
    return Footprint(read.qid, read.subject, atoms, tuple(d.composes), d.scope_links_of(read))
