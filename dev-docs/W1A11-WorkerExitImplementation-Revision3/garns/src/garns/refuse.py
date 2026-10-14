"""Refusals: the single failure channel of the compiler and runtime.

A refusal names a stage, a stable code, and a source position. Stages are
ordered; the first refusal of a pipeline is the one reported.
"""

from __future__ import annotations

from dataclasses import dataclass

STAGES: tuple[str, ...] = (
    "decode",     # the frozen grammar rejected the text
    "validate",   # names, types, worlds, storage and algebra checks
    "lower",      # relational / storage lowering
    "generate",   # artifact generation
    "ship",       # evolution and store shipping
    "load",       # opening an existing store
    "runtime",    # ledger, live, capture effects
)


@dataclass(frozen=True)
class Refusal(Exception):
    code: str
    stage: str
    file: str
    line: int
    column: int
    detail: str = ""

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError(f"unknown refusal stage {self.stage!r}")

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}:{self.column}" if self.file else f"{self.line}:{self.column}"
        tail = f": {self.detail}" if self.detail else ""
        return f"{self.code} [{self.stage}] at {where}{tail}"

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "stage": self.stage,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "detail": self.detail,
        }


def refuse(code: str, stage: str, loc: "object", detail: str = "") -> None:
    """Raise a refusal positioned at ``loc`` (anything with file/line/column)."""
    inner = getattr(loc, "loc", None)
    if inner is not None and hasattr(inner, "line"):
        loc = inner
    file = getattr(loc, "file", "") or ""
    line = int(getattr(loc, "line", 1) or 1)
    column = int(getattr(loc, "column", 1) or 1)
    raise Refusal(code, stage, file, line, column, detail)
