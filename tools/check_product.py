#!/usr/bin/env python3
"""Check the promoted product baseline without evaluation-lane dependencies."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "BASELINE.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    required = (
        "src/garns",
        "grammar/garns.lark",
        "corpus",
        "tests",
        "tools",
        "docs/PRODUCT_LAYOUT.md",
        "evidence/v9-5-b2",
        "research/api-docs",
        "research/postgres-codecs",
        "research/capture",
    )
    missing = [rel for rel in required if not (ROOT / rel).exists()]
    if missing:
        failures.append("missing product paths: " + ", ".join(missing))

    for rel, expected in BASELINE["sha256"].items():
        path = ROOT / rel
        if not path.is_file():
            failures.append(f"missing pinned input: {rel}")
        elif digest(path) != expected:
            failures.append(f"pinned input changed: {rel}")

    caches = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    )
    if caches:
        failures.append("cache files present: " + ", ".join(caches[:10]))

    forbidden_roots = (
        "/Users/owebeeone/limbo/datascad/garns-v9-5",
        "/Volumes/projects/limbo/datascad/garns-v9-5",
    )
    shipped_text = [ROOT / "README.md"]
    shipped_text.extend((ROOT / "docs").rglob("*.md"))
    shipped_text.extend((ROOT / "generated").rglob("*.json"))
    shipped_text.extend((ROOT / "generated").rglob("*.sql"))
    leaks: list[str] = []
    for path in shipped_text:
        text = path.read_text(encoding="utf-8")
        if any(prefix in text for prefix in forbidden_roots):
            leaks.append(path.relative_to(ROOT).as_posix())
    if leaks:
        failures.append("absolute v9-5 lane paths remain: " + ", ".join(leaks))

    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "src").rglob("*"))
        if path.is_file() and path.suffix in {".py", ".rs"}
    )
    if "build/B2" in source_text or "build/B1" in source_text or "build/B3" in source_text:
        failures.append("candidate path appears in product source")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("PASS product paths")
    print("PASS pinned baseline inputs")
    print("PASS cache hygiene")
    print("PASS shipped path hygiene")
    print("PASS W0 product baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
