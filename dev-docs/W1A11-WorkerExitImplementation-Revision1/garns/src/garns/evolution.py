"""Evolution: classify one world generation against its predecessor and ship.

Continuity is by qualified identity. ``renamed_from`` carries an identity
across a rename or a module move; an undeclared move is a retirement plus a
mint and demands a retirement policy. ``move_home`` is a real event with its
own disposition. Restores are checked against tombstones within the retention
window. Migration executes against the real store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import sqlite3

from . import ir as I
from .lower_sqlite import q, sql_literal
from .refuse import Refusal
from .storage import WorldIR, expected_relation_keys
from .types import sql_storage_type


@dataclass(frozen=True)
class Event:
    kind: str
    subject: str
    decision: str | None = None
    detail: str = ""

    def as_dict(self) -> dict[str, object]:
        return {"kind": self.kind, "subject": self.subject, "decision": self.decision, "detail": self.detail}


@dataclass
class Classification:
    events: list[Event] = field(default_factory=list)
    demanded: list[str] = field(default_factory=list)

    @property
    def compat(self) -> str:
        kinds = {e.kind for e in self.events}
        if kinds & {"retire_intent", "tighten", "retype", "use_removed", "lifecycle", "retire_carrier", "move_home", "link_removed"}:
            return "breaking"
        if kinds & {"intent_renamed", "intent_relocated", "meaning_delta", "link_policy", "use_added", "add_intent", "add_carrier", "restore_intent", "carry_added", "link_added"}:
            return "deprecating" if kinds & {"intent_renamed", "intent_relocated", "meaning_delta", "link_policy"} else "additive"
        return "additive"

    def as_dict(self) -> dict[str, object]:
        return {"compat": self.compat, "events": [e.as_dict() for e in self.events], "demanded": list(self.demanded)}


def _ship(code: str, at: object, detail: str) -> Refusal:
    loc = getattr(at, "loc", at)
    return Refusal(code, "ship", getattr(loc, "file", ""), getattr(loc, "line", 1), getattr(loc, "column", 1), detail)


def classify(before: I.Program, after: I.Program, history: list[I.Program] | None = None, retention: int | None = None) -> Classification:
    """Classify ``after`` against ``before``; ``history`` lists earlier generations (oldest first, ending with ``before``)."""
    cl = Classification()
    b_intents = {i.qid: i for i in before.intents}
    a_intents = {i.qid: i for i in after.intents}
    a_tombs = {t.qid: t for t in after.tombstones}
    b_tombs = {t.qid: t for t in before.tombstones}
    continued: set[str] = set()
    key_intents = {u.intent for c in after.carriers for u in c.uses if u.key}

    for qid, it in sorted(a_intents.items()):
        if it.renamed_from is not None:
            prev = b_intents.get(it.renamed_from)
            if prev is None:
                raise _ship("RENAME_TARGET_UNKNOWN", it, f"{qid} is renamed_from {it.renamed_from}, which the previous generation does not declare")
            continued.add(prev.qid)
            kind = "intent_relocated" if prev.module != it.module else "intent_renamed"
            cl.events.append(Event(kind, qid, f"renamed_from {prev.qid}", f"{prev.qid} -> {qid}"))
            cl.demanded.append(f"{kind} {prev.qid} -> {qid}")
            if prev.type.base != it.type.base:
                _retype(cl, prev, it, key_intents)
            continue
        prev = b_intents.get(qid)
        if prev is not None:
            continued.add(qid)
            if prev.meaning != it.meaning:
                cl.events.append(Event("meaning_delta", qid, None, f"{prev.meaning!r} -> {it.meaning!r}"))
            if prev.type.base != it.type.base:
                _retype(cl, prev, it, key_intents)
            elif it.retype is not None and it.retype[0] != prev.type.base:
                raise _ship("RETYPE_INCONSISTENT", it, f"{qid} declares retype from {it.retype[0]} but the previous type is {prev.type.base}")
            continue
        if it.restore:
            _restore(cl, it, b_tombs, history or [before], retention)
            continue
        moved = [p for p in b_intents.values() if p.name == it.name and p.module != it.module and p.qid not in a_intents]
        if moved:
            old = moved[0]
            tomb = a_tombs.get(old.qid)
            if tomb is None:
                raise _ship("RETIREMENT_POLICY_REQUIRED", it, f"{old.qid} moved to {qid} without renamed_from; the move is a retirement plus a mint and {old.qid} needs a tombstone")
            cl.events.append(Event("retire_intent", old.qid, tomb.disposition, f"undeclared move: {old.qid} retired"))
            cl.events.append(Event("add_intent", qid, None, f"undeclared move: {qid} minted"))
            cl.demanded.append(f"retire {old.qid} data {tomb.disposition}")
            continued.add(old.qid)
            continue
        cl.events.append(Event("add_intent", qid, None, "new intent"))
    for qid, prev in sorted(b_intents.items()):
        if qid in continued or qid in a_intents:
            continue
        tomb = a_tombs.get(qid)
        if tomb is None:
            raise _ship("RETIREMENT_POLICY_REQUIRED", prev, f"{qid} disappears without a tombstone stating its data disposition")
        cl.events.append(Event("retire_intent", qid, tomb.disposition, f"retired: {tomb.meaning}"))
        cl.demanded.append(f"retire {qid} data {tomb.disposition}")
    # move_home statements
    for mh in after.move_homes:
        source_before = next((c for c in before.carriers if c.qid == mh.source), None)
        if source_before is None or source_before.use_named(mh.intent.rsplit(".", 1)[-1]) is None:
            raise _ship("MOVE_HOME_INCONSISTENT", mh, f"{mh.source} did not use {mh.intent} in the previous generation")
        target_after = after.carrier(mh.target)
        if target_after.use_named(mh.intent.rsplit(".", 1)[-1]) is None:
            raise _ship("MOVE_HOME_INCONSISTENT", mh, f"{mh.target} does not use {mh.intent} in this generation")
        cl.events.append(Event("move_home", f"{mh.intent}@{mh.source}->{mh.target}", mh.disposition, f"data {mh.disposition}"))
        cl.demanded.append(f"move_home {mh.intent} data {mh.disposition}")
    # carriers
    b_carriers = {c.qid: c for c in before.carriers}
    a_carriers = {c.qid: c for c in after.carriers}
    for qid, c in sorted(a_carriers.items()):
        prev = b_carriers.get(qid)
        if prev is None:
            cl.events.append(Event("add_carrier", qid, None, c.kind))
            continue
        if (prev.lifecycle, prev.archived_by) != (c.lifecycle, c.archived_by):
            if not c.breaking:
                raise _ship("ACCESSOR_BREAKING_UNACKNOWLEDGED", c, f"{qid} changes lifecycle {prev.lifecycle} -> {c.lifecycle}; the carrier must state breaking \"...\"")
            cl.events.append(Event("lifecycle", qid, c.breaking[0], f"{prev.lifecycle} -> {c.lifecycle}"))
        for t in c.carries:
            if t not in prev.carries:
                cl.events.append(Event("carry_added", qid, None, t))
        prev_uses = {u.intent: u for u in prev.uses}
        moved_intents = {e.subject for e in cl.events if e.kind in ("intent_renamed", "intent_relocated")}
        for u in c.uses:
            old_qid = next((e.decision.split()[-1] for e in cl.events if e.kind in ("intent_renamed", "intent_relocated") and e.subject == u.intent and e.decision), None)
            pu = prev_uses.get(u.intent) or (prev_uses.get(old_qid) if old_qid else None)
            if pu is None:
                if not u.optional and u.default is None and u.stamp is None and not _has_repair(after, c, u):
                    raise _ship("TIGHTEN_REPAIR_REQUIRED", u, f"{qid} adds required use {u.intent} without a repair for existing rows")
                cl.events.append(Event("use_added", f"{qid}.{u.intent}", None, "required" if not u.optional else "optional"))
                continue
            if pu.optional and not u.optional:
                if not _has_repair(after, c, u):
                    raise _ship("TIGHTEN_REPAIR_REQUIRED", u, f"{qid}.{u.intent} tightens optional -> required without a repair")
                cl.events.append(Event("tighten", f"{qid}.{u.intent}", str(_repair_of(after, c, u)), "optional -> required"))
        for intent_qid in prev_uses:
            if intent_qid in {u.intent for u in c.uses} or intent_qid in continued and intent_qid not in a_intents:
                continue
            if intent_qid not in a_intents:
                continue  # retired above
            if not any(u.intent == intent_qid for u in c.uses) and not any(mh.intent == intent_qid and mh.source == qid for mh in after.move_homes):
                cl.events.append(Event("use_removed", f"{qid}.{intent_qid}", None, "use dropped"))
        prev_links = {l.name: l for l in prev.links}
        for l in c.links:
            pl = prev_links.get(l.name)
            if pl is None:
                cl.events.append(Event("link_added", l.qid, None, l.target))
            elif pl.enforcement != l.enforcement:
                cl.events.append(Event("link_policy", l.qid, l.enforcement, f"{pl.enforcement} -> {l.enforcement}"))
        for name in prev_links:
            if name not in {l.name for l in c.links}:
                cl.events.append(Event("link_removed", f"{qid}.{name}", None, "link dropped"))
    for qid in sorted(b_carriers):
        if qid not in a_carriers:
            cl.events.append(Event("retire_carrier", qid, None, "carrier dropped"))
    return cl


def _retype(cl: Classification, prev: I.Intent, it: I.Intent, key_intents: set[str]) -> None:
    if it.retype is None:
        raise _ship("RETYPE_ADAPTER_REQUIRED", it, f"{it.qid} changes type {prev.type.base} -> {it.type.base} without retype adapters")
    if it.retype[0] != prev.type.base:
        raise _ship("RETYPE_INCONSISTENT", it, f"{it.qid} declares retype from {it.retype[0]}; previous type is {prev.type.base}")
    if it.qid in key_intents and prev.type.cls != it.type.cls:
        raise _ship("RETYPE_KEY_EQUALITY", it, f"{it.qid} is a key; {prev.type.base} -> {it.type.base} does not preserve equality")
    cl.events.append(Event("retype", it.qid, f"forward {it.retype[1]} backward {it.retype[2]}", f"{prev.type.base} -> {it.type.base}"))
    cl.demanded.append(f"retype {it.qid}")


def _restore(cl: Classification, it: I.Intent, b_tombs: dict[str, I.Tombstone], history: list[I.Program], retention: int | None) -> None:
    age = None
    tomb = None
    for distance, gen in enumerate(reversed(history), start=1):
        found = next((t for t in gen.tombstones if t.qid == it.qid), None)
        if found is not None:
            age, tomb = distance, found
            break
    if tomb is None:
        raise _ship("RESTORE_TARGET_UNKNOWN", it, f"{it.qid} restores an intent no earlier generation tombstoned")
    if tomb.disposition == "drop":
        raise _ship("RESTORE_DATA_UNAVAILABLE", it, f"{it.qid} was retired with data drop; nothing to restore")
    if retention is not None and age is not None and age > retention:
        raise _ship("RESTORE_OUTSIDE_RETENTION", it, f"{it.qid} was tombstoned {age} generations ago; retention is {retention}")
    cl.events.append(Event("restore_intent", it.qid, tomb.disposition, f"restored after {age} generation(s)"))


def _has_repair(program: I.Program, c: I.Carrier, u: I.Use) -> bool:
    return _repair_of(program, c, u) is not None


def _repair_of(program: I.Program, c: I.Carrier, u: I.Use) -> object:
    for intent, repair in c.tightens:
        if intent == u.intent:
            return repair
    for t in program.tightens:
        if t.path == (c.qid, u.intent):
            return t.repair
    if u.repair is not None:
        return u.repair
    return None


# ------------------------------------------------------------------ migration


def migrate(conn: sqlite3.Connection, before: WorldIR, after: WorldIR, classification: Classification, generation: int) -> list[str]:
    """Apply a classified generation to a real store; returns the statements executed."""
    executed: list[str] = []
    before_rel = {c.qid: c for c in before.relations}
    conn.execute("BEGIN")
    try:
        for c in after.relations:
            rel = after.storage.relation(c.qid)
            uses, links = expected_relation_keys(after.program, c)
            prev = before_rel.get(c.qid)
            if prev is None:
                from .lower_sqlite import lower_ddl

                ddl = [s for s in lower_ddl(after).split("\n\n") if s.startswith(f"CREATE TABLE {q(rel.table)} ")]
                for s in ddl:
                    conn.execute(s)
                    executed.append(s)
                continue
            prev_rel = before.storage.relation(c.qid)
            prev_uses, prev_links = expected_relation_keys(before.program, prev)
            actual = {row[1] for row in conn.execute(f"PRAGMA table_info({q(rel.table)})").fetchall()}
            # continuity: renamed/relocated intents keep their column under the new name
            renamed = {e.subject: e.decision.split()[-1] for e in classification.events if e.kind in ("intent_renamed", "intent_relocated") and e.decision}
            for key, u in uses.items():
                col = rel.columns[key]
                if col in actual:
                    continue
                old_intent = renamed.get(u.intent)
                if old_intent is not None:
                    old_key = next((k for k, pu in prev_uses.items() if pu.intent == old_intent), None)
                    if old_key is not None and prev_rel.columns[old_key] in actual:
                        stmt = f"ALTER TABLE {q(rel.table)} RENAME COLUMN {q(prev_rel.columns[old_key])} TO {q(col)}"
                        conn.execute(stmt)
                        executed.append(stmt)
                        actual.add(col)
                        actual.discard(prev_rel.columns[old_key])
                        continue
                repair = _repair_of(after.program, after.carrier(key.rsplit(".", 1)[0]), u)
                spec = f"{q(col)} {sql_storage_type(u.type)}"
                if isinstance(u.default, I.Literal):
                    spec += f" DEFAULT {sql_literal(u.default)}"
                stmt = f"ALTER TABLE {q(rel.table)} ADD COLUMN {spec}"
                conn.execute(stmt)
                executed.append(stmt)
                if not u.optional and u.default is None:
                    if repair is None:
                        raise Refusal("TIGHTEN_REPAIR_REQUIRED", "ship", "", 1, 1, f"{key} is required and has no repair for existing rows")
                    value = "NULL"
                    if repair == "ship_clock":
                        value = str(generation)
                    elif isinstance(repair, I.Literal):
                        value = sql_literal(repair)
                    elif repair == "quarantine":
                        value = None
                    if value is not None:
                        stmt = f"UPDATE {q(rel.table)} SET {q(col)} = {value} WHERE {q(col)} IS NULL"
                        conn.execute(stmt)
                        executed.append(stmt)
            for key, l in links.items():
                col = rel.links[key]
                if col in actual:
                    continue
                stmt = f"ALTER TABLE {q(rel.table)} ADD COLUMN {q(col)} INTEGER"
                conn.execute(stmt)
                executed.append(stmt)
            # retired uses: quarantine or drop
            for key in prev_uses:
                pcol = prev_rel.columns[key]
                still = key in uses and rel.columns[key] == pcol
                if still or pcol not in actual:
                    continue
                event = next((e for e in classification.events if e.kind in ("retire_intent", "move_home") and (e.subject == prev_uses[key].intent or e.subject.startswith(prev_uses[key].intent + "@"))), None)
                disposition = event.decision if event else None
                if disposition == "quarantine":
                    qtable = f"{rel.table}__quarantine_{generation}"
                    stmt = f"CREATE TABLE IF NOT EXISTS {q(qtable)} ({q(rel.identity)} INTEGER, field TEXT, value ANY)"
                    conn.execute(stmt)
                    executed.append(stmt)
                    stmt = f"INSERT INTO {q(qtable)} SELECT {q(rel.identity)}, '{key}', {q(pcol)} FROM {q(rel.table)}"
                    conn.execute(stmt)
                    executed.append(stmt)
                elif disposition is None:
                    # a rename keeps the data under the new column name
                    renamed = next((e for e in classification.events if e.kind in ("intent_renamed", "intent_relocated") and e.decision and e.decision.endswith(prev_uses[key].intent)), None)
                    if renamed is not None:
                        new_key = next((k for k, u in uses.items() if u.intent == renamed.subject), None)
                        if new_key is not None:
                            stmt = f"ALTER TABLE {q(rel.table)} RENAME COLUMN {q(pcol)} TO {q(rel.columns[new_key])}"
                            conn.execute(stmt)
                            executed.append(stmt)
                            continue
                    raise Refusal("MIGRATION_UNSUPPORTED", "ship", "", 1, 1, f"column {pcol} of {rel.table} disappears without a classified disposition")
                stmt = f"ALTER TABLE {q(rel.table)} DROP COLUMN {q(pcol)}"
                conn.execute(stmt)
                executed.append(stmt)
        eng = after.storage.engine
        conn.execute(
            f"INSERT INTO {q(eng.generations)} (ordinal, ir_digest, storage_digest, shipped_at_revision) VALUES (?, ?, ?, (SELECT COALESCE(MAX(revision), 0) FROM {q(eng.revisions)}))",
            (generation, I.digest(after.program), I.digest(after.storage)),
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return executed


def open_store(conn: sqlite3.Connection, world: WorldIR, deployment: I.Deployment) -> dict[str, object]:
    """Open an existing store under a deployment; refuses on drift, lag, or window."""
    eng = world.storage.engine
    try:
        rows = conn.execute(f"SELECT ordinal, ir_digest, storage_digest FROM {q(eng.generations)} ORDER BY ordinal").fetchall()
    except sqlite3.OperationalError as exc:
        raise Refusal("STORE_UNSHIPPED", "load", "", 1, 1, f"store has no generation table {eng.generations}: {exc}") from None
    if not rows:
        raise Refusal("STORE_UNSHIPPED", "load", "", 1, 1, "store records no generation")
    ordinal, ir_digest, storage_digest = rows[-1]
    current = (I.digest(world.program), I.digest(world.storage))
    if (ir_digest, storage_digest) != current:
        if deployment.ship == "explicit":
            raise Refusal("STORE_BEHIND", "load", "", 1, 1, f"store is at generation {ordinal}; the deployment ships explicitly and the source has moved on")
        raise Refusal("STORE_BEHIND", "load", "", 1, 1, f"store generation {ordinal} does not match the source; ship first")
    for c in world.relations:
        rel = world.storage.relation(c.qid)
        actual = {row[1] for row in conn.execute(f"PRAGMA table_info({q(rel.table)})").fetchall()}
        expected = {rel.identity} | set(rel.columns.values()) | set(rel.links.values()) | ({rel.kind} if rel.kind else set())
        if not expected <= actual:
            raise Refusal("STORE_DRIFT", "load", "", 1, 1, f"table {rel.table} lacks {sorted(expected - actual)}")
        if actual - expected:
            raise Refusal("STORE_DRIFT", "load", "", 1, 1, f"table {rel.table} has undeclared columns {sorted(actual - expected)}")
    return {"generation": int(ordinal), "ir_digest": ir_digest}


def check_window(generations: list[int], retention: int, current: int) -> None:
    if generations and current - min(generations) > retention:
        raise Refusal("GENERATION_OUTSIDE_WINDOW", "load", "", 1, 1, f"generation {min(generations)} lies outside the retention window of {retention} generations")
