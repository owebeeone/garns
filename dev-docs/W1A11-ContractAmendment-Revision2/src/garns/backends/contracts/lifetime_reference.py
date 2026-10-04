"""Deterministic admission/lifetime reference state and effects.

This module is executable contract evidence.  It is not a runtime, lock,
database fence, worker, planner, or cross-process implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .admission import (
    AdmissionState, AdmittedReadHandle, LeaseState, OperationIdentity,
    OperationKind, PlanStep, ReadOperationLease, _issue_admitted_handle,
    _issue_operation_lease, required_capability, validate_step_after,
)
from .authority import RuntimeAuthority, TrustedContext
from .buffer_reference import ReferenceBufferRegistry, SubscriptionRegistration
from .consumers import ClosedPlanConsumer, ClosedStepProduct, ReferenceConsumerIssuer
from .generation_reference import ReferenceGenerationCoordinator
from .lifetime import (
    BufferedDelivery, DeploymentGenerationState, GenerationPermit,
    LocalResourceState, QueueState, ResourceIdentity, ResourceKind,
    transition_local,
)
from .semantic import BindingIdentity, Plan
from .state import CloseKnowledge, CloseOutcome
from .values import ContractRefusal, ParameterValues, RefusalCode, RevisionCursor, TransactionIdentity
from .worker_authority import WorkerAuthorizationIssuer, WorkerCommandAuthorization


class AdmissionEvidenceKind(str, Enum):
    CANONICAL_REBUILD_COMPARE = "canonical_rebuild_compare"
    REFERENCE_FIXTURE = "reference_fixture"


@dataclass(slots=True)
class _AdmissionRecord:
    plan: Plan
    binding: BindingIdentity
    state: AdmissionState
    evidence: AdmissionEvidenceKind
    registry_epoch: int
    coordinator_epoch: int


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
    binding: BindingIdentity
    registry_epoch: int
    coordinator_epoch: int
    last_step_rank: int = -1
    publication_committed: bool = False
    command: object | None = None
    worker: object | None = None
    authorization: WorkerCommandAuthorization | None = None
    registration_committed: bool = False
    completion: LeaseState | None = None


_QUERY_KINDS = frozenset({
    OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT,
    OperationKind.NESTED_FETCH, OperationKind.TOTAL_FETCH,
})
_LIVE_KINDS = frozenset({
    OperationKind.SNAPSHOT_REGISTRATION, OperationKind.REFRESH,
    OperationKind.ITERATOR_HANDOFF,
})


class ReferenceLifetimeRegistry:
    """Pure issuer-private registry with exact identities and causal counters."""

    def __init__(self, authority: RuntimeAuthority, runtime_identity: object,
                 coordinator: ReferenceGenerationCoordinator) -> None:
        if runtime_identity is None:
            raise ValueError("runtime identity is required")
        self._authority = authority
        self._runtime_identity = runtime_identity
        self._coordinator = coordinator
        self._permit_owner = object()
        self._sequence = 0
        self._registry_epoch = 1
        self._admissions: dict[AdmittedReadHandle, _AdmissionRecord] = {}
        self._leases: dict[ReadOperationLease, _LeaseRecord] = {}
        self._resources: dict[str, _ResourceRecord] = {}
        self._queues: dict[str, QueueState] = {}
        self._consumers = ReferenceConsumerIssuer()
        self._buffers = ReferenceBufferRegistry()
        self._workers = WorkerAuthorizationIssuer(
            authority, self._permit_owner, self.worker_operation_live,
        )
        self.publications = 0

    def issue_consumer(self, label: str, effect=None) -> ClosedPlanConsumer:
        return self._consumers.issue(label, effect)

    def add_resource(self, resource: ResourceIdentity) -> None:
        if type(resource) is not ResourceIdentity or resource.name in self._resources:
            raise ValueError("resource identity must be exact and unique")
        if any(name not in self._resources for name in resource.ancestors):
            raise ValueError("every resource ancestor must already exist")
        actual = tuple(self._resources[name].identity.kind for name in resource.ancestors)
        expected = {
            ResourceKind.RUNTIME: (),
            ResourceKind.POOL: (ResourceKind.RUNTIME,),
            ResourceKind.CONNECTION: (ResourceKind.RUNTIME, ResourceKind.POOL),
            ResourceKind.SUBSCRIPTION: (ResourceKind.RUNTIME,),
            ResourceKind.DELIVERY_QUEUE: (ResourceKind.RUNTIME, ResourceKind.SUBSCRIPTION),
        }[resource.kind]
        if actual != expected:
            raise ValueError("resource ancestry kinds do not form a valid containment path")
        self._resources[resource.name] = _ResourceRecord(resource)
        if resource.kind is ResourceKind.DELIVERY_QUEUE:
            self._queues[resource.name] = QueueState.OPEN

    def admit_rebuilt(self, candidate: Plan, rebuilt: Plan,
                      binding: BindingIdentity) -> AdmittedReadHandle:
        if candidate != rebuilt:
            raise ContractRefusal(RefusalCode.PLAN_PROVENANCE_MISMATCH, "canonical rebuild differs")
        return self._admit(candidate, binding, AdmissionEvidenceKind.CANONICAL_REBUILD_COMPARE)

    def setup_reference_admission(self, plan: Plan,
                                  binding: BindingIdentity) -> AdmittedReadHandle:
        """Fixture-only seam; deliberately not production provenance proof."""

        return self._admit(plan, binding, AdmissionEvidenceKind.REFERENCE_FIXTURE)

    def _admit(self, plan: Plan, binding: BindingIdentity,
               evidence: AdmissionEvidenceKind) -> AdmittedReadHandle:
        if type(plan) is not Plan or type(binding) is not BindingIdentity:
            raise TypeError("admission requires exact plan and binding values")
        if binding != self._coordinator.binding or self._coordinator.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "admission binding is not current")
        binding.validate_plan(plan)
        handle = _issue_admitted_handle()
        self._admissions[handle] = _AdmissionRecord(
            plan, binding, AdmissionState.ADMITTED, evidence,
            self._registry_epoch, self._coordinator.admission_epoch,
        )
        return handle

    def acquire(self, handle: AdmittedReadHandle, operation_kind: OperationKind,
                parameters: ParameterValues, context: TrustedContext, *,
                resource: object, owner: object) -> ReadOperationLease:
        if operation_kind is OperationKind.ITERATOR_HANDOFF:
            raise ContractRefusal(
                RefusalCode.REFETCH_REQUIRED,
                "iterator handoff is issued only by an exact buffer exchange",
            )
        return self._acquire(
            handle, operation_kind, parameters, context,
            resource=resource, owner=owner,
        )

    def _acquire(self, handle: AdmittedReadHandle, operation_kind: OperationKind,
                 parameters: ParameterValues, context: TrustedContext, *,
                 resource: object, owner: object) -> ReadOperationLease:
        if type(handle) is not AdmittedReadHandle or type(operation_kind) is not OperationKind:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "exact admitted handle is required")
        admitted = self._admissions.get(handle)
        if admitted is None or not self._admission_current(admitted):
            raise ContractRefusal(RefusalCode.ADMISSION_REVOKED, "admission is not current")
        if type(parameters) is not ParameterValues or owner is None:
            raise TypeError("acquisition requires detached parameters and an owner")
        if admitted.plan.noun == "query" and operation_kind not in _QUERY_KINDS:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "static query cannot acquire a live operation")
        if admitted.plan.noun == "question" and operation_kind not in _LIVE_KINDS:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "live question cannot acquire a static operation")
        stored = self._resource(resource)
        for name in stored.identity.path:
            state = self._resources[name].state
            if state is LocalResourceState.LOCAL_DRAINING:
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_DRAINING, name)
            if state is not LocalResourceState.LOCAL_OPEN:
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, name)
        self._authority.validate(
            context, scope=admitted.binding.scope,
            capability=required_capability(operation_kind),
        )
        admitted.binding.validate_plan(admitted.plan)
        next_sequence = self._sequence + 1
        operation = OperationIdentity(
            self._runtime_identity, next_sequence, admitted.binding.scope,
            admitted.binding.generation,
        )
        permit = self._coordinator.acquire_shared(operation, self._permit_owner)
        self._sequence = next_sequence
        lease = _issue_operation_lease()
        self._leases[lease] = _LeaseRecord(
            handle, operation, operation_kind, owner, LeaseState.ACQUIRED,
            stored.identity.path, permit, context, parameters, admitted.binding,
            self._registry_epoch, self._coordinator.admission_epoch,
        )
        for name in stored.identity.path:
            self._resources[name].charges.add(operation)
        return lease

    def run_plan_step(self, lease: ReadOperationLease, exact_step: PlanStep,
                      owner: object, consumer: ClosedPlanConsumer) -> ClosedStepProduct:
        if not self._consumers.owns(consumer):
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "consumer is not owned by this issuer")
        record = self._live_lease(lease, owner)
        rank = validate_step_after(record.kind, record.last_step_rank, exact_step)
        if exact_step is PlanStep.PUBLICATION:
            if record.kind in {OperationKind.SNAPSHOT_REGISTRATION, OperationKind.REFRESH}:
                raise ContractRefusal(
                    RefusalCode.REFETCH_REQUIRED,
                    "live visibility requires its exact registration or buffer barrier",
                )
            if record.state is not LeaseState.RUNNING or record.last_step_rank < 0:
                raise ContractRefusal(RefusalCode.LEASE_INVALID, "publication requires prior running work")
        elif record.state not in {LeaseState.ACQUIRED, LeaseState.RUNNING}:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "work is not legal in this lease state")
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        if exact_step is PlanStep.PUBLICATION:
            record.state = LeaseState.PUBLISHING
        else:
            record.state = LeaseState.RUNNING
        try:
            product = self._consumers.consume(
                consumer, admission.plan, record.parameters, record.operation, exact_step,
            )
        except Exception:
            record.state = LeaseState.CONTAINED
            raise
        record.last_step_rank = rank
        if exact_step is PlanStep.PUBLICATION:
            record.publication_committed = True
            self.publications += 1
        return product

    def transfer_owner(self, lease: ReadOperationLease, expected_owner: object,
                       new_owner: object, *, queued: bool = False) -> None:
        record = self._live_lease(lease, expected_owner)
        if new_owner is None:
            raise ValueError("new owner is required")
        if queued or record.state is not LeaseState.ACQUIRED:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "generic owner transfer cannot queue or dequeue")
        record.owner = new_owner
        record.state = LeaseState.RUNNING

    def dispatch_to_worker(self, lease: ReadOperationLease, expected_owner: object,
                           command: object, worker: object,
                           effect_ordinals: tuple[int, ...]) -> WorkerCommandAuthorization:
        record = self._live_lease(lease, expected_owner)
        if record.state is not LeaseState.ACQUIRED or command is None or worker is None:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "only acquired work can dispatch")
        self._validate_barriers(record)
        authorization = self._workers._issue_for_dispatch(
            self._permit_owner,
            record.context, required_capability(record.kind), self._runtime_identity,
            record.operation, lease, command, worker, record.binding, effect_ordinals,
        )
        record.command = command
        record.worker = worker
        record.authorization = authorization
        record.owner = command
        record.state = LeaseState.QUEUED
        return authorization

    def dequeue_worker(self, lease: ReadOperationLease, command: object, worker: object,
                       authorization: WorkerCommandAuthorization) -> None:
        record = self._live_lease(lease, command)
        exact = (
            record.state is LeaseState.QUEUED and record.command is command
            and record.worker is worker and record.authorization is authorization
        )
        if not exact:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "queued worker tuple mismatch")
        self._validate_barriers(record, worker_source=True)
        record.owner = worker
        record.state = LeaseState.RUNNING

    @property
    def worker_issuer(self) -> WorkerAuthorizationIssuer:
        return self._workers

    def contain(self, lease: ReadOperationLease, owner: object) -> None:
        record = self._live_lease(lease, owner)
        record.state = LeaseState.CONTAINED
        if record.authorization is not None:
            self._workers.revoke(record.authorization)

    def cancel_queued(self, lease: ReadOperationLease, expected_owner: object) -> None:
        record = self._live_lease(lease, expected_owner)
        if record.state is not LeaseState.QUEUED:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "queued cancellation lost the dequeue race")
        self.complete(lease, expected_owner, LeaseState.CANCELLED_CONFIRMED)

    def complete(self, lease: ReadOperationLease, owner: object, outcome: LeaseState) -> None:
        if type(lease) is not ReadOperationLease or type(outcome) is not LeaseState or not outcome.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "terminal exact lease outcome is required")
        record = self._leases.get(lease)
        if record is None or record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        if record.completion is not None:
            if record.completion is not outcome:
                raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting completion")
            return
        allowed = {
            LeaseState.ACQUIRED: frozenset({LeaseState.REFUSED, LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.QUEUED: frozenset({LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.RUNNING: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED}),
            LeaseState.PUBLISHING: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED}),
            LeaseState.CONTAINED: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED, LeaseState.CANCELLED_CONFIRMED}),
        }
        if record.state.terminal or outcome not in allowed[record.state]:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "illegal terminal lease transition")
        record.state = outcome
        record.completion = outcome
        if record.authorization is not None:
            self._workers.revoke(record.authorization)
        self._coordinator.release_shared(record.permit, self._permit_owner)
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

    def resource_state(self, resource: ResourceIdentity) -> LocalResourceState:
        return self._resource(resource).state

    def worker_operation_live(self, operation: OperationIdentity, lease: ReadOperationLease,
                              command: object, worker: object, binding: BindingIdentity,
                              authorization: WorkerCommandAuthorization) -> bool:
        record = self._leases.get(lease)
        if record is None:
            return False
        exact = (
            record.operation == operation and record.owner is worker
            and record.command is command and record.worker is worker
            and record.authorization is authorization and record.binding == binding
            and record.state is LeaseState.RUNNING
        )
        if not exact:
            return False
        try:
            self._validate_barriers(record, worker_source=True)
        except ContractRefusal:
            return False
        return True

    def register_subscription(self, lease: ReadOperationLease, owner: object,
                              subscription: ResourceIdentity, queue: ResourceIdentity,
                              cursor: RevisionCursor) -> SubscriptionRegistration:
        record = self._live_lease(lease, owner)
        if record.kind is not OperationKind.SNAPSHOT_REGISTRATION or record.registration_committed:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "registration is not legal for this lease")
        if record.state is not LeaseState.RUNNING or record.last_step_rank < 0:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "registration requires prior running work")
        subscription_record = self._resource(subscription)
        queue_record = self._resource(queue)
        if record.resources[-1] != subscription_record.identity.name:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "registration subscription ancestry mismatch")
        publication_rank = validate_step_after(
            record.kind, record.last_step_rank, PlanStep.PUBLICATION,
        )
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        registration = self._buffers.register(
            record.admission, admission.plan.root.canonical_digest, record.parameters,
            record.binding, subscription_record.identity, queue_record.identity, cursor,
        )
        record.state = LeaseState.PUBLISHING
        record.publication_committed = True
        record.registration_committed = True
        record.last_step_rank = publication_rank
        self.publications += 1
        return registration

    def create_refresh_candidate(self, lease: ReadOperationLease, owner: object,
                                 registration: SubscriptionRegistration,
                                 previous: RevisionCursor, triggered_by: RevisionCursor,
                                 observed_through: RevisionCursor, rows: object,
                                 durable_advancement: str) -> BufferedDelivery:
        record = self._live_lease(lease, owner)
        if (
            record.kind is not OperationKind.REFRESH
            or record.state is not LeaseState.RUNNING
            or record.last_step_rank < 0
        ):
            raise ContractRefusal(
                RefusalCode.LEASE_INVALID,
                "refresh candidate requires prior running work",
            )
        self._validate_barriers(record)
        subscription = self._resources[record.resources[-1]].identity
        if subscription.kind is not ResourceKind.SUBSCRIPTION:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh resource is not a subscription")
        return self._buffers.create_candidate(
            registration, record.operation, record.admission, record.parameters,
            record.binding, subscription, previous, triggered_by, observed_through, rows,
            durable_advancement,
        )

    def publish_refresh_buffer(self, lease: ReadOperationLease, owner: object,
                               queue: ResourceIdentity, envelope: BufferedDelivery) -> None:
        record = self._live_lease(lease, owner)
        if record.kind is not OperationKind.REFRESH or record.state is not LeaseState.RUNNING:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "refresh publication requires prior running work")
        queue_record = self._resource(queue)
        if self._queues.get(queue.name) is not QueueState.OPEN:
            record.state = LeaseState.CONTAINED
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "queue rejects publication")
        candidate = self._buffers.validate_publish(
            envelope, record.operation, record.admission, record.parameters,
            record.binding, queue_record.identity,
        )
        publication_rank = validate_step_after(record.kind, record.last_step_rank, PlanStep.PUBLICATION)
        self._validate_barriers(record)
        record.state = LeaseState.PUBLISHING
        try:
            permit = self._coordinator.add_buffer(envelope, self._permit_owner)
        except Exception:
            record.state = LeaseState.CONTAINED
            raise
        self._buffers.commit_publish(candidate, permit)
        record.publication_committed = True
        record.last_step_rank = publication_rank
        self.publications += 1
        self.complete(lease, owner, LeaseState.SUCCEEDED)

    def dequeue_buffer(self, queue: ResourceIdentity, envelope: BufferedDelivery,
                       handle: AdmittedReadHandle, registration: SubscriptionRegistration,
                       context: TrustedContext, owner: object) -> ReadOperationLease:
        queue_record = self._resource(queue)
        if self._queues.get(queue.name) is not QueueState.OPEN:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "dequeue lost the queue barrier")
        admitted = self._admissions.get(handle)
        if admitted is None or not self._admission_current(admitted):
            raise ContractRefusal(RefusalCode.ADMISSION_REVOKED, "handoff admission is not current")
        buffered = self._buffers.validate_dequeue(
            envelope, handle, registration, admitted.binding, queue_record.identity,
        )
        parameters = self._buffers.handoff_parameters(buffered)
        lease = self._acquire(
            handle, OperationKind.ITERATOR_HANDOFF, parameters, context,
            resource=queue_record.identity, owner=owner,
        )
        permit = self._buffers.commit_dequeue(buffered)
        self._coordinator.release_buffer(permit, self._permit_owner)
        return lease

    def start_close(self, resource: ResourceIdentity, *, hard: bool = False) -> None:
        self._resource(resource)
        selected = self._descendant_names(resource.name)
        target = LocalResourceState.LOCAL_FENCED if hard else LocalResourceState.LOCAL_DRAINING
        for name in selected:
            current = self._resources[name].state
            if current is LocalResourceState.LOCAL_OPEN:
                self._resources[name].state = transition_local(current, target)
            elif hard and current is LocalResourceState.LOCAL_DRAINING:
                self._resources[name].state = transition_local(current, target)
        for queue in self._queues:
            if queue in selected:
                self._queues[queue] = QueueState.CLOSED
        self._invalidate_buffers(selected)
        if resource.kind is ResourceKind.RUNTIME:
            for admission in self._admissions.values():
                admission.state = AdmissionState.REVOKED if hard else AdmissionState.DRAINING
        if hard:
            for record in self._leases.values():
                if not record.state.terminal and any(name in selected for name in record.resources):
                    record.state = LeaseState.CONTAINED
                    if record.authorization is not None:
                        self._workers.revoke(record.authorization)

    def close_outcome(self, resource: ResourceIdentity,
                      unresolved: tuple[TransactionIdentity, ...] = ()) -> CloseOutcome:
        root = self._resource(resource)
        if root.state is LocalResourceState.LOCAL_OPEN:
            raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_DRAINING, "close barrier is not installed")
        selected = self._descendant_names(resource.name)
        operations = tuple(sorted(
            (record.operation for record in self._leases.values()
             if not record.state.terminal and any(name in selected for name in record.resources)),
            key=lambda item: item.sequence,
        ))
        if operations or self._buffers.queued_count(selected):
            return CloseOutcome(CloseKnowledge.NONQUIESCENT, unresolved, operations)
        if unresolved:
            return CloseOutcome(CloseKnowledge.UNRESOLVED, unresolved)
        for name in selected:
            record = self._resources[name]
            if record.charges:
                raise ValueError("a parent cannot close while a descendant remains charged")
            if record.state is not LocalResourceState.LOCAL_CLOSED:
                record.state = transition_local(record.state, LocalResourceState.LOCAL_CLOSED)
        if resource.kind is ResourceKind.RUNTIME:
            for admission in self._admissions.values():
                admission.state = AdmissionState.RETIRED
        return CloseOutcome(CloseKnowledge.CLOSED)

    def migration_queue_barrier(self) -> int:
        for queue in self._queues:
            self._queues[queue] = QueueState.MIGRATION_INVALIDATING
        return self._invalidate_buffers(set(self._resources))

    def reopen_queues_no_effect(self) -> None:
        if self._coordinator.state is not DeploymentGenerationState.CURRENT:
            raise ValueError("old generation has not reopened")
        for queue, state in tuple(self._queues.items()):
            if state is QueueState.MIGRATION_INVALIDATING:
                self._queues[queue] = QueueState.OPEN

    def revoke_generation(self) -> None:
        for admission in self._admissions.values():
            admission.state = AdmissionState.REVOKED
        self._registry_epoch += 1
        for record in self._leases.values():
            if not record.state.terminal:
                record.state = LeaseState.CONTAINED
                if record.authorization is not None:
                    self._workers.revoke(record.authorization)

    def _admission_current(self, record: _AdmissionRecord) -> bool:
        return (
            record.state is AdmissionState.ADMITTED
            and record.registry_epoch == self._registry_epoch
            and record.coordinator_epoch == self._coordinator.admission_epoch
            and record.binding == self._coordinator.binding
        )

    def _validate_barriers(self, record: _LeaseRecord, *, worker_source: bool = False) -> None:
        admission = self._admissions[record.admission]
        try:
            if worker_source:
                self._authority._validate_worker_source(
                    record.context, scope=record.binding.scope,
                    capability=required_capability(record.kind),
                    owner_task=self._workers.context_owner(record.authorization),
                )
            else:
                self._authority.validate(
                    record.context, scope=record.binding.scope,
                    capability=required_capability(record.kind),
                )
            if admission.state not in {AdmissionState.ADMITTED, AdmissionState.DRAINING}:
                raise ContractRefusal(RefusalCode.ADMISSION_REVOKED, "admission is not live")
            if record.registry_epoch != self._registry_epoch or admission.registry_epoch != record.registry_epoch:
                raise ContractRefusal(RefusalCode.ADMISSION_REVOKED, "registry epoch changed")
            if record.binding != admission.binding or record.coordinator_epoch != admission.coordinator_epoch:
                raise ContractRefusal(RefusalCode.BINDING_MISMATCH, "lease binding changed")
            if not self._coordinator.permit_live(
                record.permit, self._permit_owner, record.operation,
                record.binding, record.coordinator_epoch,
            ):
                raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "generation permit is not live")
            for name in record.resources:
                if self._resources[name].state in {LocalResourceState.LOCAL_FENCED, LocalResourceState.LOCAL_CLOSED}:
                    raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, name)
        except ContractRefusal:
            if not record.state.terminal:
                record.state = LeaseState.CONTAINED
            raise

    def _live_lease(self, lease: object, owner: object) -> _LeaseRecord:
        if type(lease) is not ReadOperationLease:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact lease instance is required")
        record = self._leases.get(lease)
        if record is None or record.state.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "lease is not live")
        if record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        return record

    def _resource(self, resource: object) -> _ResourceRecord:
        if type(resource) is not ResourceIdentity:
            raise TypeError("resource must be an exact ResourceIdentity")
        record = self._resources.get(resource.name)
        if record is None or record.identity != resource:
            raise ValueError("resource is not registered")
        return record

    def _descendant_names(self, root: str) -> set[str]:
        return {name for name, record in self._resources.items() if root in record.identity.path}

    def _invalidate_buffers(self, selected: set[str]) -> int:
        discarded = 0
        for record in self._buffers.queued_for_resources(selected):
            permit = self._buffers.invalidate(record)
            self._coordinator.release_buffer(permit, self._permit_owner)
            discarded += 1
        return discarded
