#!/usr/bin/env python3
"""Regenerate ``generated/`` for every corpus world (delete and regenerate).

Each world is selected explicitly by name with its storage binding; the index
records the tree digest per world so a reviewer can compare after deleting
the directory and running this again. Run from the repository root.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from garns.generate import generate, tree_digest  # noqa: E402
from garns.parse import garns_files, parse_paths  # noqa: E402
from garns.resolve import resolve_files  # noqa: E402
from garns.storage import bind_world  # noqa: E402

WORLDS = [
    ("PRACTICE", "corpus/worlds/practice"),
    ("EVERBILITY", "corpus/worlds/everbility"),
    ("VAULTWARDEN", "corpus/worlds/vaultwarden"),
    ("APPFLOWY", "corpus/worlds/appflowy"),
    ("APPFLOWY_VEC", "corpus/worlds/appflowy"),
    ("REPORTING", "corpus/conformance/worlds/reporting"),
    ("SALES", "corpus/conformance/worlds/sales"),
    ("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse"),
]


def main() -> int:
    out_root = HERE / "generated"
    if out_root.exists():
        shutil.rmtree(out_root)
    index: dict[str, dict] = {}
    for world, rel in WORLDS:
        src = HERE / rel
        program = resolve_files(parse_paths(garns_files(src)))
        world_ir = bind_world(program, world, src / f"storage-{world}.json")
        files = generate(world_ir, out_root / world)
        index[world] = {"source": rel, "binding": f"{rel}/storage-{world}.json", "files": len(files), "tree_sha256": tree_digest(out_root / world)}
        print(f"generated {world}: {len(files)} files tree={index[world]['tree_sha256'][:12]}")
    (out_root / "INDEX.json").write_text(json.dumps({"schema": "garns-v9-5/generated-index/1", "worlds": index}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
