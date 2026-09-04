#!/usr/bin/env python3
"""Check the repository's AI-first Markdown documentation without network I/O."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "AI_DEVELOPER_GUIDE.md",
    "ARCHITECTURE.md",
    "COMPILER_PIPELINE.md",
    "DIAGNOSTICS.md",
    "DOCUMENTATION_REPORT.md",
    "DSL_REFERENCE.md",
    "EXTENDING_GARNS.md",
    "INTEGRATION.md",
    "LIMITATIONS.md",
    "TESTING.md",
}
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def slug(heading: str) -> str:
    text = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return text.replace(" ", "-")


def headings(path: Path) -> set[str]:
    return {
        slug(line.lstrip("#"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    }


def main() -> int:
    problems: list[str] = []
    present = {path.name for path in ROOT.glob("*.md")}
    for name in sorted(REQUIRED - present):
        problems.append(f"missing required document: {name}")

    checked = 0
    for path in sorted(ROOT.glob("*.md")):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if "://" in target:
                problems.append(f"{path.name}: network link is not durable evidence: {target}")
                continue
            file_part, _, anchor = target.partition("#")
            if not file_part:
                target_path = path
            else:
                target_path = (path.parent / file_part).resolve()
            checked += 1
            if not target_path.is_file():
                problems.append(f"{path.name}: missing link target: {target}")
                continue
            if anchor and anchor.lower() not in headings(target_path):
                problems.append(f"{path.name}: missing anchor: {target}")

    caches = sorted(ROOT.rglob("__pycache__"))
    problems.extend(f"cache directory present: {path.relative_to(ROOT)}" for path in caches)
    if problems:
        print("\n".join(f"FAIL {problem}" for problem in problems))
        return 1
    print(f"PASS documentation: {len(REQUIRED)} required files; {checked} local links; no caches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
