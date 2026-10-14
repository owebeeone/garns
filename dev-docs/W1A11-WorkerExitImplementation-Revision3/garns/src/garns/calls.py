"""Static call registry.

``call owner.function(...)`` resolves only against this explicit registry of
deterministic, side-effect-free functions with declared argument and result
types. Entries marked volatile or effectful exist so that such calls refuse
with a specific code instead of being unknown.
"""

from __future__ import annotations

from dataclasses import dataclass

from .types import TypeRef


@dataclass(frozen=True)
class Signature:
    qid: str
    params: tuple[str, ...]  # type classes: text | numeric | integer | instant | boolean
    result: str  # builtin name or "same" (first numeric argument's type)
    sql: str  # format template over {0}, {1}, ...
    purity: str  # pure | volatile | effectful


REGISTRY: dict[str, Signature] = {
    s.qid: s
    for s in (
        Signature("text.normalize", ("text",), "Text", "LOWER(TRIM({0}))", "pure"),
        Signature("text.lower", ("text",), "Text", "LOWER({0})", "pure"),
        Signature("text.upper", ("text",), "Text", "UPPER({0})", "pure"),
        Signature("text.length", ("text",), "Integer", "LENGTH({0})", "pure"),
        Signature("text.concat", ("text", "text"), "Text", "({0} || {1})", "pure"),
        Signature("math.abs", ("numeric",), "same", "ABS({0})", "pure"),
        Signature("math.round", ("numeric", "integer"), "Decimal", "ROUND({0}, {1})", "pure"),
        Signature("money.round", ("numeric", "integer"), "Money", "ROUND({0}, {1})", "pure"),
        Signature("money.cents", ("numeric",), "Integer", "CAST(ROUND({0} * 100) AS INTEGER)", "pure"),
        Signature("clock.now", (), "Instant", "", "volatile"),
        Signature("random.uniform", (), "Decimal", "", "volatile"),
        Signature("store.purge", ("text",), "Boolean", "", "effectful"),
    )
}


def result_type(sig: Signature, args: tuple[TypeRef, ...]) -> TypeRef:
    from .types import BUILTIN_SCALARS

    if sig.result == "same":
        first = args[0].scalar()
        return TypeRef(first.base, first.cls)
    return TypeRef(sig.result, BUILTIN_SCALARS[sig.result])


def accepts(param: str, t: TypeRef) -> bool:
    cls = t.scalar().cls
    if param == "numeric":
        return cls in ("integer", "decimal")
    return cls == param
