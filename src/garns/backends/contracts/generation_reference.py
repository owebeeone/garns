"""Deterministic generation and activation reference coordinator.

This is executable contract evidence, not a thread-safe, durable, database,
operator, or cross-process implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .admission import OperationIdentity
from .lifetime import (
    ActivationEvidence, ActivationState, BufferedDelivery,
    BufferedDeliveryPermit, DeploymentGenerationState, GenerationPermit,
    _issue_buffer_permit, _issue_generation_permit,
)
from .migration_reference import (
    AttemptPhase, LifetimeOpenRecord, MigrationAttempt, MigrationAttemptRecord,
    MigrationBarrierAcknowledgement, MigrationNoEffectProof,
    MigrationNoEffectRecord, MigrationParticipant, MigrationRequestIdentity,
    ParticipantMembership, ParticipantState, issue_acknowledgement,
    issue_attempt, issue_lifetime_open, issue_no_effect_proof,
    issue_participant, issue_request,
)
from .recovery import (
    ActivationNoEffectRecoveryProof, ActivationUnusedWithdrawalProof,
    MigrationRecoveryKind, MigrationRecoveryProof,
)
from .semantic import BindingIdentity
from .values import ContractRefusal, QualifiedDeployment, RefusalCode


@dataclass(frozen=True, slots=True)
class _PermitRecord:
    operation: OperationIdentity
    owner: object
    admission_epoch: int
    binding: BindingIdentity


@dataclass(frozen=True, slots=True)
class _BufferPermitRecord:
    envelope: BufferedDelivery
    owner: object
    admission_epoch: int
    binding: BindingIdentity


@dataclass(slots=True)
class _OpenRecord:
    runtime_identity: object
    state: ParticipantState = ParticipantState.UNJOINED
    membership: ParticipantMembership | None = None
    join_serial: int = 0


@dataclass(slots=True)
class _MembershipRecord:
    open_record: LifetimeOpenRecord
    runtime_identity: object
    join_serial: int
    state: ParticipantState = ParticipantState.JOINED


class ReferenceGenerationCoordinator:
    """Single-process exact-identity reference for shared generation state."""

    def __init__(self, deployment: QualifiedDeployment, binding: BindingIdentity) -> None:
        if binding.scope != deployment:
            raise ValueError("coordinator binding must match deployment")
        self.deployment = deployment
        self.binding = binding
        self.state = DeploymentGenerationState.CURRENT
        self.activation = ActivationState.UNACTIVATED
        self.protocol_epoch: int | None = None
        self.admission_epoch = 1
        self._highest_protocol_epoch = 0
        self._attempted_protocol_epoch: int | None = None
        self._attempted_binding: BindingIdentity | None = None
        self._activation_fence_digest: str | None = None
        self._permits: dict[GenerationPermit, _PermitRecord] = {}
        self._buffers: dict[BufferedDeliveryPermit, _BufferPermitRecord] = {}
        self._old_binding: BindingIdentity | None = None
        self._requested_binding: BindingIdentity | None = None
        self._migration_effect_begun = False
        self._opens: dict[LifetimeOpenRecord, _OpenRecord] = {}
        self._memberships: dict[ParticipantMembership, _MembershipRecord] = {}
        self._participants: set[ParticipantMembership] = set()
        self._join_serial = 0
        self._attempts: dict[MigrationAttempt, MigrationAttemptRecord] = {}
        self._current_attempt: MigrationAttempt | None = None
        self._no_effect_proofs: dict[MigrationNoEffectProof, MigrationNoEffectRecord] = {}

    def prepare_lifetime_open(self, runtime_identity: object) -> LifetimeOpenRecord:
        if runtime_identity is None:
            raise ValueError("runtime identity is required")
        record = issue_lifetime_open()
        self._opens[record] = _OpenRecord(runtime_identity)
        return record

    def join_runtime(self, open_record: LifetimeOpenRecord) -> ParticipantMembership:
        if type(open_record) is not LifetimeOpenRecord:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "exact lifetime open record required")
        opened = self._opens.get(open_record)
        if opened is None or opened.state is not ParticipantState.UNJOINED:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime open is unavailable")
        if self.activation is not ActivationState.ACTIVE or self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "runtime cannot join before active open")
        if self._current_attempt is not None:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "participant topology is frozen")
        membership = issue_participant()
        self._join_serial += 1
        opened.state = ParticipantState.JOINED
        opened.membership = membership
        opened.join_serial = self._join_serial
        self._memberships[membership] = _MembershipRecord(
            open_record, opened.runtime_identity, self._join_serial,
        )
        self._participants.add(membership)
        return membership

    def close_unjoined(self, open_record: LifetimeOpenRecord) -> None:
        if type(open_record) is not LifetimeOpenRecord:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "exact lifetime open record required")
        opened = self._opens.get(open_record)
        if opened is None or opened.state is not ParticipantState.UNJOINED:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "unjoined open is unavailable")
        opened.state = ParticipantState.LEFT

    def request_leave(self, membership: ParticipantMembership) -> ParticipantState:
        record = self._membership_record(membership)
        if record.state is ParticipantState.LEAVE_PENDING:
            return record.state
        record.state = ParticipantState.LEAVE_PENDING
        return record.state

    def finalize_leave(self, membership: ParticipantMembership) -> ParticipantState:
        record = self._membership_record(membership)
        if record.state is not ParticipantState.LEAVE_PENDING:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "membership is not pending leave")
        if self._current_attempt is not None or self._runtime_has_obligations(record.runtime_identity):
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "membership retains obligations")
        self._finish_leave(membership, record)
        return ParticipantState.LEFT

    def membership_state(self, membership: ParticipantMembership) -> ParticipantState:
        if type(membership) is not ParticipantMembership:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact membership required")
        record = self._memberships.get(membership)
        if record is None:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "membership belongs to another coordinator")
        return record.state

    def begin_activation(self, requested_epoch: int) -> None:
        if self.activation is not ActivationState.UNACTIVATED:
            raise ValueError("only an unactivated deployment can begin activation")
        if type(requested_epoch) is not int or requested_epoch <= self._highest_protocol_epoch:
            raise ValueError("activation epoch must be positive and never reused")
        self._attempted_protocol_epoch = requested_epoch
        self._attempted_binding = self.binding
        self._highest_protocol_epoch = requested_epoch
        self.activation = ActivationState.ACTIVATING

    def finish_activation(self, evidence: ActivationEvidence) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        self._validate_activation_evidence(evidence)
        self.protocol_epoch = evidence.protocol_epoch
        self._activation_fence_digest = evidence.physical_fence_digest
        self.activation = ActivationState.ACTIVE_UNUSED

    def refuse_activation_no_effect(self, proof: ActivationNoEffectRecoveryProof) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        self._validate_no_effect_proof(proof)
        self._return_unactivated()

    def mark_activation_indeterminate(self) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        self.activation = ActivationState.ACTIVATION_INDETERMINATE

    def recover_activation(self, proof: ActivationEvidence | ActivationNoEffectRecoveryProof) -> None:
        if self.activation is not ActivationState.ACTIVATION_INDETERMINATE:
            raise ValueError("activation is not indeterminate")
        if type(proof) is ActivationEvidence:
            self._validate_activation_evidence(proof)
            self.protocol_epoch = proof.protocol_epoch
            self._activation_fence_digest = proof.physical_fence_digest
            self.activation = ActivationState.ACTIVE_UNUSED
            return
        if type(proof) is ActivationNoEffectRecoveryProof:
            self._validate_no_effect_proof(proof)
            self._return_unactivated()
            return
        raise TypeError("activation recovery requires exact proof inputs")

    def first_lifetime_open(self, protocol: str, epoch: int) -> None:
        if protocol != "plan_admission_lifetime_v1":
            raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "missing lifetime capability")
        if type(epoch) is not int or self.activation is not ActivationState.ACTIVE_UNUSED or epoch != self.protocol_epoch:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "active unused epoch mismatch")
        self.activation = ActivationState.ACTIVE

    def withdraw_unused(self, proof: ActivationUnusedWithdrawalProof) -> None:
        if self.activation is not ActivationState.ACTIVE_UNUSED:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "activation is not unused")
        if type(proof) is not ActivationUnusedWithdrawalProof:
            raise TypeError("unused withdrawal requires exact proof inputs")
        exact = (
            proof.deployment == self.deployment
            and proof.binding == self._attempted_binding
            and proof.protocol_epoch == self.protocol_epoch
            and proof.physical_fence_digest == self._activation_fence_digest
        )
        if not exact:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "unused withdrawal proof mismatch")
        self._return_unactivated()

    def refuse_retirement_or_reset(self) -> None:
        raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "active protocol has no reset or retirement edge")

    def acquire_shared(self, operation: OperationIdentity, owner: object) -> GenerationPermit:
        if self.activation is not ActivationState.ACTIVE:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime protocol is not active")
        if self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "generation is not admitting work")
        if type(operation) is not OperationIdentity or owner is None:
            raise TypeError("shared permit requires exact operation and owner identities")
        if operation.deployment != self.deployment or operation.generation != self.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "operation generation mismatch")
        if any(record.operation == operation for record in self._permits.values()):
            raise ValueError("operation already owns a shared permit")
        permit = _issue_generation_permit()
        self._permits[permit] = _PermitRecord(operation, owner, self.admission_epoch, self.binding)
        return permit

    def permit_live(self, permit: GenerationPermit, owner: object, operation: OperationIdentity,
                    binding: BindingIdentity, admission_epoch: int) -> bool:
        if type(permit) is not GenerationPermit:
            return False
        record = self._permits.get(permit)
        if record is None:
            return False
        exact = (
            record.owner is owner and record.operation == operation
            and record.binding == binding and record.admission_epoch == admission_epoch
        )
        if not exact or self.activation is not ActivationState.ACTIVE:
            return False
        if self.state is DeploymentGenerationState.CURRENT:
            return binding == self.binding and admission_epoch == self.admission_epoch
        return self.state is DeploymentGenerationState.DRAINING_OLD and binding == self._old_binding

    def release_shared(self, permit: GenerationPermit, owner: object) -> None:
        if type(permit) is not GenerationPermit:
            raise ValueError("generation permit is not exact")
        record = self._permits.get(permit)
        if record is None or record.owner is not owner:
            raise ValueError("generation permit is not owned and live")
        del self._permits[permit]

    def add_buffer(self, envelope: BufferedDelivery, owner: object) -> BufferedDeliveryPermit:
        if self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "buffer enqueue is fenced")
        if type(envelope) is not BufferedDelivery or owner is None:
            raise TypeError("buffer permit requires exact envelope and owner identities")
        if envelope.deployment != self.deployment or envelope.generation != self.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "buffer generation mismatch")
        if any(record.envelope is envelope for record in self._buffers.values()):
            raise ValueError("buffer permit already exists")
        permit = _issue_buffer_permit()
        self._buffers[permit] = _BufferPermitRecord(envelope, owner, self.admission_epoch, self.binding)
        return permit

    def release_buffer(self, permit: BufferedDeliveryPermit, owner: object) -> None:
        if type(permit) is not BufferedDeliveryPermit:
            raise ValueError("buffer permit is not exact")
        record = self._buffers.get(permit)
        if record is None or record.owner is not owner:
            raise ValueError("buffer permit is not owned and live")
        del self._buffers[permit]

    def exchange_buffer_for_shared(
        self, buffer_permit: BufferedDeliveryPermit, buffer_owner: object,
        envelope: BufferedDelivery, operation: OperationIdentity, shared_owner: object,
    ) -> GenerationPermit:
        if type(buffer_permit) is not BufferedDeliveryPermit:
            raise ValueError("buffer permit is not exact")
        buffered = self._buffers.get(buffer_permit)
        if buffered is None or buffered.owner is not buffer_owner or buffered.envelope is not envelope:
            raise ValueError("buffer permit is not owned by the exact queued record")
        if self.activation is not ActivationState.ACTIVE or self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "buffer handoff is fenced")
        if type(operation) is not OperationIdentity or shared_owner is None:
            raise TypeError("buffer exchange requires exact operation and owner")
        if operation.deployment != self.deployment or operation.generation != self.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "handoff operation generation mismatch")
        permit = _issue_generation_permit()
        del self._buffers[buffer_permit]
        self._permits[permit] = _PermitRecord(operation, shared_owner, self.admission_epoch, self.binding)
        return permit

    def register_participant(self) -> MigrationParticipant:
        raise ContractRefusal(
            RefusalCode.ACTIVATION_REQUIRED,
            "participant membership is issued only by activation-bracketed join_runtime",
        )

    def begin_drain(self, expected: BindingIdentity) -> MigrationAttempt:
        if self.activation is not ActivationState.ACTIVE:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime protocol is not active")
        if type(expected) is not BindingIdentity or self.state is not DeploymentGenerationState.CURRENT or expected != self.binding:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "migration expected binding mismatch")
        self._old_binding = self.binding
        self._requested_binding = None
        self.state = DeploymentGenerationState.DRAINING_OLD
        self._migration_effect_begun = False
        attempt = issue_attempt()
        phase_request = issue_request()
        self._attempts[attempt] = MigrationAttemptRecord(
            self.deployment, self.binding, self.protocol_epoch,
            self.admission_epoch, frozenset(self._participants),
            AttemptPhase.DRAINING_OLD, 1, phase_request,
        )
        self._current_attempt = attempt
        return attempt

    def barrier_allowed(self, attempt: MigrationAttempt, participant: MigrationParticipant) -> None:
        record = self._attempt_record(attempt)
        if (
            self.state is not DeploymentGenerationState.DRAINING_OLD
            or participant not in record.required
            or participant in record.acknowledged
        ):
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "migration barrier is not legal")

    def acknowledge_barrier(
        self, attempt: MigrationAttempt, participant: MigrationParticipant,
    ) -> MigrationBarrierAcknowledgement:
        self.barrier_allowed(attempt, participant)
        acknowledgement = issue_acknowledgement()
        self._attempts[attempt].acknowledged[participant] = acknowledgement
        return acknowledgement

    def observe_request_released(
        self,
        attempt: MigrationAttempt,
        phase_request: MigrationRequestIdentity,
    ) -> MigrationNoEffectProof:
        record = self._attempt_record(attempt)
        if self.state not in {DeploymentGenerationState.DRAINING_OLD, DeploymentGenerationState.MIGRATING}:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "migration is not pre-effect")
        if record.effect_begun or self._migration_effect_begun:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "migration effect may have begun")
        if type(phase_request) is not MigrationRequestIdentity or phase_request is not record.phase_request:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "released request is not the exact current phase request")
        proof = issue_no_effect_proof()
        self._no_effect_proofs[proof] = MigrationNoEffectRecord(
            attempt, record.deployment, record.old_binding, record.protocol_epoch,
            record.admission_epoch, record.phase, record.phase_serial,
            record.phase_request, record.requested_binding,
        )
        return proof

    def reopen_no_effect(self, proof: MigrationNoEffectProof) -> None:
        if self.state not in {DeploymentGenerationState.DRAINING_OLD, DeploymentGenerationState.MIGRATING}:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "old generation cannot reopen")
        if type(proof) is not MigrationNoEffectProof:
            raise TypeError("pre-effect reopen requires an exact proof")
        proof_record = self._no_effect_proofs.get(proof)
        attempt = self._current_attempt
        if proof_record is None or attempt is None:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "no-effect proof is not current")
        record = self._attempt_record(attempt)
        exact = (
            proof_record.attempt is attempt
            and proof_record.deployment == self.deployment
            and proof_record.old_binding == self._old_binding == self.binding
            and proof_record.protocol_epoch == self.protocol_epoch
            and proof_record.admission_epoch == record.admission_epoch
            and proof_record.phase is record.phase
            and proof_record.phase_serial == record.phase_serial
            and proof_record.phase_request is record.phase_request
            and proof_record.requested_binding == record.requested_binding
            and not record.effect_begun and not self._migration_effect_begun
            and self._all_barriers_acknowledged(record)
        )
        if not exact:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "no-effect proof mismatch")
        self.admission_epoch += 1
        self.state = DeploymentGenerationState.CURRENT
        self._old_binding = None
        self._requested_binding = None
        record.closed = True
        del self._no_effect_proofs[proof]
        self._current_attempt = None
        self._finish_pending_leaves()

    def begin_migration(self, attempt: MigrationAttempt, requested: BindingIdentity) -> None:
        record = self._attempt_record(attempt)
        if (
            self.state is not DeploymentGenerationState.DRAINING_OLD
            or self.count() != 0
            or not self._all_barriers_acknowledged(record)
        ):
            raise ContractRefusal(RefusalCode.DEADLINE_EXCEEDED, "old generation is not quiescent")
        if type(requested) is not BindingIdentity or requested.scope != self.deployment:
            raise TypeError("migration requires an exact requested binding")
        if self._old_binding != self.binding or requested.generation != self.binding.generation + 1:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "requested generation must be the exact successor")
        self._requested_binding = requested
        record.requested_binding = requested
        record.phase = AttemptPhase.MIGRATING_PRE_EFFECT
        record.phase_serial += 1
        record.phase_request = issue_request()
        self.state = DeploymentGenerationState.MIGRATING

    def begin_migration_effect(self) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or self._requested_binding is None:
            raise ValueError("migration is not active")
        self._migration_effect_begun = True
        record = self._attempts[self._current_attempt]
        record.effect_begun = True
        record.phase = AttemptPhase.EFFECT_BEGUN
        record.phase_serial += 1
        record.phase_request = issue_request()

    def publish_generation(self, requested: BindingIdentity) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or not self._migration_effect_begun:
            raise ValueError("migration effect/publication order is invalid")
        if type(requested) is not BindingIdentity or requested != self._requested_binding:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "requested generation does not match pinned intent")
        self.binding = requested
        self.admission_epoch += 1
        self.state = DeploymentGenerationState.CURRENT
        self._old_binding = None
        self._requested_binding = None
        self._migration_effect_begun = False
        self._attempts[self._current_attempt].closed = True
        self._current_attempt = None
        self._finish_pending_leaves()

    def mark_indeterminate(self) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or not self._migration_effect_begun:
            raise ValueError("only an effectful migration can become indeterminate")
        self.state = DeploymentGenerationState.MIGRATION_INDETERMINATE

    def recover_migration(self, proof: MigrationRecoveryProof) -> None:
        if self.state is not DeploymentGenerationState.MIGRATION_INDETERMINATE:
            raise ValueError("migration is not indeterminate")
        if type(proof) is not MigrationRecoveryProof:
            raise TypeError("migration recovery requires exact proof inputs")
        exact = (
            proof.deployment == self.deployment and proof.old_binding == self._old_binding
            and proof.requested_binding == self._requested_binding
            and proof.protocol_epoch == self.protocol_epoch
            and proof.attempt is self._current_attempt
            and proof.requested_binding.generation == proof.old_binding.generation + 1
        )
        if not exact:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "migration recovery proof mismatch")
        if proof.kind is MigrationRecoveryKind.REQUESTED_NEXT_SUCCEEDED:
            self.binding = proof.requested_binding
            self.admission_epoch += 1
            self.state = DeploymentGenerationState.CURRENT
        elif proof.kind is MigrationRecoveryKind.FULL_ROLLBACK_NO_EFFECT:
            self.binding = proof.old_binding
            self.admission_epoch += 1
            self.state = DeploymentGenerationState.CURRENT
        else:
            self.binding = proof.old_binding
            self.state = DeploymentGenerationState.RETIRED
        self._old_binding = None
        self._requested_binding = None
        self._migration_effect_begun = False
        self._attempts[self._current_attempt].closed = True
        self._current_attempt = None
        self._finish_pending_leaves()

    def count(self) -> int:
        return len(self._permits) + len(self._buffers)

    def no_effect_reopen_complete(self, attempt: MigrationAttempt) -> bool:
        if type(attempt) is not MigrationAttempt:
            return False
        record = self._attempts.get(attempt)
        return (
            record is not None and record.closed
            and self.state is DeploymentGenerationState.CURRENT
            and self.binding == record.old_binding
            and self.admission_epoch == record.admission_epoch + 1
            and self._current_attempt is None
        )

    def _attempt_record(self, attempt: MigrationAttempt) -> MigrationAttemptRecord:
        if type(attempt) is not MigrationAttempt:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "exact migration attempt is required")
        record = self._attempts.get(attempt)
        if record is None or record.closed or attempt is not self._current_attempt:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "migration attempt is not current")
        return record

    def attempt_product(self, attempt: MigrationAttempt) -> tuple[DeploymentGenerationState, AttemptPhase, int, MigrationRequestIdentity]:
        record = self._attempt_record(attempt)
        return self.state, record.phase, record.phase_serial, record.phase_request

    def _membership_record(self, membership: ParticipantMembership) -> _MembershipRecord:
        if type(membership) is not ParticipantMembership:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "exact membership required")
        record = self._memberships.get(membership)
        if record is None or record.state is ParticipantState.LEFT:
            raise ContractRefusal(RefusalCode.LEASE_INVALID, "membership is not joined")
        return record

    def _runtime_has_obligations(self, runtime_identity: object) -> bool:
        return any(record.operation.runtime_identity is runtime_identity for record in self._permits.values())

    def _finish_leave(self, membership: ParticipantMembership, record: _MembershipRecord) -> None:
        record.state = ParticipantState.LEFT
        self._participants.discard(membership)
        opened = self._opens[record.open_record]
        opened.state = ParticipantState.LEFT

    def _finish_pending_leaves(self) -> None:
        for membership, record in tuple(self._memberships.items()):
            if record.state is ParticipantState.LEAVE_PENDING and not self._runtime_has_obligations(record.runtime_identity):
                self._finish_leave(membership, record)

    @staticmethod
    def _all_barriers_acknowledged(record: MigrationAttemptRecord) -> bool:
        return record.required == frozenset(record.acknowledged)

    def _validate_activation_evidence(self, evidence: ActivationEvidence) -> None:
        if type(evidence) is not ActivationEvidence:
            raise TypeError("activation requires exact evidence inputs")
        exact = (
            evidence.deployment == self.deployment and evidence.binding == self._attempted_binding
            and evidence.protocol_epoch == self._attempted_protocol_epoch
        )
        if not exact:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "activation evidence mismatch")
        if evidence.protocol != "plan_admission_lifetime_v1":
            raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "lifetime protocol is required")

    def _validate_no_effect_proof(self, proof: ActivationNoEffectRecoveryProof) -> None:
        if type(proof) is not ActivationNoEffectRecoveryProof:
            raise TypeError("activation no-effect recovery requires exact proof inputs")
        exact = (
            proof.deployment == self.deployment and proof.binding == self._attempted_binding
            and proof.attempted_epoch == self._attempted_protocol_epoch
        )
        if not exact:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "activation no-effect proof mismatch")

    def _return_unactivated(self) -> None:
        self.protocol_epoch = None
        self._attempted_protocol_epoch = None
        self._attempted_binding = None
        self._activation_fence_digest = None
        self.activation = ActivationState.UNACTIVATED
