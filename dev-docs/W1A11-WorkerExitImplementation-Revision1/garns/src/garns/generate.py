"""Deterministic artifact generation from the world IR.

Products per world: schema DDL, canonical IR, one SQL file per read, and for
questions only: footprint, binding, and routing descriptors. Surfaces embed
the same SQL. A manifest lists sha256 digests. Nothing here depends on time,
environment, or dictionary order.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from . import ir as I
from .footprint import derive_footprint
from .lower_sqlite import Plan, lower_ddl, lower_read
from .storage import WorldIR
from .surfaces import python_surface, rust_main, rust_surface

SCHEMA = "garns-v9-5/generated-manifest/1"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def binding_descriptor(world: WorldIR, read: I.Read, plan: Plan) -> dict:
    w = world.world
    return {
        "question": read.qid,
        "subject": read.subject,
        "shape": read.shape,
        "live_bound": read.live_bound,
        "parameters": [{"name": g.name, "type": g.type.describe(), "optional": g.type.optional} for g in read.givens],
        "scoped": plan.scoped,
        "capability": read.unscoped,
        "writers": w.writers,
        "writer_source": w.writer_source,
        "retention": w.quarantine_retention,
        "composes": list(read.composes),
    }


def routing_descriptor(world: WorldIR, read: I.Read) -> dict:
    fp = derive_footprint(world, read)
    keys = []
    for atom in fp.atoms:
        scoped = bool(world.scope_path(atom.carrier)) and not world.world.deployment_scoped
        keys.append({"partition": "scope" if scoped else "global", "carrier": atom.carrier, "field": atom.field})
    return {"question": read.qid, "routing_keys": keys}


def generate(world: WorldIR, out_dir: Path) -> dict[str, str]:
    """Write every artifact of ``world`` under ``out_dir``; returns path -> sha256."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    for sub in ("queries", "questions", "python", "rust"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}

    def write(rel: str, text: str) -> None:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        files[rel] = _sha(text)

    write("schema.sql", lower_ddl(world))
    write("ir.json", I.canonical_json({"program": world.program, "world": world.world, "storage": world.storage, "scope_paths": world.scope_paths}))
    idents: list[tuple[str, str]] = []
    for read in sorted(world.reads, key=lambda r: r.qid):
        plan = lower_read(world, read)
        folder = "questions" if read.is_question else "queries"
        write(f"{folder}/{read.qid}.sql", plan.sql + "\n" + "".join(f"-- child {c.column}\n{c.sql}\n" for c in plan.children) + (f"-- total\n{plan.total_sql}\n" if plan.total_sql else ""))
        if read.is_question:
            fp = derive_footprint(world, read)
            write(f"questions/{read.qid}.footprint.json", json.dumps(fp.as_dict(), indent=1, sort_keys=True) + "\n")
            write(f"questions/{read.qid}.binding.json", json.dumps(binding_descriptor(world, read, plan), indent=1, sort_keys=True) + "\n")
            write(f"questions/{read.qid}.routing.json", json.dumps(routing_descriptor(world, read), indent=1, sort_keys=True) + "\n")
        ident = read.qid.replace(".", "__")
        idents.append((read.qid, ident))
        write(f"python/{ident}.py", python_surface(plan))
        write(f"rust/{ident}.rs", rust_surface(plan, ident))
    write("rust/main.rs", rust_main(idents))
    write("rust/sqlite.rs", (Path(__file__).resolve().parents[1] / "garns_rust" / "sqlite.rs").read_text(encoding="utf-8"))
    manifest = {
        "schema": SCHEMA,
        "world": world.world.name,
        "ir_digest": I.digest(world.program),
        "storage_digest": I.digest(world.storage),
        "files": dict(sorted(files.items())),
    }
    text = json.dumps(manifest, indent=1, sort_keys=True) + "\n"
    (out_dir / "manifest.json").write_text(text, encoding="utf-8")
    files["manifest.json"] = _sha(text)
    return files


def tree_digest(directory: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in directory.rglob("*") if x.is_file()):
        h.update(p.relative_to(directory).as_posix().encode())
        h.update(b"\0")
        h.update(hashlib.sha256(p.read_bytes()).digest())
        h.update(b"\n")
    return h.hexdigest()
