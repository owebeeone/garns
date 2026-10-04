"""Private subscription registration and buffered-provenance reference state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .admission import AdmittedReadHandle, OperationIdentity
from .lifetime import BufferedDelivery, BufferedDeliveryPermit, ResourceIdentity, ResourceKind
from .semantic import BindingIdentity
from .values import ContractRefusal, FrozenMap, ParameterValues, RefusalCode, RevisionCursor


_REGISTRATION_SEAL = object()


class SubscriptionRegistration:
    """Empty exact identity for issuer-private subscription provenance."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not SubscriptionRegistration or seal is not _REGISTRATION_SEAL:
            raise TypeError("subscription registrations are issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _REGISTRATION_SEAL:
            raise TypeError("subscription registrations are issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("SubscriptionRegistration is immutable")

    def __repr__(self) -> str:
        return "SubscriptionRegistration(<opaque identity>)"

    def __copy__(self):
        raise TypeError("SubscriptionRegistration cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("SubscriptionRegistration cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("SubscriptionRegistration cannot be serialized")


class BufferState(str, Enum):
    CANDIDATE = "candidate"
    QUEUED = "queued"
    DEQUEUED = "dequeued"
    INVALID = "invalid"


@dataclass(slots=True)
class _RegistrationRecord:
    admission: AdmittedReadHandle
    plan_digest: str
    parameters: FrozenMap
    binding: BindingIdentity
    subscription: ResourceIdentity
    queue: ResourceIdentity
    produced_through: RevisionCursor
    delivered_through: RevisionCursor
    next_sequence: int = 1
    queued: list[int] = field(default_factory=list)
    active: int | None = None
    last_delivered_advancement: str | None = None
    retired: bool = False

@dataclass(slots=True)
class _BufferRecord:
    envelope: BufferedDelivery
    registration: SubscriptionRegistration
    admission: AdmittedReadHandle
    plan_digest: str
    parameters: FrozenMap
    binding: BindingIdentity
    producer: OperationIdentity
    queue: ResourceIdentity
    sequence: int
    state: BufferState = BufferState.CANDIDATE
    permit: BufferedDeliveryPermit | None = None


class ReferenceBufferRegistry:
    """Exact-identity candidate/queue state; no live engine is implemented."""

    def __init__(self) -> None:
        self._registrations: dict[SubscriptionRegistration, _RegistrationRecord] = {}
        self._buffers: dict[int, _BufferRecord] = {}

    def register(
        self,
        admission: AdmittedReadHandle,
        plan_digest: str,
        parameters: ParameterValues,
        binding: BindingIdentity,
        subscription: ResourceIdentity,
        queue: ResourceIdentity,
        cursor: RevisionCursor,
    ) -> SubscriptionRegistration:
        if type(admission) is not AdmittedReadHandle:
            raise TypeError("registration admission must be exact")
        if type(parameters) is not ParameterValues or type(binding) is not BindingIdentity:
            raise TypeError("registration parameters and binding must be exact")
        if subscription.kind is not ResourceKind.SUBSCRIPTION or queue.kind is not ResourceKind.DELIVERY_QUEUE:
            raise ValueError("registration requires subscription and queue resources")
        if queue.ancestors[-1] != subscription.name:
            raise ValueError("registration queue must descend from its subscription")
        if type(cursor) is not RevisionCursor or cursor.scope != binding.scope or cursor.generation != binding.generation:
            raise ValueError("registration cursor must match binding scope/generation")
        if type(plan_digest) is not str or not plan_digest:
            raise ValueError("registration plan digest is required")
        registration = SubscriptionRegistration(_REGISTRATION_SEAL)
        self._registrations[registration] = _RegistrationRecord(
            admission,
            plan_digest,
            parameters.values,
            binding,
            subscription,
            queue,
            cursor,
            cursor,
        )
        return registration

    def create_candidate(
        self,
        registration: SubscriptionRegistration,
        producer: OperationIdentity,
        admission: AdmittedReadHandle,
        parameters: ParameterValues,
        binding: BindingIdentity,
        subscription: ResourceIdentity,
        previous: RevisionCursor,
        triggered_by: RevisionCursor,
        observed_through: RevisionCursor,
        rows: object,
        durable_advancement: str,
    ) -> BufferedDelivery:
        record = self._registration(registration)
        if record.retired:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "registration is retired")
        exact = (
            type(producer) is OperationIdentity
            and producer.deployment == binding.scope
            and producer.generation == binding.generation
            and admission is record.admission
            and type(parameters) is ParameterValues
            and parameters.values == record.parameters
            and binding == record.binding
            and subscription == record.subscription
            and previous == record.produced_through
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "refresh candidate provenance mismatch")
        envelope = BufferedDelivery(
            binding.scope,
            binding.generation,
            admission,
            record.plan_digest,
            previous,
            triggered_by,
            observed_through,
            rows,
            durable_advancement,
        )
        self._buffers[id(envelope)] = _BufferRecord(
            envelope,
            registration,
            admission,
            record.plan_digest,
            record.parameters,
            binding,
            producer,
            record.queue,
            record.next_sequence,
        )
        return envelope

    def validate_publish(
        self,
        envelope: BufferedDelivery,
        producer: OperationIdentity,
        admission: AdmittedReadHandle,
        parameters: ParameterValues,
        binding: BindingIdentity,
        queue: ResourceIdentity,
    ) -> _BufferRecord:
        record = self._buffer(envelope)
        registration = self._registration(record.registration)
        exact = (
            record.state is BufferState.CANDIDATE
            and record.producer == producer
            and record.admission is admission
            and record.parameters == parameters.values
            and record.binding == binding
            and record.queue == queue
            and envelope.admission_identity is admission
            and envelope.plan_digest == registration.plan_digest
            and envelope.previous == registration.produced_through
            and envelope.generation == binding.generation
            and envelope.deployment == binding.scope
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "buffer publication provenance mismatch")
        return record

    def commit_publish(self, record: _BufferRecord, permit: BufferedDeliveryPermit) -> None:
        if record.state is not BufferState.CANDIDATE or type(permit) is not BufferedDeliveryPermit:
            raise ValueError("buffer publication commit is not legal")
        registration = self._registration(record.registration)
        record.permit = permit
        record.state = BufferState.QUEUED
        registration.queued.append(id(record.envelope))
        registration.produced_through = record.envelope.observed_through
        registration.next_sequence += 1

    def validate_dequeue(
        self,
        envelope: BufferedDelivery,
        admission: AdmittedReadHandle,
        registration: SubscriptionRegistration,
        binding: BindingIdentity,
        queue: ResourceIdentity,
    ) -> _BufferRecord:
        record = self._buffer(envelope)
        registered = self._registration(registration)
        exact = (
            record.state is BufferState.QUEUED
            and record.registration is registration
            and record.admission is admission
            and record.binding == binding
            and record.queue == queue
            and registered.admission is admission
            and registered.plan_digest == envelope.plan_digest
            and registered.parameters == record.parameters
            and registered.binding == binding
            and registered.queue == queue
            and registered.active is None
            and bool(registered.queued)
            and registered.queued[0] == id(envelope)
            and registered.delivered_through == envelope.previous
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "buffer dequeue provenance mismatch")
        return record

    def handoff_parameters(self, record: _BufferRecord) -> ParameterValues:
        if record.state is not BufferState.QUEUED:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "buffer is not queued")
        return ParameterValues(record.parameters)

    def commit_dequeue(self, record: _BufferRecord) -> BufferedDeliveryPermit:
        if record.state is not BufferState.QUEUED or record.permit is None:
            raise ValueError("buffer is not queued")
        permit = record.permit
        record.permit = None
        record.state = BufferState.DEQUEUED
        registration = self._registration(record.registration)
        if registration.active is not None or not registration.queued or registration.queued[0] != id(record.envelope):
            raise ValueError("buffer is not the exact FIFO head")
        registration.active = id(record.envelope)
        return permit

    def complete_handoff(self, envelope: BufferedDelivery) -> None:
        record = self._buffer(envelope)
        registration = self._registration(record.registration)
        if record.state is not BufferState.DEQUEUED or registration.active != id(envelope):
            raise ValueError("buffer handoff completion is not current")
        if not registration.queued or registration.queued[0] != id(envelope):
            raise ValueError("buffer handoff lost FIFO ownership")
        registration.queued.pop(0)
        registration.active = None
        registration.delivered_through = envelope.observed_through
        registration.last_delivered_advancement = envelope.durable_advancement

    def queued_for_resources(self, selected: set[str]) -> tuple[_BufferRecord, ...]:
        return tuple(
            record for record in self._buffers.values()
            if record.state is BufferState.QUEUED and any(name in selected for name in record.queue.path)
        )

    def invalidate(self, record: _BufferRecord) -> BufferedDeliveryPermit:
        if record.state is not BufferState.QUEUED or record.permit is None:
            raise ValueError("only a queued buffer can be invalidated")
        permit = record.permit
        record.permit = None
        record.state = BufferState.INVALID
        registration = self._registration(record.registration)
        if id(record.envelope) in registration.queued:
            registration.queued.remove(id(record.envelope))
        registration.retired = True
        return permit

    def candidate_lineage(
        self, registration: SubscriptionRegistration, admission: AdmittedReadHandle,
        parameters: ParameterValues, binding: BindingIdentity,
        subscription: ResourceIdentity,
    ) -> tuple[str, ResourceIdentity, RevisionCursor]:
        record = self._registration(registration)
        exact = (
            not record.retired and record.admission is admission
            and record.parameters == parameters.values and record.binding == binding
            and record.subscription == subscription
        )
        if not exact:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "registration lineage mismatch")
        return record.plan_digest, record.queue, record.produced_through

    def queued_permit(self, record: _BufferRecord) -> BufferedDeliveryPermit:
        if record.state is not BufferState.QUEUED or record.permit is None:
            raise ValueError("buffer has no queued permit")
        return record.permit

    def queued_count(self, selected: set[str]) -> int:
        return len(self.queued_for_resources(selected))

    def _registration(self, registration: SubscriptionRegistration) -> _RegistrationRecord:
        if type(registration) is not SubscriptionRegistration:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "exact registration is required")
        record = self._registrations.get(registration)
        if record is None:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "registration belongs to another issuer")
        return record

    def _buffer(self, envelope: BufferedDelivery) -> _BufferRecord:
        if type(envelope) is not BufferedDelivery:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "exact buffered envelope is required")
        record = self._buffers.get(id(envelope))
        if record is None or record.envelope is not envelope:
            raise ContractRefusal(RefusalCode.REFETCH_REQUIRED, "envelope was not issued by this registry")
        return record
