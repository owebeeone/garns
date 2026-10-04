"""Typed, qualified intermediate representation.

Everything downstream (storage, SQL, footprints, ledger, capture, surfaces,
evolution) consumes these frozen nodes. Every identity is qualified by its
owning module; bare names never leave the resolver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Union

from .ast import Loc
from .types import TypeRef


# --- provenance ---------------------------------------------------------------


@dataclass(frozen=True)
class Reference:
    """One identifier occurrence bound to a qualified identity."""

    file: str
    line: int
    column: int
    text: str
    identity: str
    role: str


# --- declarations --------------------------------------------------------------


@dataclass(frozen=True)
class Literal:
    type: TypeRef
    value: object

    def canonical(self) -> object:
        return self.value


@dataclass(frozen=True)
class Intent:
    qid: str
    module: str
    name: str
    meaning: str
    type: TypeRef
    alias: str | None
    renamed_from: str | None  # qualified previous identity
    pattern: str | None
    length: tuple[int, int | None] | None
    dimension: int | None
    retype: tuple[str, str, str] | None  # (previous base type, forward adapter, backward adapter)
    retired: str | None  # disposition
    restore: bool
    loc: Loc


@dataclass(frozen=True)
class Newtype:
    qid: str
    module: str
    name: str
    meaning: str
    of: TypeRef
    loc: Loc


@dataclass(frozen=True)
class Use:
    carrier: str  # owning (composed) carrier qid
    intent: str  # intent qid
    type: TypeRef
    key: bool
    optional: bool
    filter: bool
    order: bool
    stamp: str | None  # on_mint | on_change
    default: Union[Literal, str, None]  # literal | "ship_clock"
    repair: Union[Literal, str, None]
    origin: str  # "own" or the trait qid the use came from
    loc: Loc

    @property
    def qid(self) -> str:
        return f"{self.carrier}.{self.intent.rsplit('.', 1)[-1]}"

    @property
    def engine_owned(self) -> bool:
        return self.stamp is not None


@dataclass(frozen=True)
class Link:
    qid: str  # carrier qid + "." + link name
    carrier: str
    name: str
    target: str  # carrier qid
    enforcement: str  # restrict | cascade | detach | unenforced
    scopes: bool
    inverse: str | None
    optional: bool
    key: bool
    filter: bool
    order: bool
    default: Union[Literal, str, None]
    origin: str
    loc: Loc


@dataclass(frozen=True)
class InverseEdge:
    """A reverse traversal into ``carrier`` under the link's inverse name."""

    name: str
    link: str  # link qid on the source carrier
    source: str  # carrier qid that owns the link
    many: bool


@dataclass(frozen=True)
class Carrier:
    qid: str
    module: str
    name: str
    kind: str  # trait | resource | event | association | family | member
    meaning: str
    uses: tuple[Use, ...]
    links: tuple[Link, ...]
    carries: tuple[str, ...]
    lifecycle: str | None  # mutable | retirable | archived_by
    archived_by: str | None  # intent qid
    ordered_within: str | None  # link qid
    history_kept: bool
    breaking: tuple[str, ...]
    tightens: tuple[tuple[str, Union[Literal, str]], ...]
    invariants: tuple["Expr", ...]
    scope_via: str | None  # link qid
    family: str | None
    members: tuple[str, ...]
    inverses: tuple[InverseEdge, ...]
    loc: Loc

    @property
    def is_storable(self) -> bool:
        return self.kind not in ("trait", "member")

    def use_named(self, local: str) -> Use | None:
        for u in self.uses:
            if u.intent.rsplit(".", 1)[-1] == local or u.intent == local:
                return u
        return None

    def link_named(self, local: str) -> Link | None:
        for l in self.links:
            if l.name == local:
                return l
        return None

    def inverse_named(self, local: str) -> InverseEdge | None:
        for e in self.inverses:
            if e.name == local:
                return e
        return None

    @property
    def key_columns(self) -> tuple[str, ...]:
        keys = [u.qid for u in self.uses if u.key] + [l.qid for l in self.links if l.key]
        return tuple(keys)


