#!/usr/bin/env python3
"""Emit an explicit storage binding for a world (authoring aid).

The compiler never calls this. It exists so that a corpus author can start
from a complete binding and then rename anything. Physical names are derived
from qualified identities with a visible prefix scheme so that they cannot be
mistaken for conventions the compiler might rely on.

Usage: storage_template.py <world-name> <source-dir> [--out binding.json] [--prefix P] [--fresh SEED]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from garns.parse import garns_files, parse_paths  # noqa: E402
from garns.resolve import resolve_files  # noqa: E402
from garns.storage import binding_document  # noqa: E402


def scheme(prefix: str, fresh: str | None):
    counter = {"n": 0}

    def names(kind: str, key: str) -> str:
        if fresh is not None:
            counter["n"] += 1
            h = hashlib.sha256(f"{fresh}|{kind}|{key}".encode()).hexdigest()[:10]
            return f"{kind[:2]}_{h}"
        flat = key.replace(".", "_").replace("#", "_")
        return {
            "table": f"{prefix}tbl_{flat.lower()}",
            "identity": f"{prefix}rid_{flat.lower()}",
            "column": f"{prefix}f_{flat.split('_', 1)[-1].lower()}",
            "link": f"{prefix}ref_{flat.split('_', 1)[-1].lower()}",
            "kind": f"{prefix}member_of_{flat.lower()}",
            "engine": f"{prefix}garns_{flat}",
            "capture_table": f"{prefix}log_{flat.lower()}",
            "capture_field": f"{prefix}lg_{flat.split('_', 1)[-1].lower()}",
        }[kind]

    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("world")
    ap.add_argument("source")
    ap.add_argument("--out")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--fresh")
    args = ap.parse_args()
    program = resolve_files(parse_paths(garns_files(Path(args.source))))
    doc = binding_document(program, args.world, scheme(args.prefix, args.fresh))
    text = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
