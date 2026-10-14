"""Typed governed mutation, schema, migration, and ledger operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .semantic import BindingIdentity
from .values import ContractRefusal, FrozenMap, RefusalCode, RevisionCursor, TransactionIdentity, freeze_value


class MutationKind(str, Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class MigrationEffect(str, Enum):
    METADATA_ONLY = "metadata_only"
    BACKFILL = "backfill"
    DDL_DATA_CHANGE = "ddl_data_change"


@dataclass(frozen=True, slots=True)
class GovernedMutation:
    kind: MutationKind
    carrier_qid: str
    identity: Any
    values: FrozenMap

    def __init__(self, kind: MutationKind, carrier_qid: str, identity: Any, values: Mapping[str, Any]) -> None:
        frozen = freeze_value(dict(values))
        if not isinstance(frozen, FrozenMap):
            raise TypeError("mutation values must be a mapping")
        object.__setattr__(self, "kind", MutationKind(kind))
        object.__setattr__(self, "carrier_qid", str(carrier_qid))
        object.__setattr__(self, "identity", freeze_value(identity))
        object.__setattr__(self, "values", frozen)


@dataclass(frozen=True, slots=True)
class LedgerEffect:
    carrier_qid: str
    identity: Any
    operation: MutationKind
    changes: FrozenMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "carrier_qid", str(self.carrier_qid))
        object.__setattr__(self, "identity", freeze_value(self.identity))
        object.__setattr__(self, "operation", MutationKind(self.operation))
        if not isinstance(self.changes, FrozenMap):
            frozen = freeze_value(dict(self.changes))
            object.__setattr__(self, "changes", frozen)


@dataclass(frozen=True, slots=True)
class LedgerPublication:
    transaction: TransactionIdentity
    revision: RevisionCursor
    payload_digest: str
    effects: tuple[LedgerEffect, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload_digest", str(self.payload_digest))
        object.__setattr__(self, "effects", tuple(self.effects))
        if not self.payload_digest or any(type(effect) is not LedgerEffect for effect in self.effects):
            raise ValueError("publication requires a payload digest and typed effects")


@dataclass(frozen=True, slots=True)
class SchemaSnapshot:
    binding: BindingIdentity
    schema_digest: str
    relation_digests: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_digest", str(self.schema_digest))
        object.__setattr__(self, "relation_digests", tuple((str(name), str(digest)) for name, digest in self.relation_digests))


@dataclass(frozen=True, slots=True)
class MigrationDecision:
    effect: MigrationEffect
    atomically_accounted: bool
    changes_observable_shape: bool

    def validate(self) -> None:
        if self.effect is MigrationEffect.METADATA_ONLY:
            if self.changes_observable_shape or self.atomically_accounted:
                raise ContractRefusal(RefusalCode.MIGRATION_EFFECTS_UNACCOUNTED, "metadata-only transition changes no rows or observable shape")
            return
        if not self.atomically_accounted:
            raise ContractRefusal(RefusalCode.MIGRATION_EFFECTS_UNACCOUNTED, "data-changing migration must atomically ledger every induced effect")


@dataclass(frozen=True, slots=True)
class MigrationRequest:
    before: BindingIdentity
    after: BindingIdentity
    decision: MigrationDecision
    migration_digest: str

    def __post_init__(self) -> None:
        self.decision.validate()
        if self.before.scope != self.after.scope or self.after.generation != self.before.generation + 1:
            raise ValueError("migration must advance one generation in one qualified scope")
        if not self.migration_digest:
            raise ValueError("migration digest is required")


@dataclass(frozen=True, slots=True)
class MigrationLock:
    scope_key: str
    owner_token: str


@dataclass(frozen=True, slots=True)
class MigrationOutcome:
    request: MigrationRequest
    binding: BindingIdentity
    publication: LedgerPublication | None
    metadata_proof_digest: str | None

    def __post_init__(self) -> None:
        if self.binding != self.request.after:
            raise ValueError("migration outcome must publish the requested binding")
        if self.request.decision.effect is MigrationEffect.METADATA_ONLY:
            if self.publication is not None or not self.metadata_proof_digest:
                raise ValueError("metadata-only success requires proof and no publication")
            return
        if self.metadata_proof_digest is not None or self.publication is None or not self.publication.effects:
            raise ValueError("data-changing success requires only a nonempty publication")
        publication = self.publication
        if publication.revision.scope != self.binding.scope or publication.revision.generation != self.binding.generation:
            raise ValueError("migration publication scope/generation mismatch")
        if publication.transaction != TransactionIdentity(self.binding.scope, f"migration:{self.request.migration_digest}"):
            raise ValueError("migration transaction identity mismatch")
        if publication.payload_digest != self.request.migration_digest:
            raise ValueError("migration payload digest mismatch")

    @classmethod
    def success(cls, request: MigrationRequest, binding: BindingIdentity,
                publication: LedgerPublication | None = None,
                metadata_proof_digest: str | None = None) -> "MigrationOutcome":
        if binding != request.after:
            raise ValueError("migration outcome must publish the requested binding")
        if request.decision.effect is MigrationEffect.METADATA_ONLY:
            if publication is not None or not metadata_proof_digest:
                raise ValueError("metadata-only success requires proof and no data publication")
        else:
            if publication is None or not publication.effects:
                raise ValueError("data-changing success requires nonempty ledger effects")
            if publication.revision.scope != binding.scope or publication.revision.generation != binding.generation:
                raise ValueError("migration publication scope/generation mismatch")
            expected_identity = TransactionIdentity(binding.scope, f"migration:{request.migration_digest}")
            if publication.transaction != expected_identity:
                raise ValueError("migration publication transaction identity mismatch")
            if publication.payload_digest != request.migration_digest:
                raise ValueError("migration publication digest mismatch")
        return cls(request, binding, publication, metadata_proof_digest)


class MigrationFailureKind(str, Enum):
    REFUSED = "refused"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True, slots=True)
class MigrationNotApplied:
    request: MigrationRequest
    kind: MigrationFailureKind
    detail: str


MigrationResult = MigrationOutcome | MigrationNotApplied


@dataclass(frozen=True, slots=True)
class QualifiedName:
    catalog: str
    schema: str
    object: str

    def __post_init__(self) -> None:
        if not all((self.catalog, self.schema, self.object)):
            raise ValueError("catalog, schema, and object are required")
