"""Source nodes: a faithful, located tree of the frozen grammar.

Every identifier occurrence is a ``Name`` with its own location so that the
resolver can record a reference map (position -> qualified identity). Nothing
here is qualified or typed; that is the resolver's job.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class Loc:
    file: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Name:
    text: str
    loc: Loc

    @property
    def file(self) -> str:
        return self.loc.file

    @property
    def line(self) -> int:
        return self.loc.line

    @property
    def column(self) -> int:
        return self.loc.column


@dataclass(frozen=True)
class QName:
    parts: tuple[Name, ...]  # one or two names
    loc: Loc

    @property
    def text(self) -> str:
        return ".".join(p.text for p in self.parts)


@dataclass(frozen=True)
class Ctor:
    text: str  # includes the leading '@'
    loc: Loc


@dataclass(frozen=True)
class TypeRefNode:
    name: Name
    optional: bool
    list_of: bool
    loc: Loc


@dataclass(frozen=True)
class LiteralNode:
    kind: str  # string | int | ctor | bool
    value: object
    loc: Loc


@dataclass(frozen=True)
class ClockNode:
    loc: Loc


@dataclass(frozen=True)
class PathNode:
    names: tuple[Name, ...]
    loc: Loc

    @property
    def text(self) -> str:
        return ".".join(n.text for n in self.names)


# --- dynamic (closed) expression algebra -------------------------------------


@dataclass(frozen=True)
class OrNode:
    items: tuple["DynExpr", ...]
    loc: Loc


@dataclass(frozen=True)
class AndNode:
    items: tuple["DynExpr", ...]
    loc: Loc


@dataclass(frozen=True)
class NotNode:
    item: "DynExpr"
    loc: Loc


@dataclass(frozen=True)
class QuantNode:
    kind: str  # some | every
    item: "DynExpr"
    loc: Loc


@dataclass(frozen=True)
class AggNode:
    """``path count ( [expr] )`` | ``path max ( path )`` | ``path min ( path )``"""

    path: PathNode
    fn: str  # count | max | min
    arg: Union["DynExpr", PathNode, None]
    loc: Loc


DynValue = Union[PathNode, LiteralNode, ClockNode]


@dataclass(frozen=True)
class CmpNode:
    left: Union[PathNode, AggNode]
    op: str
    right: DynValue
    guard: bool
    loc: Loc


@dataclass(frozen=True)
class ContainsNode:
    path: PathNode
    value: DynValue
    guard: bool
    loc: Loc


@dataclass(frozen=True)
class InNode:
    path: PathNode
    value: DynValue
    guard: bool
    loc: Loc


@dataclass(frozen=True)
class IsNode:
    path: PathNode
    value: DynValue
    guard: bool
    loc: Loc


@dataclass(frozen=True)
class PresenceNode:
    path: PathNode
    present: bool
    guard: bool
    loc: Loc


@dataclass(frozen=True)
class WithinNode:
    path: PathNode
    target: PathNode  # dynamic grammar: within path_expr
    loc: Loc


DynExpr = Union[
    OrNode, AndNode, NotNode, QuantNode, CmpNode, ContainsNode, InNode, IsNode, PresenceNode, WithinNode
]


# --- static (expressive) expression algebra ----------------------------------


@dataclass(frozen=True)
class SOrNode:
    items: tuple["StaticExpr", ...]
    loc: Loc


@dataclass(frozen=True)
class SAndNode:
    items: tuple["StaticExpr", ...]
    loc: Loc


@dataclass(frozen=True)
class SNotNode:
    item: "StaticExpr"
    loc: Loc


@dataclass(frozen=True)
class SCmpNode:
    left: "StaticScalar"
    op: str  # = != < <= > >= contains in is
    right: "StaticScalar"
    loc: Loc


@dataclass(frozen=True)
class SPresenceNode:
    path: PathNode
    present: bool
    loc: Loc


@dataclass(frozen=True)
class SWithinNode:
    path: PathNode
    target: QName
    loc: Loc


@dataclass(frozen=True)
class SBinaryNode:
    op: str  # + - * / %
    left: "StaticScalar"
    right: "StaticScalar"
    loc: Loc


@dataclass(frozen=True)
class SUnaryNode:
    op: str  # + -
    item: "StaticScalar"
    loc: Loc


@dataclass(frozen=True)
class SAggregateNode:
    fn: str  # count | sum | average | minimum | maximum
    distinct: bool
    path: PathNode | None
    loc: Loc


@dataclass(frozen=True)
class SCallNode:
    function: QName
    args: tuple["StaticScalar", ...]
    loc: Loc


StaticScalar = Union[PathNode, LiteralNode, ClockNode, SBinaryNode, SUnaryNode, SAggregateNode, SCallNode]
StaticExpr = Union[SOrNode, SAndNode, SNotNode, SCmpNode, SPresenceNode, SWithinNode, StaticScalar]


# --- shows and orders --------------------------------------------------------


@dataclass(frozen=True)
class IdentityShow:
    loc: Loc


@dataclass(frozen=True)
class CountShow:
    loc: Loc


@dataclass(frozen=True)
class RankShow:
    loc: Loc


@dataclass(frozen=True)
class PathShow:
    path: PathNode
    loc: Loc


@dataclass(frozen=True)
class NestedShow:
    path: PathNode
    items: tuple["ShowItemNode", ...]
    last: int | None
    loc: Loc


@dataclass(frozen=True)
class ScalarShow:
    scalar: StaticScalar
    loc: Loc


ShowValue = Union[IdentityShow, CountShow, RankShow, PathShow, NestedShow, ScalarShow]


@dataclass(frozen=True)
class ShowItemNode:
    value: ShowValue
    alias: Name | None
    loc: Loc


@dataclass(frozen=True)
class OrderItemNode:
    key: Union[PathNode, StaticScalar]
    direction: str | None  # ascending | descending | None (grammar default)
    loc: Loc


# --- read declarations (query / question) ------------------------------------


@dataclass(frozen=True)
class GivenItem:
    name: Name
    type_ref: TypeRefNode
    default: LiteralNode | None
    loc: Loc


@dataclass(frozen=True)
class WhereItem:
    expr: Union[DynExpr, StaticExpr]
    loc: Loc


@dataclass(frozen=True)
class ShowListItem:
    items: tuple[ShowItemNode, ...]
    loc: Loc


@dataclass(frozen=True)
class OrderListItem:
    items: tuple[OrderItemNode, ...]
    loc: Loc


@dataclass(frozen=True)
class PageItem:
    name: Name
    loc: Loc


@dataclass(frozen=True)
class LimitItem:
    name: Name
    loc: Loc


@dataclass(frozen=True)
class WithTotalItem:
    loc: Loc


@dataclass(frozen=True)
class LiveItem:
    bound: int
    loc: Loc


@dataclass(frozen=True)
class IncludingArchivedItem:
    loc: Loc


@dataclass(frozen=True)
class UnscopedItem:
    capability: Name
    loc: Loc


@dataclass(frozen=True)
class ByItem:
    path: PathNode
    loc: Loc


@dataclass(frozen=True)
class OneItem:
    loc: Loc


@dataclass(frozen=True)
class DistinctItem:
    loc: Loc


@dataclass(frozen=True)
class GroupByItem:
    paths: tuple[PathNode, ...]
    loc: Loc


@dataclass(frozen=True)
class HavingItem:
    expr: StaticExpr
    loc: Loc


@dataclass(frozen=True)
class FirstItem:
    count: int
    loc: Loc


ReadItem = Union[
    GivenItem, WhereItem, ShowListItem, OrderListItem, PageItem, LimitItem, WithTotalItem, LiveItem,
    IncludingArchivedItem, UnscopedItem, ByItem, OneItem, DistinctItem, GroupByItem, HavingItem, FirstItem,
]


@dataclass(frozen=True)
class ReadDecl:
    noun: str  # query | question
    name: Name
    subject: Name
    meaning: str
    items: tuple[ReadItem, ...]
    loc: Loc


# --- intents, newtypes, carriers ---------------------------------------------


@dataclass(frozen=True)
class AliasItem:
    name: Name
    loc: Loc


@dataclass(frozen=True)
class RenamedFromItem:
    target: QName
    loc: Loc


@dataclass(frozen=True)
class ValuesItem:
    ctors: tuple[Ctor, ...]
    loc: Loc


@dataclass(frozen=True)
class PatternItem:
    pattern: str
    loc: Loc


@dataclass(frozen=True)
class LengthItem:
    minimum: int
    maximum: int | None
    loc: Loc


@dataclass(frozen=True)
class DimensionItem:
    dimension: int
    loc: Loc


@dataclass(frozen=True)
class RetypeClauseNode:
    target: Name
    forward: str
    backward: str
    loc: Loc


@dataclass(frozen=True)
class RetireClauseNode:
    disposition: str
    loc: Loc


@dataclass(frozen=True)
class RestoreClauseNode:
    loc: Loc


IntentItem = Union[
    AliasItem, RenamedFromItem, ValuesItem, PatternItem, LengthItem, DimensionItem,
    RetypeClauseNode, RetireClauseNode, RestoreClauseNode,
]


@dataclass(frozen=True)
class IntentDecl:
    name: Name
    type_ref: TypeRefNode
    meaning: str
    items: tuple[IntentItem, ...]
    loc: Loc


@dataclass(frozen=True)
class NewtypeDecl:
    name: Name
    of: TypeRefNode
    meaning: str
    loc: Loc


@dataclass(frozen=True)
class UseFlag:
    kind: str  # key | optional | filter | order | stamp | default | repair
    value: object  # stamp_when | literal/ship_clock/quarantine | None
    loc: Loc


@dataclass(frozen=True)
class UseStmt:
    intent: Name
    flags: tuple[UseFlag, ...]
    loc: Loc


@dataclass(frozen=True)
class LinkFlag:
    kind: str  # end | unenforced | scopes | inverse | optional | key | filter | order | default
    value: object  # end kind | inverse Name | default value | None
    loc: Loc


@dataclass(frozen=True)
class LinkStmt:
    name: Name
    target: Name
    flags: tuple[LinkFlag, ...]
    loc: Loc


@dataclass(frozen=True)
class LifecycleItem:
    kind: str  # mutable | retirable | archived_by
    archived_by: Name | None
    loc: Loc


@dataclass(frozen=True)
class CarryItem:
    traits: tuple[Name, ...]
    loc: Loc


@dataclass(frozen=True)
class OrderedWithinItem:
    link: Name
    loc: Loc


@dataclass(frozen=True)
class HistoryKeptItem:
    loc: Loc


@dataclass(frozen=True)
class BreakingItem:
    reason: str
    loc: Loc


@dataclass(frozen=True)
class TightenItem:
    intent: Name
    repair: object
    loc: Loc


@dataclass(frozen=True)
class InvariantItem:
    expr: DynExpr
    loc: Loc


@dataclass(frozen=True)
class ScopeViaItem:
    link: Name
    loc: Loc


CarrierItem = Union[
    UseStmt, LinkStmt, LifecycleItem, CarryItem, OrderedWithinItem, HistoryKeptItem, BreakingItem,
    TightenItem, InvariantItem, ScopeViaItem,
]


@dataclass(frozen=True)
class MemberDecl:
    name: Name
    meaning: str
    items: tuple[CarrierItem, ...]
    loc: Loc


@dataclass(frozen=True)
class CarrierDecl:
    kind: str  # trait | resource | event | association | family
    name: Name
    meaning: str
    items: tuple[CarrierItem, ...]
    members: tuple[MemberDecl, ...]
    loc: Loc


# --- verbs -------------------------------------------------------------------


@dataclass(frozen=True)
class DottedVerb:
    carrier: Name
    verb: Name
    loc: Loc


@dataclass(frozen=True)
class AliasDecl:
    name: Name
    verb: DottedVerb
    unscoped: Name | None
    loc: Loc


@dataclass(frozen=True)
class SetClause:
    target: Name
    value: Name | None  # None means absent
    loc: Loc


@dataclass(frozen=True)
class BulkDecl:
    name: Name
    meaning: str
    givens: tuple[GivenItem, ...]
    verb: DottedVerb
    over: Name
    sets: tuple[SetClause, ...]
    loc: Loc


@dataclass(frozen=True)
class RestrictedDecl:
    name: Name
    meaning: str
    verb: DottedVerb
    accepts: tuple[Name, ...]
    unscoped: Name | None
    loc: Loc


@dataclass(frozen=True)
class BindItem:
    path: PathNode
    step: Name
    loc: Loc


@dataclass(frozen=True)
class StepStmt:
    name: Name
    verb: DottedVerb
    each: Name | None
    binds: tuple[BindItem, ...]
    loc: Loc


@dataclass(frozen=True)
class CompoundDecl:
    name: Name
    meaning: str
    steps: tuple[StepStmt, ...]
    loc: Loc


# --- evolution ---------------------------------------------------------------


@dataclass(frozen=True)
class TombstoneDecl:
    name: Name
    meaning: str
    disposition: str
    loc: Loc


@dataclass(frozen=True)
class TightenStmt:
    path: PathNode
    repair: object
    loc: Loc


@dataclass(frozen=True)
class RetypeStmt:
    name: Name
    clause: RetypeClauseNode
    loc: Loc


@dataclass(frozen=True)
class RestoreStmt:
    name: Name
    loc: Loc


@dataclass(frozen=True)
class MoveHomeStmt:
    intent: Name
    source: Name
    target: Name
    disposition: str
    loc: Loc


# --- world and deployment ----------------------------------------------------


@dataclass(frozen=True)
class WorldItem:
    kind: str  # modules | durability | writers | generated | requires | scope | capabilities | writer_source | quarantine_retention
    names: tuple[Name, ...] = ()
    qname: QName | None = None
    exempt: tuple[QName, ...] = ()
    path: PathNode | None = None
    deployment_scope: bool = False
    integer: int | None = None
    loc: Loc = Loc("", 1, 1)


@dataclass(frozen=True)
class WorldDecl:
    name: Name
    meaning: str
    items: tuple[WorldItem, ...]
    loc: Loc


@dataclass(frozen=True)
class LocationNode:
    kind: str  # env | path | memory
    name: Name | None
    default: str | None
    loc: Loc


@dataclass(frozen=True)
class DepItem:
    kind: str  # world | engine | at | ship | mode | snapshot | pool
    name: Name | None = None
    location: LocationNode | None = None
    integer: int | None = None
    loc: Loc = Loc("", 1, 1)


@dataclass(frozen=True)
class DeploymentDecl:
    name: Name
    meaning: str
    extends: Name | None
    items: tuple[DepItem, ...]
    loc: Loc


# --- module / file -----------------------------------------------------------


@dataclass(frozen=True)
class ImportItem:
    source: Name
    local: Name | None
    loc: Loc


@dataclass(frozen=True)
class ImportStmt:
    owner: Name
    items: tuple[ImportItem, ...]
    loc: Loc


Decl = Union[
    IntentDecl, NewtypeDecl, CarrierDecl, ReadDecl, AliasDecl, BulkDecl, RestrictedDecl, CompoundDecl,
    TombstoneDecl, TightenStmt, RetypeStmt, RestoreStmt, MoveHomeStmt,
]


@dataclass(frozen=True)
class ModuleDecl:
    name: Name
    meaning: str
    imports: tuple[ImportStmt, ...]
    decls: tuple[Decl, ...]
    loc: Loc


TopLevel = Union[ModuleDecl, WorldDecl, DeploymentDecl, TightenStmt, RetypeStmt, RestoreStmt, MoveHomeStmt]


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str
    toplevels: tuple[TopLevel, ...]
    names: tuple[Name, ...] = field(default=(), compare=False)  # every NAME token in order
