"""Opaque admission and whole-operation lease contract foundations.

The public objects in this module carry identity only.  Issuer-private records,
including the admitted plan, belong to a runtime implementation or to the pure
reference model in :mod:`lifetime_reference`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .authority import TrustedContext
from .values import Capability, ParameterValues, QualifiedDeployment

if TYPE_CHECKING:
    from .consumers import ClosedPlanConsumer, ClosedStepProduct


LIFETIME_CAPABILITY = "plan_admission_lifetime_v1"


class AdmissionState(str, Enum):
    ADMITTED = "admitted"
    DRAINING = "draining"
    REVOKED = "revoked"
    RETIRED = "retired"


class LeaseState(str, Enum):
    ACQUIRED = "acquired"
    QUEUED = "queued"
    RUNNING = "running"
    PUBLISHING = "publishing"
    CONTAINED = "contained"
    SUCCEEDED = "succeeded"
    REFUSED = "refused"
    CANCELLED_CONFIRMED = "cancelled_confirmed"

    @property
    def terminal(self) -> bool:
        return self in {
            LeaseState.SUCCEEDED,
            LeaseState.REFUSED,
            LeaseState.CANCELLED_CONFIRMED,
        }


class OperationKind(str, Enum):
    EXECUTE = "execute"
    CONSISTENT_SNAPSHOT = "consistent_snapshot"
    SNAPSHOT_REGISTRATION = "snapshot_registration"
    REFRESH = "refresh"
    ITERATOR_HANDOFF = "iterator_handoff"
    NESTED_FETCH = "nested_fetch"
    TOTAL_FETCH = "total_fetch"


class PlanStep(str, Enum):
    VALIDATE = "validate"
    LOWER = "lower"
    QUEUE = "queue"
    ADAPTER_START = "adapter_start"
    FETCH = "fetch"
    CHILD_FETCH = "child_fetch"
    TOTAL_FETCH = "total_fetch"
    SNAPSHOT_WATERMARK = "snapshot_watermark"
    REGISTRATION = "registration"
    ASSEMBLY = "assembly"
    CURSOR_ADVANCE = "cursor_advance"
    PUBLICATION = "publication"


_STEP_ORDER = (
    PlanStep.VALIDATE,
    PlanStep.LOWER,
    PlanStep.QUEUE,
    PlanStep.ADAPTER_START,
    PlanStep.FETCH,
    PlanStep.CHILD_FETCH,
    PlanStep.TOTAL_FETCH,
    PlanStep.SNAPSHOT_WATERMARK,
    PlanStep.REGISTRATION,
    PlanStep.ASSEMBLY,
    PlanStep.CURSOR_ADVANCE,
    PlanStep.PUBLICATION,
)

_KIND_CAPABILITIES = {
    OperationKind.EXECUTE: Capability.QUERY,
    OperationKind.CONSISTENT_SNAPSHOT: Capability.QUERY,
    OperationKind.SNAPSHOT_REGISTRATION: Capability.LIVE,
    OperationKind.REFRESH: Capability.LIVE,
    OperationKind.ITERATOR_HANDOFF: Capability.LIVE,
    OperationKind.NESTED_FETCH: Capability.QUERY,
    OperationKind.TOTAL_FETCH: Capability.QUERY,
}

_KIND_STEPS = {
    OperationKind.EXECUTE: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.CHILD_FETCH,
        PlanStep.TOTAL_FETCH, PlanStep.ASSEMBLY, PlanStep.PUBLICATION,
    }),
    OperationKind.CONSISTENT_SNAPSHOT: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.CHILD_FETCH,
        PlanStep.TOTAL_FETCH, PlanStep.SNAPSHOT_WATERMARK,
        PlanStep.ASSEMBLY, PlanStep.PUBLICATION,
    }),
    OperationKind.SNAPSHOT_REGISTRATION: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.CHILD_FETCH,
        PlanStep.TOTAL_FETCH, PlanStep.SNAPSHOT_WATERMARK,
        PlanStep.REGISTRATION, PlanStep.ASSEMBLY, PlanStep.PUBLICATION,
    }),
    OperationKind.REFRESH: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.CHILD_FETCH,
        PlanStep.TOTAL_FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE,
        PlanStep.PUBLICATION,
    }),
    OperationKind.ITERATOR_HANDOFF: frozenset({
        PlanStep.VALIDATE,
        PlanStep.PUBLICATION,
    }),
    OperationKind.NESTED_FETCH: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.CHILD_FETCH,
        PlanStep.ASSEMBLY, PlanStep.PUBLICATION,
    }),
    OperationKind.TOTAL_FETCH: frozenset({
        PlanStep.VALIDATE, PlanStep.LOWER, PlanStep.QUEUE,
        PlanStep.ADAPTER_START, PlanStep.FETCH, PlanStep.TOTAL_FETCH,
        PlanStep.ASSEMBLY, PlanStep.PUBLICATION,
    }),
}


def required_capability(kind: OperationKind) -> Capability:
    if type(kind) is not OperationKind:
        raise ValueError("operation kind must be an exact declared member")
    return _KIND_CAPABILITIES[kind]


def validate_step_after(kind: OperationKind, prior_rank: int, step: PlanStep) -> int:
    if type(kind) is not OperationKind or type(step) is not PlanStep:
        raise ValueError("operation step requires exact declared members")
    if step not in _KIND_STEPS[kind]:
        raise ValueError(f"{step.value} is not legal for {kind.value}")
    rank = _STEP_ORDER.index(step)
    if rank <= prior_rank:
        raise ValueError("operation steps must move strictly forward")
    return rank


@dataclass(frozen=True, slots=True)
class OperationIdentity:
    runtime_identity: object
    sequence: int
    deployment: QualifiedDeployment
    generation: int

    def __post_init__(self) -> None:
        if self.runtime_identity is None:
            raise ValueError("operation runtime identity is required")
        if type(self.sequence) is not int or self.sequence < 1:
            raise ValueError("operation sequence must be a positive exact integer")
        if type(self.deployment) is not QualifiedDeployment:
            raise TypeError("operation deployment must be qualified")
        if type(self.generation) is not int or self.generation < 1:
            raise ValueError("operation generation must be a positive exact integer")


_ADMISSION_SEAL = object()
_LEASE_SEAL = object()


class AdmittedReadHandle:
    """Reusable empty identity handle; it never contains or unwraps a plan."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not AdmittedReadHandle or seal is not _ADMISSION_SEAL:
            raise TypeError("admitted read handles are issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _ADMISSION_SEAL:
            raise TypeError("admitted read handles are issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("AdmittedReadHandle is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("AdmittedReadHandle is immutable")

    def __repr__(self) -> str:
        return "AdmittedReadHandle(<opaque identity>)"

    def __copy__(self):
        raise TypeError("AdmittedReadHandle cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("AdmittedReadHandle cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("AdmittedReadHandle cannot be serialized")


class ReadOperationLease:
    """Single-use empty identity handle for one finite operation."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not ReadOperationLease or seal is not _LEASE_SEAL:
            raise TypeError("read operation leases are issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _LEASE_SEAL:
            raise TypeError("read operation leases are issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ReadOperationLease is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("ReadOperationLease is immutable")

    def __repr__(self) -> str:
        return "ReadOperationLease(<opaque identity>)"

    def __copy__(self):
        raise TypeError("ReadOperationLease cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("ReadOperationLease cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("ReadOperationLease cannot be serialized")


def _issue_admitted_handle() -> AdmittedReadHandle:
    return AdmittedReadHandle(_ADMISSION_SEAL)


def _issue_operation_lease() -> ReadOperationLease:
    return ReadOperationLease(_LEASE_SEAL)


@runtime_checkable
class PlanAdmissionVerifier(Protocol):
    """Runtime-owned acquisition/guard interface supplied to a backend once."""

    def acquire(
        self,
        handle: AdmittedReadHandle,
        operation_kind: OperationKind,
        parameters: ParameterValues,
        context: TrustedContext,
        *,
        resource: object,
        owner: object,
    ) -> ReadOperationLease: ...

    def run_plan_step(
        self,
        lease: ReadOperationLease,
        exact_step: PlanStep,
        owner: object,
        consumer: "ClosedPlanConsumer",
    ) -> "ClosedStepProduct": ...

    def transfer_owner(
        self,
        lease: ReadOperationLease,
        expected_owner: object,
        new_owner: object,
        *,
        queued: bool = False,
    ) -> None: ...

    def complete(
        self,
        lease: ReadOperationLease,
        owner: object,
        outcome: LeaseState,
    ) -> None: ...