# --- expressions ---------------------------------------------------------------


@dataclass(frozen=True)
class LinkStep:
    link: str
    source: str
    target: str
    inverse: bool
    many: bool
    text: str


@dataclass(frozen=True)
class UseTerminal:
    carrier: str
    use: str  # use qid
    intent: str
    type: TypeRef


@dataclass(frozen=True)
class LinkTerminal:
    carrier: str
    link: str
    target: str
    optional: bool


@dataclass(frozen=True)
class IdentityTerminal:
    carrier: str


@dataclass(frozen=True)
class KindTerminal:
    family: str


Terminal = Union[UseTerminal, LinkTerminal, IdentityTerminal, KindTerminal]


@dataclass(frozen=True)
class PathRef:
    root: str
    steps: tuple[LinkStep, ...]
    terminal: Terminal
    text: str
    loc: Loc

    @property
    def many(self) -> bool:
        return any(s.many for s in self.steps)

    @property
    def type(self) -> TypeRef:
        t = self.terminal
        if isinstance(t, UseTerminal):
            return t.type
        if isinstance(t, LinkTerminal):
            return TypeRef("Id", "text", optional=t.optional, carrier=t.target)
        if isinstance(t, IdentityTerminal):
            return TypeRef("Id", "text", carrier=t.carrier)
        if isinstance(t, KindTerminal):
            return TypeRef("Text", "text")
        raise TypeError(t)

    @property
    def end_carrier(self) -> str:
        return self.steps[-1].target if self.steps else self.root


@dataclass(frozen=True)
class GivenRef:
    name: str
    type: TypeRef
    loc: Loc


@dataclass(frozen=True)
class ClockRef:
    loc: Loc


@dataclass(frozen=True)
class AggRef:
    """Dynamic: ``path count(filter)`` | ``path max(arg)`` | ``path min(arg)``."""

    path: PathRef  # to-many link terminal
    fn: str
    filter: Union["Expr", None]
    arg: PathRef | None
    type: TypeRef
    loc: Loc


@dataclass(frozen=True)
class Arith:
    op: str
    left: "Operand"
    right: "Operand"
    type: TypeRef
    loc: Loc


@dataclass(frozen=True)
class Negate:
    item: "Operand"
    type: TypeRef
    loc: Loc


@dataclass(frozen=True)
class StaticAggregate:
    fn: str  # count | sum | average | minimum | maximum
    distinct: bool
    path: PathRef | None
    type: TypeRef
    loc: Loc


@dataclass(frozen=True)
class Call:
    function: str  # registry qid
    args: tuple["Operand", ...]
    type: TypeRef
    loc: Loc


Operand = Union[PathRef, Literal, GivenRef, ClockRef, AggRef, Arith, Negate, StaticAggregate, Call]


@dataclass(frozen=True)
class And:
    items: tuple["Expr", ...]
    loc: Loc


@dataclass(frozen=True)
class Or:
    items: tuple["Expr", ...]
    loc: Loc


@dataclass(frozen=True)
class Not:
    item: "Expr"
    loc: Loc


@dataclass(frozen=True)
class Compare:
    left: Operand
    op: str
    right: Operand
    guard: GivenRef | None
    loc: Loc


@dataclass(frozen=True)
class Contains:
    left: Operand
    right: Operand
    guard: GivenRef | None
    loc: Loc


@dataclass(frozen=True)
class In:
    left: Operand
    right: Operand
    guard: GivenRef | None
    loc: Loc


@dataclass(frozen=True)
class Is:
    left: PathRef
    right: Operand
    guard: GivenRef | None
    loc: Loc


@dataclass(frozen=True)
class Presence:
    path: PathRef
    present: bool
    guard: GivenRef | None
    loc: Loc


@dataclass(frozen=True)
class Within:
    path: PathRef  # link terminal or identity
    inner: str  # read qid
    loc: Loc


@dataclass(frozen=True)
class Quantified:
    kind: str  # some | every
    item: "Expr"
    loc: Loc


@dataclass(frozen=True)
class Truth:
    """A boolean-typed scalar used as a predicate (static algebra)."""

    item: Operand
    loc: Loc


