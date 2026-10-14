"""Storage bindings: explicit physical mappings for one world.

A binding is an input document (JSON) that maps every qualified relation, use,
link, family discriminator, engine table, and changelog field of a world to a
physical name. Nothing here is derived from a naming convention: a missing or
ambiguous mapping refuses before any lowering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from . import ir as I
from .refuse import Refusal

SCHEMA = "garns-v9-5/storage-binding/1"
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class CaptureMapping:
    table: str
    seq: str
    op: str
    revision: str
    identity: str
    columns: dict[str, str]  # use qid -> changelog column
    links: dict[str, str]  # link qid -> changelog column


@dataclass(frozen=True)
class RelationMapping:
    carrier: str
    table: str
    identity: str
    columns: dict[str, str]  # use qid -> column
    links: dict[str, str]  # link qid -> column
    kind: str | None
    capture: CaptureMapping | None


@dataclass(frozen=True)
class EngineTables:
    ledger: str
    generations: str
    revisions: str


@dataclass(frozen=True)
class StorageMapping:
    world: str
    engine: EngineTables
    relations: dict[str, RelationMapping]
    source: str

    def relation(self, carrier: str) -> RelationMapping:
        return self.relations[carrier]


@dataclass(frozen=True)
class WorldIR:
    """A selected world with its explicit storage and scope model."""

    program: I.Program
    world: I.World
    storage: StorageMapping
    scope_paths: dict[str, tuple[str, ...]]

    @property
    def carriers(self) -> tuple[I.Carrier, ...]:
        return tuple(c for c in self.program.carriers if c.module in self.world.modules)

    @property
    def relations(self) -> tuple[I.Carrier, ...]:
        return tuple(c for c in self.carriers if c.is_storable)

    @property
    def reads(self) -> tuple[I.Read, ...]:
        return tuple(r for r in self.program.reads if r.module in self.world.modules)

    def carrier(self, qid: str) -> I.Carrier:
        return self.program.carrier(qid)

    def relation_carrier(self, qid: str) -> I.Carrier:
        """The storable carrier whose table holds ``qid`` (members map to their family)."""
        c = self.program.carrier(qid)
        if c.kind == "member":
            assert c.family is not None
            return self.program.carrier(c.family)
        return c

    def relation_of(self, qid: str) -> RelationMapping:
        return self.storage.relation(self.relation_carrier(qid).qid)

    def column_of(self, carrier_qid: str, use: I.Use) -> str:
        rel = self.relation_of(carrier_qid)
        return rel.columns[self.storage_use_key(carrier_qid, use)]

    def storage_use_key(self, carrier_qid: str, use: I.Use) -> str:
        c = self.program.carrier(carrier_qid)
        local = use.intent.rsplit(".", 1)[-1]
        if c.kind == "member":
            family = self.program.carrier(c.family)  # type: ignore[arg-type]
            if family.use_named(local) is not None:
                return f"{family.qid}.{local}"
        return f"{carrier_qid}.{local}"

    def storage_link_key(self, carrier_qid: str, link: I.Link) -> str:
        c = self.program.carrier(carrier_qid)
        if c.kind == "member":
            family = self.program.carrier(c.family)  # type: ignore[arg-type]
            if family.link_named(link.name) is not None:
                return f"{family.qid}.{link.name}"
        return f"{carrier_qid}.{link.name}"

    def link_column_of(self, carrier_qid: str, link: I.Link) -> str:
        rel = self.relation_of(carrier_qid)
        return rel.links[self.storage_link_key(carrier_qid, link)]

    def scope_path(self, carrier_qid: str) -> tuple[str, ...]:
        return self.scope_paths.get(carrier_qid, ())

    def digest(self) -> str:
        return I.digest({"program": self.program, "world": self.world.name, "storage": self.storage})


def _fail(code: str, source: str, detail: str) -> None:
    raise Refusal(code, "validate", source, 1, 1, detail)


def _ident(name: object, source: str, what: str) -> str:
    if not isinstance(name, str) or not IDENT.match(name):
        _fail("STORAGE_NAME_INVALID", source, f"{what}: {name!r} is not a plain identifier")
    return name  # type: ignore[return-value]


def load_binding(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Refusal("STORAGE_BINDING_UNREADABLE", "validate", str(path), 1, 1, str(exc)) from None
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        _fail("STORAGE_SCHEMA_UNKNOWN", str(path), f"expected schema {SCHEMA}")
    return data


def expected_relation_keys(program: I.Program, carrier: I.Carrier) -> tuple[dict[str, I.Use], dict[str, I.Link]]:
    """All (storage key -> use/link) a relation must map, members included."""
    uses: dict[str, I.Use] = {}
    links: dict[str, I.Link] = {}
    for u in carrier.uses:
        uses[f"{carrier.qid}.{u.intent.rsplit('.', 1)[-1]}"] = u
    for l in carrier.links:
        links[f"{carrier.qid}.{l.name}"] = l
    for member_qid in carrier.members:
        member = program.carrier(member_qid)
        for u in member.uses:
            local = u.intent.rsplit(".", 1)[-1]
            if carrier.use_named(local) is None:
                uses[f"{member.qid}.{local}"] = u
        for l in member.links:
            if carrier.link_named(l.name) is None:
                links[f"{member.qid}.{l.name}"] = l
    return uses, links


def bind_world(program: I.Program, world_name: str, binding_path: Path) -> WorldIR:
    """Select ``world_name`` explicitly and attach its storage binding."""
    if not any(w.name == world_name for w in program.worlds):
        names = ", ".join(w.name for w in program.worlds) or "none"
        raise Refusal("WORLD_UNKNOWN", "validate", str(binding_path), 1, 1, f"world {world_name} is not declared (declared: {names})")
    world = program.world(world_name)
    source = str(binding_path)
    data = load_binding(binding_path)
    if data.get("world") != world_name:
        _fail("STORAGE_WORLD_MISMATCH", source, f"binding is for world {data.get('world')!r}, not {world_name}")
    engine_raw = data.get("engine")
    if not isinstance(engine_raw, dict):
        _fail("STORAGE_ENGINE_TABLES_MISSING", source, "engine tables (ledger, generations, revisions) are required")
    engine = EngineTables(
        _ident(engine_raw.get("ledger"), source, "engine.ledger"),
        _ident(engine_raw.get("generations"), source, "engine.generations"),
        _ident(engine_raw.get("revisions"), source, "engine.revisions"),
    )
    relations_raw = data.get("relations")
    if not isinstance(relations_raw, dict):
        _fail("STORAGE_RELATIONS_MISSING", source, "relations are required")
    storable = {c.qid: c for c in program.carriers if c.module in world.modules and c.is_storable}
    for qid in relations_raw:
        if qid not in storable:
            _fail("STORAGE_RELATION_UNKNOWN", source, f"{qid} is not a storable carrier of world {world_name}")
    tables: dict[str, str] = {engine.ledger: "engine.ledger", engine.generations: "engine.generations", engine.revisions: "engine.revisions"}
    if len(tables) != 3:
        _fail("STORAGE_TABLE_COLLISION", source, "engine tables must be distinct")
    capture_raw = data.get("capture") or {}
    if world.writers == "external_captured" and not isinstance(capture_raw, dict):
        _fail("WRITER_CAPTURE_INCOMPLETE", source, "an external_captured world maps a changelog per relation")
    if world.writers != "external_captured" and capture_raw:
        _fail("STORAGE_CAPTURE_NOT_ADMITTED", source, "capture mappings belong to external_captured worlds")
    relations: dict[str, RelationMapping] = {}
    for qid, carrier in sorted(storable.items()):
        raw = relations_raw.get(qid)
        if not isinstance(raw, dict):
            _fail("STORAGE_RELATION_MISSING", source, f"no relation mapping for {qid}")
        table = _ident(raw.get("table"), source, f"{qid}.table")
        if table in tables:
            _fail("STORAGE_TABLE_COLLISION", source, f"table {table} is mapped by both {tables[table]} and {qid}")
        tables[table] = qid
        identity = _ident(raw.get("identity"), source, f"{qid}.identity")
        uses, links = expected_relation_keys(program, carrier)
        columns_raw = raw.get("columns")
        links_raw = raw.get("links")
        if not isinstance(columns_raw, dict) or not isinstance(links_raw, dict):
            _fail("STORAGE_COLUMNS_MISSING", source, f"{qid} needs columns and links maps")
        for key in columns_raw:
            if key not in uses:
                _fail("STORAGE_COLUMN_UNKNOWN", source, f"{qid} maps unknown use {key}")
        for key in links_raw:
            if key not in links:
                _fail("STORAGE_LINK_UNKNOWN", source, f"{qid} maps unknown link {key}")
        seen: dict[str, str] = {identity: "identity"}
        columns: dict[str, str] = {}
        for key in uses:
            if key not in columns_raw:
                _fail("STORAGE_COLUMN_MISSING", source, f"{qid} maps no column for use {key}")
            col = _ident(columns_raw[key], source, f"{qid}.columns[{key}]")
            if col in seen:
                _fail("STORAGE_COLUMN_COLLISION", source, f"{qid}: column {col} is used by {seen[col]} and {key}")
            seen[col] = key
            columns[key] = col
        link_columns: dict[str, str] = {}
        for key in links:
            if key not in links_raw:
                _fail("STORAGE_LINK_MISSING", source, f"{qid} maps no column for link {key}")
            col = _ident(links_raw[key], source, f"{qid}.links[{key}]")
            if col in seen:
                _fail("STORAGE_COLUMN_COLLISION", source, f"{qid}: column {col} is used by {seen[col]} and {key}")
            seen[col] = key
            link_columns[key] = col
        kind = None
        if carrier.kind == "family":
            kind = _ident(raw.get("kind"), source, f"{qid}.kind")
            if kind in seen:
                _fail("STORAGE_COLUMN_COLLISION", source, f"{qid}: kind column {kind} collides with {seen[kind]}")
        elif raw.get("kind") is not None:
            _fail("STORAGE_KIND_NOT_ADMITTED", source, f"{qid} is not a family; kind has no meaning")
        capture = None
        if world.writers == "external_captured":
            craw = capture_raw.get(qid)
            if not isinstance(craw, dict):
                _fail("WRITER_CAPTURE_INCOMPLETE", source, f"no changelog mapping for {qid}")
            ctable = _ident(craw.get("table"), source, f"capture[{qid}].table")
            if ctable in tables:
                _fail("STORAGE_TABLE_COLLISION", source, f"changelog table {ctable} collides with {tables[ctable]}")
            tables[ctable] = f"capture:{qid}"
            fields_raw = craw.get("fields")
            if not isinstance(fields_raw, dict):
                _fail("WRITER_CAPTURE_INCOMPLETE", source, f"capture[{qid}] needs fields")
            cseen: dict[str, str] = {}
            meta: dict[str, str] = {}
            for name in ("seq", "op", "revision", "identity"):
                value = _ident(fields_raw.get(name), source, f"capture[{qid}].fields.{name}")
                if value in cseen:
                    _fail("STORAGE_COLUMN_COLLISION", source, f"capture[{qid}]: {value} used twice")
                cseen[value] = name
                meta[name] = value
            ccols_raw = fields_raw.get("columns")
            clinks_raw = fields_raw.get("links")
            if not isinstance(ccols_raw, dict) or not isinstance(clinks_raw, dict):
                _fail("WRITER_CAPTURE_INCOMPLETE", source, f"capture[{qid}] needs columns and links maps")
            ccols: dict[str, str] = {}
            for key in uses:
                if key not in ccols_raw:
                    _fail("WRITER_CAPTURE_INCOMPLETE", source, f"capture[{qid}] does not cover use {key}")
                value = _ident(ccols_raw[key], source, f"capture[{qid}].columns[{key}]")
                if value in cseen:
                    _fail("STORAGE_COLUMN_COLLISION", source, f"capture[{qid}]: {value} used twice")
                cseen[value] = key
                ccols[key] = value
            clinks: dict[str, str] = {}
            for key in links:
                if key not in clinks_raw:
                    _fail("WRITER_CAPTURE_INCOMPLETE", source, f"capture[{qid}] does not cover link {key}")
                value = _ident(clinks_raw[key], source, f"capture[{qid}].links[{key}]")
                if value in cseen:
                    _fail("STORAGE_COLUMN_COLLISION", source, f"capture[{qid}]: {value} used twice")
                cseen[value] = key
                clinks[key] = value
            for key in ccols_raw:
                if key not in uses:
                    _fail("STORAGE_COLUMN_UNKNOWN", source, f"capture[{qid}] maps unknown use {key}")
            for key in clinks_raw:
                if key not in links:
                    _fail("STORAGE_LINK_UNKNOWN", source, f"capture[{qid}] maps unknown link {key}")
            capture = CaptureMapping(ctable, meta["seq"], meta["op"], meta["revision"], meta["identity"], ccols, clinks)
        relations[qid] = RelationMapping(qid, table, identity, columns, link_columns, kind, capture)
    # the mapping records only the binding's file name: generated artifacts must not depend on where the corpus lives
    storage = StorageMapping(world_name, engine, relations, Path(binding_path).name)
    return WorldIR(program, world, storage, dict(program.scope_paths.get(world_name, {})))


def binding_document(program: I.Program, world_name: str, names) -> dict:
    """Build a binding document from a naming callback.

    ``names(kind, key)`` returns the physical name for ``kind`` in
    {"table", "identity", "column", "link", "kind", "engine", "capture_table", "capture_field"}.
    This is an authoring aid used by tools and the metamorphic harness; the
    compiler never calls it.
    """
    world = program.world(world_name)
    doc: dict = {"schema": SCHEMA, "world": world_name, "engine": {k: names("engine", k) for k in ("ledger", "generations", "revisions")}, "relations": {}}
    capture: dict = {}
    for c in sorted((c for c in program.carriers if c.module in world.modules and c.is_storable), key=lambda c: c.qid):
        uses, links = expected_relation_keys(program, c)
        rel = {
            "table": names("table", c.qid),
            "identity": names("identity", c.qid),
            "columns": {k: names("column", k) for k in uses},
            "links": {k: names("link", k) for k in links},
        }
        if c.kind == "family":
            rel["kind"] = names("kind", c.qid)
        doc["relations"][c.qid] = rel
        if world.writers == "external_captured":
            capture[c.qid] = {
                "table": names("capture_table", c.qid),
                "fields": {
                    "seq": names("capture_field", f"{c.qid}#seq"),
                    "op": names("capture_field", f"{c.qid}#op"),
                    "revision": names("capture_field", f"{c.qid}#revision"),
                    "identity": names("capture_field", f"{c.qid}#identity"),
                    "columns": {k: names("capture_field", k) for k in uses},
                    "links": {k: names("capture_field", k) for k in links},
                },
            }
    if capture:
        doc["capture"] = capture
    return doc
