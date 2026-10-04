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
        self._permits: dict[GenerationPermit, _PermitRecord] = {}
        self._buffers: dict[BufferedDeliveryPermit, _BufferPermitRecord] = {}
        self._old_binding: BindingIdentity | None = None
        self._requested_binding: BindingIdentity | None = None
        self._migration_effect_begun = False

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

    def begin_drain(self, expected: BindingIdentity) -> None:
        if self.activation is not ActivationState.ACTIVE:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime protocol is not active")
        if type(expected) is not BindingIdentity or self.state is not DeploymentGenerationState.CURRENT or expected != self.binding:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "migration expected binding mismatch")
        self._old_binding = self.binding
        self._requested_binding = None
        self.state = DeploymentGenerationState.DRAINING_OLD
        self._migration_effect_begun = False

    def reopen_no_effect(self) -> None:
        if self.state is not DeploymentGenerationState.DRAINING_OLD or self._migration_effect_begun:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "old generation cannot reopen")
        self.admission_epoch += 1
        self.state = DeploymentGenerationState.CURRENT
        self._old_binding = None

    def begin_migration(self, requested: BindingIdentity) -> None:
        if self.state is not DeploymentGenerationState.DRAINING_OLD or self.count() != 0:
            raise ContractRefusal(RefusalCode.DEADLINE_EXCEEDED, "old generation is not quiescent")
        if type(requested) is not BindingIdentity or requested.scope != self.deployment:
            raise TypeError("migration requires an exact requested binding")
        if self._old_binding != self.binding or requested.generation <= self.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "requested generation must advance old binding")
        self._requested_binding = requested
        self.state = DeploymentGenerationState.MIGRATING

    def begin_migration_effect(self) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or self._requested_binding is None:
            raise ValueError("migration is not active")
        self._migration_effect_begun = True

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

    def count(self) -> int:
        return len(self._permits) + len(self._buffers)

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
        self.activation = ActivationState.UNACTIVATED