Expr = Union[And, Or, Not, Compare, Contains, In, Is, Presence, Within, Quantified, Truth]


# --- reads ---------------------------------------------------------------------


@dataclass(frozen=True)
class Given:
    name: str
    type: TypeRef
    default: Literal | None
    loc: Loc


@dataclass(frozen=True)
class ShowPath:
    path: PathRef
    column: str
    loc: Loc


@dataclass(frozen=True)
class ShowIdentity:
    column: str
    loc: Loc


@dataclass(frozen=True)
class ShowCount:
    column: str
    loc: Loc


@dataclass(frozen=True)
class ShowRank:
    column: str
    loc: Loc


@dataclass(frozen=True)
class ShowScalar:
    expr: Operand
    column: str
    loc: Loc


@dataclass(frozen=True)
class ShowNested:
    path: PathRef  # to-many
    items: tuple["ShowTerm", ...]
    last: int | None
    column: str
    loc: Loc


ShowTerm = Union[ShowPath, ShowIdentity, ShowCount, ShowRank, ShowScalar, ShowNested]


@dataclass(frozen=True)
class OrderTerm:
    key: Operand
    descending: bool
    loc: Loc


@dataclass(frozen=True)
class Read:
    noun: str  # query | question
    qid: str
    module: str
    name: str
    subject: str
    meaning: str
    givens: tuple[Given, ...]
    predicate: Expr | None
    shows: tuple[ShowTerm, ...]
    orders: tuple[OrderTerm, ...]
    group_by: tuple[PathRef, ...]
    having: Expr | None
    distinct: bool
    shape: str  # collection | optional_single | grouped | windowed
    first: int | None
    page: GivenRef | None
    limit: GivenRef | None
    with_total: bool
    including_archived: bool
    unscoped: str | None
    by: GivenRef | None
    live_bound: int | None
    composes: tuple[str, ...]
    loc: Loc

    @property
    def is_question(self) -> bool:
        return self.noun == "question"

    @property
    def paged(self) -> bool:
        return self.page is not None or self.limit is not None

    @property
    def windowed(self) -> bool:
        return self.first is not None or self.paged or self.shape == "optional_single"


# --- verbs ---------------------------------------------------------------------


@dataclass(frozen=True)
class Alias:
    qid: str
    module: str
    name: str
    carrier: str
    verb: str
    unscoped: str | None
    loc: Loc


@dataclass(frozen=True)
class SetTerm:
    use: str  # use qid
    given: str | None  # None means absent
    loc: Loc


@dataclass(frozen=True)
class Bulk:
    qid: str
    module: str
    name: str
    meaning: str
    givens: tuple[Given, ...]
    carrier: str
    verb: str
    over: str  # read qid
    sets: tuple[SetTerm, ...]
    loc: Loc


@dataclass(frozen=True)
class Restricted:
    qid: str
    module: str
    name: str
    meaning: str
    carrier: str
    verb: str
    accepts: tuple[str, ...]  # use/link qids
    unscoped: str | None
    loc: Loc


@dataclass(frozen=True)
class Bind:
    link: str  # link qid
    step: str
    loc: Loc


@dataclass(frozen=True)
class Step:
    name: str
    carrier: str
    verb: str
    each: str | None
    binds: tuple[Bind, ...]
    loc: Loc


@dataclass(frozen=True)
class Compound:
    qid: str
    module: str
    name: str
    meaning: str
    steps: tuple[Step, ...]
    loc: Loc


# --- evolution -----------------------------------------------------------------


@dataclass(frozen=True)
class Tombstone:
    qid: str
    module: str
    name: str
    meaning: str
    disposition: str
    loc: Loc


@dataclass(frozen=True)
class TightenDecl:
    module: str
    path: tuple[str, ...]
    repair: Union[Literal, str]
    loc: Loc


@dataclass(frozen=True)
class RetypeDecl:
    module: str
    intent: str
    previous: str
    forward: str
    backward: str
    loc: Loc


@dataclass(frozen=True)
class RestoreDecl:
    module: str
    intent: str
    loc: Loc


