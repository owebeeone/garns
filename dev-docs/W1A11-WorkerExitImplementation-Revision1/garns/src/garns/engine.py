"""Store, typed governed writes, ledger, and read execution.

The engine consumes the world IR and its storage binding only. Every SQL
statement it issues names tables and columns through the binding; every
delta it records is validated against the IR before any database effect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
import sqlite3
import time
from typing import Any, Callable, Iterable

from . import ir as I
from .lower_sqlite import CLOCK_PARAM, PARENTS_PARAM, SCOPE_PARAM, ChildPlan, Plan, lower_ddl, lower_read, q
from .refuse import Refusal
from .storage import WorldIR, expected_relation_keys

TRANSACTION_ID = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
GLOBAL_SCOPE = None  # rows of unscoped carriers and deployment-scoped worlds


@dataclass(frozen=True)
class FieldChange:
    field: str  # use qid or link qid, carrier-qualified
    old: Any
    new: Any


@dataclass(frozen=True)
class Delta:
    carrier: str
    identity: int
    operation: str  # insert | update | delete
    changes: tuple[FieldChange, ...]
    scope_before: int | None
    scope_after: int | None
    writer: str
    transaction: str

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(c.field for c in self.changes)

    def as_dict(self) -> dict[str, Any]:
        return {
            "carrier": self.carrier,
            "identity": self.identity,
            "operation": self.operation,
            "changes": [{"field": c.field, "old": c.old, "new": c.new} for c in self.changes],
            "scope_before": self.scope_before,
            "scope_after": self.scope_after,
            "writer": self.writer,
            "transaction": self.transaction,
        }


@dataclass
class Result:
    rows: list[dict[str, Any]]
    keys: list[tuple[Any, ...]]
    total: int | None


def _runtime(code: str, detail: str) -> Refusal:
    return Refusal(code, "runtime", "", 1, 1, detail)


class LedgerValidator:
    """Typed pre-effect validation of every identity a ledger record names."""

    def __init__(self, world: WorldIR) -> None:
        self.world = world
        self.fields: dict[str, dict[str, I.Use | I.Link]] = {}
        for c in world.relations:
            uses, links = expected_relation_keys(world.program, c)
            table: dict[str, I.Use | I.Link] = {}
            table.update(uses)
            table.update(links)
            self.fields[c.qid] = table
            for m in c.members:
                self.fields[m] = table
        w = world.world
        self.writers = {w.writers} if w.writers == "governed" else {w.writer_source or ""}

    def check_writer(self, writer: str) -> None:
        if writer not in self.writers:
            raise _runtime("LEDGER_WRITER_UNKNOWN", f"writer {writer!r} is not declared by world {self.world.world.name} (declared: {sorted(self.writers)})")

    def check_transaction(self, txid: str) -> None:
        if not isinstance(txid, str) or not TRANSACTION_ID.match(txid):
            raise _runtime("LEDGER_TRANSACTION_INVALID", f"transaction id {txid!r} is not a typed identity")

    def check_carrier(self, carrier: str) -> None:
        if carrier not in self.fields:
            raise _runtime("LEDGER_CARRIER_UNKNOWN", f"{carrier} is not a storable carrier of world {self.world.world.name}")
        if self.world.carrier(carrier).kind == "family":
            raise _runtime("LEDGER_CARRIER_ABSTRACT", f"{carrier} is a family; write through one of its members")

    def check_field(self, carrier: str, field_qid: str) -> I.Use | I.Link:
        table = self.fields[carrier]
        c = self.world.carrier(carrier)
        candidates = [field_qid]
        if c.kind == "member" and c.family is not None:
            # a member-qualified name may denote a family field
            local = field_qid.rsplit(".", 1)[-1]
            candidates.append(f"{c.family}.{local}")
        for cand in candidates:
            if cand in table:
                return table[cand]
        raise _runtime("LEDGER_FIELD_UNKNOWN", f"{field_qid} is not a use or link of {carrier}")

    def canonical_field(self, carrier: str, field_qid: str) -> str:
        table = self.fields[carrier]
        c = self.world.carrier(carrier)
        if field_qid in table:
            return field_qid
        local = field_qid.rsplit(".", 1)[-1]
        return f"{c.family}.{local}"

    def check_value(self, field_qid: str, spec: I.Use | I.Link, value: Any) -> None:
        if value is None:
            if isinstance(spec, I.Use) and not spec.optional:
                raise _runtime("LEDGER_VALUE_TYPE", f"{field_qid} is required")
            if isinstance(spec, I.Link) and not spec.optional:
                raise _runtime("LEDGER_VALUE_TYPE", f"{field_qid} is required")
            return
        if isinstance(spec, I.Link):
            if isinstance(value, bool) or not isinstance(value, int):
                raise _runtime("LEDGER_VALUE_TYPE", f"{field_qid} takes an identity")
            return
        t = spec.type.scalar()
        ok = {
            "text": lambda v: isinstance(v, str),
            "instant": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "decimal": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "opaque": lambda v: isinstance(v, (bytes, bytearray)),
            "vector": lambda v: isinstance(v, (bytes, bytearray)),
        }[t.cls](value)
        if not ok:
            raise _runtime("LEDGER_VALUE_TYPE", f"{field_qid} is {t.describe()}; got {type(value).__name__}")
        if t.is_closed and value not in {m[1:] for m in t.closed}:
            raise _runtime("LEDGER_VALUE_TYPE", f"{value!r} is not a member of {t.describe()}")

    def check_scope(self, conn: sqlite3.Connection, scope: int | None) -> None:
        if scope is None:
            return
        root = self.world.world.scope
        assert root is not None
        rel = self.world.relation_of(root.root)
        found = conn.execute(f"SELECT 1 FROM {q(rel.table)} WHERE {q(rel.identity)} = ?", (scope,)).fetchone()
        if found is None:
            raise _runtime("LEDGER_SCOPE_UNKNOWN", f"scope {scope} is not an identity of {root.root}")


class Store:
    """One SQLite store shipped from a world IR."""

    def __init__(self, world: WorldIR, path: str = ":memory:") -> None:
        self.world = world
        self.path = path
        self.conn = sqlite3.connect(path, isolation_level=None)
        self.conn.execute("PRAGMA foreign_keys = ON")

    # ----------------------------------------------------------------- ship
    def ship(self, generation: int = 1, revision: int = 0) -> None:
        self.conn.executescript("BEGIN;\n" + lower_ddl(self.world) + "\nCOMMIT;")
        eng = self.world.storage.engine
        self.conn.execute(
            f"INSERT INTO {q(eng.generations)} (ordinal, ir_digest, storage_digest, shipped_at_revision) VALUES (?, ?, ?, ?)",
            (generation, I.digest(self.world.program), I.digest(self.world.storage), revision),
        )

    def close(self) -> None:
        self.conn.close()


class Engine:
    """Governed writes and reads over a shipped store."""

    def __init__(self, store: Store, clock: Callable[[], int] | None = None) -> None:
        self.store = store
        self.world = store.world
        self.conn = store.conn
        self.validator = LedgerValidator(self.world)
        self.clock = clock or (lambda: int(time.time()))
        self.listeners: list[Callable[[int, tuple[Delta, ...]], None]] = []
        self.revision = self._last_revision()
        self.plans: dict[str, Plan] = {}

    def _last_revision(self) -> int:
        eng = self.world.storage.engine
        row = self.conn.execute(f"SELECT COALESCE(MAX(revision), 0) FROM {q(eng.revisions)}").fetchone()
        return int(row[0])

    def plan(self, read_qid: str) -> Plan:
        if read_qid not in self.plans:
            read = self._read(read_qid)
            self.plans[read_qid] = lower_read(self.world, read)
        return self.plans[read_qid]

    def _read(self, read_qid: str) -> I.Read:
        for r in self.world.reads:
            if r.qid == read_qid:
                return r
        raise Refusal("READ_UNKNOWN", "runtime", "", 1, 1, f"{read_qid} is not a read of world {self.world.world.name}; reads are selected by qualified name")

    # ------------------------------------------------------------ transactions
    def transaction(self, writer: str, transaction_id: str, clock: int | None = None) -> "Transaction":
        return Transaction(self, writer, transaction_id, clock)

    def _commit(self, tx: "Transaction") -> int:
        eng = self.world.storage.engine
        revision = self.revision + 1
        self.conn.execute(f"INSERT INTO {q(eng.revisions)} (revision, writer, transaction_id) VALUES (?, ?, ?)", (revision, tx.writer, tx.transaction_id))
        for ordinal, d in enumerate(tx.deltas):
            self.conn.execute(
                f"INSERT INTO {q(eng.ledger)} (revision, ordinal, carrier, identity, operation, changes, scope_before, scope_after, writer, transaction_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    revision, ordinal, d.carrier, d.identity, d.operation,
                    json.dumps([{"field": c.field, "old": _jsonable(c.old), "new": _jsonable(c.new)} for c in d.changes], sort_keys=True),
                    None if d.scope_before is None else str(d.scope_before),
                    None if d.scope_after is None else str(d.scope_after),
                    d.writer, d.transaction,
                ),
            )
        self.conn.execute("COMMIT")
        self.revision = revision
        deltas = tuple(tx.deltas)
        for listener in self.listeners:
            listener(revision, deltas)
        return revision

    def ledger_rows(self) -> list[dict[str, Any]]:
        eng = self.world.storage.engine
        cur = self.conn.execute(f"SELECT revision, ordinal, carrier, identity, operation, changes, scope_before, scope_after, writer, transaction_id FROM {q(eng.ledger)} ORDER BY revision, ordinal")
        names = [d[0] for d in cur.description]
        return [dict(zip(names, row)) for row in cur.fetchall()]

    # ------------------------------------------------------------------ scope
    def scope_key_of(self, carrier: str, values: dict[str, Any]) -> int | None:
        """Follow the carrier's scope path through the store to the root identity."""
        path = self.world.scope_path(carrier)
        if not path or self.world.world.deployment_scoped:
            return GLOBAL_SCOPE
        current = values
        current_carrier = carrier
        for index, link_qid in enumerate(path):
            link = self.world.program.link(link_qid)
            key = self.validator.canonical_field(current_carrier, link_qid) if current_carrier in self.validator.fields else link_qid
            value = current.get(key)
            if value is None:
                return GLOBAL_SCOPE if link.optional else None
            if index == len(path) - 1:
                return int(value)
            current_carrier = link.target
            current = self.row_values(current_carrier, int(value)) or {}
        return GLOBAL_SCOPE

    # ------------------------------------------------------------------- rows
    def row_values(self, carrier: str, identity: int) -> dict[str, Any] | None:
        c = self.world.relation_carrier(carrier)
        rel = self.world.storage.relation(c.qid)
        uses, links = expected_relation_keys(self.world.program, c)
        keys = list(uses) + list(links)
        cols = [rel.columns[k] for k in uses] + [rel.links[k] for k in links]
        sql = f"SELECT {', '.join(q(col) for col in cols)}{', ' + q(rel.kind) if rel.kind else ''} FROM {q(rel.table)} WHERE {q(rel.identity)} = ?"
        row = self.conn.execute(sql, (identity,)).fetchone()
        if row is None:
            return None
        values = dict(zip(keys, row))
        if rel.kind:
            values["$kind"] = row[-1]
        return values

    # --------------------------------------------------------------- execute
    def execute(self, read_qid: str, params: dict[str, Any] | None = None, scope: int | None = None, capabilities: Iterable[str] = (), clock: int | None = None) -> Result:
        plan = self.plan(read_qid)
        read = self._read(read_qid)
        return self.execute_plan(plan, read, params or {}, scope, set(capabilities), clock)

    def execute_plan(self, plan: Plan, read: I.Read, params: dict[str, Any], scope: int | None, capabilities: set[str], clock: int | None) -> Result:
        bound = self.bind_params(plan, read, params, scope, capabilities, clock)
        cur = self.conn.execute(plan.sql, bound)
        names = [d[0] for d in cur.description]
        raw = cur.fetchall()
        rows: list[dict[str, Any]] = []
        keys: list[tuple[Any, ...]] = []
        for r in raw:
            record = dict(zip(names, r))
            keys.append(tuple(record[k] for k in plan.key_columns))
            rows.append({c: record[c] for c in plan.columns if c in record})
        for child in plan.children:
            self._attach_children(child, rows, keys, bound)
        total = None
        if plan.total_sql is not None:
            total = int(self.conn.execute(plan.total_sql, bound).fetchone()[0])
        return Result(rows, keys, total)

    def bind_params(self, plan: Plan, read: I.Read, params: dict[str, Any], scope: int | None, capabilities: set[str], clock: int | None) -> dict[str, Any]:
        givens = {g.name: g for g in read.givens}
        for name in params:
            if name not in givens:
                raise _runtime("PARAM_UNKNOWN", f"{read.qid} declares no given {name}")
        bound: dict[str, Any] = {}
        for name in plan.params:
            g = givens[name]
            value = params.get(name)
            if value is None and g.default is not None:
                value = g.default.value
            if value is None and not g.type.optional:
                raise _runtime("PARAM_REQUIRED", f"{read.qid} needs given {name}")
            if value is not None:
                self._check_param(g, value)
                if g.type.list_of:
                    value = json.dumps(list(value))
            bound[name] = value
        if plan.scoped:
            if scope is None:
                raise _runtime("SCOPE_REQUIRED", f"{read.qid} is scoped; a scope identity is required")
            self.validator.check_scope(self.conn, scope)
            bound[SCOPE_PARAM] = scope
        if read.unscoped is not None and read.unscoped not in capabilities:
            raise _runtime("CAPABILITY_REQUIRED", f"{read.qid} is unscoped behind capability {read.unscoped}")
        if plan.uses_clock:
            bound[CLOCK_PARAM] = clock if clock is not None else self.clock()
        return bound

    @staticmethod
    def _check_param(g: I.Given, value: Any) -> None:
        t = g.type.scalar()
        items = list(value) if g.type.list_of else [value]
        if g.type.list_of and not isinstance(value, (list, tuple)):
            raise _runtime("PARAM_TYPE", f"{g.name} takes a list")
        for item in items:
            if t.carrier is not None or t.cls in ("integer", "instant"):
                if isinstance(item, bool) or not isinstance(item, int):
                    raise _runtime("PARAM_TYPE", f"{g.name} takes an integer identity or instant")
            elif t.cls == "text":
                if not isinstance(item, str):
                    raise _runtime("PARAM_TYPE", f"{g.name} takes text")
                if t.is_closed and item not in {m[1:] for m in t.closed}:
                    raise _runtime("PARAM_TYPE", f"{item!r} is not a member of {t.describe()}")
            elif t.cls == "decimal":
                if isinstance(item, bool) or not isinstance(item, (int, float)):
                    raise _runtime("PARAM_TYPE", f"{g.name} takes a number")
            elif t.cls == "boolean":
                if not isinstance(item, bool):
                    raise _runtime("PARAM_TYPE", f"{g.name} takes a boolean")

    def _attach_children(self, child: ChildPlan, rows: list[dict[str, Any]], keys: list[tuple[Any, ...]], bound: dict[str, Any]) -> None:
        parents = [k[0] for k in keys]
        for r in rows:
            r[child.column] = []
        by_parent = {k[0]: r for k, r in zip(keys, rows)}
        cbound = {name: bound.get(name) for name in child.params}
        cbound[PARENTS_PARAM] = json.dumps(parents)
        cbound[SCOPE_PARAM] = bound.get(SCOPE_PARAM)
        cur = self.conn.execute(child.sql, cbound)
        names = [d[0] for d in cur.description]
        child_rows: list[dict[str, Any]] = []
        child_keys: list[tuple[Any, ...]] = []
        for r in cur.fetchall():
            record = dict(zip(names, r))
            parent = record[child.parent_column]
            item = {c: record[c] for c in child.columns if c in record}
            child_rows.append(item)
            child_keys.append(tuple(record[k] for k in child.key_columns))
            by_parent[parent][child.column].append(item)
        for grandchild in child.children:
            self._attach_children(grandchild, child_rows, child_keys, bound)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return {"$bytes": value.hex()}
    return value


