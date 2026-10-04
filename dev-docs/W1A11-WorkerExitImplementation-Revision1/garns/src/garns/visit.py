"""Exhaustive visitors over the IR.

A visitor dispatches on the exact node class. ``check_exhaustive`` verifies,
for a visitor class and a union of node classes, that every member has a
handler; the test suite calls it for every consumer so that adding an IR node
without updating a consumer fails loudly.
"""

from __future__ import annotations

import typing
from typing import Any, Callable, Iterable

from . import ir as I


def union_members(union: Any) -> tuple[type, ...]:
    args = typing.get_args(union)
    if not args:
        return (union,)
    out: list[type] = []
    for a in args:
        out.extend(union_members(a))
    return tuple(out)


EXPR_NODES = union_members(I.Expr)
OPERAND_NODES = union_members(I.Operand)
SHOW_NODES = union_members(I.ShowTerm)
TERMINAL_NODES = union_members(I.Terminal)
DECLARATION_NODES = (I.Intent, I.Newtype, I.Carrier, I.Read, I.Alias, I.Bulk, I.Restricted, I.Compound, I.Tombstone, I.TightenDecl, I.RetypeDecl, I.RestoreDecl, I.MoveHome, I.World, I.Deployment, I.Module)


class Visitor:
    """Dispatch ``visit(node)`` to ``visit_<ClassName>``; unknown nodes fail loudly."""

    def visit(self, node: Any, *args: Any) -> Any:
        method: Callable[..., Any] | None = getattr(self, f"visit_{type(node).__name__}", None)
        if method is None:
            raise TypeError(f"{type(self).__name__} has no handler for IR node {type(node).__name__}")
        return method(node, *args)


def check_exhaustive(visitor: type, nodes: Iterable[type]) -> list[str]:
    """Names of node classes without a handler on ``visitor`` (empty when exhaustive)."""
    missing = []
    for node in nodes:
        if not callable(getattr(visitor, f"visit_{node.__name__}", None)):
            missing.append(node.__name__)
    return missing


def assert_exhaustive(visitor: type, nodes: Iterable[type]) -> None:
    missing = check_exhaustive(visitor, nodes)
    if missing:
        raise TypeError(f"{visitor.__name__} lacks handlers for: {', '.join(missing)}")
