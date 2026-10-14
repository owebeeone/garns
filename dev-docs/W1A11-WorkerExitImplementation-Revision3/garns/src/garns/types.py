"""The Garns type universe.

Builtin scalars carry a type class that drives expression typing and SQL
storage. Newtypes and closed sets are module-qualified nominal types. A given
may also be typed as a carrier, in which case its value is that carrier's
identity.
"""

from __future__ import annotations

from dataclasses import dataclass

# builtin name -> type class
BUILTIN_SCALARS: dict[str, str] = {
    "Text": "text",
    "DisplayName": "text",
    "Email": "text",
    "Id": "text",
    "Instant": "instant",
    "Boolean": "boolean",
    "Integer": "integer",
    "Decimal": "decimal",
    "Money": "decimal",
    "Opaque": "opaque",
    "Vector": "vector",
}

NUMERIC_CLASSES = {"integer", "decimal"}
PRESENCE_ONLY_CLASSES = {"opaque", "vector"}
RESERVED_TERMS = {"identity", "kind", "rank", "count", "engine_clock", "ship_clock"}


@dataclass(frozen=True)
class TypeRef:
    """A resolved type reference.

    ``base`` is the builtin scalar the value is stored as; ``cls`` its class;
    ``nominal`` the qualified newtype/closed-set name when the type is nominal;
    ``closed`` the admitted constructors of a closed set; ``carrier`` the
    qualified carrier when the value is an identity reference.
    """

    base: str
    cls: str
    optional: bool = False
    list_of: bool = False
    nominal: str | None = None
    closed: tuple[str, ...] = ()
    carrier: str | None = None

    @property
    def is_closed(self) -> bool:
        return bool(self.closed)

    @property
    def is_identity(self) -> bool:
        return self.carrier is not None

    def scalar(self) -> "TypeRef":
        """The element type with optional/list_of stripped."""
        return TypeRef(self.base, self.cls, False, False, self.nominal, self.closed, self.carrier)

    def describe(self) -> str:
        core = self.nominal or self.carrier or self.base
        if self.list_of:
            core = f"list_of {core}"
        if self.optional:
            core = f"optional {core}"
        return core

    def canonical(self) -> dict[str, object]:
        return {
            "base": self.base,
            "class": self.cls,
            "optional": self.optional,
            "list_of": self.list_of,
            "nominal": self.nominal,
            "closed": list(self.closed),
            "carrier": self.carrier,
        }


def comparable(left: TypeRef, right: TypeRef) -> bool:
    """Whether two scalar types may be compared with = != < <= > >=."""
    a, b = left.scalar(), right.scalar()
    if a.cls in PRESENCE_ONLY_CLASSES or b.cls in PRESENCE_ONLY_CLASSES:
        return False
    if a.carrier or b.carrier:
        return a.carrier == b.carrier
    if a.is_closed or b.is_closed:
        # closed sets compare with the same nominal set, or with their base type
        if a.is_closed and b.is_closed:
            return a.nominal == b.nominal
        other = b if a.is_closed else a
        this = a if a.is_closed else b
        return other.base == this.base and other.nominal is None
    if a.cls in NUMERIC_CLASSES and b.cls in NUMERIC_CLASSES:
        return True
    return a.cls == b.cls


def ordered(t: TypeRef) -> bool:
    return t.scalar().cls in {"text", "instant", "integer", "decimal"}


def sql_storage_type(t: TypeRef) -> str:
    cls = t.scalar().cls
    if cls in ("integer", "boolean", "instant"):
        return "INTEGER"
    if cls == "decimal":
        return "REAL"
    if cls in ("opaque", "vector"):
        return "BLOB"
    return "TEXT"
