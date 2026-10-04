"""External capture: declared changelog triggers -> typed deltas.

An external_captured world's tables are written by an outside writer. The
generated schema carries one changelog table and three triggers per relation
(names and fields from the storage binding). Acquisition reads the unassigned
changelog rows, validates that the real changelog table covers every declared
field, builds typed deltas validated like any governed write, records the
revision and ledger rows, and routes live questions.
"""

from __future__ import annotations

import json
from typing import Any

from . import ir as I
from .engine import Delta, Engine, FieldChange, _jsonable, _runtime
from .lower_sqlite import q
from .refuse import Refusal
from .storage import expected_relation_keys


class CaptureAdapter:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.world = engine.world
        if self.world.world.writers != "external_captured":
            raise _runtime("CAPTURE_NOT_DECLARED", f"world {self.world.world.name} declares writers {self.world.world.writers}; capture needs external_captured")
        self.writer = self.world.world.writer_source or ""

    def check_coverage(self) -> dict[str, int]:
        """Every mapped changelog field must exist in the real store (load stage)."""
        denominators: dict[str, int] = {}
        for c in self.world.relations:
            cap = self.world.storage.relation(c.qid).capture
            assert cap is not None
            actual = {row[1] for row in self.engine.conn.execute(f"PRAGMA table_info({q(cap.table)})").fetchall()}
            needed = [cap.seq, cap.op, cap.revision, cap.identity] + list(cap.columns.values()) + list(cap.links.values())
            missing = [n for n in needed if n not in actual]
            if not actual:
                raise Refusal("WRITER_CAPTURE_INCOMPLETE", "load", "", 1, 1, f"changelog table {cap.table} for {c.qid} does not exist in the store")
            if missing:
                raise Refusal("WRITER_CAPTURE_INCOMPLETE", "load", "", 1, 1, f"changelog {cap.table} lacks declared fields {missing}")
            denominators[c.qid] = len(needed)
        return denominators

    def acquire(self, transaction_id: str) -> tuple[int, tuple[Delta, ...]]:
        """Turn unassigned changelog rows into one committed revision."""
        v = self.engine.validator
        v.check_writer(self.writer)
        v.check_transaction(transaction_id)
        self.check_coverage()
        conn = self.engine.conn
        entries: list[tuple[int, str, dict[str, Any]]] = []
        for c in self.world.relations:
            rel = self.world.storage.relation(c.qid)
            cap = rel.capture
            assert cap is not None
            uses, links = expected_relation_keys(self.world.program, c)
            keys = list(uses) + list(links)
            cols = [cap.columns[k] for k in uses] + [cap.links[k] for k in links]
            sql = f"SELECT {q(cap.seq)}, {q(cap.op)}, {q(cap.identity)}, {', '.join(q(x) for x in cols)} FROM {q(cap.table)} WHERE {q(cap.revision)} IS NULL ORDER BY {q(cap.seq)}"
            for row in conn.execute(sql).fetchall():
                values = dict(zip(keys, row[3:]))
                entries.append((int(row[0]), c.qid, {"op": row[1], "identity": int(row[2]), "values": values}))
        entries.sort(key=lambda e: e[0])
        if not entries:
            return self.engine.revision, ()
        deltas: list[Delta] = []
        pending_before: dict[tuple[str, int], dict[str, Any]] = {}
        for seq, carrier, entry in entries:
            op = entry["op"]
            identity = entry["identity"]
            values = entry["values"]
            for field_qid, value in values.items():
                spec = v.check_field(carrier, field_qid)
                v.check_value(field_qid, spec, self._coerce(spec, value))
            values = {k: self._coerce(v.check_field(carrier, k), val) for k, val in values.items()}
            if op == "before":
                pending_before[(carrier, identity)] = values
                continue
            if op == "insert":
                changes = tuple(FieldChange(k, None, val) for k, val in values.items())
                scope_after = self.engine.scope_key_of(carrier, values)
                deltas.append(Delta(carrier, identity, "insert", changes, None, scope_after, self.writer, transaction_id))
            elif op == "update":
                before = pending_before.pop((carrier, identity), None)
                if before is None:
                    raise _runtime("CAPTURE_SEQUENCE_INVALID", f"update of {carrier} {identity} without its before image")
                changes = tuple(FieldChange(k, before.get(k), val) for k, val in values.items() if before.get(k) != val)
                deltas.append(Delta(carrier, identity, "update", changes, self.engine.scope_key_of(carrier, before), self.engine.scope_key_of(carrier, values), self.writer, transaction_id))
            elif op == "delete":
                changes = tuple(FieldChange(k, val, None) for k, val in values.items())
                deltas.append(Delta(carrier, identity, "delete", changes, self.engine.scope_key_of(carrier, values), None, self.writer, transaction_id))
            else:
                raise _runtime("CAPTURE_OP_UNKNOWN", f"changelog op {op!r}")
        # commit as one revision
        eng = self.world.storage.engine
        revision = self.engine.revision + 1
        conn.execute("BEGIN")
        conn.execute(f"INSERT INTO {q(eng.revisions)} (revision, writer, transaction_id) VALUES (?, ?, ?)", (revision, self.writer, transaction_id))
        for ordinal, d in enumerate(deltas):
            conn.execute(
                f"INSERT INTO {q(eng.ledger)} (revision, ordinal, carrier, identity, operation, changes, scope_before, scope_after, writer, transaction_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (revision, ordinal, d.carrier, d.identity, d.operation, json.dumps([{"field": ch.field, "old": _jsonable(ch.old), "new": _jsonable(ch.new)} for ch in d.changes], sort_keys=True),
                 None if d.scope_before is None else str(d.scope_before), None if d.scope_after is None else str(d.scope_after), d.writer, d.transaction),
            )
        for c in self.world.relations:
            cap = self.world.storage.relation(c.qid).capture
            assert cap is not None
            conn.execute(f"UPDATE {q(cap.table)} SET {q(cap.revision)} = ? WHERE {q(cap.revision)} IS NULL", (revision,))
        conn.execute("COMMIT")
        self.engine.revision = revision
        out = tuple(deltas)
        for listener in self.engine.listeners:
            listener(revision, out)
        return revision, out

    @staticmethod
    def _coerce(spec: I.Use | I.Link, value: Any) -> Any:
        if value is None or isinstance(spec, I.Link):
            return value
        cls = spec.type.scalar().cls
        if cls == "boolean":
            return bool(value)
        if cls in ("opaque", "vector") and isinstance(value, (bytes, bytearray)):
            return bytes(value)
        return value