@dataclass(frozen=True)
class MoveHome:
    module: str
    intent: str  # intent qid
    source: str  # carrier qid
    target: str  # carrier qid
    disposition: str
    loc: Loc


# --- modules, worlds, deployments -----------------------------------------------


@dataclass(frozen=True)
class Import:
    owner: str
    source: str
    local: str
    identity: str
    loc: Loc


@dataclass(frozen=True)
class Module:
    name: str
    meaning: str
    imports: tuple[Import, ...]
    file: str
    loc: Loc


@dataclass(frozen=True)
class ScopeRoot:
    trait: str
    link: str  # link qid on the trait
    root: str  # carrier qid


@dataclass(frozen=True)
class World:
    name: str
    meaning: str
    modules: tuple[str, ...]
    durability: str
    writers: str
    generated: tuple[str, ...]
    requires: str | None
    exempt: tuple[str, ...]
    scope: ScopeRoot | None  # None means deployment scope
    capabilities: tuple[str, ...]
    writer_source: str | None
    quarantine_retention: int
    loc: Loc

    @property
    def deployment_scoped(self) -> bool:
        return self.scope is None


@dataclass(frozen=True)
class Location:
    kind: str
    name: str | None
    default: str | None


@dataclass(frozen=True)
class Deployment:
    name: str
    meaning: str
    extends: str | None
    world: str
    engine: str
    location: Location
    ship: str
    mode: str
    snapshot: str
    pool: int | None
    loc: Loc


# --- program -------------------------------------------------------------------


@dataclass(frozen=True)
class Program:
    modules: tuple[Module, ...]
    intents: tuple[Intent, ...]
    newtypes: tuple[Newtype, ...]
    carriers: tuple[Carrier, ...]
    reads: tuple[Read, ...]
    aliases: tuple[Alias, ...]
    bulks: tuple[Bulk, ...]
    restricteds: tuple[Restricted, ...]
    compounds: tuple[Compound, ...]
    tombstones: tuple[Tombstone, ...]
    tightens: tuple[TightenDecl, ...]
    retypes: tuple[RetypeDecl, ...]
    restores: tuple[RestoreDecl, ...]
    move_homes: tuple[MoveHome, ...]
    worlds: tuple[World, ...]
    deployments: tuple[Deployment, ...]
    scope_paths: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)  # world -> carrier -> link qids
    references: tuple[Reference, ...] = ()

    def carrier(self, qid: str) -> Carrier:
        for c in self.carriers:
            if c.qid == qid:
                return c
        raise KeyError(qid)

    def intent(self, qid: str) -> Intent:
        for i in self.intents:
            if i.qid == qid:
                return i
        raise KeyError(qid)

    def read(self, qid: str) -> Read:
        for r in self.reads:
            if r.qid == qid:
                return r
        raise KeyError(qid)

    def world(self, name: str) -> World:
        for w in self.worlds:
            if w.name == name:
                return w
        raise KeyError(name)

    def link(self, qid: str) -> Link:
        carrier_qid, name = qid.rsplit(".", 1)
        for l in self.carrier(carrier_qid).links:
            if l.name == name:
                return l
        raise KeyError(qid)

    def module(self, name: str) -> Module:
        for m in self.modules:
            if m.name == name:
                return m
        raise KeyError(name)


# --- canonical encoding ---------------------------------------------------------


def canonical(obj: Any) -> Any:
    """Canonical JSON-able form of any IR value (locations dropped)."""
    if isinstance(obj, Loc):
        return None
    if isinstance(obj, TypeRef):
        return obj.canonical()
    if hasattr(obj, "__dataclass_fields__"):
        out: dict[str, Any] = {"$": type(obj).__name__}
        for name in obj.__dataclass_fields__:  # type: ignore[attr-defined]
            if name in ("loc", "references", "file"):
                continue
            out[name] = canonical(getattr(obj, name))
        return out
    if isinstance(obj, (list, tuple)):
        return [canonical(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): canonical(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def canonical_json(obj: Any) -> str:
    return json.dumps(canonical(obj), sort_keys=True, indent=1, ensure_ascii=True) + "\n"


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
