"""Closed lifetime, generation, buffering, and activation contract values."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from .admission import AdmittedReadHandle, OperationIdentity, ReadOperationLease
from .semantic import BindingIdentity, FrozenPlanRoot, Plan
from .values import FrozenMap, QualifiedDeployment, RevisionCursor, freeze_rows


class ResourceKind(str, Enum):
    RUNTIME = "runtime"
    POOL = "pool"
    CONNECTION = "connection"
    SUBSCRIPTION = "subscription"
    DELIVERY_QUEUE = "delivery_queue"


class LocalResourceState(str, Enum):
    LOCAL_OPEN = "local_open"
    LOCAL_DRAINING = "local_draining"
    LOCAL_FENCED = "local_fenced"
    LOCAL_CLOSED = "local_closed"


class DeploymentGenerationState(str, Enum):
    CURRENT = "current"
    DRAINING_OLD = "draining_old"
    MIGRATING = "migrating"
    MIGRATION_INDETERMINATE = "migration_indeterminate"
    RETIRED = "retired"


class ActivationState(str, Enum):
    UNACTIVATED = "unactivated"
    ACTIVATING = "activating"
    ACTIVE_UNUSED = "active_unused"
    ACTIVE = "active"
    ACTIVATION_INDETERMINATE = "activation_indeterminate"


class QueueState(str, Enum):
    OPEN = "open"
    MIGRATION_INVALIDATING = "migration_invalidating"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class ResourceIdentity:
    """Immutable local ancestry; owner transfer never changes this path."""

    name: str
    kind: ResourceKind
    ancestors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "ancestors", tuple(str(item) for item in self.ancestors))
        if not self.name or any(not item for item in self.ancestors):
            raise ValueError("resource identity and ancestry must be nonempty")
        if type(self.kind) is not ResourceKind:
            raise ValueError("resource kind must be a declared ResourceKind member")
        if self.name in self.ancestors or len(set(self.ancestors)) != len(self.ancestors):
            raise ValueError("resource ancestry must be acyclic and unique")
        expected_depth = {
            ResourceKind.RUNTIME: 0,
            ResourceKind.POOL: 1,
            ResourceKind.CONNECTION: 2,
            ResourceKind.SUBSCRIPTION: 1,
            ResourceKind.DELIVERY_QUEUE: 2,
        }[self.kind]
        if len(self.ancestors) != expected_depth:
            raise ValueError("resource ancestry depth does not match its kind")

    @property
    def path(self) -> tuple[str, ...]:
        return self.ancestors + (self.name,)


_GENERATION_PERMIT_SEAL = object()
_BUFFER_PERMIT_SEAL = object()


class GenerationPermit:
    """Empty coordinator-issued shared permit identity."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not GenerationPermit or seal is not _GENERATION_PERMIT_SEAL:
            raise TypeError("generation permits are coordinator-issued")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _GENERATION_PERMIT_SEAL:
            raise TypeError("generation permits are coordinator-issued")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("GenerationPermit is immutable")

    def __repr__(self) -> str:
        return "GenerationPermit(<opaque identity>)"

    def __copy__(self):
        raise TypeError("GenerationPermit cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("GenerationPermit cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("GenerationPermit cannot be serialized")


class BufferedDeliveryPermit:
    """Empty coordinator-issued ownership identity for one queued envelope."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not BufferedDeliveryPermit or seal is not _BUFFER_PERMIT_SEAL:
            raise TypeError("buffer permits are coordinator-issued")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _BUFFER_PERMIT_SEAL:
            raise TypeError("buffer permits are coordinator-issued")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("BufferedDeliveryPermit is immutable")

    def __repr__(self) -> str:
        return "BufferedDeliveryPermit(<opaque identity>)"

    def __copy__(self):
        raise TypeError("BufferedDeliveryPermit cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("BufferedDeliveryPermit cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("BufferedDeliveryPermit cannot be serialized")


def _issue_generation_permit() -> GenerationPermit:
    return GenerationPermit(_GENERATION_PERMIT_SEAL)


def _issue_buffer_permit() -> BufferedDeliveryPermit:
    return BufferedDeliveryPermit(_BUFFER_PERMIT_SEAL)


@dataclass(frozen=True, slots=True)
class ActivationEvidence:
    """Proof inputs required by a future operator-owned physical activation."""

    deployment: QualifiedDeployment
    binding: BindingIdentity
    protocol_epoch: int
    inventory_digest: str
    physical_fence_digest: str
    durable_record_digest: str
    protocol: str

    def __post_init__(self) -> None:
        if type(self.deployment) is not QualifiedDeployment:
            raise TypeError("activation deployment must be qualified")
        if type(self.binding) is not BindingIdentity or self.binding.scope != self.deployment:
            raise ValueError("activation binding must match the qualified deployment")
        if type(self.protocol_epoch) is not int or self.protocol_epoch < 1:
            raise ValueError("activation protocol epoch must be positive")
        for name in ("inventory_digest", "physical_fence_digest", "durable_record_digest"):
            value = str(getattr(self, name))
            object.__setattr__(self, name, value)
            if not value:
                raise ValueError(f"{name} is required")
        if type(self.protocol) is not str:
            raise TypeError("activation protocol must be a plain string")


@dataclass(frozen=True, slots=True)
class BufferedDelivery:
    """Immutable result provenance.  It intentionally contains no plan or lease."""

    deployment: QualifiedDeployment
    generation: int
    admission_identity: object
    plan_digest: str
    previous: RevisionCursor
    triggered_by: RevisionCursor
    observed_through: RevisionCursor
    rows: tuple[FrozenMap, ...]
    durable_advancement: str

    def __init__(
        self,
        deployment: QualifiedDeployment,
        generation: int,
        admission_identity: object,
        plan_digest: str,
        previous: RevisionCursor,
        triggered_by: RevisionCursor,
        observed_through: RevisionCursor,
        rows: object,
        durable_advancement: str,
    ) -> None:
        cursors = (previous, triggered_by, observed_through)
        if type(deployment) is not QualifiedDeployment:
            raise TypeError("buffer deployment must be qualified")
        if type(generation) is not int or generation < 1:
            raise ValueError("buffer generation must be positive")
        if type(admission_identity) is not AdmittedReadHandle:
            raise TypeError("buffer admission identity must be an exact admitted handle")
        if any(type(cursor) is not RevisionCursor for cursor in cursors):
            raise TypeError("buffer cursors must be exact RevisionCursor values")
        if any(cursor.scope != deployment or cursor.generation != generation for cursor in cursors):
            raise ValueError("buffer provenance and cursors must share deployment/generation")
        if not previous.revision < triggered_by.revision <= observed_through.revision:
            raise ValueError("buffer cursor order is invalid")
        plan_digest = str(plan_digest)
        durable_advancement = str(durable_advancement)
        if not plan_digest or not durable_advancement:
            raise ValueError("buffer plan and advancement digests are required")
        object.__setattr__(self, "deployment", deployment)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "admission_identity", admission_identity)
        object.__setattr__(self, "plan_digest", plan_digest)
        object.__setattr__(self, "previous", previous)
        object.__setattr__(self, "triggered_by", triggered_by)
        object.__setattr__(self, "observed_through", observed_through)
        object.__setattr__(self, "rows", freeze_rows(rows))
        object.__setattr__(self, "durable_advancement", durable_advancement)


_LOCAL_EDGES = {
    LocalResourceState.LOCAL_OPEN: frozenset({
        LocalResourceState.LOCAL_DRAINING,
        LocalResourceState.LOCAL_FENCED,
    }),
    LocalResourceState.LOCAL_DRAINING: frozenset({
        LocalResourceState.LOCAL_CLOSED,
        LocalResourceState.LOCAL_FENCED,
    }),
    LocalResourceState.LOCAL_FENCED: frozenset({LocalResourceState.LOCAL_CLOSED}),
    LocalResourceState.LOCAL_CLOSED: frozenset(),
}


def transition_local(current: LocalResourceState, target: LocalResourceState) -> LocalResourceState:
    if type(current) is not LocalResourceState or type(target) is not LocalResourceState:
        raise ValueError("local transition requires declared state members")
    if target not in _LOCAL_EDGES[current]:
        raise ValueError(f"illegal local transition: {current.value} -> {target.value}")
    return target


@runtime_checkable
class SharedGenerationCoordinator(Protocol):
    """Contract seam for a future authoritative deployment-wide coordinator."""

    deployment: QualifiedDeployment
    binding: BindingIdentity
    state: DeploymentGenerationState

    def acquire_shared(self, operation: OperationIdentity, owner: object) -> GenerationPermit: ...
    def release_shared(self, permit: GenerationPermit, owner: object) -> None: ...
    def add_buffer(self, envelope: BufferedDelivery, owner: object) -> BufferedDeliveryPermit: ...
    def release_buffer(self, permit: BufferedDeliveryPermit, owner: object) -> None: ...
    def permit_live(self, permit: GenerationPermit, owner: object,
                    operation: OperationIdentity, binding: BindingIdentity,
                    admission_epoch: int) -> bool: ...
    def begin_drain(self, expected: BindingIdentity) -> None: ...
    def begin_migration(self, requested: BindingIdentity) -> None: ...
    def publish_generation(self, requested: BindingIdentity) -> None: ...
    def mark_indeterminate(self) -> None: ...
    def count(self) -> int: ...


def assert_no_plan_or_lease(buffer: BufferedDelivery) -> None:
    """Small exhaustive contract check used by reference and architecture tests."""

    for value in (
        buffer.deployment,
        buffer.generation,
        buffer.admission_identity,
        buffer.plan_digest,
        buffer.previous,
        buffer.triggered_by,
        buffer.observed_through,
        buffer.rows,
        buffer.durable_advancement,
    ):
        if isinstance(value, (Plan, FrozenPlanRoot, ReadOperationLease)):
            raise TypeError("buffered deliveries cannot contain plans or operation leases")
