"""Program resolution: source nodes -> typed qualified IR.

The resolver owns every naming rule. It records a reference map (identifier
position -> qualified identity) that the metamorphic harness later uses to
rename sources without touching compiler code.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from . import ast as A
from . import ir as I
from .refuse import Refusal, refuse
from .types import BUILTIN_SCALARS, RESERVED_TERMS, TypeRef

DERIVED_VERBS = frozenset({
    "mint", "ensure", "upsert", "change", "delete", "archive", "restore", "retire",
    "append", "apply", "remove", "by", "list", "count", "page", "history", "kind",
})
BULKABLE = frozenset({"change", "archive", "delete", "retire", "restore", "apply", "remove"})
DURABILITIES = frozenset({"durable", "ephemeral"})
WRITER_CLASSES = frozenset({"governed", "external_captured"})
TARGETS = frozenset({"python", "rust"})
ENGINES = frozenset({"sqlite", "postgres"})  # recognised engines
LOWERED_ENGINES = frozenset({"sqlite"})  # engines this build can lower; a recognised engine without a lowering refuses
SHIP_MODES = frozenset({"on_open", "explicit"})
MODES = frozenset({"readwrite", "readonly"})
SNAPSHOTS = frozenset({"none", "before_ship"})

DECL_KINDS = ("intent", "newtype", "carrier", "member", "read", "alias", "bulk", "restricted", "compound", "tombstone")


@dataclass
class DeclEntry:
    kind: str
    node: object
    qid: str
    module: str


@dataclass
class ImportEntry:
    owner: str
    source: str
    local: str
    identity: str
    kind: str
    node: A.ImportItem
    used: bool = False


@dataclass
class ModuleScope:
    decl: A.ModuleDecl
    decls: dict[str, DeclEntry] = field(default_factory=dict)
    imports: dict[str, ImportEntry] = field(default_factory=dict)
    tombstones: dict[str, DeclEntry] = field(default_factory=dict)


class Resolver:
    def __init__(self, files: Iterable[A.SourceFile]) -> None:
        self.files = list(files)
        self.scopes: dict[str, ModuleScope] = {}
        self.refs: list[I.Reference] = []
        self.intents: dict[str, I.Intent] = {}
        self.newtypes: dict[str, I.Newtype] = {}
        self.closed_types: dict[str, TypeRef] = {}  # module.TypeName -> TypeRef
        self.carriers: dict[str, I.Carrier] = {}
        self.reads: dict[str, I.Read] = {}
        self.aliases: dict[str, I.Alias] = {}
        self.bulks: dict[str, I.Bulk] = {}
        self.restricteds: dict[str, I.Restricted] = {}
        self.compounds: dict[str, I.Compound] = {}
        self.tombstones: dict[str, I.Tombstone] = {}
        self.tightens: list[I.TightenDecl] = []
        self.retypes: list[I.RetypeDecl] = []
        self.restores: list[I.RestoreDecl] = []
        self.move_homes: list[I.MoveHome] = []
        self.worlds: dict[str, I.World] = {}
        self.deployments: dict[str, I.Deployment] = {}
        self.world_of_module: dict[str, str] = {}
        self.modules: list[I.Module] = []
        self.world_nodes: list[A.WorldDecl] = []
        self.dep_nodes: list[A.DeploymentDecl] = []
        self.top_stmts: list[A.TopLevel] = []
        self.scope_paths: dict[str, dict[str, tuple[str, ...]]] = {}

    # ------------------------------------------------------------------ helpers
    def ref(self, name: A.Name, identity: str, role: str) -> None:
        self.refs.append(I.Reference(name.loc.file, name.loc.line, name.loc.column, name.text, identity, role))

    def qid(self, module: str, name: str) -> str:
        return f"{module}.{name}"

    @staticmethod
    def link_identity(link: I.Link) -> str:
        """The identity of the declaration a (possibly composed) link came from."""
        return link.qid if link.origin == "own" else f"{link.origin}.{link.name}"

    def declare(self, scope: ModuleScope, name: A.Name, kind: str, node: object) -> str:
        if name.text in RESERVED_TERMS and kind in ("intent", "carrier", "member"):
            refuse("TERM_RESERVED", "validate", name, f"{name.text!r} is a language term and cannot be declared")
        qid = self.qid(scope.decl.name.text, name.text)
        if kind == "tombstone":
            if name.text in scope.tombstones:
                refuse("ID_DUPLICATED", "validate", name, f"{qid} is tombstoned twice")
            scope.tombstones[name.text] = DeclEntry(kind, node, qid, scope.decl.name.text)
            self.ref(name, qid, kind)
            return qid
        if name.text in scope.decls:
            refuse("ID_DUPLICATED", "validate", name, f"{scope.decl.name.text}.{name.text} is declared twice")
        scope.decls[name.text] = DeclEntry(kind, node, qid, scope.decl.name.text)
        self.ref(name, qid, kind)
        return qid

    def lookup(self, module: str, name: A.Name, kinds: tuple[str, ...], missing_code: str) -> DeclEntry:
        """Resolve a bare name in ``module`` to a declaration of one of ``kinds``."""
        scope = self.scopes[module]
        entry = scope.decls.get(name.text)
        imported = scope.imports.get(name.text)
        if entry is not None and imported is not None:
            refuse("NAME_AMBIGUOUS", "validate", name, f"{name.text} is both declared and imported in {module}")
        if entry is None and imported is not None:
            imported.used = True
            owner_scope = self.scopes[imported.owner]
            entry = owner_scope.decls[imported.source]
        if entry is None:
            owners = [m for m, s in self.scopes.items() if name.text in s.decls and s.decls[name.text].kind in kinds]
            if owners:
                refuse("NAME_NOT_IMPORTED", "validate", name, f"{name.text} is declared by {', '.join(owners)} and not imported into {module}")
            refuse(missing_code, "validate", name, f"{name.text} is not declared")
        if entry.kind not in kinds:
            refuse(missing_code, "validate", name, f"{name.text} is a {entry.kind}, not one of {', '.join(kinds)}")
        return entry

    def lookup_qualified(self, qn: A.QName, kinds: tuple[str, ...], missing_code: str, role: str) -> DeclEntry:
        if len(qn.parts) != 2:
            refuse("QNAME_REQUIRED", "validate", qn, f"{qn.text} must be module-qualified")
        module_name, local = qn.parts
        scope = self.scopes.get(module_name.text)
        if scope is None:
            refuse("MODULE_UNKNOWN", "validate", module_name, f"module {module_name.text} is not declared")
        self.ref(module_name, module_name.text, "module")
        entry = scope.decls.get(local.text)
        if entry is None or entry.kind not in kinds:
            refuse(missing_code, "validate", local, f"{qn.text} is not a declared {'/'.join(kinds)}")
        self.ref(local, entry.qid, role)
        return entry

    # -------------------------------------------------------------- phase 1: names
    def collect(self) -> None:
        for sf in self.files:
            for top in sf.toplevels:
                if isinstance(top, A.ModuleDecl):
                    if top.name.text in self.scopes:
                        refuse("MODULE_DUPLICATED", "validate", top.name, f"module {top.name.text} is declared twice")
                    self.scopes[top.name.text] = ModuleScope(top)
                    self.ref(top.name, top.name.text, "module")
                elif isinstance(top, A.WorldDecl):
                    self.world_nodes.append(top)
                elif isinstance(top, A.DeploymentDecl):
                    self.dep_nodes.append(top)
                else:
                    self.top_stmts.append(top)
        for scope in self.scopes.values():
            module = scope.decl.name.text
            for d in scope.decl.decls:
                if isinstance(d, A.IntentDecl):
                    self.declare(scope, d.name, "intent", d)
                elif isinstance(d, A.NewtypeDecl):
                    self.declare(scope, d.name, "newtype", d)
                elif isinstance(d, A.CarrierDecl):
                    self.declare(scope, d.name, "carrier", d)
                    for m in d.members:
                        self.declare(scope, m.name, "member", (d, m))
                elif isinstance(d, A.ReadDecl):
                    self.declare(scope, d.name, "read", d)
                elif isinstance(d, A.AliasDecl):
                    self.declare(scope, d.name, "alias", d)
                elif isinstance(d, A.BulkDecl):
                    self.declare(scope, d.name, "bulk", d)
                elif isinstance(d, A.RestrictedDecl):
                    self.declare(scope, d.name, "restricted", d)
                elif isinstance(d, A.CompoundDecl):
                    self.declare(scope, d.name, "compound", d)
                elif isinstance(d, A.TombstoneDecl):
                    self.declare(scope, d.name, "tombstone", d)
                elif isinstance(d, (A.TightenStmt, A.RetypeStmt, A.RestoreStmt, A.MoveHomeStmt)):
                    pass
                else:
                    raise TypeError(d)

    # ----------------------------------------------------------- phase 2: imports
    def resolve_imports(self) -> None:
        graph: dict[str, set[str]] = defaultdict(set)
        for scope in self.scopes.values():
            module = scope.decl.name.text
            for stmt in scope.decl.imports:
                owner = self.scopes.get(stmt.owner.text)
                if owner is None:
                    refuse("IMPORT_UNKNOWN", "validate", stmt.owner, f"module {stmt.owner.text} is not declared")
                if stmt.owner.text == module:
                    refuse("IMPORT_SELF", "validate", stmt.owner, f"{module} imports itself")
                self.ref(stmt.owner, stmt.owner.text, "module")
                graph[module].add(stmt.owner.text)
                for item in stmt.items:
                    entry = owner.decls.get(item.source.text)
                    if entry is None:
                        if item.source.text in owner.imports:
                            refuse("IMPORT_NOT_OWNER", "validate", item.source, f"{stmt.owner.text} imports {item.source.text}; it does not own it")
                        refuse("IMPORT_UNKNOWN", "validate", item.source, f"{stmt.owner.text} does not declare {item.source.text}")
                    self.ref(item.source, entry.qid, entry.kind)
                    local = item.local or item.source
                    if item.local is not None:
                        self.ref(item.local, entry.qid, entry.kind)
                    if local.text in scope.imports:
                        refuse("IMPORT_AMBIGUOUS", "validate", local, f"{local.text} is imported twice into {module}")
                    if local.text in scope.decls:
                        refuse("NAME_AMBIGUOUS", "validate", local, f"{local.text} is both declared and imported in {module}")
                    scope.imports[local.text] = ImportEntry(stmt.owner.text, item.source.text, local.text, entry.qid, entry.kind, item)
        # cycles
        state: dict[str, int] = {}

        def visit(node: str, path: list[str]) -> None:
            state[node] = 1
            for nxt in sorted(graph.get(node, ())):
                if state.get(nxt) == 1:
                    cycle = path[path.index(nxt):] + [nxt] if nxt in path else [node, nxt]
                    decl = self.scopes[cycle[0]].decl
                    refuse("MODULE_CYCLE", "validate", decl.name, " -> ".join(cycle))
                if state.get(nxt) is None:
                    visit(nxt, path + [nxt])
            state[node] = 2

        for module in sorted(self.scopes):
            if state.get(module) is None:
                visit(module, [module])

    def check_unused_imports(self) -> None:
        for scope in self.scopes.values():
            for entry in scope.imports.values():
                if not entry.used:
                    refuse("IMPORT_UNUSED", "validate", entry.node.source, f"{scope.decl.name.text} imports {entry.local} and never uses it")

    # -------------------------------------------------------------- phase 3: types
    def resolve_type(self, module: str, node: A.TypeRefNode, *, allow_carrier: bool, closed: tuple[str, ...] = ()) -> TypeRef:
        name = node.name
        if name.text in BUILTIN_SCALARS:
            base = name.text
            t = TypeRef(base, BUILTIN_SCALARS[base], node.optional, node.list_of, None, ())
            if closed:
                t = TypeRef(base, BUILTIN_SCALARS[base], node.optional, node.list_of, None, closed)
            return t
        # nominal: newtype, closed set type, or carrier (givens only)
        scope = self.scopes[module]
        entry = scope.decls.get(name.text)
        imported = scope.imports.get(name.text)
        if entry is None and imported is not None:
            imported.used = True
            entry = self.scopes[imported.owner].decls[imported.source]
        if entry is not None and entry.kind == "newtype":
            nt = self.newtypes.get(entry.qid)
            if nt is None:
                nt = self.resolve_newtype(entry)  # type: ignore[arg-type]
            self.ref(name, entry.qid, "newtype")
            return TypeRef(nt.of.base, nt.of.cls, node.optional, node.list_of, entry.qid, nt.of.closed)
        if entry is not None and entry.kind in ("carrier", "member") and allow_carrier:
            self.ref(name, entry.qid, entry.kind)
            return TypeRef("Id", "text", node.optional, node.list_of, None, (), entry.qid)
        closed_qid = self.qid(module, name.text)
        if closed:
            # the intent declares a nominal closed-set type named by its type_ref
            t = TypeRef("Text", "text", node.optional, node.list_of, closed_qid, closed)
            previous = self.closed_types.get(closed_qid)
            if previous is not None and previous.closed != closed:
                refuse("CLOSED_SET_CONFLICT", "validate", name, f"{closed_qid} is declared with different members")
            self.closed_types[closed_qid] = t.scalar()
            self.ref(name, closed_qid, "closedtype")
            return t
        known = self.closed_types.get(closed_qid)
        if known is not None:
            self.ref(name, closed_qid, "closedtype")
            return TypeRef(known.base, known.cls, node.optional, node.list_of, known.nominal, known.closed)
        if entry is not None:
            refuse("TYPE_UNKNOWN", "validate", name, f"{name.text} is a {entry.kind}, not a type")
        refuse("TYPE_UNKNOWN", "validate", name, f"type {name.text} is not declared")
        raise AssertionError

    def resolve_newtype(self, entry: DeclEntry) -> I.Newtype:
        node: A.NewtypeDecl = entry.node  # type: ignore[assignment]
        if node.of.optional or node.of.list_of:
            refuse("NEWTYPE_SHAPE", "validate", node.of, "a newtype is of a scalar type")
        if node.of.name.text not in BUILTIN_SCALARS:
            refuse("TYPE_UNKNOWN", "validate", node.of.name, f"newtype {node.name.text} must be of a builtin scalar")
        of = TypeRef(node.of.name.text, BUILTIN_SCALARS[node.of.name.text])
        nt = I.Newtype(entry.qid, entry.module, node.name.text, node.meaning, of, node.loc)
        self.newtypes[entry.qid] = nt
        return nt

    def resolve_intents(self) -> None:
        for scope in self.scopes.values():
            module = scope.decl.name.text
            for entry in scope.decls.values():
                if entry.kind == "newtype" and entry.qid not in self.newtypes:
                    self.resolve_newtype(entry)
        # closed-set declarations first so that other intents may reference the nominal type
        pending: list[tuple[ModuleScope, DeclEntry]] = []
        for scope in self.scopes.values():
            for entry in scope.decls.values():
                if entry.kind == "intent":
                    node: A.IntentDecl = entry.node  # type: ignore[assignment]
                    if any(isinstance(i, A.ValuesItem) for i in node.items):
                        self.resolve_intent(scope, entry)
                    else:
                        pending.append((scope, entry))
        for scope, entry in pending:
            self.resolve_intent(scope, entry)

    def resolve_intent(self, scope: ModuleScope, entry: DeclEntry) -> None:
        node: A.IntentDecl = entry.node  # type: ignore[assignment]
        module = scope.decl.name.text
        seen: set[str] = set()
        alias = renamed_from = pattern = None
        values: tuple[str, ...] = ()
        length = dimension = retype = retired = None
        restore = False
        for item in node.items:
            kind = type(item).__name__
            if kind in seen:
                refuse("INTENT_ITEM_REPEATED", "validate", item, f"{kind} stated twice on {entry.qid}")
            seen.add(kind)
            if isinstance(item, A.AliasItem):
                alias = item.name.text
                self.ref(item.name, f"{entry.qid}#alias", "intent-alias")
            elif isinstance(item, A.RenamedFromItem):
                if len(item.target.parts) == 1:
                    renamed_from = self.qid(module, item.target.parts[0].text)
                    self.ref(item.target.parts[0], renamed_from, "intent-previous")
                else:
                    previous_module = item.target.parts[0]
                    renamed_from = item.target.text
                    self.ref(previous_module, previous_module.text, "module")
                    self.ref(item.target.parts[1], renamed_from, "intent-previous")
            elif isinstance(item, A.ValuesItem):
                members = []
                for c in item.ctors:
                    if c.text in members:
                        refuse("CLOSED_SET_MEMBER_DUPLICATED", "validate", c, f"{c.text} listed twice")
                    members.append(c.text)
                values = tuple(members)
            elif isinstance(item, A.PatternItem):
                pattern = item.pattern
            elif isinstance(item, A.LengthItem):
                if item.maximum is not None and item.maximum < item.minimum:
                    refuse("LENGTH_RANGE_INVALID", "validate", item, "maximum below minimum")
                length = (item.minimum, item.maximum)
            elif isinstance(item, A.DimensionItem):
                if item.dimension <= 0:
                    refuse("DIMENSION_NOT_POSITIVE", "validate", item, "dimension must be a positive integer")
                dimension = item.dimension
            elif isinstance(item, A.RetypeClauseNode):
                if item.target.text not in BUILTIN_SCALARS:
                    refuse("TYPE_UNKNOWN", "validate", item.target, f"retype from unknown builtin {item.target.text}")
                retype = (item.target.text, item.forward, item.backward)
            elif isinstance(item, A.RetireClauseNode):
                retired = item.disposition
            elif isinstance(item, A.RestoreClauseNode):
                restore = True
            else:
                raise TypeError(item)
        if node.type_ref.optional or node.type_ref.list_of:
            refuse("INTENT_TYPE_SHAPE", "validate", node.type_ref, "an intent is of a scalar type; optionality belongs to the use")
        t = self.resolve_type(module, node.type_ref, allow_carrier=False, closed=values)
        cls = t.cls
        if (pattern is not None or length is not None) and cls != "text":
            refuse("INTENT_REFINEMENT_TYPE", "validate", node.type_ref, "pattern/length refine text types only")
        if dimension is not None and cls != "vector":
            refuse("DIMENSION_NOT_VECTOR", "validate", node.type_ref, "dimension refines a Vector intent only")
        if cls == "vector" and dimension is None:
            refuse("DIMENSION_REQUIRED", "validate", node.type_ref, "a Vector intent states its dimension")
        if values and cls not in ("text",):
            refuse("CLOSED_SET_TYPE", "validate", node.type_ref, "a closed set refines a text type")
        if retired is not None and restore:
            refuse("INTENT_ITEM_CONFLICT", "validate", node.name, "retired and restore are exclusive")
        self.intents[entry.qid] = I.Intent(
            entry.qid, module, node.name.text, node.meaning, t, alias, renamed_from, pattern, length,
            dimension, retype, retired, restore, node.loc,
        )

    # ----------------------------------------------------------- phase 4: carriers
    def resolve_carriers(self) -> None:
        raw: dict[str, tuple[ModuleScope, DeclEntry]] = {}
        for scope in self.scopes.values():
            for entry in scope.decls.values():
                if entry.kind == "carrier":
                    raw[entry.qid] = (scope, entry)
        # traits first (composition order), then others, members last
        order = self._trait_order(raw)
        for qid in order:
            scope, entry = raw[qid]
            self.resolve_carrier(scope, entry)
        for scope in self.scopes.values():
            for entry in scope.decls.values():
                if entry.kind == "member":
                    self.resolve_member(scope, entry)
        self.compute_inverses()
        self.validate_link_targets()

    def _trait_order(self, raw: dict[str, tuple[ModuleScope, DeclEntry]]) -> list[str]:
        graph: dict[str, list[str]] = {}
        for qid, (scope, entry) in raw.items():
            node: A.CarrierDecl = entry.node  # type: ignore[assignment]
            deps = []
            for item in node.items:
                if isinstance(item, A.CarryItem):
                    for t in item.traits:
                        dep = self.lookup(scope.decl.name.text, t, ("carrier",), "TRAIT_UNKNOWN")
                        deps.append(dep.qid)
            graph[qid] = deps
        order: list[str] = []
        state: dict[str, int] = {}

        def visit(q: str, path: list[str]) -> None:
            state[q] = 1
            for d in graph.get(q, ()):
                if state.get(d) == 1:
                    node: A.CarrierDecl = raw[q][1].node  # type: ignore[assignment]
                    refuse("TRAIT_CYCLE", "validate", node.name, " -> ".join(path + [d]))
                if state.get(d) is None:
                    visit(d, path + [d])
            state[q] = 2
            order.append(q)

        for q in sorted(raw):
            if state.get(q) is None:
                visit(q, [q])
        return order

    def resolve_use(self, module: str, carrier_qid: str, node: A.UseStmt, origin: str) -> I.Use:
        entry = self.lookup(module, node.intent, ("intent",), "TERM_UNKNOWN")
        self.ref(node.intent, entry.qid, "intent")
        intent = self.intents[entry.qid]
        seen: set[str] = set()
        key = optional = flt = order = False
        stamp = default = repair = None
        for flag in node.flags:
            if flag.kind in seen:
                refuse("USE_FLAG_REPEATED", "validate", flag, f"{flag.kind} repeated on use {node.intent.text}")
            seen.add(flag.kind)
            if flag.kind == "key":
                key = True
            elif flag.kind == "optional":
                optional = True
            elif flag.kind == "filter":
                flt = True
            elif flag.kind == "order":
                order = True
            elif flag.kind == "stamp":
                if intent.type.cls != "instant":
                    refuse("STAMP_NOT_INSTANT", "validate", flag, "stamps are written to Instant uses only")
                stamp = str(flag.value)
            elif flag.kind == "default":
                default = self.resolve_default(flag.value, intent.type, flag)
            elif flag.kind == "repair":
                repair = self.resolve_repair(flag.value, intent.type, flag)
            else:
                raise AssertionError(flag.kind)
        if key and optional:
            refuse("USE_FLAG_CONFLICT", "validate", node, "a key use cannot be optional")
        if intent.type.cls in ("opaque", "vector") and (order or key):
            refuse("OPAQUE_POLICY", "validate", node, "opaque and vector uses are neither keys nor order terms")
        return I.Use(carrier_qid, entry.qid, intent.type, key, optional, flt, order, stamp, default, repair, origin, node.loc)

    def resolve_default(self, value: object, t: TypeRef, at: object) -> I.Literal | str:
        if value == "ship_clock":
            if t.cls != "instant":
                refuse("DEFAULT_TYPE", "validate", at, "ship_clock defaults an Instant")
            return "ship_clock"
        assert isinstance(value, A.LiteralNode)
        return self.literal_of_type(value, t, "DEFAULT_TYPE")

    def resolve_repair(self, value: object, t: TypeRef, at: object) -> I.Literal | str:
        if value == "ship_clock":
            if t.cls != "instant":
                refuse("REPAIR_TYPE", "validate", at, "ship_clock repairs an Instant")
            return "ship_clock"
        if value == "quarantine":
            return "quarantine"
        assert isinstance(value, A.LiteralNode)
        return self.literal_of_type(value, t, "REPAIR_TYPE")

    def literal_of_type(self, lit: A.LiteralNode, t: TypeRef, code: str) -> I.Literal:
        s = t.scalar()
        if lit.kind == "ctor":
            if not s.is_closed:
                refuse(code, "validate", lit, f"{lit.value} is a closed-set member; {s.describe()} is not a closed set")
            if lit.value not in s.closed:
                refuse("CLOSED_SET_MEMBER_UNKNOWN", "validate", lit, f"{lit.value} is not a member of {s.describe()}")
            return I.Literal(s, str(lit.value)[1:])
        if s.is_closed:
            refuse(code, "validate", lit, f"a closed set takes a @member, not {lit.kind}")
        if lit.kind == "string" and s.cls == "text":
            return I.Literal(s, lit.value)
        if lit.kind == "int" and s.cls in ("integer", "decimal", "instant"):
            return I.Literal(s, lit.value)
        if lit.kind == "bool" and s.cls == "boolean":
            return I.Literal(s, lit.value)
        if s.carrier and lit.kind in ("int", "string"):
            return I.Literal(s, lit.value)
        refuse(code, "validate", lit, f"{lit.kind} literal does not fit {s.describe()}")
        raise AssertionError

    def resolve_link(self, module: str, carrier_qid: str, node: A.LinkStmt, origin: str) -> I.Link:
        entry = self.lookup(module, node.target, ("carrier", "member"), "CARRIER_UNKNOWN")
        self.ref(node.target, entry.qid, entry.kind)
        seen: set[str] = set()
        end: str | None = None
        unenforced = scopes = optional = key = flt = order = False
        inverse = None
        default = None
        for flag in node.flags:
            if flag.kind in seen:
                code = "LINK_ENFORCEMENT_REPEATED" if flag.kind in ("end", "unenforced") else "LINK_FLAG_REPEATED"
                refuse(code, "validate", flag, f"{flag.kind} repeated on link {node.name.text}")
            seen.add(flag.kind)
            if flag.kind == "end":
                end = str(flag.value)
            elif flag.kind == "unenforced":
                unenforced = True
            elif flag.kind == "scopes":
                scopes = True
            elif flag.kind == "inverse":
                inverse = flag.value.text  # type: ignore[union-attr]
                self.ref(flag.value, f"{carrier_qid}.{node.name.text}#inverse", "inverse")  # type: ignore[arg-type]
            elif flag.kind == "optional":
                optional = True
            elif flag.kind == "key":
                key = True
            elif flag.kind == "filter":
                flt = True
            elif flag.kind == "order":
                order = True
            elif flag.kind == "default":
                default = self.resolve_default(flag.value, TypeRef("Id", "text", carrier=entry.qid), flag)
            else:
                raise AssertionError(flag.kind)
        if unenforced and end is not None:
            refuse("LINK_ENFORCEMENT_CONFLICT", "validate", node, f"link {node.name.text} combines unenforced with end {end}")
        enforcement = "unenforced" if unenforced else (end or "restrict")
        if enforcement == "detach" and not optional:
            refuse("DETACH_NOT_OPTIONAL", "validate", node, f"link {node.name.text} detaches but is not optional")
        if key and optional:
            refuse("LINK_FLAG_CONFLICT", "validate", node, "a key link cannot be optional")
        qid = f"{carrier_qid}.{node.name.text}"
        self.ref(node.name, qid, "link")
        return I.Link(qid, carrier_qid, node.name.text, entry.qid, enforcement, scopes, inverse, optional, key, flt, order, default, origin, node.loc)

    def resolve_carrier(self, scope: ModuleScope, entry: DeclEntry) -> None:
        node: A.CarrierDecl = entry.node  # type: ignore[assignment]
        module = scope.decl.name.text
        qid = entry.qid
        uses: list[I.Use] = []
        links: list[I.Link] = []
        carries: list[str] = []
        lifecycle = archived_by_name = ordered_within_name = scope_via_name = None
        history = False
        breaking: list[str] = []
        tightens: list[tuple[A.Name, object]] = []
        invariants: list[A.DynExpr] = []
        for item in node.items:
            if isinstance(item, A.UseStmt):
                uses.append(self.resolve_use(module, qid, item, "own"))
            elif isinstance(item, A.LinkStmt):
                links.append(self.resolve_link(module, qid, item, "own"))
            elif isinstance(item, A.LifecycleItem):
                if lifecycle is not None:
                    refuse("LIFECYCLE_REPEATED", "validate", item, f"{qid} states lifecycle twice")
                lifecycle = item.kind
                archived_by_name = item.archived_by
            elif isinstance(item, A.CarryItem):
                for t in item.traits:
                    dep = self.lookup(module, t, ("carrier",), "TRAIT_UNKNOWN")
                    if self.carriers[dep.qid].kind != "trait":
                        refuse("CARRY_NOT_TRAIT", "validate", t, f"{t.text} is not a trait")
                    if dep.qid in carries:
                        refuse("CARRY_REPEATED", "validate", t, f"{qid} carries {t.text} twice")
                    self.ref(t, dep.qid, "carrier")
                    carries.append(dep.qid)
            elif isinstance(item, A.OrderedWithinItem):
                if ordered_within_name is not None:
                    refuse("ORDERED_WITHIN_REPEATED", "validate", item, "ordered_within stated twice")
                if node.kind != "event":
                    refuse("ORDERED_WITHIN_NOT_EVENT", "validate", item, "only events are ordered within a link")
                ordered_within_name = item.link
            elif isinstance(item, A.HistoryKeptItem):
                if history:
                    refuse("PRESET_CONFLICT", "validate", item, "history kept stated twice")
                history = True
            elif isinstance(item, A.BreakingItem):
                breaking.append(item.reason)
            elif isinstance(item, A.TightenItem):
                tightens.append((item.intent, item.repair))
            elif isinstance(item, A.InvariantItem):
                invariants.append(item.expr)
            elif isinstance(item, A.ScopeViaItem):
                if scope_via_name is not None:
                    refuse("SCOPE_VIA_REPEATED", "validate", item, "scope_via stated twice")
                scope_via_name = item.link
            else:
                raise TypeError(item)
        if node.kind == "trait" and lifecycle is not None:
            refuse("TRAIT_LIFECYCLE", "validate", node.name, "a trait has no lifecycle")
        if node.kind == "association" and len(links) < 2:
            refuse("ASSOCIATION_ARITY", "validate", node.name, f"association {qid} needs at least two links")
        # compose traits
        composed_uses: list[I.Use] = []
        composed_links: list[I.Link] = []
        for trait_qid in carries:
            trait = self.carriers[trait_qid]
            for tu in trait.uses:
                composed_uses = self._merge_use(composed_uses, I.Use(qid, tu.intent, tu.type, tu.key, tu.optional, tu.filter, tu.order, tu.stamp, tu.default, tu.repair, trait_qid, tu.loc), node)
            for tl in trait.links:
                if any(cl.name == tl.name for cl in composed_links):
                    refuse("TRAIT_POLICY_CONFLICT", "validate", node.name, f"link {tl.name} is composed from two traits")
                composed_links.append(I.Link(f"{qid}.{tl.name}", qid, tl.name, tl.target, tl.enforcement, tl.scopes, tl.inverse, tl.optional, tl.key, tl.filter, tl.order, tl.default, trait_qid, tl.loc))
        for u in uses:
            if any(cu.intent == u.intent and cu.origin == "own" for cu in composed_uses):
                refuse("USE_DUPLICATED", "validate", u, f"{qid} uses {u.intent} twice")
            composed_uses = self._merge_use(composed_uses, u, node)
        for l in links:
            if any(cl.name == l.name for cl in composed_links):
                refuse("LINK_DUPLICATED", "validate", l, f"{qid} links {l.name} twice")
            composed_links.append(l)
        # lifecycle validation
        archived_by = None
        if lifecycle == "archived_by":
            assert archived_by_name is not None
            target = self._use_by_local(composed_uses, archived_by_name.text)
            if target is None or not target.optional or target.type.cls != "instant":
                refuse("ARCHIVED_BY_INVALID", "validate", archived_by_name, "archived_by names an optional Instant use of the carrier")
            self.ref(archived_by_name, target.intent, "intent")
            archived_by = target.intent
        ordered_within = None
        if ordered_within_name is not None:
            lk = self._link_by_local(composed_links, ordered_within_name.text)
            if lk is None:
                refuse("ORDERED_WITHIN_UNKNOWN", "validate", ordered_within_name, f"{ordered_within_name.text} is not a link of {qid}")
            self.ref(ordered_within_name, self.link_identity(lk), "link")
            ordered_within = lk.qid
        scope_via = None
        if scope_via_name is not None:
            lk = self._link_by_local(composed_links, scope_via_name.text)
            if lk is None:
                refuse("SCOPE_VIA_UNKNOWN", "validate", scope_via_name, f"{scope_via_name.text} is not a link of {qid}")
            self.ref(scope_via_name, self.link_identity(lk), "link")
            scope_via = lk.qid
        resolved_tightens: list[tuple[str, I.Literal | str]] = []
        for tn, repair in tightens:
            target = self._use_by_local(composed_uses, tn.text)
            if target is None:
                refuse("TIGHTEN_UNKNOWN", "validate", tn, f"{tn.text} is not a use of {qid}")
            self.ref(tn, target.intent, "intent")
            resolved_tightens.append((target.intent, self.resolve_repair(repair, target.type, tn)))
        self.carriers[qid] = I.Carrier(
            qid, module, node.name.text, node.kind, node.meaning, tuple(composed_uses), tuple(composed_links),
            tuple(carries), lifecycle, archived_by, ordered_within, history, tuple(breaking), tuple(resolved_tightens),
            (), scope_via, None, tuple(f"{module}.{m.name.text}" for m in node.members), (), node.loc,
        )
        self._pending_invariants.append((qid, invariants))
        self._required_link_cycle_check.append(qid)

    def _merge_use(self, composed: list[I.Use], new: I.Use, at: A.CarrierDecl) -> list[I.Use]:
        for index, existing in enumerate(composed):
            if existing.intent != new.intent:
                continue
            if new.origin == "own":
                # restating a trait use: narrowing only
                if (existing.key and not new.key) or (not existing.optional and new.optional):
                    refuse("TRAIT_WIDENED", "validate", new, f"{new.intent} restated wider than its trait")
                if new.stamp is not None and new.stamp != existing.stamp:
                    refuse("TRAIT_POLICY_CONFLICT", "validate", new, f"{new.intent} stamp differs from its trait")
                if new.default is not None and new.default != existing.default:
                    refuse("TRAIT_POLICY_CONFLICT", "validate", new, f"{new.intent} default differs from its trait")
                merged = I.Use(
                    new.carrier, new.intent, new.type, existing.key or new.key, existing.optional,
                    existing.filter or new.filter, existing.order or new.order, existing.stamp, existing.default,
                    new.repair or existing.repair, existing.origin, new.loc,
                )
                composed[index] = merged
                return composed
            # two traits supply the same intent: policies must agree
            same = (existing.key, existing.optional, existing.stamp, existing.default) == (new.key, new.optional, new.stamp, new.default)
            if not same:
                refuse("TRAIT_POLICY_CONFLICT", "validate", at.name, f"{new.intent} is composed with conflicting policies from {existing.origin} and {new.origin}")
            merged = I.Use(
                existing.carrier, existing.intent, existing.type, existing.key, existing.optional,
                existing.filter or new.filter, existing.order or new.order, existing.stamp, existing.default,
                existing.repair, existing.origin, existing.loc,
            )
            composed[index] = merged
            return composed
        composed.append(new)
        return composed

    @staticmethod
    def _use_by_local(uses: list[I.Use], local: str) -> I.Use | None:
        for u in uses:
            if u.intent.rsplit(".", 1)[-1] == local:
                return u
        return None

    @staticmethod
    def _link_by_local(links: list[I.Link], local: str) -> I.Link | None:
        for l in links:
            if l.name == local:
                return l
        return None

    def resolve_member(self, scope: ModuleScope, entry: DeclEntry) -> None:
        family_node, node = entry.node  # type: ignore[misc]
        module = scope.decl.name.text
        family_qid = self.qid(module, family_node.name.text)
        family = self.carriers[family_qid]
        if family.kind != "family":
            refuse("MEMBER_OF_NON_FAMILY", "validate", node.name, "members belong to families")
        qid = entry.qid
        uses = list(I.Use(qid, u.intent, u.type, u.key, u.optional, u.filter, u.order, u.stamp, u.default, u.repair, u.origin if u.origin != "own" else family_qid, u.loc) for u in family.uses)
        links = list(I.Link(f"{qid}.{l.name}", qid, l.name, l.target, l.enforcement, l.scopes, l.inverse, l.optional, l.key, l.filter, l.order, l.default, l.origin if l.origin != "own" else family_qid, l.loc) for l in family.links)
        breaking: list[str] = []
        tightens: list[tuple[str, I.Literal | str]] = []
        invariants: list[A.DynExpr] = []
        for item in node.items:
            if isinstance(item, A.UseStmt):
                u = self.resolve_use(module, qid, item, "own")
                if any(x.intent == u.intent for x in uses):
                    refuse("USE_DUPLICATED", "validate", item, f"member {qid} restates {u.intent}")
                uses.append(u)
            elif isinstance(item, A.LinkStmt):
                l = self.resolve_link(module, qid, item, "own")
                if any(x.name == l.name for x in links):
                    refuse("LINK_DUPLICATED", "validate", item, f"member {qid} restates link {l.name}")
                links.append(l)
            elif isinstance(item, A.BreakingItem):
                breaking.append(item.reason)
            elif isinstance(item, A.TightenItem):
                target = self._use_by_local(uses, item.intent.text)
                if target is None:
                    refuse("TIGHTEN_UNKNOWN", "validate", item.intent, f"{item.intent.text} is not a use of {qid}")
                self.ref(item.intent, target.intent, "intent")
                tightens.append((target.intent, self.resolve_repair(item.repair, target.type, item.intent)))
            elif isinstance(item, A.InvariantItem):
                invariants.append(item.expr)
            else:
                raise TypeError(item)
        self.carriers[qid] = I.Carrier(
            qid, module, node.name.text, "member", node.meaning, tuple(uses), tuple(links), family.carries,
            family.lifecycle, family.archived_by, family.ordered_within, family.history_kept, tuple(breaking),
            tuple(tightens), (), family.scope_via, family_qid, (), (), node.loc,
        )
        self._pending_invariants.append((qid, invariants))

    def compute_inverses(self) -> None:
        edges: dict[str, list[I.InverseEdge]] = defaultdict(list)
        for c in self.carriers.values():
            if c.kind in ("member", "trait"):
                continue
            for l in c.links:
                if l.inverse is None:
                    continue
                target = self.carriers[l.target]
                many = not (l.key and target is not None and c.key_columns == (l.qid,))
                edge = I.InverseEdge(l.inverse, l.qid, c.qid, many)
                for existing in edges[l.target]:
                    if existing.name == l.inverse:
                        refuse("INVERSE_DUPLICATED", "validate", l, f"{l.target} already has an inverse named {l.inverse}")
                if target.use_named(l.inverse) is not None or target.link_named(l.inverse) is not None:
                    refuse("NAME_AMBIGUOUS", "validate", l, f"inverse {l.inverse} collides with a term of {l.target}")
                edges[l.target].append(edge)
                # members of a family target share its inverses
        def position(edge: I.InverseEdge) -> tuple[str, int, int]:
            link = self.carriers[edge.source].link_named(edge.link.rsplit(".", 1)[-1])
            assert link is not None
            return (link.loc.file, link.loc.line, link.loc.column)

        for qid, c in list(self.carriers.items()):
            own = tuple(sorted(edges.get(qid, ()), key=position))
            if c.kind == "member" and c.family:
                own = own + tuple(sorted((e for e in edges.get(c.family, ()) if e not in own), key=position))
            self.carriers[qid] = I.Carrier(
                c.qid, c.module, c.name, c.kind, c.meaning, c.uses, c.links, c.carries, c.lifecycle, c.archived_by,
                c.ordered_within, c.history_kept, c.breaking, c.tightens, c.invariants, c.scope_via, c.family,
                c.members, own, c.loc,
            )

    def validate_link_targets(self) -> None:
        for c in self.carriers.values():
            for l in c.links:
                target = self.carriers[l.target]
                if target.kind == "trait":
                    refuse("LINK_TO_TRAIT", "validate", l, f"{l.qid} targets a trait")
        # required-link cycles make minting impossible
        graph: dict[str, list[tuple[str, I.Link]]] = defaultdict(list)
        for c in self.carriers.values():
            if c.kind in ("trait", "member"):
                continue
            for l in c.links:
                if not l.optional:
                    graph[c.qid].append((l.target, l))
        state: dict[str, int] = {}

        def visit(q: str, path: list[str]) -> None:
            state[q] = 1
            for target, link in graph.get(q, ()):
                if state.get(target) == 1:
                    refuse("LINK_CYCLE_UNMINTABLE", "validate", self.carriers[path[0]], " -> ".join(path + [target]))
                if state.get(target) is None:
                    visit(target, path + [target])
            state[q] = 2

        for q in sorted(graph):
            if state.get(q) is None:
                visit(q, [q])

    # ------------------------------------------------------------ phase 5: reads
    def resolve_reads_and_invariants(self) -> None:
        from .resolve_read import ReadResolver

        rr = ReadResolver(self)
        for qid, invariants in self._pending_invariants:
            c = self.carriers[qid]
            resolved = tuple(rr.resolve_invariant(c, expr) for expr in invariants)
            self.carriers[qid] = I.Carrier(
                c.qid, c.module, c.name, c.kind, c.meaning, c.uses, c.links, c.carries, c.lifecycle, c.archived_by,
                c.ordered_within, c.history_kept, c.breaking, c.tightens, resolved, c.scope_via, c.family, c.members,
                c.inverses, c.loc,
            )
        for scope in self.scopes.values():
            for entry in scope.decls.values():
                if entry.kind == "read":
                    self.reads[entry.qid] = rr.resolve_read(scope.decl.name.text, entry.qid, entry.node)  # type: ignore[arg-type]
        rr.check_compositions(self.reads)

    # ------------------------------------------------------------ phase 6: verbs
    def resolve_verbs(self) -> None:
        for scope in self.scopes.values():
            module = scope.decl.name.text
            for entry in scope.tombstones.values():
                node: A.TombstoneDecl = entry.node  # type: ignore[assignment]
                self.tombstones[entry.qid] = I.Tombstone(entry.qid, module, node.name.text, node.meaning, node.disposition, node.loc)
                if not node.meaning.strip():
                    refuse("RETIRE_REASON_REQUIRED", "validate", node.name, "a tombstone states why the intent retired")
            for entry in scope.decls.values():
                if entry.kind == "alias":
                    self.resolve_alias(module, entry)
                elif entry.kind == "bulk":
                    self.resolve_bulk(module, entry)
                elif entry.kind == "restricted":
                    self.resolve_restricted(module, entry)
                elif entry.kind == "compound":
                    self.resolve_compound(module, entry)
            for d in scope.decl.decls:
                if isinstance(d, (A.TightenStmt, A.RetypeStmt, A.RestoreStmt, A.MoveHomeStmt)):
                    self.resolve_evolution_stmt(module, d)
        for stmt in self.top_stmts:
            refuse("EVOLUTION_STATEMENT_HOMELESS", "validate", stmt, "evolution statements belong inside a module")

    def verb_of(self, module: str, dv: A.DottedVerb) -> tuple[str, str]:
        entry = self.lookup(module, dv.carrier, ("carrier", "member"), "CARRIER_UNKNOWN")
        self.ref(dv.carrier, entry.qid, entry.kind)
        carrier = self.carriers[entry.qid]
        if carrier.kind == "trait":
            refuse("VERB_ON_TRAIT", "validate", dv.carrier, "traits have no verbs")
        verb = dv.verb.text
        if verb not in DERIVED_VERBS:
            refuse("ALIAS_NOT_DERIVED", "validate", dv.verb, f"{verb} is not a derived verb")
        if verb == "mint" and carrier.kind == "family":
            refuse("FAMILY_MEMBER_MINT_ONLY", "validate", dv.verb, "a family is minted through one of its members")
        if verb == "append" and carrier.kind != "event":
            refuse("VERB_NOT_ADMITTED", "validate", dv.verb, "append is an event verb")
        return entry.qid, verb

    def resolve_alias(self, module: str, entry: DeclEntry) -> None:
        node: A.AliasDecl = entry.node  # type: ignore[assignment]
        carrier, verb = self.verb_of(module, node.verb)
        unscoped = node.unscoped.text if node.unscoped else None
        if node.unscoped is not None:
            self._capability_refs.append((module, node.unscoped))
        self.aliases[entry.qid] = I.Alias(entry.qid, module, node.name.text, carrier, verb, unscoped, node.loc)

    def resolve_bulk(self, module: str, entry: DeclEntry) -> None:
        from .resolve_read import ReadResolver

        node: A.BulkDecl = entry.node  # type: ignore[assignment]
        carrier_qid, verb = self.verb_of(module, node.verb)
        if verb not in BULKABLE:
            refuse("BULK_NOT_DERIVED_VERB", "validate", node.verb.verb, f"bulk over {verb} is not admitted")
        over_entry = self.lookup(module, node.over, ("read",), "READ_UNKNOWN")
        self.ref(node.over, over_entry.qid, "read")
        over = self.reads[over_entry.qid]
        if over.subject != carrier_qid:
            refuse("BULK_OVER_MISMATCH", "validate", node.over, f"{over.qid} reads {over.subject}, not {carrier_qid}")
        if over.windowed:
            refuse("BULK_OVER_PAGED", "validate", node.over, f"bulk over windowed read {over.qid} is refused")
        rr = ReadResolver(self)
        givens = tuple(rr.resolve_given(module, g) for g in node.givens)
        given_types = {g.name: g.type for g in givens}
        carrier = self.carriers[carrier_qid]
        sets: list[I.SetTerm] = []
        for sc in node.sets:
            use = carrier.use_named(sc.target.text)
            if use is None:
                refuse("BULK_SET_UNKNOWN", "validate", sc.target, f"{sc.target.text} is not a use of {carrier_qid}")
            self.ref(sc.target, use.intent, "intent")
            if use.engine_owned:
                refuse("VERB_INPUT_ENGINE_OWNED", "validate", sc.target, f"{use.intent} is stamped by the engine")
            if sc.value is None:
                if not use.optional:
                    refuse("SET_ABSENT_REQUIRED", "validate", sc, f"{use.intent} is required and cannot be set absent")
                sets.append(I.SetTerm(use.qid, None, sc.loc))
                continue
            gt = given_types.get(sc.value.text)
            if gt is None:
                refuse("BULK_PARAM_UNDECLARED", "validate", sc.value, f"{sc.value.text} is not a given of {entry.qid}")
            self.ref(sc.value, f"{entry.qid}#{sc.value.text}", "given")
            if gt.scalar() != use.type.scalar() and not (gt.base == use.type.base and not gt.list_of):
                refuse("BULK_SET_TYPE", "validate", sc.value, f"{sc.value.text} is {gt.describe()}, {use.intent} is {use.type.describe()}")
            sets.append(I.SetTerm(use.qid, sc.value.text, sc.loc))
        self.bulks[entry.qid] = I.Bulk(entry.qid, module, node.name.text, node.meaning, givens, carrier_qid, verb, over.qid, tuple(sets), node.loc)

    def resolve_restricted(self, module: str, entry: DeclEntry) -> None:
        node: A.RestrictedDecl = entry.node  # type: ignore[assignment]
        carrier_qid, verb = self.verb_of(module, node.verb)
        carrier = self.carriers[carrier_qid]
        accepts: list[str] = []
        for a in node.accepts:
            use = carrier.use_named(a.text)
            link = carrier.link_named(a.text)
            if use is not None:
                if use.engine_owned:
                    refuse("VERB_INPUT_ENGINE_OWNED", "validate", a, f"{use.intent} is stamped by the engine")
                self.ref(a, use.intent, "intent")
                accepts.append(use.qid)
            elif link is not None:
                self.ref(a, self.link_identity(link), "link")
                accepts.append(link.qid)
            else:
                refuse("RESTRICTED_ACCEPTS_UNKNOWN", "validate", a, f"{a.text} is not a use or link of {carrier_qid}")
        unscoped = node.unscoped.text if node.unscoped else None
        if node.unscoped is not None:
            self._capability_refs.append((module, node.unscoped))
        self.restricteds[entry.qid] = I.Restricted(entry.qid, module, node.name.text, node.meaning, carrier_qid, verb, tuple(accepts), unscoped, node.loc)

    def resolve_compound(self, module: str, entry: DeclEntry) -> None:
        node: A.CompoundDecl = entry.node  # type: ignore[assignment]
        steps: list[I.Step] = []
        names: dict[str, str] = {}
        for st in node.steps:
            if st.name.text in names:
                refuse("STEP_NAME_DUPLICATED", "validate", st.name, f"step {st.name.text} declared twice")
            carrier_qid, verb = self.verb_of(module, st.verb)
            self.ref(st.name, f"{entry.qid}#{st.name.text}", "step")
            carrier = self.carriers[carrier_qid]
            binds: list[I.Bind] = []
            for b in st.binds:
                if len(b.path.names) != 1:
                    refuse("STEP_BIND_PATH", "validate", b.path, "a bind names one link of the step's carrier")
                link = carrier.link_named(b.path.names[0].text)
                if link is None:
                    refuse("STEP_BIND_UNKNOWN", "validate", b.path, f"{b.path.text} is not a link of {carrier_qid}")
                self.ref(b.path.names[0], self.link_identity(link), "link")
                if b.step.text == st.name.text:
                    refuse("STEP_CYCLE", "validate", b.step, f"step {st.name.text} binds itself")
                if b.step.text not in names:
                    if any(s.name.text == b.step.text for s in node.steps):
                        refuse("STEP_CYCLE", "validate", b.step, f"step {st.name.text} binds later step {b.step.text}")
                    refuse("STEP_REFERENCE_UNRESOLVED", "validate", b.step, f"{b.step.text} is not a step of {entry.qid}")
                bound_carrier = names[b.step.text]
                if bound_carrier != link.target and self.carriers[bound_carrier].family != link.target:
                    refuse("STEP_BIND_TYPE", "validate", b.step, f"{link.qid} targets {link.target}; step {b.step.text} yields {bound_carrier}")
                self.ref(b.step, f"{entry.qid}#{b.step.text}", "step")
                binds.append(I.Bind(link.qid, b.step.text, b.loc))
            names[st.name.text] = carrier_qid
            steps.append(I.Step(st.name.text, carrier_qid, verb, st.each.text if st.each else None, tuple(binds), st.loc))
        self.compounds[entry.qid] = I.Compound(entry.qid, module, node.name.text, node.meaning, tuple(steps), node.loc)

    def resolve_evolution_stmt(self, module: str, d: A.TopLevel) -> None:
        if isinstance(d, A.TightenStmt):
            if len(d.path.names) != 2:
                refuse("TIGHTEN_PATH_INVALID", "validate", d.path, "tighten names Carrier.intent")
            centry = self.lookup(module, d.path.names[0], ("carrier", "member"), "CARRIER_UNKNOWN")
            self.ref(d.path.names[0], centry.qid, centry.kind)
            carrier = self.carriers[centry.qid]
            use = carrier.use_named(d.path.names[1].text)
            if use is None:
                refuse("TIGHTEN_UNKNOWN", "validate", d.path.names[1], f"{d.path.text} is not a use")
            self.ref(d.path.names[1], use.intent, "intent")
            self.tightens.append(I.TightenDecl(module, (centry.qid, use.intent), self.resolve_repair(d.repair, use.type, d), d.loc))
        elif isinstance(d, A.RetypeStmt):
            entry = self.lookup(module, d.name, ("intent",), "TERM_UNKNOWN")
            self.ref(d.name, entry.qid, "intent")
            if d.clause.target.text not in BUILTIN_SCALARS:
                refuse("TYPE_UNKNOWN", "validate", d.clause.target, "retype from unknown builtin")
            self.retypes.append(I.RetypeDecl(module, entry.qid, d.clause.target.text, d.clause.forward, d.clause.backward, d.loc))
        elif isinstance(d, A.RestoreStmt):
            entry = self.lookup(module, d.name, ("intent",), "TERM_UNKNOWN")
            self.ref(d.name, entry.qid, entry.kind)
            self.restores.append(I.RestoreDecl(module, entry.qid, d.loc))
        elif isinstance(d, A.MoveHomeStmt):
            ientry = self.lookup(module, d.intent, ("intent",), "TERM_UNKNOWN")
            self.ref(d.intent, ientry.qid, "intent")
            sentry = self.lookup(module, d.source, ("carrier", "member"), "CARRIER_UNKNOWN")
            self.ref(d.source, sentry.qid, sentry.kind)
            tentry = self.lookup(module, d.target, ("carrier", "member"), "CARRIER_UNKNOWN")
            self.ref(d.target, tentry.qid, tentry.kind)
            self.move_homes.append(I.MoveHome(module, ientry.qid, sentry.qid, tentry.qid, d.disposition, d.loc))
        else:
            raise TypeError(d)

    # ----------------------------------------------------------- phase 7: worlds
    def resolve_worlds(self) -> None:
        for node in self.world_nodes:
            if node.name.text in self.worlds:
                refuse("WORLD_DUPLICATED", "validate", node.name, f"world {node.name.text} declared twice")
            self.ref(node.name, node.name.text, "world")
            self.worlds[node.name.text] = self.resolve_world(node)
        self.check_capabilities()
        for node in self.dep_nodes:
            if node.name.text in self.deployments:
                refuse("DEPLOYMENT_DUPLICATED", "validate", node.name, f"deployment {node.name.text} declared twice")
            self.ref(node.name, node.name.text, "deployment")
        for node in self.dep_nodes:
            self.deployments[node.name.text] = self.resolve_deployment(node, set())

    def resolve_world(self, node: A.WorldDecl) -> I.World:
        seen: dict[str, A.WorldItem] = {}
        for item in node.items:
            if item.kind in seen:
                refuse("WORLD_ITEM_REPEATED", "validate", item, f"{item.kind} stated twice in world {node.name.text}")
            seen[item.kind] = item
        for required, code in (
            ("modules", "WORLD_MODULES_REQUIRED"),
            ("durability", "WORLD_DURABILITY_REQUIRED"),
            ("writers", "WORLD_WRITERS_REQUIRED"),
            ("generated", "WORLD_GENERATED_REQUIRED"),
            ("scope", "WORLD_SCOPE_REQUIRED"),
            ("quarantine_retention", "QUARANTINE_RETENTION_REQUIRED"),
        ):
            if required not in seen:
                refuse(code, "validate", node.name, f"world {node.name.text} states no {required}")
        modules: list[str] = []
        for m in seen["modules"].names:
            if m.text not in self.scopes:
                refuse("MODULE_UNKNOWN", "validate", m, f"module {m.text} is not declared")
            if m.text in modules:
                refuse("WORLD_MODULE_REPEATED", "validate", m, f"module {m.text} listed twice")
            if m.text in self.world_of_module:
                refuse("WORLD_MODULE_COLLISION", "validate", m, f"module {m.text} already belongs to world {self.world_of_module[m.text]}")
            self.ref(m, m.text, "module")
            modules.append(m.text)
        for m in modules:
            self.world_of_module[m] = node.name.text
        # transitive imports must be listed
        for m in modules:
            for imp in self.scopes[m].decl.imports:
                if imp.owner.text not in modules:
                    refuse("MODULE_NOT_LISTED", "validate", imp.owner, f"{m} imports {imp.owner.text}, which world {node.name.text} does not list")
        durability = seen["durability"].names[0]
        if durability.text not in DURABILITIES:
            refuse("DURABILITY_UNKNOWN", "validate", durability, f"durability {durability.text} is not admitted")
        writers = seen["writers"].names[0]
        if writers.text not in WRITER_CLASSES:
            refuse("WRITER_CLASS_UNKNOWN", "validate", writers, f"writers {writers.text} is not admitted")
        generated: list[str] = []
        for g in seen["generated"].names:
            if g.text not in TARGETS:
                refuse("TARGET_UNKNOWN", "validate", g, f"generated target {g.text} has no surface in this build")
            if g.text in generated:
                refuse("WORLD_TARGET_REPEATED", "validate", g, f"target {g.text} listed twice")
            generated.append(g.text)
        writer_source = None
        if "writer_source" in seen:
            if writers.text != "external_captured":
                refuse("WRITER_SOURCE_NOT_ADMITTED", "validate", seen["writer_source"], "writer_source belongs to external_captured worlds")
            writer_source = seen["writer_source"].names[0].text
            self.ref(seen["writer_source"].names[0], f"{node.name.text}#writer_source:{writer_source}", "writer")
        elif writers.text == "external_captured":
            refuse("WRITER_SOURCE_REQUIRED", "validate", writers, "an external_captured world names its writer_source")
        retention = seen["quarantine_retention"].integer
        assert retention is not None
        if retention <= 0:
            refuse("QUARANTINE_RETENTION_INVALID", "validate", seen["quarantine_retention"], "retention is a positive generation count")
        capabilities: list[str] = []
        if "capabilities" in seen:
            for c in seen["capabilities"].names:
                if c.text in capabilities:
                    refuse("CAPABILITY_REPEATED", "validate", c, f"capability {c.text} listed twice")
                self.ref(c, f"{node.name.text}#capability:{c.text}", "capability")
                capabilities.append(c.text)
        requires: str | None = None
        exempt: list[str] = []
        if "requires" in seen:
            item = seen["requires"]
            assert item.qname is not None
            entry = self.lookup_qualified(item.qname, ("carrier",), "TRAIT_UNKNOWN", "carrier")
            if item.qname.parts[0].text not in modules:
                refuse("MODULE_NOT_LISTED", "validate", item.qname.parts[0], f"{item.qname.text} lives outside the world's modules")
            trait = self.carriers[entry.qid]
            if trait.kind != "trait":
                refuse("REQUIRES_NOT_TRAIT", "validate", item.qname, f"{item.qname.text} is not a trait")
            requires = entry.qid
            for ex in item.exempt:
                xentry = self.lookup_qualified(ex, ("carrier", "member"), "EXEMPT_UNKNOWN", "carrier")
                if ex.parts[0].text not in modules:
                    refuse("MODULE_NOT_LISTED", "validate", ex.parts[0], f"{ex.text} lives outside the world's modules")
                xc = self.carriers[xentry.qid]
                if xc.kind in ("trait", "member"):
                    refuse("EXEMPT_NOT_CARRIER", "validate", ex, f"{ex.text} cannot be exempted")
                if requires in xc.carries:
                    refuse("EXEMPT_REDUNDANT", "validate", ex, f"{ex.text} carries {requires} and is also exempted")
                if xentry.qid in exempt:
                    refuse("EXEMPT_REPEATED", "validate", ex, f"{ex.text} exempted twice")
                exempt.append(xentry.qid)
        scope_item = seen["scope"]
        scope: I.ScopeRoot | None = None
        if not scope_item.deployment_scope:
            assert scope_item.path is not None
            names = scope_item.path.names
            if len(names) != 3:
                refuse("SCOPE_PATH_INVALID", "validate", scope_item.path, "scope names module.Trait.link")
            if names[0].text not in self.scopes:
                refuse("MODULE_UNKNOWN", "validate", names[0], f"module {names[0].text} is not declared")
            if names[0].text not in modules:
                refuse("MODULE_NOT_LISTED", "validate", names[0], f"scope module {names[0].text} is not listed")
            self.ref(names[0], names[0].text, "module")
            tentry = self.scopes[names[0].text].decls.get(names[1].text)
            if tentry is None or tentry.kind != "carrier" or self.carriers[tentry.qid].kind != "trait":
                refuse("TRAIT_UNKNOWN", "validate", names[1], f"{names[0].text}.{names[1].text} is not a trait")
            self.ref(names[1], tentry.qid, "carrier")
            if requires is None:
                refuse("WORLD_REQUIRES_REQUIRED", "validate", scope_item, "a scoped world requires its scope trait")
            if tentry.qid != requires:
                refuse("SCOPE_ROOT_MISMATCH", "validate", names[1], f"scope trait {tentry.qid} differs from required trait {requires}")
            link = self.carriers[tentry.qid].link_named(names[2].text)
            if link is None:
                refuse("SCOPE_LINK_UNKNOWN", "validate", names[2], f"{names[2].text} is not a link of {tentry.qid}")
            self.ref(names[2], link.qid, "link")
            if not link.scopes:
                refuse("SCOPE_ROOT_NOT_SCOPED", "validate", names[2], f"{link.qid} is not marked scopes")
            scope = I.ScopeRoot(tentry.qid, link.qid, link.target)
        world = I.World(
            node.name.text, node.meaning, tuple(modules), durability.text, writers.text, tuple(generated), requires,
            tuple(exempt), scope, tuple(capabilities), writer_source, retention, node.loc,
        )
        self.scope_paths[world.name] = self.compute_scope_paths(world, node)
        return world

    def compute_scope_paths(self, world: I.World, node: A.WorldDecl) -> dict[str, tuple[str, ...]]:
        paths: dict[str, tuple[str, ...]] = {}
        in_world = [c for c in self.carriers.values() if c.module in world.modules]
        for c in in_world:
            for l in c.links:
                if not l.scopes or c.kind == "member":
                    continue
                if world.scope is not None and (l.qid == world.scope.link or l.origin == world.scope.trait):
                    continue
                refuse("SCOPE_LINK_NOT_ROOT", "validate", l, f"{l.qid} is marked scopes but is not the world's scope root")
        if world.scope is None:
            for c in in_world:
                if c.is_storable:
                    paths[c.qid] = ()
            return paths
        root_link = self.carriers[world.scope.trait].link_named(world.scope.link.rsplit(".", 1)[-1])
        assert root_link is not None
        storable = [c for c in in_world if c.is_storable]
        # direct carriers of the trait
        for c in storable:
            if world.scope.trait in c.carries:
                paths[c.qid] = (f"{c.qid}.{root_link.name}",)
        # explicit scope_via first, then implicit unique links; iterate to a fixpoint
        changed = True
        while changed:
            changed = False
            for c in storable:
                if c.qid in paths or c.qid in world.exempt:
                    continue
                if c.scope_via is not None:
                    link = self.carriers[c.qid].link_named(c.scope_via.rsplit(".", 1)[-1])
                    assert link is not None
                    if link.target in paths:
                        paths[c.qid] = (link.qid,) + paths[link.target]
                        changed = True
                    continue
                candidates = [l for l in c.links if l.target in paths]
                if len(candidates) == 1:
                    paths[c.qid] = (candidates[0].qid,) + paths[candidates[0].target]
                    changed = True
        for c in storable:
            if c.qid in paths:
                continue
            if c.qid in world.exempt:
                paths[c.qid] = ()
                continue
            if c.scope_via is not None:
                link = self.carriers[c.qid].link_named(c.scope_via.rsplit(".", 1)[-1])
                assert link is not None
                refuse("SCOPE_PATH_TO_EXEMPT", "validate", link, f"{c.qid} is scoped via {link.qid}, whose target {link.target} carries no scope path")
            candidates = [l for l in c.links if l.target in paths and paths[l.target]]
            if len(candidates) > 1:
                refuse("SCOPE_PATH_AMBIGUOUS", "validate", c, f"{c.qid} reaches the scope root through {', '.join(l.name for l in candidates)}; declare scope_via")
            refuse("TRAIT_REQUIRED", "validate", c, f"{c.qid} neither carries {world.scope.trait}, is exempt, nor is scoped through a link")
        for c in in_world:
            if c.kind == "member" and c.family in paths:
                paths[c.qid] = paths[c.family]
        return paths

    def check_capabilities(self) -> None:
        for module, name in self._capability_refs:
            world_name = self.world_of_module.get(module)
            if world_name is None:
                continue
            world = self.worlds[world_name]
            if name.text not in world.capabilities:
                refuse("CAPABILITY_UNKNOWN", "validate", name, f"world {world_name} declares no capability {name.text}")
            self.ref(name, f"{world_name}#capability:{name.text}", "capability")

    def resolve_deployment(self, node: A.DeploymentDecl, chain: set[str]) -> I.Deployment:
        if node.name.text in self.deployments:
            return self.deployments[node.name.text]
        if node.name.text in chain:
            refuse("DEPLOYMENT_EXTENDS_CYCLE", "validate", node.name, "extends cycle")
        base: I.Deployment | None = None
        if node.extends is not None:
            base_node = next((d for d in self.dep_nodes if d.name.text == node.extends.text), None)
            if base_node is None:
                refuse("DEPLOYMENT_EXTENDS_UNKNOWN", "validate", node.extends, f"deployment {node.extends.text} is not declared")
            self.ref(node.extends, node.extends.text, "deployment")
            base = self.resolve_deployment(base_node, chain | {node.name.text})
        values: dict[str, object] = {}
        if base is not None:
            values = {"world": base.world, "engine": base.engine, "at": base.location, "ship": base.ship, "mode": base.mode, "snapshot": base.snapshot, "pool": base.pool}
        seen: set[str] = set()
        engine_at: A.Name | None = None
        for item in node.items:
            if item.kind in seen:
                refuse("DEPLOYMENT_ITEM_REPEATED", "validate", item, f"{item.kind} stated twice")
            seen.add(item.kind)
            if item.kind == "world":
                assert item.name is not None
                if item.name.text not in self.worlds:
                    refuse("WORLD_UNKNOWN", "validate", item.name, f"world {item.name.text} is not declared")
                self.ref(item.name, item.name.text, "world")
                values["world"] = item.name.text
            elif item.kind == "engine":
                assert item.name is not None
                if item.name.text not in ENGINES:
                    refuse("ENGINE_UNKNOWN", "validate", item.name, f"engine {item.name.text} is not admitted")
                values["engine"] = item.name.text
                engine_at = item.name
            elif item.kind == "at":
                assert item.location is not None
                values["at"] = I.Location(item.location.kind, item.location.name.text if item.location.name else None, item.location.default)
            elif item.kind == "ship":
                assert item.name is not None
                if item.name.text not in SHIP_MODES:
                    refuse("SHIP_MODE_UNKNOWN", "validate", item.name, f"ship {item.name.text} is not admitted")
                values["ship"] = item.name.text
            elif item.kind == "mode":
                assert item.name is not None
                if item.name.text not in MODES:
                    refuse("DEPLOYMENT_MODE_UNKNOWN", "validate", item.name, f"mode {item.name.text} is not admitted")
                values["mode"] = item.name.text
            elif item.kind == "snapshot":
                assert item.name is not None
                if item.name.text not in SNAPSHOTS:
                    refuse("SNAPSHOT_UNKNOWN", "validate", item.name, f"snapshot {item.name.text} is not admitted")
                values["snapshot"] = item.name.text
            elif item.kind == "pool":
                values["pool"] = item.integer
        for key, code in (
            ("world", "DEPLOYMENT_WORLD_REQUIRED"),
            ("engine", "ENGINE_REQUIRED"),
            ("at", "DEPLOYMENT_LOCATION_REQUIRED"),
            ("ship", "SHIP_MODE_REQUIRED"),
            ("mode", "DEPLOYMENT_MODE_REQUIRED"),
            ("snapshot", "DEPLOYMENT_SNAPSHOT_REQUIRED"),
        ):
            if key not in values:
                refuse(code, "validate", node.name, f"deployment {node.name.text} states no {key}")
        engine = str(values["engine"])
        if engine not in LOWERED_ENGINES:
            # a recognised engine without a lowering: refuse at validation, before any schema, store, ledger,
            # generation, or migration effect (R1 P2.4 repair)
            refuse(
                "ENGINE_LOWERING_ABSENT", "validate", engine_at if engine_at is not None else node.name,
                f"deployment {node.name.text} uses engine {engine}, which this build recognises but cannot lower (lowered engines: {', '.join(sorted(LOWERED_ENGINES))})",
            )
        dep = I.Deployment(
            node.name.text, node.meaning, node.extends.text if node.extends else None, str(values["world"]),
            str(values["engine"]), values["at"], str(values["ship"]), str(values["mode"]), str(values["snapshot"]),  # type: ignore[arg-type]
            values.get("pool"), node.loc,  # type: ignore[arg-type]
        )
        self.deployments[node.name.text] = dep
        return dep

    # ---------------------------------------------------------- phase 8: closure
    def check_homeless_intents(self) -> None:
        used: set[str] = set()
        for c in self.carriers.values():
            for u in c.uses:
                used.add(u.intent)
        for t in self.tombstones.values():
            used.add(t.qid)
        for i in self.intents.values():
            if i.qid not in used and not i.retired:
                refuse("INTENT_HOMELESS", "validate", i, f"intent {i.qid} is used by no carrier")

    def check_tombstones(self) -> None:
        for t in self.tombstones.values():
            same = self.scopes[t.module].decls.get(t.name)
            if same is not None and same.kind == "intent":
                intent = self.intents[same.qid]
                if not intent.restore:
                    refuse("ID_RESERVED", "validate", intent, f"{t.qid} is tombstoned; redeclaring it requires restore")
            elif same is not None:
                refuse("ID_RESERVED", "validate", same.node, f"{t.qid} is tombstoned and cannot be redeclared as a {same.kind}")

    # ------------------------------------------------------------------- driver
    _pending_invariants: list[tuple[str, list[A.DynExpr]]]
    _required_link_cycle_check: list[str]
    _capability_refs: list[tuple[str, A.Name]]

    def run(self) -> I.Program:
        self._pending_invariants = []
        self._required_link_cycle_check = []
        self._capability_refs = []
        self.collect()
        self.resolve_imports()
        self.resolve_intents()
        self.resolve_carriers()
        self.resolve_reads_and_invariants()
        self.resolve_verbs()
        self.check_tombstones()
        self.resolve_worlds()
        self.check_homeless_intents()
        self.check_unused_imports()
        modules = []
        for scope in self.scopes.values():
            imports = tuple(I.Import(e.owner, e.source, e.local, e.identity, e.node.loc) for e in scope.imports.values())
            modules.append(I.Module(scope.decl.name.text, scope.decl.meaning, imports, scope.decl.loc.file, scope.decl.loc))
        return I.Program(
            tuple(modules),
            tuple(self.intents[k] for k in sorted(self.intents)),
            tuple(self.newtypes[k] for k in sorted(self.newtypes)),
            tuple(self.carriers[k] for k in sorted(self.carriers)),
            tuple(self.reads[k] for k in sorted(self.reads)),
            tuple(self.aliases[k] for k in sorted(self.aliases)),
            tuple(self.bulks[k] for k in sorted(self.bulks)),
            tuple(self.restricteds[k] for k in sorted(self.restricteds)),
            tuple(self.compounds[k] for k in sorted(self.compounds)),
            tuple(self.tombstones[k] for k in sorted(self.tombstones)),
            tuple(self.tightens),
            tuple(self.retypes),
            tuple(self.restores),
            tuple(self.move_homes),
            tuple(self.worlds[k] for k in sorted(self.worlds)),
            tuple(self.deployments[k] for k in sorted(self.deployments)),
            self.scope_paths,
            tuple(self.refs),
        )


def resolve_files(files: Iterable[A.SourceFile]) -> I.Program:
    return Resolver(files).run()


def resolve_paths(paths: Iterable) -> I.Program:
    from .parse import parse_path

    return resolve_files([parse_path(p) for p in paths])
