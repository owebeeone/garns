"""Deterministic reference state/effect models for admission and lifetime.

These models make contract transitions executable for tests.  They are not a
runtime, lock implementation, database fence, worker, or cross-process proof.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any

from .admission import (
    AdmissionState,
    AdmittedReadHandle,
    LeaseState,
    OperationIdentity,
    OperationKind,
    PlanStep,
    ReadOperationLease,
    _issue_admitted_handle,
    _issue_operation_lease,
)
from .authority import RuntimeAuthority, TrustedContext
from .generation_reference import ReferenceGenerationCoordinator
from .lifetime import (
    BufferedDelivery,
    DeploymentGenerationState,
    GenerationPermit,
    LocalResourceState,
    QueueState,
    ResourceIdentity,
    ResourceKind,
)
from .semantic import BindingIdentity, FrozenPlanRoot, Plan
from .state import CloseKnowledge, CloseOutcome
from .values import (
    Capability,
    ContractRefusal,
    ParameterValues,
    RefusalCode,
    TransactionIdentity,
)


class AdmissionEvidenceKind(str, Enum):
    CANONICAL_REBUILD_COMPARE = "canonical_rebuild_compare"
    REFERENCE_FIXTURE = "reference_fixture"


@dataclass(slots=True)
class _AdmissionRecord:
    plan: Plan
    binding: BindingIdentity
    state: AdmissionState
    evidence: AdmissionEvidenceKind
    epoch: int


@dataclass(slots=True)
class _ResourceRecord:
    identity: ResourceIdentity
    state: LocalResourceState = LocalResourceState.LOCAL_OPEN
    charges: set[OperationIdentity] = field(default_factory=set)


@dataclass(slots=True)
class _LeaseRecord:
    admission: AdmittedReadHandle
    operation: OperationIdentity
    kind: OperationKind
    owner: object
    state: LeaseState
    resources: tuple[str, ...]
    permit: GenerationPermit
    context: TrustedContext
    parameters: ParameterValues
    completion: LeaseState | None = None


@dataclass(slots=True)
class _BufferRecord:
    envelope: BufferedDelivery
    queue: str
    permit_live: bool = True


class ReferenceLifetimeRegistry:
    """Pure state/effect verifier with issuer-private plans and ownership."""

    def __init__(
        self,
        authority: RuntimeAuthority,
        runtime_identity: object,
        coordinator: ReferenceGenerationCoordinator,
    ) -> None:
        if runtime_identity is None:
            raise ValueError("runtime identity is required")
        self._authority = authority
        self._runtime_identity = runtime_identity
        self._coordinator = coordinator
        self._sequence = 0
        self._registry_epoch = 1
        self._admissions: dict[AdmittedReadHandle, _AdmissionRecord] = {}
        self._leases: dict[ReadOperationLease, _LeaseRecord] = {}
        self._resources: dict[str, _ResourceRecord] = {}
        self._queues: dict[str, QueueState] = {}
        self._buffers: dict[int, _BufferRecord] = {}
        self.publications = 0

    def add_resource(self, resource: ResourceIdentity) -> None:
        if type(resource) is not ResourceIdentity or resource.name in self._resources:
            raise ValueError("resource identity must be exact and unique")
        if any(name not in self._resources for name in resource.ancestors):
            raise ValueError("every resource ancestor must already exist")
        actual_kinds = tuple(self._resources[name].identity.kind for name in resource.ancestors)
        expected_kinds = {
            ResourceKind.RUNTIME: (),
            ResourceKind.POOL: (ResourceKind.RUNTIME,),
            ResourceKind.CONNECTION: (ResourceKind.RUNTIME, ResourceKind.POOL),
            ResourceKind.SUBSCRIPTION: (ResourceKind.RUNTIME,),
            ResourceKind.DELIVERY_QUEUE: (ResourceKind.RUNTIME, ResourceKind.SUBSCRIPTION),
        }[resource.kind]
        if actual_kinds != expected_kinds:
            raise ValueError("resource ancestry kinds do not form a valid containment path")
        self._resources[resource.name] = _ResourceRecord(resource)
        if resource.kind is ResourceKind.DELIVERY_QUEUE:
            self._queues[resource.name] = QueueState.OPEN

    def admit_rebuilt(self, candidate: Plan, rebuilt: Plan, binding: BindingIdentity) -> AdmittedReadHandle:
        if candidate != rebuilt:
            raise ContractRefusal(RefusalCode.PLAN_PROVENANCE_MISMATCH, "canonical rebuild differs")
        return self._admit(candidate, binding, AdmissionEvidenceKind.CANONICAL_REBUILD_COMPARE)

    def setup_reference_admission(self, plan: Plan, binding: BindingIdentity) -> AdmittedReadHandle:
        """Fixture-only seam; it is deliberately not production provenance proof."""

        return self._admit(plan, binding, AdmissionEvidenceKind.REFERENCE_FIXTURE)

    def _admit(self, plan: Plan, binding: BindingIdentity, evidence: AdmissionEvidenceKind) -> AdmittedReadHandle:
        if type(plan) is not Plan or type(binding) is not BindingIdentity:
            raise TypeError("admission requires exact plan and binding values")
        binding.validate_plan(plan)
        handle = _issue_admitted_handle()
        self._admissions[handle] = _AdmissionRecord(
            plan=plan,
            binding=binding,
            state=AdmissionState.ADMITTED,
            evidence=evidence,
            epoch=self._registry_epoch,
        )
        return handle

    def acquire(
        self,
        handle: AdmittedReadHandle,
        operation_kind: OperationKind,
        parameters: ParameterValues,
        context: TrustedContext,
        *,
        resource: object,
        owner: object,
    ) -> ReadOperationLease:
        if type(handle) is not AdmittedReadHandle or type(operation_kind) is not OperationKind:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "exact admitted handle is required")
        admitted = self._admissions.get(handle)
        if (
            admitted is None
            or admitted.state is not AdmissionState.ADMITTED
            or admitted.epoch != self._registry_epoch
        ):
            raise ContractRefusal(RefusalCode.ADMISSION_REVOKED, "admission is not current")
        if type(parameters) is not ParameterValues or owner is None:
            raise TypeError("acquisition requires detached parameters and an owner")
        if type(resource) is not ResourceIdentity or resource.name not in self._resources:
            raise ValueError("acquisition resource is not registered")
        stored = self._resources[resource.name].identity
        if stored != resource:
            raise ValueError("acquisition resource identity mismatch")
        path = resource.path
        for name in path:
            state = self._resources[name].state
            if state is LocalResourceState.LOCAL_DRAINING:
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_DRAINING, name)
            if state is not LocalResourceState.LOCAL_OPEN:
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, name)
        capability = Capability.LIVE if operation_kind in {
            OperationKind.SNAPSHOT_REGISTRATION,
            OperationKind.REFRESH,
            OperationKind.ITERATOR_HANDOFF,
        } else Capability.QUERY
        self._authority.validate(context, scope=admitted.binding.scope, capability=capability)
        admitted.binding.validate_plan(admitted.plan)
        self._sequence += 1
        operation = OperationIdentity(
            self._runtime_identity,
            self._sequence,
            admitted.binding.scope,
            admitted.binding.generation,
        )
        permit = self._coordinator.acquire_shared(operation)
        lease = _issue_operation_lease()
        self._leases[lease] = _LeaseRecord(
            admission=handle,
            operation=operation,
            kind=operation_kind,
            owner=owner,
            state=LeaseState.ACQUIRED,
            resources=path,
            permit=permit,
            context=context,
            parameters=parameters,
        )
        for name in path:
            self._resources[name].charges.add(operation)
        return lease

    def run_plan_step(self, lease, exact_step, owner, continuation):
        record = self._live_lease(lease, owner)
        if type(exact_step) is not PlanStep:
            raise ValueError("step must be a declared PlanStep member")
        for name in record.resources:
            if self._resources[name].state in {
                LocalResourceState.LOCAL_FENCED,
                LocalResourceState.LOCAL_CLOSED,
            }:
                self.contain(lease, owner)
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, name)
        admission = self._admissions[record.admission]
        capability = Capability.LIVE if record.kind in {
            OperationKind.SNAPSHOT_REGISTRATION,
            OperationKind.REFRESH,
            OperationKind.ITERATOR_HANDOFF,
        } else Capability.QUERY
        self._authority.validate(record.context, scope=admission.binding.scope, capability=capability)
        if exact_step is PlanStep.PUBLICATION:
            record.state = LeaseState.PUBLISHING
        elif record.state is LeaseState.ACQUIRED:
            record.state = LeaseState.RUNNING
        result = continuation(admission.plan)
        if _contains_plan(result):
            raise TypeError("guarded plan consumers cannot leak plans, roots, or plan closures")
        if exact_step is PlanStep.PUBLICATION:
            self.publications += 1
        return result

    def transfer_owner(self, lease, expected_owner, new_owner, *, queued=False) -> None:
        record = self._live_lease(lease, expected_owner)
        if new_owner is None:
            raise ValueError("new owner is required")
        record.owner = new_owner
        if queued:
            if record.state is not LeaseState.ACQUIRED:
                raise ValueError("only an acquired lease can queue")
            record.state = LeaseState.QUEUED
        elif record.state in {LeaseState.ACQUIRED, LeaseState.QUEUED}:
            record.state = LeaseState.RUNNING

    def contain(self, lease: ReadOperationLease, owner: object) -> None:
        record = self._live_lease(lease, owner)
        record.state = LeaseState.CONTAINED

    def cancel_queued(self, lease: ReadOperationLease, expected_owner: object) -> None:
        record = self._live_lease(lease, expected_owner)
        if record.state is not LeaseState.QUEUED:
            raise ContractRefusal(
                RefusalCode.LEASE_OWNER_CONFLICT,
                "queued cancellation lost the dequeue/owner race",
            )
        self.complete(lease, expected_owner, LeaseState.CANCELLED_CONFIRMED)

    def complete(self, lease, owner, outcome) -> None:
        if type(lease) is not ReadOperationLease or type(outcome) is not LeaseState or not outcome.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "terminal exact lease outcome is required")
        record = self._leases.get(lease)
        if record is None or record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        if record.completion is not None:
            if record.completion is not outcome:
                raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting completion")
            return
        if record.state.terminal:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "terminal lease has no completion record")
        allowed = {
            LeaseState.ACQUIRED: frozenset({LeaseState.REFUSED, LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.QUEUED: frozenset({LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.RUNNING: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED}),
            LeaseState.PUBLISHING: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED}),
            LeaseState.CONTAINED: frozenset({
                LeaseState.SUCCEEDED,
                LeaseState.REFUSED,
                LeaseState.CANCELLED_CONFIRMED,
            }),
        }
        if outcome not in allowed[record.state]:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "illegal terminal lease transition")
        record.state = outcome
        record.completion = outcome
        self._coordinator.release_shared(record.permit)
        for name in record.resources:
            self._resources[name].charges.remove(record.operation)

    def operation(self, lease: ReadOperationLease) -> OperationIdentity:
        record = self._leases.get(lease)
        if record is None:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "lease is not registered")
        return record.operation

    def lease_state(self, lease: ReadOperationLease) -> LeaseState:
        record = self._leases.get(lease)
        if record is None:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "lease is not registered")
        return record.state

    def worker_operation_live(self, operation, lease, command, worker, binding) -> bool:
        record = self._leases.get(lease)
        if record is None or record.operation != operation or record.owner is not worker:
            return False
        admission = self._admissions[record.admission]
        if admission.binding != binding or record.state not in {LeaseState.QUEUED, LeaseState.RUNNING}:
            return False
        return all(
            self._resources[name].state not in {
                LocalResourceState.LOCAL_FENCED,
                LocalResourceState.LOCAL_CLOSED,
            }
            for name in record.resources
        )

    def start_close(self, resource: ResourceIdentity, *, hard: bool = False) -> None:
        root = self._resource(resource)
        target = LocalResourceState.LOCAL_FENCED if hard else LocalResourceState.LOCAL_DRAINING
        if root.state is LocalResourceState.LOCAL_OPEN:
            root.state = target
        elif hard and root.state is LocalResourceState.LOCAL_DRAINING:
            root.state = LocalResourceState.LOCAL_FENCED
        selected = self._descendant_names(resource.name)
        if resource.kind is ResourceKind.RUNTIME:
            for admission in self._admissions.values():
                admission.state = AdmissionState.REVOKED if hard else AdmissionState.DRAINING
        if hard:
            for record in self._leases.values():
                if not record.state.terminal and any(name in selected for name in record.resources):
                    record.state = LeaseState.CONTAINED

    def close_outcome(
        self,
        resource: ResourceIdentity,
        unresolved: tuple[TransactionIdentity, ...] = (),
    ) -> CloseOutcome:
        root = self._resource(resource)
        selected = self._descendant_names(resource.name)
        operations = tuple(sorted(
            (
                record.operation for record in self._leases.values()
                if not record.state.terminal and any(name in selected for name in record.resources)
            ),
            key=lambda item: item.sequence,
        ))
        if operations:
            return CloseOutcome(CloseKnowledge.NONQUIESCENT, unresolved, operations)
        if unresolved:
            return CloseOutcome(CloseKnowledge.UNRESOLVED, unresolved)
        for name in selected:
            record = self._resources[name]
            if record.charges:
                raise ValueError("a parent cannot close while a descendant remains charged")
            record.state = LocalResourceState.LOCAL_CLOSED
        if resource.kind is ResourceKind.RUNTIME:
            for admission in self._admissions.values():
                admission.state = AdmissionState.RETIRED
        return CloseOutcome(CloseKnowledge.CLOSED)

    def enqueue_buffer(self, queue: ResourceIdentity, envelope: BufferedDelivery) -> None:
        record = self._resource(queue)
        if record.identity.kind is not ResourceKind.DELIVERY_QUEUE:
            raise ValueError("buffer destination must be a delivery queue")
        if self._queues[queue.name] is not QueueState.OPEN:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "queue rejects late enqueue")
        if envelope.deployment != self._coordinator.deployment or envelope.generation != self._coordinator.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "buffer generation mismatch")
        self._coordinator.add_buffer(envelope)
        self._buffers[id(envelope)] = _BufferRecord(envelope, queue.name)

    def publish_refresh_buffer(
        self,
        lease: ReadOperationLease,
        owner: object,
        queue: ResourceIdentity,
        envelope: BufferedDelivery,
    ) -> None:
        record = self._live_lease(lease, owner)
        if record.kind is not OperationKind.REFRESH:
            raise ValueError("only a refresh lease can publish a buffered delivery")
        self.enqueue_buffer(queue, envelope)
        self.complete(lease, owner, LeaseState.SUCCEEDED)

    def dequeue_buffer(
        self,
        queue: ResourceIdentity,
        envelope: BufferedDelivery,
        handle: AdmittedReadHandle,
        parameters: ParameterValues,
        context: TrustedContext,
        owner: object,
    ) -> ReadOperationLease:
        record = self._buffers.get(id(envelope))
        if record is None or not record.permit_live or record.queue != queue.name:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "buffer is not live in this queue")
        if self._queues.get(queue.name) is not QueueState.OPEN:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "dequeue lost the migration barrier race")
        lease = self.acquire(
            handle,
            OperationKind.ITERATOR_HANDOFF,
            parameters,
            context,
            resource=queue,
            owner=owner,
        )
        self._coordinator.release_buffer(envelope)
        record.permit_live = False
        return lease

    def discard_buffer(self, envelope: BufferedDelivery) -> None:
        record = self._buffers.get(id(envelope))
        if record is None or not record.permit_live:
            raise ValueError("buffer is not live")
        self._coordinator.release_buffer(envelope)
        record.permit_live = False

    def migration_queue_barrier(self) -> int:
        discarded = 0
        for queue in self._queues:
            self._queues[queue] = QueueState.MIGRATION_INVALIDATING
        for record in self._buffers.values():
            if record.permit_live:
                self._coordinator.release_buffer(record.envelope)
                record.permit_live = False
                discarded += 1
        return discarded

    def reopen_queues_no_effect(self) -> None:
        if self._coordinator.state is not DeploymentGenerationState.CURRENT:
            raise ValueError("old generation has not reopened")
        for queue in self._queues:
            self._queues[queue] = QueueState.OPEN

    def revoke_generation(self) -> None:
        for admission in self._admissions.values():
            admission.state = AdmissionState.REVOKED
        self._registry_epoch += 1

    def _live_lease(self, lease: object, owner: object) -> _LeaseRecord:
        if type(lease) is not ReadOperationLease:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact lease instance is required")
        record = self._leases.get(lease)
        if record is None or record.state.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "lease is not live")
        if record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        return record

    def _resource(self, resource: ResourceIdentity) -> _ResourceRecord:
        if type(resource) is not ResourceIdentity:
            raise TypeError("resource must be an exact ResourceIdentity")
        record = self._resources.get(resource.name)
        if record is None or record.identity != resource:
            raise ValueError("resource is not registered")
        return record

    def _descendant_names(self, root: str) -> set[str]:
        return {
            name for name, record in self._resources.items()
            if root in record.identity.path
        }


def _contains_plan(value: Any, seen: set[int] | None = None) -> bool:
    if isinstance(value, (Plan, FrozenPlanRoot)) or callable(value):
        return True
    if value is None or type(value) in {bool, int, float, str, bytes}:
        return False
    if seen is None:
        seen = set()
    marker = id(value)
    if marker in seen:
        return False
    seen.add(marker)
    if type(value) in {tuple, list, set, frozenset}:
        return any(_contains_plan(item, seen) for item in value)
    if type(value) is dict:
        return any(_contains_plan(key, seen) or _contains_plan(item, seen) for key, item in value.items())
    if is_dataclass(value) and not isinstance(value, type):
        return any(_contains_plan(getattr(value, item.name), seen) for item in fields(value))
    attributes = getattr(value, "__dict__", None)
    if type(attributes) is dict and any(_contains_plan(item, seen) for item in attributes.values()):
        return True
    slots = getattr(type(value), "__slots__", ())
    if type(slots) is str:
        slots = (slots,)
    for name in slots:
        if name not in {"__weakref__", "__dict__"} and hasattr(value, name):
            if _contains_plan(getattr(value, name), seen):
                return True
    return False