class Transaction:
    """Collects typed deltas; commits the ledger and routes on exit."""

    def __init__(self, engine: Engine, writer: str, transaction_id: str, clock: int | None) -> None:
        self.engine = engine
        self.world = engine.world
        self.conn = engine.conn
        self.writer = writer
        self.transaction_id = transaction_id
        self.clock = clock
        self.deltas: list[Delta] = []
        self.revision: int | None = None
        self.rolled_back = False

    def __enter__(self) -> "Transaction":
        v = self.engine.validator
        v.check_writer(self.writer)
        v.check_transaction(self.transaction_id)
        if self.clock is None:
            self.clock = self.engine.clock()
        self.conn.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            if not self.rolled_back and self.conn.in_transaction:
                self.conn.execute("ROLLBACK")
            self.rolled_back = True
            return False
        self.revision = self.engine._commit(self)
        return False

    def rollback(self) -> None:
        self.conn.execute("ROLLBACK")
        self.rolled_back = True

    # --------------------------------------------------------------- helpers
    def _prepare(self, carrier: str, values: dict[str, Any]) -> dict[str, Any]:
        v = self.engine.validator
        v.check_carrier(carrier)
        out: dict[str, Any] = {}
        for field_qid, value in values.items():
            spec = v.check_field(carrier, field_qid)
            if isinstance(spec, I.Use) and spec.engine_owned:
                raise _runtime("VERB_INPUT_ENGINE_OWNED", f"{field_qid} is stamped by the engine")
            v.check_value(field_qid, spec, value)
            out[v.canonical_field(carrier, field_qid)] = value
        return out

    def _columns(self, carrier: str) -> tuple[I.Carrier, dict[str, I.Use | I.Link], dict[str, str]]:
        c = self.world.relation_carrier(carrier)
        rel = self.world.storage.relation(c.qid)
        uses, links = expected_relation_keys(self.world.program, c)
        specs: dict[str, I.Use | I.Link] = {}
        specs.update(uses)
        specs.update(links)
        cols = {k: rel.columns[k] for k in uses}
        cols.update({k: rel.links[k] for k in links})
        return c, specs, cols

    def mint(self, carrier: str, values: dict[str, Any]) -> int:
        given = self._prepare(carrier, values)
        c, specs, cols = self._columns(carrier)
        member = self.world.carrier(carrier)
        rel = self.world.storage.relation(c.qid)
        own_keys = set(self.engine.validator.fields[carrier].keys())
        if member.kind == "member":
            own_keys = {k for k in own_keys if k.rsplit(".", 1)[0] in (c.qid, member.qid)}
        row: dict[str, Any] = {}
        for key, spec in specs.items():
            if key not in own_keys:
                continue
            if key in given:
                row[key] = given[key]
                continue
            if isinstance(spec, I.Use):
                if spec.stamp == "on_mint" or spec.default == "ship_clock":
                    row[key] = self.clock
                elif isinstance(spec.default, I.Literal):
                    row[key] = spec.default.value
                elif spec.optional:
                    row[key] = None
                else:
                    raise _runtime("VERB_INPUT_REQUIRED", f"mint {carrier} requires {key}")
            else:
                if isinstance(spec.default, I.Literal):
                    row[key] = spec.default.value
                elif spec.optional:
                    row[key] = None
                else:
                    raise _runtime("VERB_INPUT_REQUIRED", f"mint {carrier} requires link {key}")
        scope_after = self.engine.scope_key_of(carrier, row)
        self.engine.validator.check_scope(self.conn, scope_after)
        names = [cols[k] for k in row]
        params = list(row.values())
        if rel.kind is not None:
            names.append(rel.kind)
            params.append(member.name)
        placeholders = ", ".join("?" for _ in params)
        try:
            cur = self.conn.execute(f"INSERT INTO {q(rel.table)} ({', '.join(q(n) for n in names)}) VALUES ({placeholders})", params)
        except sqlite3.IntegrityError as exc:
            self.conn.execute("ROLLBACK")
            self.rolled_back = True
            raise _runtime("KEY_DUPLICATED" if "UNIQUE" in str(exc) else "CONSTRAINT_VIOLATED", str(exc)) from None
        identity = int(cur.lastrowid)
        self._check_invariants(carrier, identity)
        changes = tuple(FieldChange(k, None, v) for k, v in row.items())
        self.deltas.append(Delta(carrier, identity, "insert", changes, None, scope_after, self.writer, self.transaction_id))
        return identity

    def change(self, carrier: str, identity: int, values: dict[str, Any]) -> None:
        given = self._prepare(carrier, values)
        c, specs, cols = self._columns(carrier)
        rel = self.world.storage.relation(c.qid)
        before = self.engine.row_values(carrier, identity)
        if before is None:
            raise _runtime("IDENTITY_UNKNOWN", f"{carrier} has no row {identity}")
        member = self.world.carrier(carrier)
        if member.kind == "member" and before.get("$kind") != member.name:
            raise _runtime("IDENTITY_UNKNOWN", f"row {identity} is not a {member.name}")
        after = dict(before)
        after.update(given)
        for key, spec in specs.items():
            if isinstance(spec, I.Use) and spec.stamp == "on_change":
                after[key] = self.clock
        changed = {k: v for k, v in after.items() if k != "$kind" and before.get(k) != v}
        scope_before = self.engine.scope_key_of(carrier, before)
        scope_after = self.engine.scope_key_of(carrier, after)
        self.engine.validator.check_scope(self.conn, scope_after)
        if changed:
            sets = ", ".join(f"{q(cols[k])} = ?" for k in changed)
            try:
                self.conn.execute(f"UPDATE {q(rel.table)} SET {sets} WHERE {q(rel.identity)} = ?", list(changed.values()) + [identity])
            except sqlite3.IntegrityError as exc:
                self.conn.execute("ROLLBACK")
                self.rolled_back = True
                raise _runtime("KEY_DUPLICATED" if "UNIQUE" in str(exc) else "CONSTRAINT_VIOLATED", str(exc)) from None
            self._check_invariants(carrier, identity)
        changes = tuple(FieldChange(k, before.get(k), v) for k, v in changed.items())
        self.deltas.append(Delta(carrier, identity, "update", changes, scope_before, scope_after, self.writer, self.transaction_id))

    def delete(self, carrier: str, identity: int) -> None:
        self.engine.validator.check_carrier(carrier)
        c, specs, cols = self._columns(carrier)
        rel = self.world.storage.relation(c.qid)
        before = self.engine.row_values(carrier, identity)
        if before is None:
            raise _runtime("IDENTITY_UNKNOWN", f"{carrier} has no row {identity}")
        scope_before = self.engine.scope_key_of(carrier, before)
        try:
            self.conn.execute(f"DELETE FROM {q(rel.table)} WHERE {q(rel.identity)} = ?", (identity,))
        except sqlite3.IntegrityError as exc:
            self.conn.execute("ROLLBACK")
            self.rolled_back = True
            raise _runtime("LINK_RESTRICTED", str(exc)) from None
        changes = tuple(FieldChange(k, v, None) for k, v in before.items() if k != "$kind")
        self.deltas.append(Delta(carrier, identity, "delete", changes, scope_before, None, self.writer, self.transaction_id))

    def _check_invariants(self, carrier: str, identity: int) -> None:
        c = self.world.carrier(carrier)
        invariants = list(c.invariants)
        if c.kind == "member" and c.family:
            invariants = list(self.world.carrier(c.family).invariants) + invariants
        if not invariants:
            return
        from .lower_sqlite import _Frame, _Lowerer

        rel = self.world.relation_of(carrier)
        for inv in invariants:
            frame = _Frame(self.world, carrier, "s0", [], {}, [0], set(), False)
            low = _Lowerer(self.world, frame, set())
            pred = low.visit(inv)
            joins = "".join(" " + j for j in frame.joins)
            sql = f"SELECT {pred} FROM {q(rel.table)} AS s0{joins} WHERE s0.{q(rel.identity)} = ?"
            ok = self.conn.execute(sql, (identity,)).fetchone()
            if not ok or not ok[0]:
                self.conn.execute("ROLLBACK")
                self.rolled_back = True
                raise _runtime("INVARIANT_VIOLATED", f"{carrier} row {identity} violates an invariant")
