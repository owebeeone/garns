"""Immutable semantic values shared by backend contracts."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
import math
from typing import Any
from uuid import UUID


class Capability(str, Enum):
    QUERY = "query"
    GOVERNED_WRITE = "governed_write"
    LIVE = "live"
    REPLAY = "replay"
    SCHEMA_INSPECT = "schema_inspect"
    MIGRATE_METADATA = "migrate_metadata"
    MIGRATE_DATA = "migrate_data"


class RefusalCode(str, Enum):
    CAPABILITY_UNSUPPORTED = "capability_unsupported"
    AUTHORITY_INVALID = "authority_invalid"
    CONTEXT_EXPIRED = "context_expired"
    CONTEXT_OWNER_MISMATCH = "context_owner_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    CONCURRENT_TRANSACTION_USE = "concurrent_transaction_use"
    NESTED_TRANSACTION_UNSUPPORTED = "nested_transaction_unsupported"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    CURSOR_EXPIRED = "cursor_expired"
    GENERATION_MISMATCH = "generation_mismatch"
    BINDING_MISMATCH = "binding_mismatch"
    MIGRATION_EFFECTS_UNACCOUNTED = "migration_effects_unaccounted"
    TRANSACTION_IDENTITY_CONFLICT = "transaction_identity_conflict"
    NAMESPACE_UNSAFE = "namespace_unsafe"
    PRIVILEGE_UNSUPPORTED = "privilege_unsupported"
    EXTERNAL_CAPTURE_DEFERRED = "external_capture_deferred"
    PLAN_ADMISSION_REQUIRED = "plan_admission_required"
    PLAN_PROVENANCE_MISMATCH = "plan_provenance_mismatch"
    ADMISSION_REVOKED = "admission_revoked"
    LEASE_INVALID = "lease_invalid"
    LEASE_OWNER_CONFLICT = "lease_owner_conflict"
    OPERATION_OUTCOME_CONFLICT = "operation_outcome_conflict"
    LOCAL_RESOURCE_DRAINING = "local_resource_draining"
    LOCAL_RESOURCE_FENCED = "local_resource_fenced"
    LIFETIME_PROTOCOL_REQUIRED = "lifetime_protocol_required"
    MIGRATION_INDETERMINATE = "migration_indeterminate"
    REFETCH_REQUIRED = "refetch_required"
    WORKER_AUTHORITY_INVALID = "worker_authority_invalid"
    EFFECT_ORDINAL_REUSED = "effect_ordinal_reused"
    ACTIVATION_REQUIRED = "activation_required"
    ACTIVATION_INDETERMINATE = "activation_indeterminate"


@dataclass(frozen=True, slots=True)
class ContractRefusal(Exception):
    code: RefusalCode
    detail: str


@dataclass(frozen=True, slots=True)
class QualifiedDeployment:
    world: str
    deployment: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "world", str(self.world))
        object.__setattr__(self, "deployment", str(self.deployment))
        if not self.world or not self.deployment:
            raise ValueError("world and deployment are required")


@dataclass(frozen=True, slots=True)
class TransactionIdentity:
    scope: QualifiedDeployment
    client_id: str

    def __post_init__(self) -> None:
        if type(self.scope) is not QualifiedDeployment:
            raise TypeError("transaction scope must be qualified")
        object.__setattr__(self, "client_id", str(self.client_id))
        if not self.client_id:
            raise ValueError("client transaction identity is required")


@dataclass(frozen=True, slots=True)
class RevisionCursor:
    scope: QualifiedDeployment
    generation: int
    revision: int

    def __post_init__(self) -> None:
        if type(self.scope) is not QualifiedDeployment:
            raise TypeError("cursor scope must be qualified")
        if self.generation < 1 or self.revision < 0:
            raise ValueError("cursor generation/revision is invalid")


@dataclass(frozen=True, slots=True)
class DeadlinePolicy:
    acquire_seconds: float
    statement_seconds: float
    commit_seconds: float
    cleanup_seconds: float
    shutdown_seconds: float
    migration_lock_seconds: float

    def __post_init__(self) -> None:
        names = ("acquire_seconds", "statement_seconds", "commit_seconds", "cleanup_seconds",
                 "shutdown_seconds", "migration_lock_seconds")
        if any(type(getattr(self, name)) not in {int, float} or type(getattr(self, name)) is bool for name in names):
            raise ValueError("deadlines must be numeric")
        for name in names:
            object.__setattr__(self, name, float(getattr(self, name)))
        values = tuple(getattr(self, name) for name in names)
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError("all deadlines must be finite and positive")


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    backend: str
    supported: frozenset[Capability]
    isolation_levels: frozenset[str]
    server_version: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "backend", str(self.backend))
        object.__setattr__(self, "server_version", str(self.server_version))
        object.__setattr__(self, "supported", frozenset(Capability(item) for item in self.supported))
        object.__setattr__(self, "isolation_levels", frozenset(str(item) for item in self.isolation_levels))

    def require(self, capability: Capability) -> None:
        if capability not in self.supported:
            raise ContractRefusal(RefusalCode.CAPABILITY_UNSUPPORTED, capability.value)


@dataclass(frozen=True, slots=True)
class FrozenMap(Mapping[str, "ImmutableValue"]):
    items_tuple: tuple[tuple[str, "ImmutableValue"], ...]

    def __post_init__(self) -> None:
        if any(type(key) is not str for key, _ in self.items_tuple):
            raise TypeError("structured keys must be plain strings")
        normalized = tuple(sorted((key, freeze_value(value)) for key, value in self.items_tuple))
        object.__setattr__(self, "items_tuple", normalized)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self.items_tuple)

    def __len__(self) -> int:
        return len(self.items_tuple)

    def __getitem__(self, key: str) -> "ImmutableValue":
        for candidate, value in self.items_tuple:
            if candidate == key:
                return value
        raise KeyError(key)


ScalarValue = type(None) | bool | int | float | str | bytes | Decimal | UUID | date | datetime | time | timedelta
ImmutableValue = ScalarValue | tuple["ImmutableValue", ...] | frozenset["ImmutableValue"] | FrozenMap


def freeze_value(value: Any) -> ImmutableValue:
    """Detach the supported parameter/result algebra; reject arbitrary objects."""
    if isinstance(value, FrozenMap):
        return value
    if value is None or type(value) in {bool, int, float, str, bytes, Decimal, UUID, date, datetime, time, timedelta}:
        return value
    if type(value) in {list, tuple}:
        return tuple(freeze_value(item) for item in value)
    if type(value) in {set, frozenset}:
        return frozenset(freeze_value(item) for item in value)
    if type(value) is dict:
        if not all(type(key) is str for key in value):
            raise TypeError("structured value keys must be plain strings")
        return FrozenMap(tuple(sorted((key, freeze_value(item)) for key, item in value.items())))
    raise TypeError(f"unsupported mutable or custom contract value: {type(value).__name__}")


def freeze_rows(rows: Any) -> tuple[FrozenMap, ...]:
    frozen = freeze_value(list(rows))
    if not isinstance(frozen, tuple) or not all(isinstance(row, FrozenMap) for row in frozen):
        raise TypeError("rows must be mappings with plain string keys")
    return frozen


@dataclass(frozen=True, slots=True)
class ParameterValues:
    values: FrozenMap

    def __init__(self, values: Mapping[str, Any]) -> None:
        frozen = freeze_value(dict(values))
        if not isinstance(frozen, FrozenMap):
            raise TypeError("parameters must be a mapping")
        object.__setattr__(self, "values", frozen)


@dataclass(frozen=True, slots=True)
class Snapshot:
    cursor: RevisionCursor
    rows: tuple[FrozenMap, ...]

    def __init__(self, cursor: RevisionCursor, rows: Any) -> None:
        object.__setattr__(self, "cursor", cursor)
        object.__setattr__(self, "rows", freeze_rows(rows))


@dataclass(frozen=True, slots=True)
class RefetchRequired:
    scope: QualifiedDeployment
    reason: RefusalCode
    retained_floor: RevisionCursor | None


@dataclass(frozen=True, slots=True)
class Delivery:
    previous: RevisionCursor
    triggered_by: RevisionCursor
    observed_through: RevisionCursor
    rows: tuple[FrozenMap, ...]

    def __init__(self, previous: RevisionCursor, triggered_by: RevisionCursor,
                 observed_through: RevisionCursor, rows: Any) -> None:
        cursors = (previous, triggered_by, observed_through)
        if len({cursor.scope for cursor in cursors}) != 1 or len({cursor.generation for cursor in cursors}) != 1:
            raise ValueError("delivery cursors must share scope and generation")
        if not previous.revision < triggered_by.revision <= observed_through.revision:
            raise ValueError("delivery revision order is invalid")
        object.__setattr__(self, "previous", previous)
        object.__setattr__(self, "triggered_by", triggered_by)
        object.__setattr__(self, "observed_through", observed_through)
        object.__setattr__(self, "rows", freeze_rows(rows))
