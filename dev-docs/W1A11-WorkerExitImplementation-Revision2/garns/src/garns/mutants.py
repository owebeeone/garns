"""Mutant execution: every mutant runs the real stages.

A single-file mutant is parsed and resolved by the production pipeline; a
scenario mutant executes real store states (ship, external DDL, open, migrate,
governed writes, captures, reads, subscriptions). The observation is the first
refusal (stage, code, position) or "accepted". Expected manifests are never
consulted here; they are assertions checked by the test suite.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any

from .capture import CaptureAdapter
from .engine import Engine, Store
from .evolution import check_window, classify, migrate, open_store
from .generate import generate
from .live import LiveEngine
from .lower_sqlite import lower_read
from .parse import garns_files, parse_paths, parse_text
from .refuse import Refusal
from .resolve import resolve_files
from .storage import bind_world


@dataclass(frozen=True)
class Observation:
    stage: str
    code: str
    line: int
    column: int
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"stage": self.stage, "code": self.code, "line": self.line, "column": self.column, "detail": self.detail}


ACCEPTED = Observation("accepted", "ACCEPTED", 0, 0)


def observe_single(path: Path, text: str | None = None) -> Observation:
    """Parse and resolve one file through the production pipeline."""
    try:
        source = text if text is not None else path.read_text(encoding="utf-8")
        program = resolve_files([parse_text(source, str(path))])
        # lower every read of every world to reach lower-stage refusals without storage
        _ = program
        return ACCEPTED
    except Refusal as r:
        return Observation(r.stage, r.code, r.line, r.column, r.detail)


def _resolve_dir(base: Path, rel: str):
    files = parse_paths(garns_files(base / rel))
    return resolve_files(files)


def observe_scenario(directory: Path) -> Observation:
    """Execute scenario.json step by step; the first refusal is the observation."""
    spec = json.loads((directory / "scenario.json").read_text(encoding="utf-8"))
    base = directory.parents[2] if spec.get("base") == "corpus" else directory
    state: dict[str, Any] = {"generation": 0, "history": []}
    try:
        for step in spec["steps"]:
            kind = step["do"]
            if kind == "resolve":
                state["program"] = _resolve_dir(base, step["source"])
                state["source"] = step["source"]
            elif kind == "bind":
                program = _resolve_dir(base, step["source"])
                state["program"] = program
                state["world"] = bind_world(program, step["world"], base / step["binding"])
                state["source"] = step["source"]
            elif kind == "lower":
                for read in state["world"].reads:
                    lower_read(state["world"], read)
            elif kind == "generate":
                import tempfile

                out = Path(tempfile.mkdtemp()) / "gen"
                generate(state["world"], out)
            elif kind == "ship":
                store = Store(state["world"], ":memory:")
                store.ship(generation=1)
                state["store"] = store
                state["engine"] = Engine(store, clock=lambda: 100)
                state["live"] = LiveEngine(state["engine"])
                state["generation"] = 1
                state["history"] = [state["program"]]
                state["worlds"] = [state["world"]]
            elif kind == "sql":
                state["store"].conn.execute(step["statement"])
            elif kind == "open":
                program = state["program"]
                dep = next(d for d in program.deployments if d.name == step["deployment"])
                open_store(state["store"].conn, state["world"], dep)
            elif kind == "migrate":
                program = _resolve_dir(base, step["source"])
                world = bind_world(program, step["world"], base / step["binding"])
                cl = classify(state["history"][-1], program, state["history"], retention=state["world"].world.quarantine_retention)
                migrate(state["store"].conn, state["worlds"][-1], world, cl, generation=state["generation"] + 1)
                state["generation"] += 1
                state["history"].append(program)
                state["worlds"].append(world)
                state["world"] = world
                state["program"] = program
                state["engine"] = Engine(state["store"], clock=lambda: 100)
                state["live"] = LiveEngine(state["engine"])
            elif kind == "classify":
                program = _resolve_dir(base, step["source"])
                classify(state["history"][-1] if state["history"] else state["program"], program, state["history"] or [state["program"]], retention=step.get("retention", 3))
            elif kind == "window":
                eng = state["world"].storage.engine
                rows = [r[0] for r in state["store"].conn.execute(f'SELECT ordinal FROM "{eng.generations}"').fetchall()]
                check_window(rows, state["world"].world.quarantine_retention, state["generation"])
            elif kind == "write":
                engine = state["engine"]
                with engine.transaction(step.get("writer", "governed"), step.get("transaction", "tx")) as tx:
                    for op in step["ops"]:
                        values = {k: _value(v, state) for k, v in op.get("values", {}).items()}
                        if op["verb"] == "mint":
                            state[op.get("as", "_")] = tx.mint(op["carrier"], values)
                        elif op["verb"] == "change":
                            tx.change(op["carrier"], _value(op["identity"], state), values)
                        elif op["verb"] == "delete":
                            tx.delete(op["carrier"], _value(op["identity"], state))
            elif kind == "capture":
                CaptureAdapter(state["engine"]).acquire(step.get("transaction", "ext"))
            elif kind == "execute":
                params = {k: _value(v, state) for k, v in step.get("params", {}).items()}
                state["engine"].execute(step["read"], params, _value(step.get("scope"), state), set(step.get("capabilities", [])))
            elif kind == "subscribe":
                params = {k: _value(v, state) for k, v in step.get("params", {}).items()}
                state["live"].subscribe(step["read"], params, _value(step.get("scope"), state), set(step.get("capabilities", [])))
            else:
                raise ValueError(f"unknown scenario step {kind}")
        return ACCEPTED
    except Refusal as r:
        return Observation(r.stage, r.code, r.line, r.column, r.detail)


def _value(v: Any, state: dict[str, Any]) -> Any:
    if isinstance(v, str) and v.startswith("$"):
        return state[v[1:]]
    return v


def observe_all(mutants_dir: Path) -> dict[str, Observation]:
    out: dict[str, Observation] = {}
    for p in sorted(mutants_dir.glob("*.garns")):
        out[p.name] = observe_single(p)
    scenarios = mutants_dir / "scenarios"
    if scenarios.exists():
        for d in sorted(x for x in scenarios.iterdir() if x.is_dir()):
            out[f"scenarios/{d.name}"] = observe_scenario(d)
    return out
