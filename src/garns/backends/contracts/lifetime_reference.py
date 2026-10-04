"""Deterministic admission/lifetime reference state and effects.

This module is executable contract evidence.  It is not a runtime, lock,
database fence, worker, planner, or cross-process implementation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from .admission import (
    AdmissionState, AdmittedReadHandle, LeaseState, OperationIdentity,
    OperationKind, PlanStep, ReadOperationLease, _issue_admitted_handle,
    _issue_operation_lease, required_capability, validate_step_after,
)
from .authority import RuntimeAuthority, TrustedContext
from .buffer_reference import (
    ReferenceBufferRegistry, RegistrationState, SubscriptionRegistration,
)
from .consumers import (
    ClosedDerivedCommand, ClosedPlanConsumer, ClosedStepProduct,
    ReferenceConsumerIssuer,
)
from .generation_reference import ReferenceGenerationCoordinator
from .lifetime import (
    BufferedDelivery, DeploymentGenerationState, GenerationPermit,
    LocalResourceState, QueueState, ResourceIdentity, ResourceKind,
    transition_local,
)
from .migration_reference import (
    LifetimeOpenRecord, MigrationAttempt, MigrationParticipant,
    ParticipantMembership, ParticipantState,
)
from .snapshot_reference import (
    InitialSnapshotCandidate, InitialSnapshotPublication,
    NeutralRefreshReceipt, ReferenceSnapshotRegistry, RefreshSnapshotCandidate,
    issue_neutral_receipt,
)
from .semantic import BindingIdentity, Plan
from .state import CloseKnowledge, CloseOutcome
from .values import (
    Capability, ContractRefusal, ParameterValues, RefusalCode, RevisionCursor,
    RefetchRequired, RefreshCommitRefused, RefreshContainmentPending,
    RefreshRecordUnavailable, TransactionIdentity, freeze_rows, freeze_value,
)
from .worker_authority import (
    ClosedWorkerCommand, ClosedWorkerFailure, ClosedWorkerResult,
    DeliveryPublicationCandidate, DeliveryRetirementReceipt,
    DeliverySettlementReceipt, DeliveryStopObservation, EffectKnowledge,
    ReceivingTaskLifecycleObservation, RuntimeContinuationOwner,
    WorkerAuthorizationIssuer, WorkerCommandAuthorization, WorkerCommandSpec,
    WorkerCommandState, WorkerContainmentOwner, WorkerEffectReservation,
    WorkerExitKind, WorkerExitReceipt, WorkerStopReceipt, _issue,
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
    completed_steps: set[PlanStep] = field(default_factory=set)
    issued_derived_ordinals: set[int] = field(default_factory=set)
    next_derived_ordinal: int = 1
    handoff_envelope: BufferedDelivery | None = None
    receiving_task: object | None = None
    lifecycle_serial: int = 0
    continuation_owner: RuntimeContinuationOwner | None = None
    containment_owner: WorkerContainmentOwner | None = None
    command_schedule: tuple[WorkerCommandSpec, ...] = ()
    command_ledger: list["_WorkerCommandRecord"] = field(default_factory=list)
    active_command_serial: int | None = None
    receiver_live: bool = True
    publication_candidate: DeliveryPublicationCandidate | None = None
    delivery_settlement: DeliverySettlementReceipt | None = None
    delivery_retirement: DeliveryRetirementReceipt | None = None
    delivery_stop: DeliveryStopObservation | None = None
    refresh_candidate: RefreshSnapshotCandidate | None = None
    refresh_snapshot: object | None = None
    neutral_receipt: NeutralRefreshReceipt | None = None
    refresh_refetch: RefetchRequired | None = None
    refresh_containment_stop: WorkerStopReceipt | None = None


@dataclass(slots=True)
class _WorkerCommandRecord:
    serial: int
    command: ClosedWorkerCommand
    authorization: WorkerCommandAuthorization
    worker: object
    spec: WorkerCommandSpec
    state: WorkerCommandState = WorkerCommandState.QUEUED
    remaining_ordinals: set[int] = field(default_factory=set)
    completed_ordinals: set[int] = field(default_factory=set)
    active_reservation: WorkerEffectReservation | None = None
    reservation_ordinal: int | None = None
    exit_receipt: WorkerExitReceipt | None = None
    exit_kind: WorkerExitKind | None = None
    exit_serial: int = 0
    effect_knowledge: EffectKnowledge = EffectKnowledge.NOT_BEGUN
    result: ClosedWorkerResult | None = None
    result_value: object | None = None
    failure: ClosedWorkerFailure | None = None
    stop_receipt: WorkerStopReceipt | None = None
    cleanup_diagnostics: list[ClosedWorkerFailure] = field(default_factory=list)
    cancel_diagnostic: bool = False
    next_cleanup_step: int = 1


@dataclass(frozen=True, slots=True)
class _LifecycleObservationRecord:
    lease: ReadOperationLease
    task: object
    serial: int


@dataclass(frozen=True, slots=True)
class _StopRecord:
    lease: ReadOperationLease
    command_serial: int


@dataclass(frozen=True, slots=True)
class _DeliveryStopRecord:
    lease: ReadOperationLease
    retirement: DeliveryRetirementReceipt


_QUERY_KINDS = frozenset({
    OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT,
})
_LIVE_KINDS = frozenset({
    OperationKind.SNAPSHOT_REGISTRATION, OperationKind.REFRESH,
    OperationKind.ITERATOR_HANDOFF,
})


class ReferenceLifetimeRegistry:
    """Pure issuer-private registry with exact identities and causal counters."""

    def __init__(
        self,
        authority: RuntimeAuthority,
        runtime_identity: object,
        coordinator: ReferenceGenerationCoordinator,
        *,
        command_schedule_provider: Callable[[OperationKind], tuple[WorkerCommandSpec, ...]] | None = None,
        assigned_worker_provider: Callable[[int], object] | None = None,
        effect_provider: Callable[[str, int], Callable[[], object]] | None = None,
        cleanup_provider: Callable[[str, int], Callable[[], None]] | None = None,
    ) -> None:
        if runtime_identity is None:
            raise ValueError("runtime identity is required")
        self._authority = authority
        self._runtime_identity = runtime_identity
        self._coordinator = coordinator
        self._open_record: LifetimeOpenRecord = coordinator.prepare_lifetime_open(runtime_identity)
        self._membership: ParticipantMembership | None = None
        self._permit_owner = object()
        self._sequence = 0
        self._registry_epoch = 1
        self._admissions: dict[AdmittedReadHandle, _AdmissionRecord] = {}
        self._leases: dict[ReadOperationLease, _LeaseRecord] = {}
        self._resources: dict[str, _ResourceRecord] = {}
        self._queues: dict[str, QueueState] = {}
        self._consumers = ReferenceConsumerIssuer()
        self._buffers = ReferenceBufferRegistry()
        self._snapshots = ReferenceSnapshotRegistry()
        self._migration_participant: MigrationParticipant | None = None
        self._barrier_attempt: MigrationAttempt | None = None
        self._command_schedule_provider = command_schedule_provider or (
            lambda kind: (WorkerCommandSpec(f"{kind.value}-command", (1,)),)
        )
        self._assigned_worker_provider = assigned_worker_provider or (lambda serial: authority.capture_task_owner())
        self._effect_provider = effect_provider or (lambda label, ordinal: lambda: (label, ordinal))
        self._cleanup_provider = cleanup_provider or (lambda label, step: lambda: None)
        self._lifecycle_serial = 0
        self._observations: dict[ReceivingTaskLifecycleObservation, _LifecycleObservationRecord] = {}
        self._consumed_observations: set[ReceivingTaskLifecycleObservation] = set()
        self._stops: dict[WorkerStopReceipt, _StopRecord] = {}
        self._delivery_stops: dict[DeliveryStopObservation, _DeliveryStopRecord] = {}
        self._results: dict[ClosedWorkerResult, tuple[WorkerCommandAuthorization, object]] = {}
        self._failures: dict[ClosedWorkerFailure, WorkerCommandAuthorization | ReadOperationLease] = {}
        self._workers = WorkerAuthorizationIssuer(
            self.run_worker_effect, self._worker_context_owner, self._revoke_worker_authorization,
        )
        self.publications = 0

    def open_lifetime(self) -> ParticipantMembership:
        if self._membership is not None:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "runtime membership already joined")
        self._membership = self._coordinator.join_runtime(self._open_record)
        self._migration_participant = self._membership
        return self._membership

    @property
    def membership(self) -> ParticipantMembership | None:
        return self._membership

    def issue_consumer(self, label: str) -> ClosedPlanConsumer:
        return self._consumers.issue(label)

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
        if self._membership is None:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "runtime has not joined the active lifetime")
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
        receiver = self._authority.capture_task_owner()
        schedule = tuple(self._command_schedule_provider(operation_kind))
        if not schedule or any(type(item) is not WorkerCommandSpec for item in schedule):
            self._coordinator.release_shared(permit, self._permit_owner)
            raise ValueError("trusted command schedule must be finite, positive and closed")
        self._lifecycle_serial += 1
        self._sequence = next_sequence
        lease = _issue_operation_lease()
        self._leases[lease] = _LeaseRecord(
            handle, operation, operation_kind, owner, LeaseState.ACQUIRED,
            stored.identity.path, permit, context, parameters, admitted.binding,
            self._registry_epoch, self._coordinator.admission_epoch,
            receiving_task=receiver,
            lifecycle_serial=self._lifecycle_serial,
            continuation_owner=_issue(RuntimeContinuationOwner),
            containment_owner=_issue(WorkerContainmentOwner),
            command_schedule=schedule,
        )
        for name in stored.identity.path:
            self._resources[name].charges.add(operation)
        return lease

    def run_plan_step(self, lease: ReadOperationLease, exact_step: PlanStep,
                      owner: object, consumer: ClosedPlanConsumer) -> ClosedStepProduct:
        if not self._consumers.owns(consumer):
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "consumer is not owned by this issuer")
        record = self._lease_record(lease)
        if record.owner is record.continuation_owner:
            if (
                owner is not record.receiving_task
                or not record.receiver_live
                or not self._authority.is_current_task(record.receiving_task)
            ):
                raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "runtime continuation is not current")
        elif record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        rank = validate_step_after(record.kind, record.last_step_rank, exact_step)
        if exact_step is PlanStep.PUBLICATION:
            if record.kind in {OperationKind.SNAPSHOT_REGISTRATION, OperationKind.REFRESH}:
                raise ContractRefusal(
                    RefusalCode.REFETCH_REQUIRED,
                    "live visibility requires its exact registration or buffer barrier",
                )
            if record.state is not LeaseState.RUNNING or record.last_step_rank < 0:
                raise ContractRefusal(RefusalCode.LEASE_INVALID, "publication requires prior running work")
            if record.kind is OperationKind.ITERATOR_HANDOFF and (
                len(record.command_ledger) != len(record.command_schedule)
                or not record.command_ledger
                or record.command_ledger[-1].state is not WorkerCommandState.RESULT_ACCEPTED
            ):
                raise ContractRefusal(
                    RefusalCode.LEASE_INVALID,
                    "delivery publication requires every scheduled command result",
                )
        elif record.state not in {LeaseState.ACQUIRED, LeaseState.RUNNING}:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "work is not legal in this lease state")
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        if exact_step is PlanStep.PUBLICATION and record.kind is not OperationKind.ITERATOR_HANDOFF:
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
        record.completed_steps.add(exact_step)
        if exact_step is PlanStep.PUBLICATION:
            if record.kind is OperationKind.ITERATOR_HANDOFF:
                record.publication_candidate = _issue(DeliveryPublicationCandidate)
                record.state = LeaseState.PUBLICATION_READY
            else:
                record.publication_committed = True
                self.publications += 1
                self._terminalize(record, LeaseState.SUCCEEDED)
        return product

    def issue_derived_command(
        self, lease: ReadOperationLease, owner: object, step: PlanStep,
        ordinal: int, label: str,
    ) -> ClosedDerivedCommand:
        record = self._live_lease(lease, owner)
        if record.kind not in {OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT,
                               OperationKind.SNAPSHOT_REGISTRATION, OperationKind.REFRESH}:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "operation cannot own derived fetches")
        if record.state is not LeaseState.RUNNING or PlanStep.LOWER not in record.completed_steps:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "parent work has not reached derived fetches")
        if type(ordinal) is not int or ordinal < 1 or ordinal in record.issued_derived_ordinals:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "derived command ordinal is unavailable")
        self._validate_barriers(record)
        command = self._consumers.issue_command(record.operation, step, ordinal, label)
        record.issued_derived_ordinals.add(ordinal)
        return command

    def run_derived_command(
        self, lease: ReadOperationLease, owner: object,
        command: ClosedDerivedCommand, ordinal: int,
    ) -> ClosedStepProduct:
        record = self._live_lease(lease, owner)
        if record.state is not LeaseState.RUNNING or ordinal != record.next_derived_ordinal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "derived command is out of parent order")
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        product = self._consumers.consume_command(
            command, admission.plan, record.parameters, record.operation, ordinal,
        )
        record.next_derived_ordinal += 1
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

    def dispatch_worker(self, lease: ReadOperationLease) -> WorkerCommandAuthorization:
        """Dispatch the next issuer-owned schedule slot for the receiving task."""

        record = self._lease_record(lease)
        if not record.receiver_live or not self._authority.is_current_task(record.receiving_task):
            raise ContractRefusal(RefusalCode.CONTEXT_OWNER_MISMATCH, "only the bound receiver may dispatch")
        next_index = len(record.command_ledger)
        if record.active_command_serial is not None or next_index >= len(record.command_schedule):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "no command slot is dispatchable")
        if next_index:
            prior = record.command_ledger[-1]
            if prior.state is not WorkerCommandState.RESULT_ACCEPTED:
                raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "prior command result is not accepted")
        elif record.state not in {LeaseState.ACQUIRED, LeaseState.RUNNING}:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "first command is not dispatchable")
        self._validate_barriers(record)
        serial = next_index + 1
        worker = self._assigned_worker_provider(serial)
        if worker is None:
            raise ValueError("trusted assigned-worker provider returned no worker")
        command = _issue(ClosedWorkerCommand)
        authorization = _issue(WorkerCommandAuthorization)
        spec = record.command_schedule[next_index]
        command_record = _WorkerCommandRecord(
            serial, command, authorization, worker, spec,
            remaining_ordinals=set(spec.required_effects + spec.optional_effects),
        )
        record.command_ledger.append(command_record)
        record.active_command_serial = serial
        record.command = command
        record.worker = worker
        record.authorization = authorization
        record.owner = command
        record.state = LeaseState.QUEUED
        return authorization

    def dequeue_worker(
        self, lease: ReadOperationLease, authorization: WorkerCommandAuthorization,
    ) -> None:
        record, command = self._command_for(authorization, lease=lease)
        if command.state is not WorkerCommandState.QUEUED or record.state is not LeaseState.QUEUED:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command is not queued")
        if not self._authority.is_current_task(command.worker):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "assigned worker is not current")
        self._validate_worker_barriers(record, command)
        command.state = WorkerCommandState.RUNNING_IDLE
        record.owner = command.worker
        record.state = LeaseState.RUNNING

    def run_worker_effect(
        self, authorization: WorkerCommandAuthorization, ordinal: int,
    ) -> object:
        record, command = self._command_for(authorization)
        if command.state is not WorkerCommandState.RUNNING_IDLE or command.active_reservation is not None:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command cannot reserve another effect")
        if type(ordinal) is not int or ordinal not in command.remaining_ordinals:
            code = (
                RefusalCode.EFFECT_ORDINAL_REUSED
                if ordinal in command.completed_ordinals
                else RefusalCode.WORKER_AUTHORITY_INVALID
            )
            raise ContractRefusal(code, "effect ordinal is unavailable")
        self._validate_worker_barriers(record, command)
        reservation = _issue(WorkerEffectReservation)
        command.remaining_ordinals.remove(ordinal)
        command.active_reservation = reservation
        command.reservation_ordinal = ordinal
        command.state = WorkerCommandState.EFFECT_IN_FLIGHT
        try:
            action = self._effect_provider(command.spec.label, ordinal)
            if not callable(action):
                raise ValueError("trusted effect provider did not return a fixed action")
            result = action()
        except BaseException:
            if command.exit_receipt is None:
                self._contain_command(record, command, WorkerExitKind.FAILURE, EffectKnowledge.BEGUN_UNCERTAIN)
            elif len(command.cleanup_diagnostics) < command.spec.cleanup_steps + 1:
                failure = _issue(ClosedWorkerFailure)
                self._failures[failure] = authorization
                command.cleanup_diagnostics.append(failure)
            raise
        if command.state is not WorkerCommandState.EFFECT_IN_FLIGHT or command.active_reservation is not reservation:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "effect lost its active reservation")
        command.active_reservation = None
        command.reservation_ordinal = None
        command.completed_ordinals.add(ordinal)
        command.effect_knowledge = EffectKnowledge.RETURNED
        command.state = WorkerCommandState.RUNNING_IDLE
        return freeze_value(result)

    def setup_reference_worker_result(
        self, authorization: WorkerCommandAuthorization, value: object,
    ) -> ClosedWorkerResult:
        self._command_for(authorization)
        result = _issue(ClosedWorkerResult)
        self._results[result] = (authorization, freeze_value(value))
        return result

    def setup_reference_worker_failure(
        self, authorization: WorkerCommandAuthorization,
    ) -> ClosedWorkerFailure:
        self._command_for(authorization)
        failure = _issue(ClosedWorkerFailure)
        self._failures[failure] = authorization
        return failure

    def worker_exit_success(
        self, authorization: WorkerCommandAuthorization, result: ClosedWorkerResult,
    ) -> WorkerExitReceipt:
        record, command = self._command_for(authorization)
        expected = self._results.get(result)
        if type(result) is not ClosedWorkerResult or expected is None or expected[0] is not authorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "closed result does not belong to command")
        if command.exit_receipt is not None:
            if command.exit_kind is WorkerExitKind.SUCCESS and command.result is result:
                return command.exit_receipt
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "worker exit already committed")
        if command.state is not WorkerCommandState.RUNNING_IDLE or command.active_reservation is not None:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command is not idle for success")
        if not set(command.spec.required_effects).issubset(command.completed_ordinals):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "required effects are incomplete")
        if command.next_cleanup_step <= command.spec.cleanup_steps:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "trusted cleanup schedule is incomplete")
        self._validate_worker_barriers(record, command)
        command.remaining_ordinals.clear()
        receipt = _issue(WorkerExitReceipt)
        command.exit_serial += 1
        command.exit_receipt = receipt
        command.exit_kind = WorkerExitKind.SUCCESS
        command.result = result
        command.result_value = expected[1]
        command.state = WorkerCommandState.SUCCESS_PENDING
        record.owner = self._permit_owner
        return receipt

    def worker_exit_failure(
        self, authorization: WorkerCommandAuthorization, failure: ClosedWorkerFailure,
    ) -> WorkerExitReceipt:
        record, command = self._command_for(authorization)
        if self._failures.get(failure) is not authorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "closed failure does not belong to command")
        if command.exit_receipt is not None:
            if command.exit_kind is WorkerExitKind.FAILURE:
                return command.exit_receipt
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "worker exit already committed")
        if command.state not in {WorkerCommandState.RUNNING_IDLE, WorkerCommandState.EFFECT_IN_FLIGHT}:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "worker failure is not legal")
        self._validate_worker_barriers(record, command)
        knowledge = (
            EffectKnowledge.NOT_BEGUN
            if not command.completed_ordinals and command.active_reservation is None
            else EffectKnowledge.BEGUN_UNCERTAIN
            if command.active_reservation is not None
            else EffectKnowledge.RETURNED
        )
        return self._contain_command(record, command, WorkerExitKind.FAILURE, knowledge, failure)

    def run_worker_cleanup(
        self, authorization: WorkerCommandAuthorization, step: int,
    ) -> None:
        record, command = self._command_for(authorization)
        if (
            type(step) is not int
            or step != command.next_cleanup_step
            or step > command.spec.cleanup_steps
        ):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "cleanup step is unavailable")
        try:
            if not self._authority.is_current_task(command.worker):
                raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "assigned worker is not current")
            action = self._cleanup_provider(command.spec.label, step)
            if not callable(action):
                raise ValueError("trusted cleanup provider did not return a fixed action")
            action()
        except BaseException:
            failure = _issue(ClosedWorkerFailure)
            self._failures[failure] = authorization
            if command.exit_receipt is None:
                self._contain_command(record, command, WorkerExitKind.FAILURE, command.effect_knowledge, failure)
            elif len(command.cleanup_diagnostics) < command.spec.cleanup_steps:
                command.cleanup_diagnostics.append(failure)
            raise
        finally:
            command.next_cleanup_step += 1

    def request_worker_cancel(self, lease: ReadOperationLease) -> WorkerExitReceipt | None:
        record = self._lease_record(lease)
        if not self._authority.is_current_task(record.receiving_task) or not record.receiver_live:
            raise ContractRefusal(RefusalCode.CONTEXT_OWNER_MISMATCH, "only the live receiver may cancel")
        return self._cancel_or_remove(record, WorkerExitKind.CANCEL)

    def setup_reference_receiving_task_done(
        self, lease: ReadOperationLease,
    ) -> ReceivingTaskLifecycleObservation:
        record = self._lease_record(lease)
        observation = _issue(ReceivingTaskLifecycleObservation)
        self._observations[observation] = _LifecycleObservationRecord(
            lease, record.receiving_task, record.lifecycle_serial,
        )
        return observation

    def observe_receiving_task_done(
        self, observation: ReceivingTaskLifecycleObservation,
    ) -> WorkerExitReceipt | None:
        if type(observation) is not ReceivingTaskLifecycleObservation:
            raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "exact lifecycle observation required")
        observed = self._observations.get(observation)
        if observed is None:
            raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "lifecycle observation is unavailable")
        record = self._lease_record(observed.lease, allow_terminal=True)
        exact = observed.task is record.receiving_task and observed.serial == record.lifecycle_serial
        if not exact:
            raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "lifecycle observation binding mismatch")
        if observation in self._consumed_observations:
            return self._active_exit(record)
        self._consumed_observations.add(observation)
        if record.state.terminal:
            return None
        record.receiver_live = False
        self._authority.invalidate(record.context)
        return self._cancel_or_remove(record, WorkerExitKind.CANCEL)

    def setup_reference_worker_stop(
        self, authorization: WorkerCommandAuthorization,
    ) -> WorkerStopReceipt:
        record, command = self._command_for(authorization)
        if command.state not in {WorkerCommandState.SUCCESS_PENDING, WorkerCommandState.CONTAINED}:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command has not exited")
        receipt = _issue(WorkerStopReceipt)
        self._stops[receipt] = _StopRecord(self._lease_for(record), command.serial)
        return receipt

    def observe_worker_stopped(self, receipt: WorkerStopReceipt) -> None:
        if type(receipt) is not WorkerStopReceipt:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "exact stop receipt required")
        stopped = self._stops.get(receipt)
        if stopped is None:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "stop receipt is unavailable")
        record = self._lease_record(stopped.lease, allow_terminal=True)
        command = record.command_ledger[stopped.command_serial - 1]
        if command.stop_receipt is not None:
            if command.stop_receipt is receipt:
                return
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting stop receipt")
        command.stop_receipt = receipt
        command.active_reservation = None
        command.reservation_ordinal = None
        if command.state is WorkerCommandState.SUCCESS_PENDING:
            command.state = WorkerCommandState.QUIESCENT_SUCCESS
        elif command.state is WorkerCommandState.CONTAINED:
            command.state = WorkerCommandState.QUIESCENT_CONTAINED
        else:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command is not stoppable")

    def accept_worker_result(self, receipt: WorkerExitReceipt) -> object:
        record, command = self._command_for_exit(receipt)
        if command.state is WorkerCommandState.RESULT_ACCEPTED:
            return command.result_value
        if command.state is not WorkerCommandState.QUIESCENT_SUCCESS:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "worker result is not quiescent success")
        if not record.receiver_live or not self._authority.is_current_task(record.receiving_task):
            raise ContractRefusal(RefusalCode.CONTEXT_OWNER_MISMATCH, "result receiver is not current")
        self._validate_barriers(record)
        command.state = WorkerCommandState.RESULT_ACCEPTED
        record.active_command_serial = None
        record.owner = record.continuation_owner
        record.state = LeaseState.RUNNING
        return command.result_value

    @property
    def worker_issuer(self) -> WorkerAuthorizationIssuer:
        return self._workers

    def complete(self, lease: ReadOperationLease, owner: object, outcome: LeaseState) -> None:
        if type(lease) is not ReadOperationLease or type(outcome) is not LeaseState or not outcome.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "terminal exact lease outcome is required")
        record = self._leases.get(lease)
        if record is None or record.owner is not owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "lease owner mismatch")
        if record.kind is OperationKind.ITERATOR_HANDOFF:
            raise ContractRefusal(
                RefusalCode.OPERATION_OUTCOME_CONFLICT,
                "iterator handoff requires specialized delivery settlement",
            )
        if record.completion is not None:
            if record.completion is not outcome:
                raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting completion")
            return
        if record.active_command_serial is not None or record.command_ledger:
            raise ContractRefusal(
                RefusalCode.OPERATION_OUTCOME_CONFLICT,
                "worker-backed operation requires worker-exit terminalization",
            )
        allowed = {
            LeaseState.ACQUIRED: frozenset({LeaseState.REFUSED, LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.QUEUED: frozenset({LeaseState.CANCELLED_CONFIRMED}),
            LeaseState.RUNNING: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED}),
            LeaseState.PUBLISHING: frozenset({LeaseState.SUCCEEDED}),
            LeaseState.CONTAINED: frozenset({LeaseState.SUCCEEDED, LeaseState.REFUSED, LeaseState.CANCELLED_CONFIRMED}),
        }
        if record.state.terminal or outcome not in allowed[record.state]:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "illegal terminal lease transition")
        self._terminalize(record, outcome)

    def complete_contained(self, lease: ReadOperationLease) -> None:
        record = self._lease_record(lease)
        if record.kind is OperationKind.ITERATOR_HANDOFF:
            raise ContractRefusal(
                RefusalCode.OPERATION_OUTCOME_CONFLICT,
                "delivery containment requires specialized retirement",
            )
        if record.owner is not record.containment_owner:
            raise ContractRefusal(RefusalCode.LEASE_OWNER_CONFLICT, "containment owner is not current")
        if record.active_command_serial is not None:
            command = record.command_ledger[record.active_command_serial - 1]
            if command.state is not WorkerCommandState.QUIESCENT_CONTAINED:
                raise ContractRefusal(RefusalCode.LEASE_INVALID, "contained command is not quiescent")
        self._terminalize(record, LeaseState.REFUSED)

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

    def worker_command_state(
        self, authorization: WorkerCommandAuthorization,
    ) -> WorkerCommandState:
        return self._command_for(authorization)[1].state

    def worker_effect_knowledge(
        self, authorization: WorkerCommandAuthorization,
    ) -> EffectKnowledge:
        return self._command_for(authorization)[1].effect_knowledge

    def worker_ordinals(
        self, authorization: WorkerCommandAuthorization,
    ) -> tuple[frozenset[int], frozenset[int]]:
        command = self._command_for(authorization)[1]
        return frozenset(command.remaining_ordinals), frozenset(command.completed_ordinals)

    def worker_exit_facts(
        self, authorization: WorkerCommandAuthorization,
    ) -> tuple[WorkerExitKind | None, WorkerExitReceipt | None, int, bool]:
        command = self._command_for(authorization)[1]
        return (
            command.exit_kind,
            command.exit_receipt,
            len(command.cleanup_diagnostics),
            command.cancel_diagnostic,
        )

    def setup_reference_initial_snapshot(
        self, lease: ReadOperationLease, owner: object,
        subscription: ResourceIdentity, queue: ResourceIdentity,
        rows: object, watermark: RevisionCursor,
    ) -> InitialSnapshotCandidate:
        record = self._live_lease(lease, owner)
        if (
            record.kind is not OperationKind.SNAPSHOT_REGISTRATION
            or record.state is not LeaseState.RUNNING
            or not {PlanStep.FETCH, PlanStep.SNAPSHOT_WATERMARK}.issubset(record.completed_steps)
        ):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "initial snapshot evidence is incomplete")
        subscription_record = self._resource(subscription)
        queue_record = self._resource(queue)
        self._validate_queue_target(record, subscription_record, queue_record)
        if (
            type(watermark) is not RevisionCursor
            or watermark.scope != record.binding.scope
            or watermark.generation != record.binding.generation
        ):
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "initial watermark does not match the lease")
        self._validate_barriers(record)
        frozen_rows = freeze_rows(rows)
        self._validate_queue_target(record, subscription_record, queue_record)
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        return self._snapshots.setup_initial(
            lease, record.operation, record.admission, record.parameters,
            record.binding, admission.plan.root.canonical_digest,
            subscription_record.identity, queue_record.identity, frozen_rows, watermark,
        )

    def register_subscription(
        self, lease: ReadOperationLease, owner: object,
        candidate: InitialSnapshotCandidate,
    ) -> InitialSnapshotPublication:
        record = self._live_lease(lease, owner)
        if record.kind is not OperationKind.SNAPSHOT_REGISTRATION or record.registration_committed:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "registration is not legal for this lease")
        if (
            record.state is not LeaseState.RUNNING
            or not {PlanStep.REGISTRATION, PlanStep.ASSEMBLY}.issubset(record.completed_steps)
        ):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "registration step is incomplete")
        try:
            snapshot = self._snapshots.initial_record(candidate)
        except (TypeError, ValueError) as error:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, str(error)) from error
        subscription_record = self._resource(snapshot.subscription)
        queue_record = self._resource(snapshot.queue)
        self._validate_queue_target(record, subscription_record, queue_record)
        exact = (
            snapshot.lease is lease and snapshot.operation == record.operation
            and snapshot.admission is record.admission
            and snapshot.parameters == record.parameters.values
            and snapshot.binding == record.binding
            and snapshot.plan_digest == self._admissions[record.admission].plan.root.canonical_digest
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "initial snapshot candidate mismatch")
        publication_rank = validate_step_after(
            record.kind, record.last_step_rank, PlanStep.PUBLICATION,
        )
        self._validate_barriers(record)
        admission = self._admissions[record.admission]
        registration = self._buffers.register(
            record.admission, admission.plan.root.canonical_digest, record.parameters,
            record.binding, subscription_record.identity, queue_record.identity,
            snapshot.watermark,
            admission.plan.live_bound,
        )
        record.state = LeaseState.PUBLISHING
        record.publication_committed = True
        record.registration_committed = True
        record.last_step_rank = publication_rank
        self.publications += 1
        self._snapshots.consume_initial(snapshot)
        return InitialSnapshotPublication(snapshot.rows, snapshot.watermark, registration)

    def setup_reference_refresh_candidate(
        self, lease: ReadOperationLease, owner: object,
        registration: SubscriptionRegistration, previous: RevisionCursor,
        triggered_by: RevisionCursor, observed_through: RevisionCursor,
        rows: object, durable_advancement: str,
    ) -> RefreshSnapshotCandidate:
        record = self._live_lease(lease, owner)
        if (
            record.kind is not OperationKind.REFRESH
            or record.state is not LeaseState.RUNNING
            or not {PlanStep.FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE}.issubset(
                record.completed_steps
            )
        ):
            raise ContractRefusal(
                RefusalCode.LEASE_INVALID,
                "refresh candidate requires prior running work",
            )
        self._validate_barriers(record)
        subscription = self._resources[record.resources[-1]].identity
        if subscription.kind is not ResourceKind.SUBSCRIPTION:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh resource is not a subscription")
        plan_digest, queue, produced_through = self._buffers.candidate_lineage(
            registration, record.admission, record.parameters, record.binding, subscription,
        )
        if previous != produced_through:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh is not the next produced range")
        queue_record = self._resource(queue)
        subscription_record = self._resource(subscription)
        self._validate_queue_target(record, subscription_record, queue_record)
        frozen_rows = freeze_rows(rows)
        self._validate_queue_target(record, subscription_record, queue_record)
        self._validate_barriers(record)
        candidate = self._snapshots.setup_refresh(
            lease, record.operation, record.admission, record.parameters,
            record.binding, plan_digest, registration, subscription, queue,
            previous, triggered_by, observed_through, frozen_rows, durable_advancement,
        )
        record.refresh_candidate = candidate
        record.refresh_snapshot = self._snapshots.take_refresh(candidate)
        return candidate

    def publish_refresh_buffer(
        self, lease: ReadOperationLease, owner: object,
        candidate: RefreshSnapshotCandidate,
    ) -> BufferedDelivery | RefreshCommitRefused:
        current = next(
            (
                record for record in self._leases.values()
                if record.refresh_candidate is candidate and not record.state.terminal
            ),
            None,
        )
        if current is not None and (
            type(lease) is not ReadOperationLease
            or self._leases.get(lease) is not current
            or current.owner is not owner
        ):
            return RefreshCommitRefused()
        record = self._live_lease(lease, owner)
        result = self._commit_refresh_record(record, candidate)
        if type(result) is not BufferedDelivery:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh is neutral and has no envelope")
        return result

    def commit_refresh(
        self, candidate: RefreshSnapshotCandidate,
    ) -> BufferedDelivery | NeutralRefreshReceipt | RefetchRequired | RefreshContainmentPending | RefreshRecordUnavailable:
        replay = self._buffers.replay_neutral(candidate)
        if replay is not None:
            return replay
        for record in self._leases.values():
            if record.refresh_candidate is candidate and not record.state.terminal:
                return self._commit_refresh_record(record, candidate)
        return RefreshRecordUnavailable()

    def replay_neutral(
        self, receipt: NeutralRefreshReceipt,
    ) -> NeutralRefreshReceipt | RefreshRecordUnavailable:
        replay = self._buffers.replay_neutral(receipt)
        return replay if replay is not None else RefreshRecordUnavailable()

    def _commit_refresh_record(
        self, record: _LeaseRecord, candidate: RefreshSnapshotCandidate,
    ) -> BufferedDelivery | NeutralRefreshReceipt | RefetchRequired | RefreshContainmentPending:
        if record.kind is not OperationKind.REFRESH or record.state.terminal:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "refresh publication requires prior running work")
        if type(candidate) is not RefreshSnapshotCandidate or record.refresh_candidate is not candidate:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh candidate is not current")
        if record.state is LeaseState.CONTAINED:
            return self._dispose_refresh(record)
        if record.state is not LeaseState.RUNNING:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "refresh publication requires prior running work")
        snapshot = record.refresh_snapshot
        if snapshot is None:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh candidate is unavailable")
        lease = self._lease_for(record)
        queue_record = self._resource(snapshot.queue)
        subscription_record = self._resource(snapshot.subscription)
        try:
            self._validate_queue_target(record, subscription_record, queue_record)
            self._validate_barriers(record)
        except ContractRefusal:
            return self._dispose_refresh(record)
        exact = (
            snapshot.lease is lease and snapshot.operation == record.operation
            and snapshot.admission is record.admission
            and snapshot.parameters == record.parameters.values
            and snapshot.binding == record.binding
            and snapshot.plan_digest == self._admissions[record.admission].plan.root.canonical_digest
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh snapshot candidate mismatch")
        if self._buffers.registration_state(snapshot.registration) is not RegistrationState.ACTIVE:
            return self._dispose_refresh(record)
        if not snapshot.rows:
            receipt = issue_neutral_receipt()
            self._buffers.commit_neutral(
                snapshot.registration,
                candidate,
                receipt,
                snapshot.previous,
                snapshot.observed_through,
            )
            record.refresh_candidate = None
            record.refresh_snapshot = None
            record.neutral_receipt = receipt
            self._terminalize(record, LeaseState.SUCCEEDED)
            return receipt
        if not self._buffers.changed_capacity_available(snapshot.registration):
            for permit in self._buffers.retire_registration(snapshot.registration):
                self._coordinator.release_buffer(permit, self._permit_owner)
            self._retire_active_delivery(self._buffers.active_envelope(snapshot.registration))
            return self._dispose_refresh(record)
        envelope = self._buffers.create_candidate(
            snapshot.registration, record.operation, record.admission,
            record.parameters, record.binding, snapshot.subscription,
            snapshot.previous, snapshot.triggered_by, snapshot.observed_through,
            snapshot.rows, snapshot.durable_advancement,
        )
        buffered = self._buffers.validate_publish(
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
        self._buffers.commit_publish(buffered, permit)
        record.refresh_candidate = None
        record.refresh_snapshot = None
        record.publication_committed = True
        record.last_step_rank = publication_rank
        self.publications += 1
        self._terminalize(record, LeaseState.SUCCEEDED)
        return envelope

    def settle_contained_refresh(
        self,
        lease: ReadOperationLease,
        stop_receipt: WorkerStopReceipt,
    ) -> RefetchRequired:
        record = self._lease_record(lease, allow_terminal=True)
        if record.refresh_refetch is not None:
            if record.refresh_containment_stop is stop_receipt:
                return record.refresh_refetch
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "refresh stop conflicts")
        if (
            record.kind is not OperationKind.REFRESH
            or record.state is not LeaseState.CONTAINED
            or record.active_command_serial is None
        ):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "refresh is not awaiting worker stop")
        command = record.command_ledger[record.active_command_serial - 1]
        if command.stop_receipt is not stop_receipt or command.state is not WorkerCommandState.QUIESCENT_CONTAINED:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "refresh worker stop is not exact")
        record.refresh_containment_stop = stop_receipt
        record.refresh_refetch = RefetchRequired(
            record.binding.scope, RefusalCode.REFETCH_REQUIRED, None,
        )
        self._terminalize(record, LeaseState.REFUSED)
        return record.refresh_refetch

    def _dispose_refresh(
        self, record: _LeaseRecord,
    ) -> RefetchRequired | RefreshContainmentPending:
        record.refresh_candidate = None
        record.refresh_snapshot = None
        if record.active_command_serial is not None:
            command = record.command_ledger[record.active_command_serial - 1]
            if command.state is WorkerCommandState.QUEUED:
                command.remaining_ordinals.clear()
                command.state = WorkerCommandState.QUEUE_REMOVED
                record.active_command_serial = None
            elif command.state not in {
                WorkerCommandState.QUEUE_REMOVED,
                WorkerCommandState.QUIESCENT_CONTAINED,
                WorkerCommandState.RESULT_ACCEPTED,
            }:
                self._cancel_or_remove(record, WorkerExitKind.CANCEL)
            if command.state not in {
                WorkerCommandState.QUEUE_REMOVED,
                WorkerCommandState.QUIESCENT_CONTAINED,
                WorkerCommandState.RESULT_ACCEPTED,
            }:
                record.state = LeaseState.CONTAINED
                record.owner = record.containment_owner
                return RefreshContainmentPending()
        record.state = LeaseState.CONTAINED
        record.owner = record.containment_owner
        record.refresh_refetch = RefetchRequired(
            record.binding.scope, RefusalCode.REFETCH_REQUIRED, None,
        )
        self._terminalize(record, LeaseState.REFUSED)
        return record.refresh_refetch

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
        self._authority.validate(context, scope=admitted.binding.scope, capability=Capability.LIVE)
        for name in queue_record.identity.path:
            if self._resources[name].state is not LocalResourceState.LOCAL_OPEN:
                raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, name)
        next_sequence = self._sequence + 1
        operation = OperationIdentity(
            self._runtime_identity, next_sequence, admitted.binding.scope,
            admitted.binding.generation,
        )
        buffer_permit = self._buffers.queued_permit(buffered)
        permit = self._coordinator.exchange_buffer_for_shared(
            buffer_permit, self._permit_owner, envelope, operation, self._permit_owner,
        )
        self._buffers.commit_dequeue(buffered)
        receiver = self._authority.capture_task_owner()
        schedule = tuple(self._command_schedule_provider(OperationKind.ITERATOR_HANDOFF))
        if not schedule or any(type(item) is not WorkerCommandSpec for item in schedule):
            raise ValueError("trusted handoff command schedule must be finite and positive")
        self._lifecycle_serial += 1
        self._sequence = next_sequence
        lease = _issue_operation_lease()
        self._leases[lease] = _LeaseRecord(
            handle, operation, OperationKind.ITERATOR_HANDOFF, owner,
            LeaseState.ACQUIRED, queue_record.identity.path, permit, context,
            parameters, admitted.binding, self._registry_epoch,
            self._coordinator.admission_epoch,
            handoff_envelope=envelope,
            receiving_task=receiver,
            lifecycle_serial=self._lifecycle_serial,
            continuation_owner=_issue(RuntimeContinuationOwner),
            containment_owner=_issue(WorkerContainmentOwner),
            command_schedule=schedule,
        )
        for name in queue_record.identity.path:
            self._resources[name].charges.add(operation)
        return lease

    def delivery_publication_candidate(
        self, lease: ReadOperationLease,
    ) -> DeliveryPublicationCandidate:
        record = self._lease_record(lease)
        if record.kind is not OperationKind.ITERATOR_HANDOFF or record.state is not LeaseState.PUBLICATION_READY:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery is not publication-ready")
        if record.publication_candidate is None:
            raise ValueError("publication-ready delivery has no candidate")
        return record.publication_candidate

    def prepare_delivery_publication(
        self, lease: ReadOperationLease,
    ) -> DeliveryPublicationCandidate:
        record = self._lease_record(lease)
        exact = (
            record.kind is OperationKind.ITERATOR_HANDOFF
            and record.owner is record.continuation_owner
            and record.receiver_live
            and self._authority.is_current_task(record.receiving_task)
            and len(record.command_ledger) == len(record.command_schedule)
            and bool(record.command_ledger)
            and record.command_ledger[-1].state is WorkerCommandState.RESULT_ACCEPTED
        )
        if not exact:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery continuation is not ready")
        self._validate_barriers(record)
        candidate = _issue(DeliveryPublicationCandidate)
        record.publication_candidate = candidate
        record.state = LeaseState.PUBLICATION_READY
        record.completed_steps.update({PlanStep.VALIDATE, PlanStep.PUBLICATION})
        record.last_step_rank = validate_step_after(
            record.kind,
            validate_step_after(record.kind, -1, PlanStep.VALIDATE),
            PlanStep.PUBLICATION,
        )
        return candidate

    def settle_delivery_success(
        self,
        lease: ReadOperationLease,
        candidate: DeliveryPublicationCandidate,
    ) -> DeliverySettlementReceipt:
        record = self._lease_record(lease, allow_terminal=True)
        if record.delivery_settlement is not None:
            if candidate is record.publication_candidate:
                return record.delivery_settlement
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "delivery settlement conflict")
        if record.delivery_retirement is not None:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "delivery is retiring")
        exact = (
            record.kind is OperationKind.ITERATOR_HANDOFF
            and record.state is LeaseState.PUBLICATION_READY
            and type(candidate) is DeliveryPublicationCandidate
            and candidate is record.publication_candidate
            and record.receiver_live
            and self._authority.is_current_task(record.receiving_task)
            and record.owner is record.continuation_owner
            and record.handoff_envelope is not None
        )
        if not exact:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "delivery candidate is not current")
        self._validate_barriers(record)
        settlement = _issue(DeliverySettlementReceipt)
        self._buffers.complete_handoff(record.handoff_envelope)
        record.publication_committed = True
        record.delivery_settlement = settlement
        self.publications += 1
        self._terminalize(record, LeaseState.SUCCEEDED)
        return settlement

    def begin_delivery_non_success(
        self,
        lease: ReadOperationLease,
        cause: WorkerExitReceipt | ReceivingTaskLifecycleObservation | ClosedWorkerFailure,
    ) -> DeliveryRetirementReceipt:
        record = self._lease_record(lease, allow_terminal=True)
        if record.delivery_retirement is not None:
            return record.delivery_retirement
        if record.delivery_settlement is not None or record.state.terminal:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "delivery already settled")
        known_cause = False
        if type(cause) is WorkerExitReceipt:
            try:
                known_cause = self._command_for_exit(cause)[0] is record
            except ContractRefusal:
                known_cause = False
        elif type(cause) is ReceivingTaskLifecycleObservation:
            observed = self._observations.get(cause)
            known_cause = observed is not None and observed.lease is lease
        elif type(cause) is ClosedWorkerFailure:
            source = self._failures.get(cause)
            if type(source) is WorkerCommandAuthorization:
                known_cause = self._command_for(source)[0] is record
            elif type(source) is ReadOperationLease:
                known_cause = source is lease
        if not known_cause or record.handoff_envelope is None:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "delivery cause is not exact")
        retirement = _issue(DeliveryRetirementReceipt)
        queued_permits = self._buffers.begin_handoff_retirement(record.handoff_envelope)
        for permit in queued_permits:
            self._coordinator.release_buffer(permit, self._permit_owner)
        record.delivery_retirement = retirement
        record.state = LeaseState.RETIRING_HANDOFF
        record.owner = record.containment_owner
        if record.active_command_serial is not None:
            command = record.command_ledger[record.active_command_serial - 1]
            if command.state in {
                WorkerCommandState.QUEUED,
                WorkerCommandState.RUNNING_IDLE,
                WorkerCommandState.EFFECT_IN_FLIGHT,
                WorkerCommandState.SUCCESS_PENDING,
                WorkerCommandState.QUIESCENT_SUCCESS,
            }:
                self._cancel_or_remove(record, WorkerExitKind.CANCEL)
                record.state = LeaseState.RETIRING_HANDOFF
        return retirement

    def setup_reference_delivery_stop(
        self, retirement: DeliveryRetirementReceipt,
    ) -> DeliveryStopObservation:
        record = self._delivery_record(retirement)
        if record.active_command_serial is not None:
            command = record.command_ledger[record.active_command_serial - 1]
            if command.state not in {
                WorkerCommandState.QUEUE_REMOVED,
                WorkerCommandState.QUIESCENT_CONTAINED,
                WorkerCommandState.RESULT_ACCEPTED,
            }:
                raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery worker has not stopped")
        observation = _issue(DeliveryStopObservation)
        self._delivery_stops[observation] = _DeliveryStopRecord(
            self._lease_for(record), retirement,
        )
        return observation

    def observe_delivery_stopped(
        self,
        retirement: DeliveryRetirementReceipt,
        observation: DeliveryStopObservation,
    ) -> None:
        record = self._delivery_record(retirement)
        stopped = self._delivery_stops.get(observation)
        if (
            type(observation) is not DeliveryStopObservation
            or stopped is None
            or stopped.retirement is not retirement
            or stopped.lease is not self._lease_for(record)
        ):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery stop observation mismatch")
        if record.delivery_stop is not None and record.delivery_stop is not observation:
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting delivery stop")
        record.delivery_stop = observation

    def settle_delivery_non_success(
        self,
        lease: ReadOperationLease,
        retirement: DeliveryRetirementReceipt,
    ) -> RefetchRequired:
        record = self._lease_record(lease, allow_terminal=True)
        if record.completion is LeaseState.REFUSED and record.delivery_retirement is retirement:
            return RefetchRequired(record.binding.scope, RefusalCode.REFETCH_REQUIRED, None)
        if (
            record.delivery_retirement is not retirement
            or record.delivery_stop is None
            or record.handoff_envelope is None
            or record.state is not LeaseState.RETIRING_HANDOFF
        ):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery retirement is not quiescent")
        self._buffers.settle_handoff_retirement(record.handoff_envelope)
        self._terminalize(record, LeaseState.REFUSED)
        return RefetchRequired(record.binding.scope, RefusalCode.REFETCH_REQUIRED, None)

    def delivery_cursors(
        self, registration: SubscriptionRegistration,
    ) -> tuple[RevisionCursor, RevisionCursor]:
        return self._buffers.registration_cursors(registration)

    def delivery_retirement(
        self, lease: ReadOperationLease,
    ) -> DeliveryRetirementReceipt:
        record = self._lease_record(lease)
        if record.delivery_retirement is None:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery is not retiring")
        return record.delivery_retirement

    def neutral_lineage_sizes(
        self, registration: SubscriptionRegistration,
    ) -> tuple[int, int, int, int]:
        return self._buffers.lineage_sizes(registration)

    def current_refresh_candidates(self) -> int:
        return sum(
            1 for record in self._leases.values()
            if not record.state.terminal and record.refresh_candidate is not None
        )

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
            if self._membership is not None:
                self._coordinator.request_leave(self._membership)
        if hard:
            for lease, record in self._leases.items():
                if not record.state.terminal and any(name in selected for name in record.resources):
                    if (
                        record.kind is OperationKind.ITERATOR_HANDOFF
                        and record.delivery_retirement is not None
                    ):
                        continue
                    if record.authorization is not None:
                        self._workers.revoke(record.authorization)
                    else:
                        record.state = LeaseState.CONTAINED
                        record.owner = record.containment_owner or record.owner
                    if record.kind is OperationKind.ITERATOR_HANDOFF and record.delivery_retirement is None:
                        cause = self._active_exit(record)
                        if cause is None and record.authorization is not None:
                            failure = _issue(ClosedWorkerFailure)
                            self._failures[failure] = record.authorization
                            self.begin_delivery_non_success(lease, failure)
                        elif cause is None:
                            failure = _issue(ClosedWorkerFailure)
                            self._failures[failure] = lease
                            self.begin_delivery_non_success(lease, failure)
                        elif cause is not None:
                            self.begin_delivery_non_success(lease, cause)

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
            if self._membership is None:
                self._coordinator.close_unjoined(self._open_record)
            else:
                state = self._coordinator.membership_state(self._membership)
                if state is ParticipantState.LEAVE_PENDING:
                    self._coordinator.finalize_leave(self._membership)
        return CloseOutcome(CloseKnowledge.CLOSED)

    def migration_queue_barrier(self, attempt: MigrationAttempt) -> int:
        if self._migration_participant is None:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "runtime is not joined")
        self._coordinator.barrier_allowed(attempt, self._migration_participant)
        for queue in self._queues:
            self._queues[queue] = QueueState.MIGRATION_INVALIDATING
        discarded = self._invalidate_buffers(set(self._resources))
        for lease, record in tuple(self._leases.items()):
            if (
                record.kind is OperationKind.ITERATOR_HANDOFF
                and not record.state.terminal
                and record.delivery_retirement is None
            ):
                cause = self._active_exit(record)
                if cause is None:
                    failure = _issue(ClosedWorkerFailure)
                    self._failures[failure] = lease
                    self.begin_delivery_non_success(lease, failure)
                else:
                    self.begin_delivery_non_success(lease, cause)
        self._coordinator.acknowledge_barrier(attempt, self._migration_participant)
        self._barrier_attempt = attempt
        return discarded

    def reopen_queues_no_effect(self, attempt: MigrationAttempt) -> None:
        if (
            attempt is not self._barrier_attempt
            or not self._coordinator.no_effect_reopen_complete(attempt)
        ):
            raise ValueError("old generation has not reopened")
        for queue, state in tuple(self._queues.items()):
            if state is QueueState.MIGRATION_INVALIDATING:
                self._queues[queue] = QueueState.OPEN
        self._barrier_attempt = None

    def revoke_generation(self) -> None:
        for admission in self._admissions.values():
            admission.state = AdmissionState.REVOKED
        self._registry_epoch += 1
        for record in self._leases.values():
            if not record.state.terminal:
                record.state = LeaseState.CONTAINED
                if record.containment_owner is not None:
                    record.owner = record.containment_owner
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
                if record.containment_owner is not None:
                    record.owner = record.containment_owner
            raise

    def _lease_for(self, target: _LeaseRecord) -> ReadOperationLease:
        for lease, record in self._leases.items():
            if record is target:
                return lease
        raise ValueError("lease record is not registered")

    def _lease_record(
        self, lease: object, *, allow_terminal: bool = False,
    ) -> _LeaseRecord:
        if type(lease) is not ReadOperationLease:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact lease instance is required")
        record = self._leases.get(lease)
        if record is None or (record.state.terminal and not allow_terminal):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "lease is not live")
        return record

    def _command_for(
        self,
        authorization: WorkerCommandAuthorization,
        *,
        lease: ReadOperationLease | None = None,
    ) -> tuple[_LeaseRecord, _WorkerCommandRecord]:
        if type(authorization) is not WorkerCommandAuthorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "exact authorization required")
        candidates = (
            ((lease, self._leases.get(lease)),)
            if lease is not None
            else tuple(self._leases.items())
        )
        for _, record in candidates:
            if record is None:
                continue
            for command in record.command_ledger:
                if command.authorization is authorization:
                    return record, command
        raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "authorization is unavailable")

    def _command_for_exit(
        self, receipt: WorkerExitReceipt,
    ) -> tuple[_LeaseRecord, _WorkerCommandRecord]:
        if type(receipt) is not WorkerExitReceipt:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "exact exit receipt required")
        for record in self._leases.values():
            for command in record.command_ledger:
                if command.exit_receipt is receipt:
                    return record, command
        raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "exit receipt is unavailable")

    def _active_exit(self, record: _LeaseRecord) -> WorkerExitReceipt | None:
        if record.active_command_serial is None:
            return None
        return record.command_ledger[record.active_command_serial - 1].exit_receipt

    def _delivery_record(
        self, retirement: DeliveryRetirementReceipt,
    ) -> _LeaseRecord:
        if type(retirement) is not DeliveryRetirementReceipt:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact delivery retirement required")
        for record in self._leases.values():
            if record.delivery_retirement is retirement:
                return record
        raise ContractRefusal(RefusalCode.LEASE_INVALID, "delivery retirement is unavailable")

    def _worker_context_owner(self, authorization: WorkerCommandAuthorization) -> object:
        return self._command_for(authorization)[0].receiving_task

    def _validate_worker_barriers(
        self, record: _LeaseRecord, command: _WorkerCommandRecord,
    ) -> None:
        if record.active_command_serial != command.serial or record.authorization is not command.authorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "command is not active")
        if not self._authority.is_current_task(command.worker):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "assigned worker is not current")
        try:
            self._validate_barriers(record, worker_source=True)
        except ContractRefusal:
            if command.state in {WorkerCommandState.RUNNING_IDLE, WorkerCommandState.EFFECT_IN_FLIGHT}:
                knowledge = (
                    EffectKnowledge.BEGUN_UNCERTAIN
                    if command.active_reservation is not None
                    else command.effect_knowledge
                )
                self._contain_command(record, command, WorkerExitKind.CANCEL, knowledge)
            raise

    def _contain_command(
        self,
        record: _LeaseRecord,
        command: _WorkerCommandRecord,
        kind: WorkerExitKind,
        knowledge: EffectKnowledge,
        failure: ClosedWorkerFailure | None = None,
    ) -> WorkerExitReceipt:
        if command.exit_receipt is not None:
            if command.exit_kind is kind:
                return command.exit_receipt
            if kind is WorkerExitKind.CANCEL and not command.cancel_diagnostic:
                command.cancel_diagnostic = True
                return command.exit_receipt
            raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "worker exit already committed")
        receipt = _issue(WorkerExitReceipt)
        command.exit_serial += 1
        command.exit_receipt = receipt
        command.exit_kind = kind
        command.effect_knowledge = knowledge
        command.failure = failure
        command.remaining_ordinals.clear()
        command.state = WorkerCommandState.CONTAINED
        record.state = LeaseState.CONTAINED
        record.owner = record.containment_owner
        return receipt

    def _cancel_or_remove(
        self, record: _LeaseRecord, kind: WorkerExitKind,
    ) -> WorkerExitReceipt | None:
        if record.active_command_serial is None:
            if record.state.terminal:
                return None
            record.state = LeaseState.CONTAINED
            record.owner = record.containment_owner
            return None
        command = record.command_ledger[record.active_command_serial - 1]
        if command.state is WorkerCommandState.QUEUED:
            command.remaining_ordinals.clear()
            command.state = WorkerCommandState.QUEUE_REMOVED
            record.active_command_serial = None
            record.state = LeaseState.CONTAINED
            record.owner = record.containment_owner
            if record.kind is OperationKind.ITERATOR_HANDOFF:
                return None
            outcome = LeaseState.CANCELLED_CONFIRMED if command.serial == 1 else LeaseState.REFUSED
            self._terminalize(record, outcome)
            return None
        if command.state in {WorkerCommandState.RUNNING_IDLE, WorkerCommandState.EFFECT_IN_FLIGHT}:
            knowledge = (
                EffectKnowledge.BEGUN_UNCERTAIN
                if command.active_reservation is not None
                else command.effect_knowledge
            )
            return self._contain_command(record, command, kind, knowledge)
        if command.state is WorkerCommandState.SUCCESS_PENDING:
            command.state = WorkerCommandState.CONTAINED
            record.state = LeaseState.CONTAINED
            record.owner = record.containment_owner
            return command.exit_receipt
        if command.state is WorkerCommandState.QUIESCENT_SUCCESS:
            command.state = WorkerCommandState.QUIESCENT_CONTAINED
            record.state = LeaseState.CONTAINED
            record.owner = record.containment_owner
            return command.exit_receipt
        if command.state is WorkerCommandState.RESULT_ACCEPTED:
            record.active_command_serial = None
            record.state = LeaseState.CONTAINED
            record.owner = record.containment_owner
            return command.exit_receipt
        return command.exit_receipt

    def _revoke_worker_authorization(self, authorization: WorkerCommandAuthorization) -> None:
        try:
            record, command = self._command_for(authorization)
        except ContractRefusal:
            return
        if command.state in {
            WorkerCommandState.QUEUED,
            WorkerCommandState.RUNNING_IDLE,
            WorkerCommandState.EFFECT_IN_FLIGHT,
            WorkerCommandState.SUCCESS_PENDING,
            WorkerCommandState.QUIESCENT_SUCCESS,
        }:
            self._cancel_or_remove(record, WorkerExitKind.CANCEL)
            if record.delivery_retirement is not None and not record.state.terminal:
                record.state = LeaseState.RETIRING_HANDOFF

    def _terminalize(self, record: _LeaseRecord, outcome: LeaseState) -> None:
        if record.completion is not None:
            if record.completion is not outcome:
                raise ContractRefusal(RefusalCode.OPERATION_OUTCOME_CONFLICT, "conflicting completion")
            return
        record.state = outcome
        record.completion = outcome
        self._coordinator.release_shared(record.permit, self._permit_owner)
        for name in record.resources:
            self._resources[name].charges.remove(record.operation)

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

    def _validate_queue_target(
        self, lease: _LeaseRecord, subscription: _ResourceRecord,
        queue: _ResourceRecord,
    ) -> None:
        exact = (
            lease.resources[-1] == subscription.identity.name
            and subscription.identity.kind is ResourceKind.SUBSCRIPTION
            and queue.identity.kind is ResourceKind.DELIVERY_QUEUE
            and queue.identity.ancestors[-1] == subscription.identity.name
            and subscription.state is LocalResourceState.LOCAL_OPEN
            and queue.state is LocalResourceState.LOCAL_OPEN
            and self._queues.get(queue.identity.name) is QueueState.OPEN
        )
        if not exact:
            if not lease.state.terminal:
                lease.state = LeaseState.CONTAINED
                if lease.containment_owner is not None:
                    lease.owner = lease.containment_owner
            raise ContractRefusal(RefusalCode.LOCAL_RESOURCE_FENCED, "delivery queue publication barrier")

    def _descendant_names(self, root: str) -> set[str]:
        return {name for name, record in self._resources.items() if root in record.identity.path}

    def _invalidate_buffers(self, selected: set[str]) -> int:
        permits, active = self._buffers.retire_for_resources(selected)
        for permit in permits:
            self._coordinator.release_buffer(permit, self._permit_owner)
        for envelope in active:
            self._retire_active_delivery(envelope)
        return len(permits)

    def _retire_active_delivery(self, envelope: BufferedDelivery | None) -> None:
        if envelope is None:
            return
        for lease, record in self._leases.items():
            if (
                record.handoff_envelope is envelope
                and not record.state.terminal
                and record.delivery_retirement is None
            ):
                cause = self._active_exit(record)
                if cause is None:
                    failure = _issue(ClosedWorkerFailure)
                    self._failures[failure] = lease
                    self.begin_delivery_non_success(lease, failure)
                else:
                    self.begin_delivery_non_success(lease, cause)
                return
