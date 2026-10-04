"""Lossless type, result-shape, and binding-aware opaque plan boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .values import ContractRefusal, QualifiedDeployment, RefusalCode


@dataclass(frozen=True, slots=True)
class SemanticType:
    base: str
    storage_class: str
    optional: bool = False
    list_of: bool = False
    nominal: str | None = None
    closed: tuple[str, ...] = ()
    carrier: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "base", str(self.base))
        object.__setattr__(self, "storage_class", str(self.storage_class))
        object.__setattr__(self, "optional", bool(self.optional))
        object.__setattr__(self, "list_of", bool(self.list_of))
        for name in ("base", "storage_class"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "closed", tuple(str(item) for item in self.closed))
        if self.nominal is not None:
            object.__setattr__(self, "nominal", str(self.nominal))
        if self.carrier is not None:
            object.__setattr__(self, "carrier", str(self.carrier))
        if self.closed and self.nominal is None:
            raise ValueError("closed constructors require a qualified nominal type")

    @classmethod
    def from_type_ref(cls, type_ref: Any) -> "SemanticType":
        """Faithful adapter for inherited ``garns.types.TypeRef`` without owning it."""
        required = ("base", "cls", "optional", "list_of", "nominal", "closed", "carrier")
        if any(not hasattr(type_ref, field) for field in required):
            raise TypeError("not a resolved Garns TypeRef")
        return cls(
            str(type_ref.base), str(type_ref.cls), bool(type_ref.optional), bool(type_ref.list_of),
            None if type_ref.nominal is None else str(type_ref.nominal),
            tuple(str(item) for item in type_ref.closed),
            None if type_ref.carrier is None else str(type_ref.carrier),
        )


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    type: SemanticType

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        if type(self.type) is not SemanticType:
            raise TypeError("parameter type must be a SemanticType")


@dataclass(frozen=True, slots=True)
class ResultField:
    qualified_name: str
    type: SemanticType
    key: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "qualified_name", str(self.qualified_name))
        object.__setattr__(self, "key", bool(self.key))
        if type(self.type) is not SemanticType:
            raise TypeError("result field type must be a SemanticType")


@dataclass(frozen=True, slots=True)
class NestedResult:
    owner_qualified_name: str
    shape: "ResultShape"

    def __post_init__(self) -> None:
        object.__setattr__(self, "owner_qualified_name", str(self.owner_qualified_name))
        if type(self.shape) is not ResultShape:
            raise TypeError("nested result shape must be a ResultShape")


@dataclass(frozen=True, slots=True)
class ResultShape:
    fields: tuple[ResultField, ...]
    nested: tuple[NestedResult, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", tuple(self.fields))
        object.__setattr__(self, "nested", tuple(self.nested))
        if any(type(field) is not ResultField for field in self.fields):
            raise TypeError("result fields must be ResultField values")
        if any(type(child) is not NestedResult for child in self.nested):
            raise TypeError("nested results must be NestedResult values")
        names = {field.qualified_name for field in self.fields}
        if len(names) != len(self.fields):
            raise ValueError("result field identities must be unique")
        if any(child.owner_qualified_name not in names for child in self.nested):
            raise ValueError("nested result owner must be a named result field")


@dataclass(frozen=True, slots=True)
class PlanOrigin:
    world: str
    ir_digest: str
    storage_digest: str
    generation: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "world", str(self.world))
        object.__setattr__(self, "ir_digest", str(self.ir_digest))
        object.__setattr__(self, "storage_digest", str(self.storage_digest))
        if type(self.generation) is not int or self.generation < 1:
            raise ValueError("plan generation must be a positive integer")
        if not all((self.world, self.ir_digest, self.storage_digest)) or self.generation < 1:
            raise ValueError("complete plan origin is required")


@dataclass(frozen=True, slots=True)
class FrozenPlanRoot:
    """Opaque immutable W2 product; W1 does not define expression nodes."""

    format_id: str
    canonical_digest: str
    canonical_payload: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "format_id", str(self.format_id))
        object.__setattr__(self, "canonical_digest", str(self.canonical_digest))
        if not self.format_id or not self.canonical_digest or type(self.canonical_payload) is not bytes:
            raise TypeError("plan root requires a format, digest, and owned bytes payload")


@dataclass(frozen=True, slots=True)
class Plan:
    read_qid: str
    noun: str
    parameters: tuple[Parameter, ...]
    result: ResultShape
    root: FrozenPlanRoot
    origin: PlanOrigin
    live_bound: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "read_qid", str(self.read_qid))
        object.__setattr__(self, "noun", str(self.noun))
        object.__setattr__(self, "parameters", tuple(self.parameters))
        if any(type(parameter) is not Parameter for parameter in self.parameters):
            raise TypeError("plan parameters must be Parameter values")
        if type(self.result) is not ResultShape or type(self.root) is not FrozenPlanRoot or type(self.origin) is not PlanOrigin:
            raise TypeError("plan result, root, and origin require exact immutable contract values")
        if self.noun not in {"query", "question"}:
            raise ValueError("noun must be query or question")
        if self.noun == "question" and (self.live_bound is None or self.live_bound < 1):
            raise ValueError("a question requires a positive live bound")
        if self.noun == "query" and self.live_bound is not None:
            raise ValueError("a query cannot have a live bound")


@dataclass(frozen=True, slots=True)
class BindingIdentity:
    scope: QualifiedDeployment
    ir_digest: str
    storage_digest: str
    generation: int

    def validate_plan(self, plan: Plan) -> None:
        expected = (self.scope.world, self.ir_digest, self.storage_digest, self.generation)
        actual = (plan.origin.world, plan.origin.ir_digest, plan.origin.storage_digest, plan.origin.generation)
        if actual != expected:
            code = RefusalCode.GENERATION_MISMATCH if actual[:3] == expected[:3] else RefusalCode.BINDING_MISMATCH
            raise ContractRefusal(code, "plan origin does not match the opened authored binding")
