"""Closed proof-input shapes for activation and migration recovery.

These values describe evidence required by future authoritative implementations.
Constructing one in a reference test is not physical or durable proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .semantic import BindingIdentity
from .values import QualifiedDeployment


def _require_digest(value: str, name: str) -> str:
    if type(value) is not str or not value:
        raise ValueError(f"{name} is required")
    return value


@dataclass(frozen=True, slots=True)
class ActivationNoEffectRecoveryProof:
    deployment: QualifiedDeployment
    binding: BindingIdentity
    attempted_epoch: int
    inventory_absence_digest: str
    durable_record_absence_digest: str
    restored_legacy_access_digest: str

    def __post_init__(self) -> None:
        if type(self.deployment) is not QualifiedDeployment:
            raise TypeError("recovery deployment must be qualified")
        if type(self.binding) is not BindingIdentity or self.binding.scope != self.deployment:
            raise ValueError("recovery binding must match the deployment")
        if type(self.attempted_epoch) is not int or self.attempted_epoch < 1:
            raise ValueError("attempted activation epoch must be positive")
        for name in (
            "inventory_absence_digest",
            "durable_record_absence_digest",
            "restored_legacy_access_digest",
        ):
            _require_digest(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class ActivationUnusedWithdrawalProof:
    deployment: QualifiedDeployment
    binding: BindingIdentity
    protocol_epoch: int
    physical_fence_digest: str
    no_ever_open_digest: str
    durable_withdrawal_digest: str
    restored_legacy_access_digest: str

    def __post_init__(self) -> None:
        if type(self.deployment) is not QualifiedDeployment:
            raise TypeError("withdrawal deployment must be qualified")
        if type(self.binding) is not BindingIdentity or self.binding.scope != self.deployment:
            raise ValueError("withdrawal binding must match the deployment")
        if type(self.protocol_epoch) is not int or self.protocol_epoch < 1:
            raise ValueError("withdrawal epoch must be positive")
        for name in (
            "physical_fence_digest",
            "no_ever_open_digest",
            "durable_withdrawal_digest",
            "restored_legacy_access_digest",
        ):
            _require_digest(getattr(self, name), name)


class MigrationRecoveryKind(str, Enum):
    REQUESTED_NEXT_SUCCEEDED = "requested_next_succeeded"
    FULL_ROLLBACK_NO_EFFECT = "full_rollback_no_effect"
    BINDING_NON_REUSE = "binding_non_reuse"


@dataclass(frozen=True, slots=True)
class MigrationRecoveryProof:
    kind: MigrationRecoveryKind
    deployment: QualifiedDeployment
    old_binding: BindingIdentity
    requested_binding: BindingIdentity
    protocol_epoch: int
    outcome_digest: str
    durable_binding_digest: str
    accounting_digest: str

    def __post_init__(self) -> None:
        if type(self.kind) is not MigrationRecoveryKind:
            raise ValueError("migration recovery kind must be an exact declared member")
        if type(self.deployment) is not QualifiedDeployment:
            raise TypeError("migration recovery deployment must be qualified")
        if type(self.old_binding) is not BindingIdentity or type(self.requested_binding) is not BindingIdentity:
            raise TypeError("migration recovery requires exact binding values")
        if self.old_binding.scope != self.deployment or self.requested_binding.scope != self.deployment:
            raise ValueError("migration recovery bindings must match the deployment")
        if self.requested_binding.generation <= self.old_binding.generation:
            raise ValueError("requested migration binding must advance generation")
        if type(self.protocol_epoch) is not int or self.protocol_epoch < 1:
            raise ValueError("migration recovery protocol epoch must be positive")
        _require_digest(self.outcome_digest, "outcome_digest")
        _require_digest(self.durable_binding_digest, "durable_binding_digest")
        _require_digest(self.accounting_digest, "accounting_digest")
