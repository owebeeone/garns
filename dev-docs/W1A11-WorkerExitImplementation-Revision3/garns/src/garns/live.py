"""Live questions: scope-partitioned zero-scan routing, refresh, deltas, fold.

Every measurement here is taken from real operations: index probes are counted
where they happen, and listener scans are counted by an instrumented registry
whose iteration is the only way to visit every instance. The routing path never
iterates the registry, so the scan count stays at zero by construction, and a
test can prove the counter is live by iterating deliberately.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Iterable, Iterator

from . import ir as I
from .engine import Delta, Engine
from .footprint import STRUCTURE, Footprint, derive_footprint
from .refuse import Refusal

GLOBAL = "global"


def partition_of(scope: int | None) -> str:
    return GLOBAL if scope is None else f"scope:{scope}"


@dataclass(frozen=True)
class Change:
    op: str  # upsert | delete
    key: tuple[Any, ...]
    row: dict[str, Any] | None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"op": self.op, "key": list(self.key)}
        if self.row is not None:
            out["row"] = self.row
        return out


@dataclass(frozen=True)
class Batch:
    instance: str
    base_seq: int
    seq: int
    revision: int
    changes: tuple[Change, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"instance": self.instance, "base_seq": self.base_seq, "seq": self.seq, "revision": self.revision, "changes": [c.as_dict() for c in self.changes]}


@dataclass
class Stats:
    probes: int = 0  # index dictionary probes
    candidates: int = 0  # instance ids returned by probes
    refreshes: int = 0  # instance refreshes executed
    listener_scans: int = 0  # instances visited by iterating the registry
    batches: int = 0

    def as_dict(self) -> dict[str, int]:
        return {"probes": self.probes, "candidates": self.candidates, "refreshes": self.refreshes, "listener_scans": self.listener_scans, "batches": self.batches}


class Registry:
    """Instances by id. Iterating it is a listener scan and is measured."""

    def __init__(self, stats: Stats) -> None:
        self._items: dict[str, "Instance"] = {}
        self._stats = stats

    def add(self, inst: "Instance") -> None:
        self._items[inst.id] = inst

    def get(self, instance_id: str) -> "Instance":
        return self._items[instance_id]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator["Instance"]:
        for inst in list(self._items.values()):
            self._stats.listener_scans += 1
            yield inst

    def ids(self) -> list[str]:
        return list(self._items)


def canonical_rows(rows: list[dict[str, Any]]) -> str:
    return json.dumps(rows, sort_keys=True, separators=(",", ":"), default=_default)


def _default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return {"$bytes": value.hex()}
    raise TypeError(type(value))


class Instance:
    def __init__(self, live: "LiveEngine", instance_id: str, read: I.Read, footprint: Footprint, params: dict[str, Any], scope: int | None, capabilities: set[str]) -> None:
        self.live = live
        self.id = instance_id
        self.read = read
        self.footprint = footprint
        self.params = params
        self.scope = scope
        self.capabilities = capabilities
        self.seq = 0
        self.state: dict[tuple[Any, ...], dict[str, Any]] = {}
        self.order: list[tuple[Any, ...]] = []
        self.log: list[Batch] = []
        self.revision = 0

    def rows(self) -> list[dict[str, Any]]:
        return [self.state[k] for k in self.order]

    def _fetch(self) -> tuple[dict[tuple[Any, ...], dict[str, Any]], list[tuple[Any, ...]]]:
        engine = self.live.engine
        result = engine.execute(self.read.qid, self.params, self.scope, self.capabilities)
        if self.read.live_bound is not None and len(result.rows) > self.read.live_bound:
            raise Refusal("LIVE_BOUND_EXCEEDED", "runtime", "", 1, 1, f"{self.read.qid} holds {len(result.rows)} rows; live bounded {self.read.live_bound}")
        state: dict[tuple[Any, ...], dict[str, Any]] = {}
        order: list[tuple[Any, ...]] = []
        for key, row in zip(result.keys, result.rows):
            state[key] = row
            order.append(key)
        return state, order

    def initialize(self, revision: int) -> list[dict[str, Any]]:
        self.state, self.order = self._fetch()
        self.revision = revision
        return self.rows()

    def refresh(self, revision: int) -> Batch | None:
        self.live.stats.refreshes += 1
        fresh, order = self._fetch()
        changes: list[Change] = []
        for key in self.order:
            if key not in fresh:
                changes.append(Change("delete", key, None))
        for key in order:
            if key not in self.state or canonical_rows([self.state[key]]) != canonical_rows([fresh[key]]):
                changes.append(Change("upsert", key, fresh[key]))
        self.state, self.order = fresh, order
        self.revision = revision
        if not changes:
            return None
        batch = Batch(self.id, self.seq, self.seq + 1, revision, tuple(changes))
        self.seq += 1
        self.log.append(batch)
        self.live.stats.batches += 1
        return batch


class LiveEngine:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.world = engine.world
        self.stats = Stats()
        self.registry = Registry(self.stats)
        self.index: dict[tuple[str, str, str], set[str]] = {}
        self.footprints: dict[str, Footprint] = {}
        self.last_routing: dict[str, bool] = {}
        self.last_batches: dict[str, Batch | None] = {}
        self._counter = 0
        engine.listeners.append(self.on_commit)

    # -------------------------------------------------------------- subscribe
    def footprint(self, read_qid: str) -> Footprint:
        if read_qid not in self.footprints:
            read = self.engine._read(read_qid)
            self.footprints[read_qid] = derive_footprint(self.world, read)
        return self.footprints[read_qid]

    def routing_keys(self, footprint: Footprint, scope: int | None) -> list[tuple[str, str, str]]:
        keys: list[tuple[str, str, str]] = []
        for atom in footprint.atoms:
            scoped = bool(self.world.scope_path(atom.carrier)) and not self.world.world.deployment_scoped
            partition = partition_of(scope) if scoped else GLOBAL
            keys.append((partition, atom.carrier, atom.field))
        return keys

    def subscribe(self, read_qid: str, params: dict[str, Any] | None = None, scope: int | None = None, capabilities: Iterable[str] = ()) -> Instance:
        read = self.engine._read(read_qid)
        if not read.is_question:
            raise Refusal("QUERY_NOT_LIVE", "runtime", "", 1, 1, f"{read_qid} is a static query and cannot be subscribed")
        footprint = self.footprint(read_qid)
        # a scoped question subscribed without scope, or unscoped without capability, refuses in execute
        self._counter += 1
        inst = Instance(self, f"inst{self._counter}", read, footprint, dict(params or {}), scope, set(capabilities))
        inst.initialize(self.engine.revision)
        # registration happens only after the initial fetch succeeded (no partial registrations)
        for key in self.routing_keys(footprint, scope if read.unscoped is None else None):
            self.index.setdefault(key, set()).add(inst.id)
        if read.unscoped is not None:
            # unscoped instances observe every partition of their atoms' carriers
            for atom in footprint.atoms:
                self.index.setdefault((GLOBAL, atom.carrier, atom.field), set()).add(inst.id)
                self.index.setdefault(("*", atom.carrier, atom.field), set()).add(inst.id)
        self.registry.add(inst)
        return inst

    # ---------------------------------------------------------------- routing
    def _probe(self, key: tuple[str, str, str], out: set[str]) -> None:
        self.stats.probes += 1
        found = self.index.get(key)
        if found:
            self.stats.candidates += len(found)
            out.update(found)

    def match(self, deltas: Iterable[Delta]) -> set[str]:
        affected: set[str] = set()
        for d in deltas:
            scoped = bool(self.world.scope_path(d.carrier)) and not self.world.world.deployment_scoped
            partitions = {GLOBAL} if not scoped else {partition_of(s) for s in (d.scope_before, d.scope_after)}
            partitions.add("*")
            fields = list(d.fields)
            if d.operation in ("insert", "delete"):
                fields.append(STRUCTURE)
            family = self.world.carrier(d.carrier).family
            carriers = [d.carrier] + ([family] if family else [])
            for partition in partitions:
                for carrier in carriers:
                    for f in fields:
                        self._probe((partition, carrier, f), affected)
                        if family and carrier == family and f != STRUCTURE:
                            self._probe((partition, carrier, f"{family}.{f.rsplit('.', 1)[-1]}"), affected)
        return affected

    def on_commit(self, revision: int, deltas: tuple[Delta, ...]) -> dict[str, Batch | None]:
        affected = self.match(deltas)
        batches: dict[str, Batch | None] = {}
        routing: dict[str, bool] = {}
        for instance_id in sorted(affected):
            inst = self.registry.get(instance_id)
            routing[instance_id] = True
            batches[instance_id] = inst.refresh(revision)
        self.last_routing = routing
        self.last_batches = batches
        return batches


def fold(initial: list[dict[str, Any]], keys: list[tuple[Any, ...]], batches: Iterable[Batch]) -> list[dict[str, Any]]:
    """Apply batches to an initial keyed state; the result is the folded rows (unordered)."""
    state = {k: r for k, r in zip(keys, initial)}
    for b in batches:
        for c in b.changes:
            if c.op == "delete":
                state.pop(c.key, None)
            else:
                assert c.row is not None
                state[c.key] = c.row
    return [state[k] for k in sorted(state, key=lambda k: json.dumps(list(k), default=str))]
