"""Deterministic deployment generation/activation reference coordinator.

This is executable state-machine evidence only.  It is not an operational,
thread-safe, database-backed, or cross-process coordinator.
"""

from __future__ import annotations

from .admission import OperationIdentity
from .lifetime import (
    ActivationEvidence,
    ActivationState,
    BufferedDelivery,
    DeploymentGenerationState,
    GenerationPermit,
)
from .semantic import BindingIdentity
from .values import ContractRefusal, QualifiedDeployment, RefusalCode


class ReferenceGenerationCoordinator:
    """Single-process reference for the shared coordinator state algebra."""

    def __init__(self, deployment: QualifiedDeployment, binding: BindingIdentity) -> None:
        if binding.scope != deployment:
            raise ValueError("coordinator binding must match deployment")
        self.deployment = deployment
        self.binding = binding
        self.state = DeploymentGenerationState.CURRENT
        self.activation = ActivationState.UNACTIVATED
        self.protocol_epoch: int | None = None
        self.admission_epoch = 1
        self._permits: dict[OperationIdentity, GenerationPermit] = {}
        self._buffers: set[int] = set()
        self._migration_effect_begun = False

    def finish_activation(self, evidence: ActivationEvidence) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        if type(evidence) is not ActivationEvidence:
            raise TypeError("activation requires exact evidence inputs")
        if evidence.deployment != self.deployment or evidence.binding != self.binding:
            raise ValueError("activation evidence belongs to another binding")
        if evidence.protocol != "plan_admission_lifetime_v1":
            raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "lifetime protocol is required")
        self.protocol_epoch = evidence.protocol_epoch
        self.activation = ActivationState.ACTIVE_UNUSED

    def begin_activation(self) -> None:
        if self.activation is not ActivationState.UNACTIVATED:
            raise ValueError("only an unactivated deployment can begin activation")
        self.activation = ActivationState.ACTIVATING

    def refuse_activation_no_effect(self) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        self.activation = ActivationState.UNACTIVATED

    def mark_activation_indeterminate(self) -> None:
        if self.activation is not ActivationState.ACTIVATING:
            raise ValueError("activation is not in progress")
        self.activation = ActivationState.ACTIVATION_INDETERMINATE

    def recover_activation(self, evidence: ActivationEvidence | None) -> None:
        if self.activation is not ActivationState.ACTIVATION_INDETERMINATE:
            raise ValueError("activation is not indeterminate")
        if evidence is None:
            self.protocol_epoch = None
            self.activation = ActivationState.UNACTIVATED
        else:
            if type(evidence) is not ActivationEvidence:
                raise TypeError("activation recovery requires exact evidence inputs")
            if evidence.deployment != self.deployment or evidence.binding != self.binding:
                raise ValueError("activation evidence belongs to another binding")
            if evidence.protocol != "plan_admission_lifetime_v1":
                raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "lifetime protocol is required")
            self.protocol_epoch = evidence.protocol_epoch
            self.activation = ActivationState.ACTIVE_UNUSED

    def first_lifetime_open(self, protocol: str, epoch: int) -> None:
        if protocol != "plan_admission_lifetime_v1":
            raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "missing lifetime capability")
        if type(epoch) is not int or self.activation is not ActivationState.ACTIVE_UNUSED or epoch != self.protocol_epoch:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "active unused epoch mismatch")
        self.activation = ActivationState.ACTIVE

    def withdraw_unused(self, epoch: int) -> None:
        if self.activation is not ActivationState.ACTIVE_UNUSED or epoch != self.protocol_epoch:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "no unused activation at this epoch")
        self.activation = ActivationState.UNACTIVATED
        self.protocol_epoch = None

    def refuse_retirement_or_reset(self) -> None:
        raise ContractRefusal(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, "active protocol has no reset or retirement edge")

    def acquire_shared(self, operation: OperationIdentity) -> GenerationPermit:
        if self.activation is not ActivationState.ACTIVE:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime protocol is not active")
        if self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "generation is not admitting work")
        if type(operation) is not OperationIdentity:
            raise TypeError("shared permit requires an exact operation identity")
        if operation.deployment != self.deployment or operation.generation != self.binding.generation:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "operation generation mismatch")
        if operation in self._permits:
            raise ValueError("operation already owns a shared permit")
        permit = GenerationPermit(operation, self.admission_epoch)
        self._permits[operation] = permit
        return permit

    def release_shared(self, permit: GenerationPermit) -> None:
        if self._permits.get(permit.operation) != permit:
            raise ValueError("generation permit is not live")
        del self._permits[permit.operation]

    def add_buffer(self, envelope: BufferedDelivery) -> None:
        if self.state is not DeploymentGenerationState.CURRENT:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "buffer enqueue is fenced")
        token = id(envelope)
        if token in self._buffers:
            raise ValueError("buffer permit already exists")
        self._buffers.add(token)

    def release_buffer(self, envelope: BufferedDelivery) -> None:
        token = id(envelope)
        if token not in self._buffers:
            raise ValueError("buffer permit is not live")
        self._buffers.remove(token)

    def begin_drain(self, expected: BindingIdentity) -> None:
        if self.activation is not ActivationState.ACTIVE:
            raise ContractRefusal(RefusalCode.ACTIVATION_REQUIRED, "lifetime protocol is not active")
        if type(expected) is not BindingIdentity or self.state is not DeploymentGenerationState.CURRENT or expected != self.binding:
            raise ContractRefusal(RefusalCode.GENERATION_MISMATCH, "migration expected binding mismatch")
        self.state = DeploymentGenerationState.DRAINING_OLD
        self._migration_effect_begun = False

    def reopen_no_effect(self) -> None:
        if self.state is not DeploymentGenerationState.DRAINING_OLD or self._migration_effect_begun:
            raise ContractRefusal(RefusalCode.MIGRATION_INDETERMINATE, "old generation cannot reopen")
        self.admission_epoch += 1
        self.state = DeploymentGenerationState.CURRENT

    def begin_migration(self) -> None:
        if self.state is not DeploymentGenerationState.DRAINING_OLD or self.count() != 0:
            raise ContractRefusal(RefusalCode.DEADLINE_EXCEEDED, "old generation is not quiescent")
        self.state = DeploymentGenerationState.MIGRATING

    def begin_migration_effect(self) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING:
            raise ValueError("migration is not active")
        self._migration_effect_begun = True

    def publish_generation(self, requested: BindingIdentity) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or not self._migration_effect_begun:
            raise ValueError("migration effect/publication order is invalid")
        if type(requested) is not BindingIdentity:
            raise TypeError("generation publication requires an exact binding")
        if requested.scope != self.deployment or requested.generation <= self.binding.generation:
            raise ValueError("requested generation must advance this deployment")
        self.binding = requested
        self.admission_epoch += 1
        self.state = DeploymentGenerationState.CURRENT
        self._migration_effect_begun = False

    def mark_indeterminate(self) -> None:
        if self.state is not DeploymentGenerationState.MIGRATING or not self._migration_effect_begun:
            raise ValueError("only an effectful migration can become indeterminate")
        self.state = DeploymentGenerationState.MIGRATION_INDETERMINATE

    def count(self) -> int:
        return len(self._permits) + len(self._buffers)
